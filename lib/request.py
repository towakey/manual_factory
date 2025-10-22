"""
Request handler for CGI application
Python 3.7+ standard library only
"""

import os
import sys
import json
from urllib.parse import parse_qs, unquote
from http.cookies import SimpleCookie


class Request:
    """HTTP Request wrapper for CGI"""
    
    def __init__(self):
        self.method = os.environ.get('REQUEST_METHOD', 'GET')
        self.path = os.environ.get('PATH_INFO', '/')
        self.query_string = os.environ.get('QUERY_STRING', '')
        self.content_type = os.environ.get('CONTENT_TYPE', '')
        self.content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        
        # Parse query parameters
        self.args = self._parse_query_string()
        
        # Parse form data
        self.form = {}
        self.files = {}
        if self.method == 'POST':
            self._parse_post_data()
        
        # Parse cookies
        self.cookies = self._parse_cookies()
        
    def _parse_query_string(self):
        """Parse URL query string"""
        if not self.query_string:
            return {}
        
        parsed = parse_qs(self.query_string)
        # Convert lists to single values
        return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
    
    def _parse_cookies(self):
        """Parse HTTP cookies"""
        cookie_string = os.environ.get('HTTP_COOKIE', '')
        if not cookie_string:
            return {}
        
        cookie = SimpleCookie()
        cookie.load(cookie_string)
        return {k: v.value for k, v in cookie.items()}
    
    def _parse_post_data(self):
        """Parse POST data"""
        if self.content_length <= 0:
            return
        
        # Read POST data
        post_data = sys.stdin.buffer.read(self.content_length)
        
        if 'application/x-www-form-urlencoded' in self.content_type:
            # Form data
            parsed = parse_qs(post_data.decode('utf-8'))
            self.form = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
            
        elif 'multipart/form-data' in self.content_type:
            # File upload
            self._parse_multipart(post_data)
            
        elif 'application/json' in self.content_type:
            # JSON data
            self.form = json.loads(post_data.decode('utf-8'))
    
    def _parse_multipart(self, data):
        """Parse multipart/form-data"""
        # Extract boundary
        boundary = None
        for part in self.content_type.split(';'):
            if 'boundary=' in part:
                boundary = part.split('=')[1].strip()
                break
        
        if not boundary:
            return
        
        # Split by boundary
        boundary_bytes = ('--' + boundary).encode('utf-8')
        parts = data.split(boundary_bytes)
        
        for part in parts[1:-1]:  # Skip first empty and last closing
            if not part or part == b'--\r\n':
                continue
            
            # Split headers and content
            try:
                header_end = part.find(b'\r\n\r\n')
                if header_end == -1:
                    continue
                
                headers = part[:header_end].decode('utf-8')
                content = part[header_end+4:]
                
                # Remove trailing \r\n
                if content.endswith(b'\r\n'):
                    content = content[:-2]
                
                # Parse Content-Disposition
                name = None
                filename = None
                for line in headers.split('\r\n'):
                    if line.startswith('Content-Disposition:'):
                        for item in line.split(';'):
                            if 'name=' in item:
                                name = item.split('=')[1].strip('"')
                            elif 'filename=' in item:
                                filename = item.split('=')[1].strip('"')
                
                if name:
                    if filename:
                        # File upload
                        self.files[name] = {
                            'filename': filename,
                            'content': content
                        }
                    else:
                        # Regular form field
                        self.form[name] = content.decode('utf-8')
            except Exception:
                continue
    
    def get(self, key, default=None):
        """Get form or query parameter"""
        return self.form.get(key) or self.args.get(key, default)
