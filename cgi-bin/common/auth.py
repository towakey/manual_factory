#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
認証・セッション管理モジュール
"""

import hashlib
import uuid
import os
import http.cookies
from datetime import datetime, timedelta
from .database import get_db_connection

# セッション有効期限（時間）
SESSION_LIFETIME_HOURS = 24

def hash_password(password):
    """パスワードをSHA-256でハッシュ化"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password, password_hash):
    """パスワードを検証"""
    return hash_password(password) == password_hash

def create_session(user_id):
    """新しいセッションを作成"""
    session_id = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(hours=SESSION_LIFETIME_HOURS)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (id, user_id, expires_at)
            VALUES (?, ?, ?)
        ''', (session_id, user_id, expires_at.strftime('%Y-%m-%d %H:%M:%S')))
    
    return session_id

def get_session_user(session_id):
    """セッションIDからユーザー情報を取得"""
    if not session_id:
        return None
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.* FROM users u
            JOIN sessions s ON u.id = s.user_id
            WHERE s.id = ? AND s.expires_at > datetime('now', 'localtime')
            AND u.is_deleted = 0
        ''', (session_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None

def delete_session(session_id):
    """セッションを削除（ログアウト）"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))

def cleanup_expired_sessions():
    """期限切れセッションを削除"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE expires_at <= datetime('now', 'localtime')")

def get_cookie_value(cookie_name):
    """Cookieから値を取得"""
    cookie_string = os.environ.get('HTTP_COOKIE', '')
    cookie = http.cookies.SimpleCookie()
    cookie.load(cookie_string)
    
    if cookie_name in cookie:
        return cookie[cookie_name].value
    return None

def set_cookie(name, value, expires_hours=24):
    """Cookie設定用のヘッダー文字列を生成"""
    expires = datetime.utcnow() + timedelta(hours=expires_hours)
    expires_str = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
    return f'{name}={value}; Expires={expires_str}; Path=/; HttpOnly; SameSite=Strict'

def delete_cookie(name):
    """Cookie削除用のヘッダー文字列を生成"""
    return f'{name}=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/; HttpOnly; SameSite=Strict'

def require_auth(func):
    """認証が必要な関数のデコレータ"""
    def wrapper(*args, **kwargs):
        session_id = get_cookie_value('session_id')
        user = get_session_user(session_id)
        
        if not user:
            return {
                'status': 401,
                'error': 'Unauthorized',
                'message': '認証が必要です'
            }
        
        return func(user, *args, **kwargs)
    
    return wrapper

def require_admin(func):
    """管理者権限が必要な関数のデコレータ"""
    def wrapper(*args, **kwargs):
        session_id = get_cookie_value('session_id')
        user = get_session_user(session_id)
        
        if not user:
            return {
                'status': 401,
                'error': 'Unauthorized',
                'message': '認証が必要です'
            }
        
        if user['role'] != 'admin':
            return {
                'status': 403,
                'error': 'Forbidden',
                'message': '管理者権限が必要です'
            }
        
        return func(user, *args, **kwargs)
    
    return wrapper
