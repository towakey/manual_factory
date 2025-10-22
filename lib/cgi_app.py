"""
CGI Application Framework
Python 3.7+ standard library only
"""

import sys
import traceback
from .request import Request
from .response import Response
from .router import Router
from .session import Session


class CGIApp:
    """Main CGI application"""
    
    def __init__(self):
        self.router = Router()
    
    def route(self, pattern, methods=None):
        """Route decorator"""
        return self.router.route(pattern, methods)
    
    def run(self):
        """Run CGI application"""
        try:
            # Create request and response objects
            request = Request()
            response = Response()
            
            # Load or create session
            session_id = request.cookies.get('session_id')
            session = Session(session_id)
            
            # Set session cookie if new
            if not session_id:
                response.set_cookie('session_id', session.session_id, max_age=3600*24*30)
            
            # Match route
            handler, params = self.router.match(request.path, request.method)
            
            if handler:
                # Call handler
                result = handler(request, response, session, **params)
                
                # Save session
                session.save()
                
                # Send response
                if result is not None:
                    result.send()
                else:
                    response.send()
            else:
                # 404 Not Found
                response.status = 404
                response.body = '<h1>404 Not Found</h1>'
                response.send()
        
        except Exception as e:
            # 500 Internal Server Error
            error_response = Response()
            error_response.status = 500
            error_response.body = self._format_error(e)
            error_response.send()
    
    def _format_error(self, error):
        """Format error message"""
        error_trace = ''.join(traceback.format_exception(
            type(error), error, error.__traceback__
        ))
        
        # In production, log this and show a generic error
        # For development, show full traceback
        return f'''
        <h1>500 Internal Server Error</h1>
        <pre style="background:#f5f5f5;padding:20px;border:1px solid #ddd;">
{error_trace}
        </pre>
        '''
