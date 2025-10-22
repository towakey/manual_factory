#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Initialize database for Manual Factory CGI Application
Python 3.7+ standard library only
"""

import sys
import os

# Add current directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import config
from lib.database import Database
from lib.auth import Auth

# Configure database
Database.DB_PATH = config.DATABASE_PATH

def init_database():
    """Initialize database"""
    print("データベースを初期化しています...")
    
    # Read schema
    schema_file = os.path.join(BASE_DIR, 'schema.sql')
    if not os.path.exists(schema_file):
        print(f"[ERROR] schema.sql が見つかりません: {schema_file}")
        return False
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = f.read()
    
    # Execute schema
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.executescript(schema)
        conn.commit()
        conn.close()
        print("[OK] データベーススキーマ作成完了")
    except Exception as e:
        print(f"[ERROR] スキーマ作成エラー: {e}")
        return False
    
    # Check if admin user exists
    try:
        query = "SELECT COUNT(*) as count FROM users WHERE role = 'admin'"
        result = Database.execute(query, fetch_one=True)
        
        if result and result['count'] > 0:
            print("[OK] 管理者アカウントは既に存在します")
        else:
            # Create default admin user
            admin_email = 'admin@example.com'
            admin_password = 'admin123'
            admin_name = '管理者'
            
            password_hash = Auth.hash_password(admin_password)
            query = """
                INSERT INTO users (name, email, password_hash, role)
                VALUES (?, ?, ?, 'admin')
            """
            Database.execute(query, (admin_name, admin_email, password_hash))
            
            print("[OK] デフォルト管理者アカウント作成完了")
            print("")
            print("--- ログイン情報 ---")
            print(f"メールアドレス: {admin_email}")
            print(f"パスワード: {admin_password}")
            print("※ 初回ログイン後、必ずパスワードを変更してください")
            print("")
    except Exception as e:
        print(f"[ERROR] 管理者アカウント作成エラー: {e}")
        return False
    
    print("完了!")
    return True

if __name__ == '__main__':
    init_database()
