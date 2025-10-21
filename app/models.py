# -*- coding: utf-8 -*-
"""
Database models
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import execute_query, execute_many, get_db


class User:
    """User model"""
    
    @staticmethod
    def create(name, email, password, role='user', department=None):
        """Create a new user"""
        password_hash = generate_password_hash(password)
        query = """
            INSERT INTO users (name, email, password_hash, role, department)
            VALUES (?, ?, ?, ?, ?)
        """
        return execute_query(query, (name, email, password_hash, role, department))
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        query = "SELECT * FROM users WHERE id = ? AND deleted_at IS NULL"
        return execute_query(query, (user_id,), fetch_one=True)
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        query = "SELECT * FROM users WHERE email = ? AND deleted_at IS NULL"
        return execute_query(query, (email,), fetch_one=True)
    
    @staticmethod
    def verify_password(user, password):
        """Verify user password"""
        if not user:
            return False
        return check_password_hash(user['password_hash'], password)
    
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
        execute_query(query, tuple(params))
        return True
    
    @staticmethod
    def update_password(user_id, new_password):
        """Update user password"""
        password_hash = generate_password_hash(new_password)
        query = "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        execute_query(query, (password_hash, user_id))
        return True
    
    @staticmethod
    def soft_delete(user_id):
        """Soft delete user"""
        query = "UPDATE users SET deleted_at = CURRENT_TIMESTAMP, is_active = 0 WHERE id = ?"
        execute_query(query, (user_id,))
        return True
    
    @staticmethod
    def get_all(include_deleted=False):
        """Get all users"""
        if include_deleted:
            query = "SELECT * FROM users ORDER BY created_at DESC"
        else:
            query = "SELECT * FROM users WHERE deleted_at IS NULL ORDER BY created_at DESC"
        return execute_query(query, fetch_all=True)


class Manual:
    """Manual model"""
    
    @staticmethod
    def create(title, description, tags, status, visibility, author_id):
        """Create a new manual"""
        query = """
            INSERT INTO manuals (title, description, tags, status, visibility, author_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return execute_query(query, (title, description, tags, status, visibility, author_id))
    
    @staticmethod
    def find_by_id(manual_id, include_deleted=False):
        """Find manual by ID"""
        if include_deleted:
            query = "SELECT * FROM manuals WHERE id = ?"
        else:
            query = "SELECT * FROM manuals WHERE id = ? AND deleted_at IS NULL"
        return execute_query(query, (manual_id,), fetch_one=True)
    
    @staticmethod
    def get_all(status=None, author_id=None, limit=None, offset=0):
        """Get all manuals with optional filters"""
        query = "SELECT * FROM manuals WHERE deleted_at IS NULL"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if author_id:
            query += " AND author_id = ?"
            params.append(author_id)
        
        query += " ORDER BY updated_at DESC"
        
        if limit:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        return execute_query(query, tuple(params), fetch_all=True)
    
    @staticmethod
    def search(keyword=None, tags=None, author_id=None, status=None, limit=None, offset=0):
        """Search manuals"""
        query = """
            SELECT m.*, u.name as author_name
            FROM manuals m
            LEFT JOIN users u ON m.author_id = u.id
            WHERE m.deleted_at IS NULL
        """
        params = []
        
        if keyword:
            query += " AND (m.title LIKE ? OR m.description LIKE ?)"
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern])
        
        if tags:
            query += " AND m.tags LIKE ?"
            params.append(f"%{tags}%")
        
        if author_id:
            query += " AND m.author_id = ?"
            params.append(author_id)
        
        if status:
            query += " AND m.status = ?"
            params.append(status)
        
        query += " ORDER BY m.updated_at DESC"
        
        if limit:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        return execute_query(query, tuple(params), fetch_all=True)
    
    @staticmethod
    def update(manual_id, **kwargs):
        """Update manual"""
        allowed_fields = ['title', 'description', 'tags', 'status', 'visibility']
        updates = []
        params = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(manual_id)
        
        query = f"UPDATE manuals SET {', '.join(updates)} WHERE id = ?"
        execute_query(query, tuple(params))
        return True
    
    @staticmethod
    def soft_delete(manual_id):
        """Soft delete manual"""
        query = "UPDATE manuals SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?"
        execute_query(query, (manual_id,))
        return True
    
    @staticmethod
    def count(status=None, author_id=None):
        """Count manuals"""
        query = "SELECT COUNT(*) as count FROM manuals WHERE deleted_at IS NULL"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if author_id:
            query += " AND author_id = ?"
            params.append(author_id)
        
        result = execute_query(query, tuple(params), fetch_one=True)
        return result['count'] if result else 0


class ManualStep:
    """Manual step model"""
    
    @staticmethod
    def create(manual_id, step_number, title, content, image_path=None):
        """Create a new step"""
        query = """
            INSERT INTO manual_steps (manual_id, step_number, title, content, image_path)
            VALUES (?, ?, ?, ?, ?)
        """
        return execute_query(query, (manual_id, step_number, title, content, image_path))
    
    @staticmethod
    def create_many(steps_data):
        """Create multiple steps at once"""
        query = """
            INSERT INTO manual_steps (manual_id, step_number, title, content, image_path)
            VALUES (?, ?, ?, ?, ?)
        """
        return execute_many(query, steps_data)
    
    @staticmethod
    def get_by_manual(manual_id):
        """Get all steps for a manual"""
        query = "SELECT * FROM manual_steps WHERE manual_id = ? ORDER BY step_number ASC"
        return execute_query(query, (manual_id,), fetch_all=True)
    
    @staticmethod
    def update(step_id, **kwargs):
        """Update step"""
        allowed_fields = ['step_number', 'title', 'content', 'image_path']
        updates = []
        params = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(step_id)
        
        query = f"UPDATE manual_steps SET {', '.join(updates)} WHERE id = ?"
        execute_query(query, tuple(params))
        return True
    
    @staticmethod
    def delete_by_manual(manual_id):
        """Delete all steps for a manual"""
        query = "DELETE FROM manual_steps WHERE manual_id = ?"
        execute_query(query, (manual_id,))
        return True


class ManualHistory:
    """Manual history model"""
    
    @staticmethod
    def create(manual_id, user_id, action, changes=None):
        """Create a history entry"""
        query = """
            INSERT INTO manual_history (manual_id, user_id, action, changes)
            VALUES (?, ?, ?, ?)
        """
        return execute_query(query, (manual_id, user_id, action, changes))
    
    @staticmethod
    def get_by_manual(manual_id, limit=None):
        """Get history for a manual"""
        query = """
            SELECT h.*, u.name as user_name
            FROM manual_history h
            LEFT JOIN users u ON h.user_id = u.id
            WHERE h.manual_id = ?
            ORDER BY h.created_at DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        return execute_query(query, (manual_id,), fetch_all=True)


class AccessLog:
    """Access log model"""
    
    @staticmethod
    def create(manual_id, user_id=None, ip_address=None):
        """Create an access log"""
        query = """
            INSERT INTO access_logs (manual_id, user_id, ip_address)
            VALUES (?, ?, ?)
        """
        return execute_query(query, (manual_id, user_id, ip_address))
    
    @staticmethod
    def get_by_manual(manual_id, limit=None):
        """Get access logs for a manual"""
        query = """
            SELECT a.*, u.name as user_name
            FROM access_logs a
            LEFT JOIN users u ON a.user_id = u.id
            WHERE a.manual_id = ?
            ORDER BY a.accessed_at DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        return execute_query(query, (manual_id,), fetch_all=True)
    
    @staticmethod
    def count_by_manual(manual_id):
        """Count access logs for a manual"""
        query = "SELECT COUNT(*) as count FROM access_logs WHERE manual_id = ?"
        result = execute_query(query, (manual_id,), fetch_one=True)
        return result['count'] if result else 0
