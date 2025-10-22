"""
WSGI Application Framework
Python 3.7+ standard library only
"""

import sys
import traceback
from urllib.parse import parse_qs
from http.cookies import SimpleCookie
from .session import Session


class WSGIRequest:
    """WSGI Request wrapper"""
    
    def __init__(self, environ):
        self.environ = environ
        self.method = environ.get('REQUEST_METHOD', 'GET')
        self.path = environ.get('PATH_INFO', '/')
        self.query_string = environ.get('QUERY_STRING', '')
        
        # Parse query parameters
        self.args = parse_qs(self.query_string)
        # Convert lists to single values
        self.args = {k: v[0] if len(v) == 1 else v for k, v in self.args.items()}
        
        # Parse form data
        self.form = {}
        self.files = {}
        
        if self.method == 'POST':
            self._parse_post_data()
        
        # Parse cookies
        self.cookies = self._parse_cookies()
    
    def _parse_cookies(self):
        """Parse HTTP cookies"""
        cookie_string = self.environ.get('HTTP_COOKIE', '')
        if not cookie_string:
            return {}
        
        cookie = SimpleCookie()
        cookie.load(cookie_string)
        return {k: v.value for k, v in cookie.items()}
    
    def _parse_post_data(self):
        """Parse POST data"""
        try:
            content_length = int(self.environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            content_length = 0
        
        if content_length <= 0:
            return
        
        # Read POST data
        post_data = self.environ['wsgi.input'].read(content_length)
        content_type = self.environ.get('CONTENT_TYPE', '')
        
        if 'application/x-www-form-urlencoded' in content_type:
            # Form data
            parsed = parse_qs(post_data.decode('utf-8'))
            self.form = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
            
        elif 'multipart/form-data' in content_type:
            # File upload
            self._parse_multipart(post_data, content_type)
            
        elif 'application/json' in content_type:
            # JSON data
            import json
            self.form = json.loads(post_data.decode('utf-8'))
    
    def _parse_multipart(self, data, content_type):
        """Parse multipart/form-data"""
        # Extract boundary
        boundary = None
        for part in content_type.split(';'):
            if 'boundary=' in part:
                boundary = part.split('=')[1].strip()
                break
        
        if not boundary:
            return
        
        # Split by boundary
        boundary_bytes = ('--' + boundary).encode('utf-8')
        parts = data.split(boundary_bytes)
        
        for part in parts[1:-1]:
            if not part or part == b'--\r\n':
                continue
            
            try:
                header_end = part.find(b'\r\n\r\n')
                if header_end == -1:
                    continue
                
                headers = part[:header_end].decode('utf-8')
                content = part[header_end+4:]
                
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
                        self.files[name] = {
                            'filename': filename,
                            'content': content
                        }
                    else:
                        self.form[name] = content.decode('utf-8')
            except Exception:
                continue
    
    def get(self, key, default=None):
        """Get form or query parameter"""
        return self.form.get(key) or self.args.get(key, default)


class WSGIResponse:
    """WSGI Response wrapper"""
    
    def __init__(self):
        self.status = '200 OK'
        self.headers = [('Content-Type', 'text/html; charset=utf-8')]
        self.cookies = SimpleCookie()
        self.body = b''
    
    def set_status(self, code):
        """Set HTTP status"""
        status_messages = {
            200: 'OK',
            302: 'Found',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            500: 'Internal Server Error'
        }
        message = status_messages.get(code, 'OK')
        self.status = f'{code} {message}'
    
    def set_header(self, key, value):
        """Set HTTP header"""
        # Remove existing header with same key
        self.headers = [(k, v) for k, v in self.headers if k.lower() != key.lower()]
        self.headers.append((key, value))
    
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
    
    def redirect(self, location):
        """Redirect to another URL"""
        self.set_status(302)
        self.set_header('Location', location)
        self.body = b''
    
    def get_headers(self):
        """Get all headers including cookies"""
        headers = self.headers.copy()
        for cookie in self.cookies.values():
            headers.append(('Set-Cookie', cookie.OutputString()))
        return headers


class WSGIApp:
    """WSGI Application"""
    
    def __init__(self):
        self.routes = {}
    
    def route(self, pattern, methods=None):
        """Route decorator"""
        if methods is None:
            methods = ['GET']
        
        def decorator(func):
            for method in methods:
                key = f'{method}:{pattern}'
                self.routes[key] = func
            return func
        return decorator
    
    def match_route(self, path, method):
        """Match path to route"""
        # Exact match
        key = f'{method}:{path}'
        if key in self.routes:
            return self.routes[key], {}
        
        # Pattern match with parameters
        for route_key, handler in self.routes.items():
            route_method, route_pattern = route_key.split(':', 1)
            if route_method != method:
                continue
            
            # Simple pattern matching: /manual/<manual_id>
            if '<' in route_pattern:
                pattern_parts = route_pattern.split('/')
                path_parts = path.split('/')
                
                if len(pattern_parts) != len(path_parts):
                    continue
                
                params = {}
                match = True
                
                for pp, path_part in zip(pattern_parts, path_parts):
                    if pp.startswith('<') and pp.endswith('>'):
                        # Extract parameter: <int:manual_id> -> manual_id
                        param_def = pp[1:-1]
                        if ':' in param_def:
                            param_type, param_name = param_def.split(':', 1)
                            # Convert to type if specified
                            if param_type == 'int':
                                try:
                                    params[param_name] = int(path_part)
                                except ValueError:
                                    match = False
                                    break
                            else:
                                params[param_name] = path_part
                        else:
                            params[param_def] = path_part
                    elif pp != path_part:
                        match = False
                        break
                
                if match:
                    return handler, params
        
        return None, {}
    
    def __call__(self, environ, start_response):
        """WSGI application entry point"""
        try:
            # Create request and response
            request = WSGIRequest(environ)
            response = WSGIResponse()
            
            # Load or create session
            session_id = request.cookies.get('session_id')
            session = Session(session_id)
            
            # Match route
            handler, params = self.match_route(request.path, request.method)
            
            if handler:
                # Call handler
                result = handler(request, response, session, **params)
                
                # Save session
                session.save()
                
                # Use returned response if any
                if result is not None:
                    response = result
                
                # Always ensure session cookie is set
                # This is important for redirects and new sessions
                response.set_cookie('session_id', session.session_id, max_age=3600*24*30)
            else:
                # 404 Not Found
                response.set_status(404)
                response.body = b'<h1>404 Not Found</h1>'
            
            # Prepare response
            if isinstance(response.body, str):
                response.body = response.body.encode('utf-8')
            
            # Start response
            start_response(response.status, response.get_headers())
            return [response.body]
        
        except Exception as e:
            # 500 Internal Server Error
            error_trace = ''.join(traceback.format_exception(
                type(e), e, e.__traceback__
            ))
            
            error_html = f'''
            <h1>500 Internal Server Error</h1>
            <pre style="background:#f5f5f5;padding:20px;border:1px solid #ddd;">
{error_trace}
            </pre>
            '''
            
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/html; charset=utf-8')
            ])
            return [error_html.encode('utf-8')]
