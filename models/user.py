"""
User model
Python 3.7+ standard library only
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.database import Database
from lib.auth import Auth


class User:
    """User model"""
    
    @staticmethod
    def create(name, email, password, role='user', department=None):
        """Create a new user"""
        password_hash = Auth.hash_password(password)
        query = """
            INSERT INTO users (name, email, password_hash, role, department)
            VALUES (?, ?, ?, ?, ?)
        """
        return Database.execute(query, (name, email, password_hash, role, department))
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        query = "SELECT * FROM users WHERE id = ? AND deleted_at IS NULL"
        return Database.execute(query, (user_id,), fetch_one=True)
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        query = "SELECT * FROM users WHERE email = ? AND deleted_at IS NULL"
        return Database.execute(query, (email,), fetch_one=True)
    
    @staticmethod
    def verify_password(user, password):
        """Verify user password"""
        if not user:
            return False
        return Auth.verify_password(password, user['password_hash'])
    
    @staticmethod
    def update(user_id, **kwargs):
        """Update user information"""
        allowed_fields = ['name', 'email', 'department', 'role', 'is_active']
        updates = []
        params = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        Database.execute(query, tuple(params))
        return True
    
    @staticmethod
    def update_password(user_id, new_password):
        """Update user password"""
        password_hash = Auth.hash_password(new_password)
        query = "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        Database.execute(query, (password_hash, user_id))
        return True
    
    @staticmethod
    def delete(user_id):
        """Soft delete user"""
        query = "UPDATE users SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?"
        Database.execute(query, (user_id,))
        return True
    
    @staticmethod
    def get_all(include_deleted=False):
        """Get all users"""
        if include_deleted:
            query = "SELECT * FROM users ORDER BY created_at DESC"
        else:
            query = "SELECT * FROM users WHERE deleted_at IS NULL ORDER BY created_at DESC"
        return Database.execute(query, fetch_all=True)
    
    @staticmethod
    def count(role=None):
        """Count users"""
        if role:
            query = "SELECT COUNT(*) as count FROM users WHERE role = ? AND deleted_at IS NULL"
            result = Database.execute(query, (role,), fetch_one=True)
        else:
            query = "SELECT COUNT(*) as count FROM users WHERE deleted_at IS NULL"
            result = Database.execute(query, fetch_one=True)
        
        return result['count'] if result else 0
