# -*- coding: utf-8 -*-
"""
Database connection and utilities
"""
import sqlite3
import os
from contextlib import contextmanager
from config import DATABASE_PATH, BASE_DIR


def init_db():
    """Initialize the database with schema"""
    schema_path = os.path.join(BASE_DIR, 'schema.sql')
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()


@contextmanager
def get_db():
    """Get database connection context manager"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    if row is None:
        return None
    return dict(zip(row.keys(), row))


def execute_query(query, params=(), fetch_one=False, fetch_all=False):
    """Execute a query and return results"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if fetch_one:
            result = cursor.fetchone()
            return dict_from_row(result) if result else None
        elif fetch_all:
            results = cursor.fetchall()
            return [dict_from_row(row) for row in results]
        else:
            conn.commit()
            return cursor.lastrowid


def execute_many(query, params_list):
    """Execute multiple queries with different parameters"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        return cursor.rowcount
