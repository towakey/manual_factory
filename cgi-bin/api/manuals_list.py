#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手順書一覧取得API
"""

import sys
import os

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common.database import get_db_connection
from common.auth import get_cookie_value, get_session_user
from common.utils import json_response, get_query_params

def get_manuals():
    """手順書一覧を取得"""
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
        tag = params.get('tag', '')
        author = params.get('author', '')
        is_published = params.get('is_published', '')
        sort = params.get('sort', 'updated_at')
        order = params.get('order', 'desc')
        
        offset = (page - 1) * limit
        
        # 手順書一覧を取得
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # WHERE条件を構築
            where_conditions = ['m.is_deleted = 0']
            query_params = []
            
            # 公開状態フィルタ
            if is_published == '1':
                where_conditions.append('m.is_published = 1')
            elif is_published == '0':
                # 下書きは作成者本人のみ閲覧可能
                where_conditions.append('(m.is_published = 0 AND m.author_id = ?)')
                query_params.append(current_user['id'])
            
            # 検索キーワード
            if search:
                where_conditions.append('(m.title LIKE ? OR m.description LIKE ?)')
                search_pattern = f'%{search}%'
                query_params.extend([search_pattern, search_pattern])
            
            # 作成者フィルタ
            if author:
                where_conditions.append('m.author_id = ?')
                query_params.append(int(author))
            
            # タグフィルタ
            tag_join = ''
            if tag:
                tag_join = '''
                    JOIN manual_tags mt ON m.id = mt.manual_id
                    JOIN tags t ON mt.tag_id = t.id
                '''
                where_conditions.append('t.name = ?')
                query_params.append(tag)
            
            # ソート順
            valid_sorts = ['created_at', 'updated_at', 'title']
            if sort not in valid_sorts:
                sort = 'updated_at'
            
            valid_orders = ['asc', 'desc']
            if order.lower() not in valid_orders:
                order = 'desc'
            
            # クエリ実行
            query = f'''
                SELECT DISTINCT
                    m.id, m.title, m.description, m.is_published,
                    m.visibility, m.created_at, m.updated_at,
                    u.name as author_name, u.id as author_id
                FROM manuals m
                JOIN users u ON m.author_id = u.id
                {tag_join}
                WHERE {' AND '.join(where_conditions)}
                ORDER BY m.{sort} {order.upper()}
                LIMIT ? OFFSET ?
            '''
            query_params.extend([limit, offset])
            
            cursor.execute(query, tuple(query_params))
            manuals = []
            
            for row in cursor.fetchall():
                manual = dict(row)
                
                # タグを取得
                cursor.execute('''
                    SELECT t.id, t.name
                    FROM tags t
                    JOIN manual_tags mt ON t.id = mt.tag_id
                    WHERE mt.manual_id = ?
                ''', (manual['id'],))
                manual['tags'] = [dict(tag) for tag in cursor.fetchall()]
                
                # ステップ数を取得
                cursor.execute('''
                    SELECT COUNT(*) as count
                    FROM manual_steps
                    WHERE manual_id = ?
                ''', (manual['id'],))
                manual['step_count'] = cursor.fetchone()['count']
                
                manuals.append(manual)
            
            # 総件数を取得
            count_query = f'''
                SELECT COUNT(DISTINCT m.id) as count
                FROM manuals m
                {tag_join}
                WHERE {' AND '.join(where_conditions)}
            '''
            cursor.execute(count_query, tuple(query_params[:-2]))  # LIMIT/OFFSETを除く
            total = cursor.fetchone()['count']
        
        return json_response({
            'manuals': manuals,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit if total > 0 else 0
            }
        })
        
    except Exception as e:
        return json_response({
            'error': 'サーバーエラーが発生しました',
            'details': str(e)
        }, status=500)

if __name__ == '__main__':
    get_manuals()
