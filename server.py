#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Manual Factory - Built-in HTTP Server
Python 3.7+ standard library only
"""

import sys
import os
from http.server import HTTPServer, CGIHTTPRequestHandler
from functools import partial

# Add current directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Change to the manual_factory directory
os.chdir(BASE_DIR)

class CustomCGIHandler(CGIHTTPRequestHandler):
    """Custom CGI handler"""
    
    def is_cgi(self):
        """Check if path is a CGI script"""
        path = self.path
        
        # Remove query string
        if '?' in path:
            path = path[:path.index('?')]
        
        # Check if it's app_cgi.py
        if path.endswith('app_cgi.py') or path == '/' or path == '':
            return True
        
        return False
    
    def do_GET(self):
        """Handle GET request"""
        # Redirect / to app_cgi.py
        if self.path == '/' or self.path == '':
            self.path = '/app_cgi.py'
        
        # Check if it's a static file
        if self.path.startswith('/static/') or \
           self.path.startswith('/uploads/'):
            return CGIHTTPRequestHandler.do_GET(self)
        
        # Otherwise, route to app_cgi.py
        if not self.path.startswith('/app_cgi.py'):
            # Store original path for CGI
            query = self.path[1:]  # Remove leading /
            self.path = f'/app_cgi.py?{query}'
        
        # Handle as CGI
        if self.is_cgi():
            self.run_cgi()
        else:
            CGIHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """Handle POST request"""
        # Redirect to app_cgi.py
        if not self.path.startswith('/app_cgi.py'):
            query = self.path[1:]
            self.path = f'/app_cgi.py?{query}'
        
        if self.is_cgi():
            self.run_cgi()
        else:
            CGIHTTPRequestHandler.do_POST(self)


def run_server(port=8080):
    """Run the server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, CustomCGIHandler)
    
    print(f"""
===============================================================
        Manual Factory - CGI Application Server
             Python 3.7+ Standard Library Only
===============================================================

Server running at: http://localhost:{port}/

Default login:
  Email: admin@example.com
  Password: admin123

Press Ctrl+C to stop the server.
""")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        httpd.shutdown()


if __name__ == '__main__':
    import config
    
    # Ensure directories exist
    os.makedirs(config.SESSION_DIR, exist_ok=True)
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    
    # Check if database exists
    if not os.path.exists(config.DATABASE_PATH):
        print("[WARNING] Database not found. Running initialization...")
        os.system('python init_db_cgi.py')
        print("")
    
    # Get port from command line
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}, using default 8080")
    
    run_server(port)
