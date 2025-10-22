"""
Access Log model
Python 3.7+ standard library only
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.database import Database


class AccessLog:
    """Access log model"""
    
    @staticmethod
    def create(manual_id, user_id):
        """Create access log entry"""
        query = """
            INSERT INTO access_logs (manual_id, user_id)
            VALUES (?, ?)
        """
        return Database.execute(query, (manual_id, user_id))
    
    @staticmethod
    def get_count_by_manual(manual_id):
        """Get access count for a manual"""
        query = "SELECT COUNT(*) as count FROM access_logs WHERE manual_id = ?"
        result = Database.execute(query, (manual_id,), fetch_one=True)
        return result['count'] if result else 0
