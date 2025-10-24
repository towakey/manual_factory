#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ログインAPI
"""

import sys
import os

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common.database import get_db_connection
from common.auth import hash_password, verify_password, create_session, set_cookie, cleanup_expired_sessions
from common.utils import json_response, get_request_data, validate_required_fields, validate_email

def login():
    """ログイン処理"""
    try:
        # 期限切れセッションをクリーンアップ
        cleanup_expired_sessions()
        
        # リクエストデータ取得
        data = get_request_data()
        
        # バリデーション
        valid, error = validate_required_fields(data, ['email', 'password'])
        if not valid:
            return json_response({'error': error}, status=400)
        
        email = data['email']
        password = data['password']
        
        if not validate_email(email):
            return json_response({'error': 'メールアドレスの形式が正しくありません'}, status=400)
        
        # ユーザー検索
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM users
                WHERE email = ? AND is_deleted = 0
            ''', (email,))
            user = cursor.fetchone()
        
        # ユーザーが存在しない、またはパスワードが一致しない
        if not user or not verify_password(password, user['password_hash']):
            return json_response({
                'error': 'メールアドレスまたはパスワードが正しくありません'
            }, status=401)
        
        # セッション作成
        session_id = create_session(user['id'])
        
        # Cookie設定
        cookie = set_cookie('session_id', session_id, expires_hours=24)
        
        # レスポンス
        return json_response({
            'success': True,
            'message': 'ログインしました',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'role': user['role'],
                'department': user['department']
            }
        }, cookies=[cookie])
        
    except Exception as e:
        return json_response({
            'error': 'サーバーエラーが発生しました',
            'details': str(e)
        }, status=500)

if __name__ == '__main__':
    login()
