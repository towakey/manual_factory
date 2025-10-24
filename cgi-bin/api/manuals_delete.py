#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手順書削除API（論理削除）
"""

import sys
import os

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common.database import get_db_connection
from common.auth import get_cookie_value, get_session_user
from common.utils import json_response, get_query_params

def delete_manual():
    """手順書を削除（論理削除）"""
    try:
        # 認証チェック
        session_id = get_cookie_value('session_id')
        current_user = get_session_user(session_id)
        
        if not current_user:
            return json_response({'error': '認証が必要です'}, status=401)
        
        # パラメータ取得
        params = get_query_params()
        manual_id = params.get('id')
        
        if not manual_id:
            return json_response({'error': '手順書IDが指定されていません'}, status=400)
        
        manual_id = int(manual_id)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 手順書が存在するか、削除権限があるか確認
            cursor.execute('''
                SELECT * FROM manuals
                WHERE id = ? AND is_deleted = 0
            ''', (manual_id,))
            
            manual = cursor.fetchone()
            if not manual:
                return json_response({'error': '手順書が見つかりません'}, status=404)
            
            # 作成者または管理者のみ削除可能
            if manual['author_id'] != current_user['id'] and current_user['role'] != 'admin':
                return json_response({'error': '削除権限がありません'}, status=403)
            
            # 論理削除
            cursor.execute('''
                UPDATE manuals
                SET is_deleted = 1, updated_at = datetime('now', 'localtime')
                WHERE id = ?
            ''', (manual_id,))
            
            # 履歴を記録
            cursor.execute('''
                INSERT INTO manual_histories (manual_id, user_id, action, description)
                VALUES (?, ?, 'deleted', '手順書を削除しました')
            ''', (manual_id, current_user['id']))
            
            conn.commit()
        
        return json_response({
            'success': True,
            'message': '手順書を削除しました'
        })
        
    except Exception as e:
        return json_response({
            'error': 'サーバーエラーが発生しました',
            'details': str(e)
        }, status=500)

if __name__ == '__main__':
    delete_manual()
