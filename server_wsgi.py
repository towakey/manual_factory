#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Manual Factory - Multi-threaded WSGI Server
Python 3.7+ standard library only
"""

import sys
import os
from wsgiref.simple_server import make_server, WSGIServer
from socketserver import ThreadingMixIn

# Add current directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import config


class ThreadedWSGIServer(ThreadingMixIn, WSGIServer):
    """Multi-threaded WSGI server"""
    daemon_threads = True
    allow_reuse_address = True


def run_server(port=8000, host='0.0.0.0'):
    """Run multi-threaded WSGI server"""
    from app_wsgi import application
    
    # Ensure directories exist
    os.makedirs(config.SESSION_DIR, exist_ok=True)
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    
    # Check if database exists
    if not os.path.exists(config.DATABASE_PATH):
        print("[WARNING] Database not found. Running initialization...")
        os.system('python init_db_cgi.py')
        print("")
    
    print(f"""
===============================================================
   Manual Factory - Multi-threaded WSGI Server
        Python 3.7+ Standard Library Only
===============================================================

Server running at: http://localhost:{port}/
Listening on: {host}:{port}

Features:
  - Multi-threaded request handling
  - Keep-alive connections
  - Better performance than CGI

Default login:
  Email: admin@example.com
  Password: admin123

Press Ctrl+C to stop the server.
""")
    
    httpd = make_server(host, port, application, server_class=ThreadedWSGIServer)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        httpd.shutdown()


if __name__ == '__main__':
    port = 8000
    host = '0.0.0.0'  # Listen on all interfaces
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}, using default 8000")
    
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    run_server(port, host)
