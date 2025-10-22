"""
Manual Step model
Python 3.7+ standard library only
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.database import Database


class ManualStep:
    """Manual step model"""
    
    @staticmethod
    def create(manual_id, step_number, title, content, notes=None, image_path=None):
        """Create a new step"""
        query = """
            INSERT INTO manual_steps (manual_id, step_number, title, content, notes, image_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return Database.execute(query, (manual_id, step_number, title, content, notes, image_path))
    
    @staticmethod
    def get_by_manual(manual_id):
        """Get all steps for a manual"""
        query = "SELECT * FROM manual_steps WHERE manual_id = ? ORDER BY step_number ASC"
        return Database.execute(query, (manual_id,), fetch_all=True)
    
    @staticmethod
    def update(step_id, **kwargs):
        """Update step"""
        allowed_fields = ['step_number', 'title', 'content', 'notes', 'image_path']
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
        Database.execute(query, tuple(params))
        return True
    
    @staticmethod
    def delete(step_id):
        """Delete step"""
        query = "DELETE FROM manual_steps WHERE id = ?"
        Database.execute(query, (step_id,))
        return True
    
    @staticmethod
    def delete_by_manual(manual_id):
        """Delete all steps for a manual"""
        query = "DELETE FROM manual_steps WHERE manual_id = ?"
        Database.execute(query, (manual_id,))
        return True
