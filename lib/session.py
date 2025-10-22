"""
Session management for CGI application
Python 3.7+ standard library only
"""

import os
import json
import time
import secrets
from pathlib import Path


class Session:
    """File-based session management"""
    
    SESSION_DIR = None
    SESSION_LIFETIME = 3600 * 24  # 24 hours
    
    def __init__(self, session_id=None):
        if Session.SESSION_DIR is None:
            raise ValueError("SESSION_DIR not configured")
        
        self.session_id = session_id or self._generate_session_id()
        self.data = {}
        self.modified = False
        
        if session_id:
            self._load()
    
    @staticmethod
    def _generate_session_id():
        """Generate secure session ID"""
        return secrets.token_urlsafe(32)
    
    def _get_session_file(self):
        """Get session file path"""
        return Path(Session.SESSION_DIR) / f'sess_{self.session_id}'
    
    def _load(self):
        """Load session from file"""
        session_file = self._get_session_file()
        
        if not session_file.exists():
            return
        
        # Check expiration
        if time.time() - session_file.stat().st_mtime > Session.SESSION_LIFETIME:
            session_file.unlink()
            return
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception:
            self.data = {}
    
    def save(self):
        """Save session to file"""
        if not self.modified and self._get_session_file().exists():
            # Touch file to update mtime
            os.utime(self._get_session_file(), None)
            return
        
        session_file = self._get_session_file()
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f)
        except Exception as e:
            pass
    
    def get(self, key, default=None):
        """Get session value"""
        return self.data.get(key, default)
    
    def set(self, key, value):
        """Set session value"""
        self.data[key] = value
        self.modified = True
    
    def delete(self, key):
        """Delete session key"""
        if key in self.data:
            del self.data[key]
            self.modified = True
    
    def clear(self):
        """Clear all session data"""
        self.data = {}
        self.modified = True
    
    def destroy(self):
        """Destroy session"""
        session_file = self._get_session_file()
        if session_file.exists():
            try:
                session_file.unlink()
            except Exception:
                pass
        self.data = {}
    
    @staticmethod
    def cleanup_expired():
        """Clean up expired sessions"""
        if Session.SESSION_DIR is None:
            return
        
        session_dir = Path(Session.SESSION_DIR)
        if not session_dir.exists():
            return
        
        current_time = time.time()
        for session_file in session_dir.glob('sess_*'):
            try:
                if current_time - session_file.stat().st_mtime > Session.SESSION_LIFETIME:
                    session_file.unlink()
            except Exception:
                continue
