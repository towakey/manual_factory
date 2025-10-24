#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ユーザー一覧取得API
"""

import sys
import os

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common.database import get_db_connection
from common.auth import get_cookie_value, get_session_user
from common.utils import json_response, get_query_params

def get_users():
    """ユーザー一覧を取得"""
    try:
        # 認証チェック
        session_id = get_cookie_value('session_id')
        current_user = get_session_user(session_id)
        
        if not current_user:
            return json_response({'error': '認証が必要です'}, status=401)
        
        # クエリパラメータ取得
        params = get_query_params()
        page = int(params.get('page', '1'))
        limit = int(params.get('limit', '20'))
        search = params.get('search', '')
        
        offset = (page - 1) * limit
        
        # ユーザー一覧を取得
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 検索条件
            if search:
                query = '''
                    SELECT id, email, name, role, department, created_at, updated_at
                    FROM users
                    WHERE is_deleted = 0
                    AND (name LIKE ? OR email LIKE ? OR department LIKE ?)
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                '''
                search_pattern = f'%{search}%'
                cursor.execute(query, (search_pattern, search_pattern, search_pattern, limit, offset))
            else:
                query = '''
                    SELECT id, email, name, role, department, created_at, updated_at
                    FROM users
                    WHERE is_deleted = 0
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                '''
                cursor.execute(query, (limit, offset))
            
            users = [dict(row) for row in cursor.fetchall()]
            
            # 総件数を取得
            if search:
                cursor.execute('''
                    SELECT COUNT(*) as count FROM users
                    WHERE is_deleted = 0
                    AND (name LIKE ? OR email LIKE ? OR department LIKE ?)
                ''', (search_pattern, search_pattern, search_pattern))
            else:
                cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_deleted = 0')
            
            total = cursor.fetchone()['count']
        
        return json_response({
            'users': users,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })
        
    except Exception as e:
        return json_response({
            'error': 'サーバーエラーが発生しました',
            'details': str(e)
        }, status=500)

if __name__ == '__main__':
    get_users()
