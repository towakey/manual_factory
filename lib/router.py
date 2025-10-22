"""
Router for CGI application
Python 3.7+ standard library only
"""

import re


class Router:
    """URL router"""
    
    def __init__(self):
        self.routes = []
    
    def add_route(self, pattern, handler, methods=None):
        """Add route"""
        if methods is None:
            methods = ['GET']
        
        # Convert pattern to regex
        # /users/<id> -> /users/(?P<id>[^/]+)
        regex_pattern = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', pattern)
        regex_pattern = '^' + regex_pattern + '$'
        
        self.routes.append({
            'pattern': pattern,
            'regex': re.compile(regex_pattern),
            'handler': handler,
            'methods': methods
        })
    
    def route(self, pattern, methods=None):
        """Decorator for adding routes"""
        def decorator(func):
            self.add_route(pattern, func, methods)
            return func
        return decorator
    
    def match(self, path, method):
        """Match path to route"""
        for route in self.routes:
            match = route['regex'].match(path)
            if match and method in route['methods']:
                return route['handler'], match.groupdict()
        return None, {}
