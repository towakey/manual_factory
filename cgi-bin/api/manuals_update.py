#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手順書更新API
"""

import sys
import os

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common.database import get_db_connection
from common.auth import get_cookie_value, get_session_user
from common.utils import json_response, get_request_data, get_query_params

def update_manual():
    """手順書を更新"""
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
        
        # リクエストデータ取得
        data = get_request_data()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 手順書が存在するか、編集権限があるか確認
            cursor.execute('''
                SELECT * FROM manuals
                WHERE id = ? AND is_deleted = 0
            ''', (manual_id,))
            
            manual = cursor.fetchone()
            if not manual:
                return json_response({'error': '手順書が見つかりません'}, status=404)
            
            # 作成者または管理者のみ編集可能
            if manual['author_id'] != current_user['id'] and current_user['role'] != 'admin':
                return json_response({'error': '編集権限がありません'}, status=403)
            
            # 更新フィールド
            update_fields = []
            update_values = []
            
            if 'title' in data:
                update_fields.append('title = ?')
                update_values.append(data['title'])
            
            if 'description' in data:
                update_fields.append('description = ?')
                update_values.append(data['description'])
            
            if 'is_published' in data:
                update_fields.append('is_published = ?')
                update_values.append(data['is_published'])
            
            if 'visibility' in data:
                if data['visibility'] not in ['public', 'private', 'department']:
                    return json_response({'error': '公開範囲が不正です'}, status=400)
                update_fields.append('visibility = ?')
                update_values.append(data['visibility'])
            
            # 手順書の基本情報を更新
            if update_fields:
                update_fields.append("updated_at = datetime('now', 'localtime')")
                update_values.append(manual_id)
                
                query = f"UPDATE manuals SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, update_values)
            
            # ステップを更新
            if 'steps' in data:
                # 既存のステップを削除
                cursor.execute('DELETE FROM manual_steps WHERE manual_id = ?', (manual_id,))
                
                # 新しいステップを挿入
                for i, step in enumerate(data['steps'], start=1):
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
            
            # タグを更新
            if 'tags' in data:
                # 既存のタグ関連を削除
                cursor.execute('DELETE FROM manual_tags WHERE manual_id = ?', (manual_id,))
                
                # 新しいタグを処理
                for tag_name in data['tags']:
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
            cursor.execute('''
                INSERT INTO manual_histories (manual_id, user_id, action, description)
                VALUES (?, ?, 'updated', '手順書を更新しました')
            ''', (manual_id, current_user['id']))
            
            conn.commit()
        
        return json_response({
            'success': True,
            'message': '手順書を更新しました'
        })
        
    except Exception as e:
        return json_response({
            'error': 'サーバーエラーが発生しました',
            'details': str(e)
        }, status=500)

if __name__ == '__main__':
    update_manual()
