#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手順書作成API
"""

import sys
import os

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common.database import get_db_connection
from common.auth import get_cookie_value, get_session_user
from common.utils import json_response, get_request_data, validate_required_fields

def create_manual():
    """手順書を作成"""
    try:
        # 認証チェック
        session_id = get_cookie_value('session_id')
        current_user = get_session_user(session_id)
        
        if not current_user:
            return json_response({'error': '認証が必要です'}, status=401)
        
        # リクエストデータ取得
        data = get_request_data()
        
        # バリデーション
        valid, error = validate_required_fields(data, ['title'])
        if not valid:
            return json_response({'error': error}, status=400)
        
        title = data['title']
        description = data.get('description', '')
        is_published = data.get('is_published', 0)
        visibility = data.get('visibility', 'public')
        steps = data.get('steps', [])
        tags = data.get('tags', [])
        
        # 公開範囲のチェック
        if visibility not in ['public', 'private', 'department']:
            return json_response({'error': '公開範囲が不正です'}, status=400)
        
        # 手順書を作成
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 手順書を挿入
            cursor.execute('''
                INSERT INTO manuals (title, description, author_id, is_published, visibility)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, description, current_user['id'], is_published, visibility))
            
            manual_id = cursor.lastrowid
            
            # ステップを挿入
            for i, step in enumerate(steps, start=1):
                cursor.execute('''
                    INSERT INTO manual_steps (manual_id, step_number, title, content, note, image_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    manual_id,
                    i,
                    step.get('title', f'ステップ {i}'),
                    step.get('content', ''),
                    step.get('note', ''),
                    step.get('image_path', '')
                ))
            
            # タグを処理
            for tag_name in tags:
                if not tag_name:
                    continue
                
                # タグが存在するか確認
                cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
                tag_row = cursor.fetchone()
                
                if tag_row:
                    tag_id = tag_row['id']
                else:
                    # 新しいタグを作成
                    cursor.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
                    tag_id = cursor.lastrowid
                
                # 手順書とタグを関連付け
                cursor.execute('''
                    INSERT OR IGNORE INTO manual_tags (manual_id, tag_id)
                    VALUES (?, ?)
                ''', (manual_id, tag_id))
            
            # 履歴を記録
            action = 'published' if is_published else 'created'
            cursor.execute('''
                INSERT INTO manual_histories (manual_id, user_id, action, description)
                VALUES (?, ?, ?, ?)
            ''', (manual_id, current_user['id'], action, f'手順書を{action}しました'))
            
            conn.commit()
        
        return json_response({
            'success': True,
            'message': '手順書を作成しました',
            'manual_id': manual_id
        }, status=201)
        
    except Exception as e:
        return json_response({
            'error': 'サーバーエラーが発生しました',
            'details': str(e)
        }, status=500)

if __name__ == '__main__':
    create_manual()
