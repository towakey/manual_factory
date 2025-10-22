"""
Authentication system for CGI application
Python 3.7+ standard library only
"""

import hashlib
import secrets


class Auth:
    """Authentication utilities"""
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return f'{salt}${hashed}'
    
    @staticmethod
    def verify_password(password, hashed_password):
        """Verify password against hash"""
        try:
            salt, expected_hash = hashed_password.split('$')
            actual_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
            return secrets.compare_digest(actual_hash, expected_hash)
        except Exception:
            return False
    
    @staticmethod
    def generate_token(length=32):
        """Generate secure random token"""
        return secrets.token_urlsafe(length)


def login_required(func):
    """Decorator for routes that require authentication"""
    def wrapper(request, response, session, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            response.redirect('/')
            return response
        return func(request, response, session, **kwargs)
    return wrapper


def admin_required(func):
    """Decorator for routes that require admin role"""
    def wrapper(request, response, session, **kwargs):
        user_id = session.get('user_id')
        is_admin = session.get('is_admin', False)
        
        if not user_id:
            response.redirect('/')
            return response
        
        if not is_admin:
            response.status = 403
            response.body = '<h1>403 Forbidden</h1><p>Admin access required</p>'
            return response
        
        return func(request, response, session, **kwargs)
    return wrapper
