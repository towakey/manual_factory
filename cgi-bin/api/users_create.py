#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ユーザー作成API（管理者のみ）
"""

import sys
import os

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common.database import get_db_connection
from common.auth import get_cookie_value, get_session_user, hash_password
from common.utils import json_response, get_request_data, validate_required_fields, validate_email

def create_user():
    """ユーザーを作成"""
    try:
        # 認証チェック（管理者のみ）
        session_id = get_cookie_value('session_id')
        current_user = get_session_user(session_id)
        
        if not current_user:
            return json_response({'error': '認証が必要です'}, status=401)
        
        if current_user['role'] != 'admin':
            return json_response({'error': '管理者権限が必要です'}, status=403)
        
        # リクエストデータ取得
        data = get_request_data()
        
        # バリデーション
        valid, error = validate_required_fields(data, ['email', 'name', 'password', 'role'])
        if not valid:
            return json_response({'error': error}, status=400)
        
        email = data['email']
        name = data['name']
        password = data['password']
        role = data['role']
        department = data.get('department', '')
        
        # メールアドレスの形式チェック
        if not validate_email(email):
            return json_response({'error': 'メールアドレスの形式が正しくありません'}, status=400)
        
        # 役割のチェック
        if role not in ['admin', 'user']:
            return json_response({'error': '役割は admin または user を指定してください'}, status=400)
        
        # パスワードの長さチェック
        if len(password) < 6:
            return json_response({'error': 'パスワードは6文字以上にしてください'}, status=400)
        
        # ユーザー作成
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # メールアドレスの重複チェック
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                return json_response({'error': 'このメールアドレスは既に使用されています'}, status=400)
            
            # ユーザーを挿入
            cursor.execute('''
                INSERT INTO users (email, password_hash, name, role, department)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, hash_password(password), name, role, department))
            
            user_id = cursor.lastrowid
        
        return json_response({
            'success': True,
            'message': 'ユーザーを作成しました',
            'user_id': user_id
        }, status=201)
        
    except Exception as e:
        return json_response({
            'error': 'サーバーエラーが発生しました',
            'details': str(e)
        }, status=500)

if __name__ == '__main__':
    create_user()
