#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ユーザー更新API
"""

import sys
import os

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common.database import get_db_connection
from common.auth import get_cookie_value, get_session_user, hash_password
from common.utils import json_response, get_request_data, validate_email, get_query_params

def update_user():
    """ユーザー情報を更新"""
    try:
        # 認証チェック
        session_id = get_cookie_value('session_id')
        current_user = get_session_user(session_id)
        
        if not current_user:
            return json_response({'error': '認証が必要です'}, status=401)
        
        # リクエストデータ取得
        data = get_request_data()
        params = get_query_params()
        
        # 更新対象のユーザーID
        target_user_id = params.get('id')
        if not target_user_id:
            return json_response({'error': 'ユーザーIDが指定されていません'}, status=400)
        
        target_user_id = int(target_user_id)
        
        # 権限チェック
        # 管理者は全ユーザーを編集可能、一般ユーザーは自分自身のみ編集可能
        if current_user['role'] != 'admin' and current_user['id'] != target_user_id:
            return json_response({'error': '権限がありません'}, status=403)
        
        # 更新データ
        update_fields = []
        update_values = []
        
        # 名前
        if 'name' in data and data['name']:
            update_fields.append('name = ?')
            update_values.append(data['name'])
        
        # メールアドレス
        if 'email' in data and data['email']:
            if not validate_email(data['email']):
                return json_response({'error': 'メールアドレスの形式が正しくありません'}, status=400)
            update_fields.append('email = ?')
            update_values.append(data['email'])
        
        # パスワード
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return json_response({'error': 'パスワードは6文字以上にしてください'}, status=400)
            update_fields.append('password_hash = ?')
            update_values.append(hash_password(data['password']))
        
        # 部署
        if 'department' in data:
            update_fields.append('department = ?')
            update_values.append(data['department'])
        
        # 役割（管理者のみ変更可能）
        if 'role' in data:
            if current_user['role'] != 'admin':
                return json_response({'error': '役割の変更は管理者のみ可能です'}, status=403)
            if data['role'] not in ['admin', 'user']:
                return json_response({'error': '役割は admin または user を指定してください'}, status=400)
            update_fields.append('role = ?')
            update_values.append(data['role'])
        
        if not update_fields:
            return json_response({'error': '更新する項目がありません'}, status=400)
        
        # 更新日時
        update_fields.append("updated_at = datetime('now', 'localtime')")
        update_values.append(target_user_id)
        
        # 更新実行
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # メールアドレスの重複チェック
            if 'email' in data:
                cursor.execute('SELECT id FROM users WHERE email = ? AND id != ?', (data['email'], target_user_id))
                if cursor.fetchone():
                    return json_response({'error': 'このメールアドレスは既に使用されています'}, status=400)
            
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, update_values)
        
        return json_response({
            'success': True,
            'message': 'ユーザー情報を更新しました'
        })
        
    except Exception as e:
        return json_response({
            'error': 'サーバーエラーが発生しました',
            'details': str(e)
        }, status=500)

if __name__ == '__main__':
    update_user()
