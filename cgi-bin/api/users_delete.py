#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ユーザー削除API（管理者のみ、論理削除）
"""

import sys
import os

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common.database import get_db_connection
from common.auth import get_cookie_value, get_session_user
from common.utils import json_response, get_query_params

def delete_user():
    """ユーザーを削除（論理削除）"""
    try:
        # 認証チェック（管理者のみ）
        session_id = get_cookie_value('session_id')
        current_user = get_session_user(session_id)
        
        if not current_user:
            return json_response({'error': '認証が必要です'}, status=401)
        
        if current_user['role'] != 'admin':
            return json_response({'error': '管理者権限が必要です'}, status=403)
        
        # パラメータ取得
        params = get_query_params()
        user_id = params.get('id')
        
        if not user_id:
            return json_response({'error': 'ユーザーIDが指定されていません'}, status=400)
        
        user_id = int(user_id)
        
        # 自分自身は削除できない
        if user_id == current_user['id']:
            return json_response({'error': '自分自身を削除することはできません'}, status=400)
        
        # 論理削除
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # ユーザーが存在するかチェック
            cursor.execute('SELECT id FROM users WHERE id = ? AND is_deleted = 0', (user_id,))
            if not cursor.fetchone():
                return json_response({'error': 'ユーザーが見つかりません'}, status=404)
            
            # 論理削除実行
            cursor.execute('''
                UPDATE users
                SET is_deleted = 1, updated_at = datetime('now', 'localtime')
                WHERE id = ?
            ''', (user_id,))
            
            # ユーザーのセッションを削除
            cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        
        return json_response({
            'success': True,
            'message': 'ユーザーを削除しました'
        })
        
    except Exception as e:
        return json_response({
            'error': 'サーバーエラーが発生しました',
            'details': str(e)
        }, status=500)

if __name__ == '__main__':
    delete_user()
