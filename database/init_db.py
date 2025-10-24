#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
データベース初期化スクリプト
"""

import sqlite3
import hashlib
import os
import sys

# データベースパス
DB_PATH = os.path.join(os.path.dirname(__file__), 'manual_factory.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

def hash_password(password):
    """パスワードをSHA-256でハッシュ化"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_database():
    """データベースを初期化"""
    # 既存のデータベースがあれば削除
    if os.path.exists(DB_PATH):
        response = input(f'既存のデータベース {DB_PATH} が見つかりました。削除して再作成しますか? (yes/no): ')
        if response.lower() == 'yes':
            os.remove(DB_PATH)
            print('既存のデータベースを削除しました。')
        else:
            print('初期化をキャンセルしました。')
            return
    
    # データベース接続
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # スキーマファイルを読み込んで実行
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)
    
    # 初期管理者ユーザーを作成
    admin_email = 'admin@example.com'
    admin_password = 'admin123'  # 本番環境では必ず変更してください
    admin_name = '管理者'
    
    cursor.execute('''
        INSERT INTO users (email, password_hash, name, role, department)
        VALUES (?, ?, ?, 'admin', 'システム管理部')
    ''', (admin_email, hash_password(admin_password), admin_name))
    
    conn.commit()
    conn.close()
    
    print('データベースの初期化が完了しました。')
    print(f'データベースパス: {DB_PATH}')
    print(f'初期管理者アカウント:')
    print(f'  Email: {admin_email}')
    print(f'  Password: {admin_password}')
    print('※パスワードは必ず変更してください。')

if __name__ == '__main__':
    init_database()
