#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ログアウトAPI
"""

import sys
import os

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common.auth import delete_session, get_cookie_value, delete_cookie
from common.utils import json_response

def logout():
    """ログアウト処理"""
    try:
        # セッションIDを取得
        session_id = get_cookie_value('session_id')
        
        if session_id:
            # セッションを削除
            delete_session(session_id)
        
        # Cookie削除
        cookie = delete_cookie('session_id')
        
        return json_response({
            'success': True,
            'message': 'ログアウトしました'
        }, cookies=[cookie])
        
    except Exception as e:
        return json_response({
            'error': 'サーバーエラーが発生しました',
            'details': str(e)
        }, status=500)

if __name__ == '__main__':
    logout()
