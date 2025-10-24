#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
現在のユーザー情報取得API
"""

import sys
import os

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common.auth import get_cookie_value, get_session_user
from common.utils import json_response

def get_current_user():
    """現在のユーザー情報を取得"""
    try:
        # セッションIDを取得
        session_id = get_cookie_value('session_id')
        
        if not session_id:
            return json_response({
                'error': '認証されていません'
            }, status=401)
        
        # ユーザー情報を取得
        user = get_session_user(session_id)
        
        if not user:
            return json_response({
                'error': 'セッションが無効です'
            }, status=401)
        
        return json_response({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'role': user['role'],
                'department': user['department']
            }
        })
        
    except Exception as e:
        return json_response({
            'error': 'サーバーエラーが発生しました',
            'details': str(e)
        }, status=500)

if __name__ == '__main__':
    get_current_user()
