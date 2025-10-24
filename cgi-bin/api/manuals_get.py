#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手順書詳細取得API
"""

import sys
import os

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common.database import get_db_connection
from common.auth import get_cookie_value, get_session_user
from common.utils import json_response, get_query_params

def get_manual():
    """手順書の詳細を取得"""
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
        
        # 手順書を取得
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 手順書の基本情報
            cursor.execute('''
                SELECT m.*, u.name as author_name, u.email as author_email
                FROM manuals m
                JOIN users u ON m.author_id = u.id
                WHERE m.id = ? AND m.is_deleted = 0
            ''', (manual_id,))
            
            row = cursor.fetchone()
            if not row:
                return json_response({'error': '手順書が見つかりません'}, status=404)
            
            manual = dict(row)
            
            # 下書きは作成者のみ閲覧可能
            if manual['is_published'] == 0 and manual['author_id'] != current_user['id']:
                return json_response({'error': '閲覧権限がありません'}, status=403)
            
            # タグを取得
            cursor.execute('''
                SELECT t.id, t.name
                FROM tags t
                JOIN manual_tags mt ON t.id = mt.tag_id
                WHERE mt.manual_id = ?
            ''', (manual_id,))
            manual['tags'] = [dict(tag) for tag in cursor.fetchall()]
            
            # ステップを取得
            cursor.execute('''
                SELECT id, step_number, title, content, note, image_path
                FROM manual_steps
                WHERE manual_id = ?
                ORDER BY step_number ASC
            ''', (manual_id,))
            manual['steps'] = [dict(step) for step in cursor.fetchall()]
            
            # 更新履歴を取得
            cursor.execute('''
                SELECT h.*, u.name as user_name
                FROM manual_histories h
                JOIN users u ON h.user_id = u.id
                WHERE h.manual_id = ?
                ORDER BY h.created_at DESC
                LIMIT 10
            ''', (manual_id,))
            manual['histories'] = [dict(history) for history in cursor.fetchall()]
            
            # 閲覧ログを記録
            cursor.execute('''
                INSERT INTO view_logs (manual_id, user_id)
                VALUES (?, ?)
            ''', (manual_id, current_user['id']))
            
            conn.commit()
        
        return json_response({'manual': manual})
        
    except Exception as e:
        return json_response({
            'error': 'サーバーエラーが発生しました',
            'details': str(e)
        }, status=500)

if __name__ == '__main__':
    get_manual()
