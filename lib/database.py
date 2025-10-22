"""
Database layer for CGI application
Python 3.7+ standard library only
"""

import sqlite3
from pathlib import Path


class Database:
    """SQLite database wrapper"""
    
    DB_PATH = None
    
    @staticmethod
    def get_connection():
        """Get database connection"""
        if Database.DB_PATH is None:
            raise ValueError("DB_PATH not configured")
        
        conn = sqlite3.connect(Database.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    @staticmethod
    def execute(query, params=None, fetch_one=False, fetch_all=False):
        """Execute SQL query"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch_one:
                result = cursor.fetchone()
                conn.close()
                return dict(result) if result else None
            
            if fetch_all:
                results = cursor.fetchall()
                conn.close()
                return [dict(row) for row in results]
            
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    @staticmethod
    def execute_many(query, params_list):
        """Execute multiple queries"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.executemany(query, params_list)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
