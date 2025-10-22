"""
Manual model
Python 3.7+ standard library only
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.database import Database


class Manual:
    """Manual model"""
    
    @staticmethod
    def create(title, description, tags, status, visibility, author_id):
        """Create a new manual"""
        query = """
            INSERT INTO manuals (title, description, tags, status, visibility, author_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return Database.execute(query, (title, description, tags, status, visibility, author_id))
    
    @staticmethod
    def find_by_id(manual_id):
        """Find manual by ID"""
        query = "SELECT * FROM manuals WHERE id = ? AND deleted_at IS NULL"
        return Database.execute(query, (manual_id,), fetch_one=True)
    
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
        Database.execute(query, tuple(params))
        return True
    
    @staticmethod
    def delete(manual_id):
        """Soft delete manual"""
        query = "UPDATE manuals SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?"
        Database.execute(query, (manual_id,))
        return True
    
    @staticmethod
    def search(keyword=None, tags=None, status=None, author_id=None, limit=20, offset=0):
        """Search manuals"""
        query = "SELECT * FROM manuals WHERE deleted_at IS NULL"
        params = []
        
        if keyword:
            query += " AND (title LIKE ? OR description LIKE ?)"
            search_term = f'%{keyword}%'
            params.extend([search_term, search_term])
        
        if tags:
            query += " AND tags LIKE ?"
            params.append(f'%{tags}%')
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if author_id:
            query += " AND author_id = ?"
            params.append(author_id)
        
        query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        return Database.execute(query, tuple(params), fetch_all=True)
    
    @staticmethod
    def count(keyword=None, tags=None, status=None, author_id=None):
        """Count manuals"""
        query = "SELECT COUNT(*) as count FROM manuals WHERE deleted_at IS NULL"
        params = []
        
        if keyword:
            query += " AND (title LIKE ? OR description LIKE ?)"
            search_term = f'%{keyword}%'
            params.extend([search_term, search_term])
        
        if tags:
            query += " AND tags LIKE ?"
            params.append(f'%{tags}%')
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if author_id:
            query += " AND author_id = ?"
            params.append(author_id)
        
        result = Database.execute(query, tuple(params) if params else None, fetch_one=True)
        return result['count'] if result else 0
