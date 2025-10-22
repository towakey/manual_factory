"""
Response handler for CGI application
Python 3.7+ standard library only
"""

import sys
from http.cookies import SimpleCookie


class Response:
    """HTTP Response wrapper for CGI"""
    
    def __init__(self):
        self.status = 200
        self.headers = {}
        self.cookies = SimpleCookie()
        self.body = ''
        
    def set_header(self, key, value):
        """Set HTTP header"""
        self.headers[key] = value
    
    def set_cookie(self, key, value, max_age=None, path='/', httponly=True, samesite='Lax'):
        """Set cookie"""
        self.cookies[key] = value
        if max_age:
            self.cookies[key]['max-age'] = max_age
        self.cookies[key]['path'] = path
        if httponly:
            self.cookies[key]['httponly'] = True
        self.cookies[key]['samesite'] = samesite
    
    def delete_cookie(self, key, path='/'):
        """Delete cookie"""
        self.cookies[key] = ''
        self.cookies[key]['max-age'] = 0
        self.cookies[key]['path'] = path
    
    def redirect(self, location, status=302):
        """Redirect to another URL"""
        self.status = status
        self.set_header('Location', location)
        self.body = ''
    
    def send(self):
        """Send response to client"""
        # Status line
        status_messages = {
            200: 'OK',
            302: 'Found',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            500: 'Internal Server Error'
        }
        status_message = status_messages.get(self.status, 'OK')
        
        # Default content type
        if 'Content-Type' not in self.headers:
            self.headers['Content-Type'] = 'text/html; charset=utf-8'
        
        # Output headers
        print(f'Status: {self.status} {status_message}')
        
        for key, value in self.headers.items():
            print(f'{key}: {value}')
        
        # Output cookies
        for cookie in self.cookies.values():
            print(f'Set-Cookie: {cookie.OutputString()}')
        
        # Empty line to separate headers from body
        print()
        
        # Output body
        if isinstance(self.body, str):
            sys.stdout.write(self.body)
        elif isinstance(self.body, bytes):
            sys.stdout.buffer.write(self.body)
        
        sys.stdout.flush()
