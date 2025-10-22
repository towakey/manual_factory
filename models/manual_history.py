"""
Manual History model
Python 3.7+ standard library only
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.database import Database


class ManualHistory:
    """Manual history model"""
    
    @staticmethod
    def create(manual_id, user_id, action, changes=None):
        """Create history entry"""
        query = """
            INSERT INTO manual_history (manual_id, user_id, action, changes)
            VALUES (?, ?, ?, ?)
        """
        return Database.execute(query, (manual_id, user_id, action, changes))
    
    @staticmethod
    def get_by_manual(manual_id, limit=50):
        """Get history for a manual"""
        query = """
            SELECT h.*, u.name as user_name
            FROM manual_history h
            LEFT JOIN users u ON h.user_id = u.id
            WHERE h.manual_id = ?
            ORDER BY h.created_at DESC
            LIMIT ?
        """
        return Database.execute(query, (manual_id, limit), fetch_all=True)
