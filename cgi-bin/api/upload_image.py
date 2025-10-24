#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
画像アップロードAPI
"""

import sys
import os
import cgi

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common.auth import get_cookie_value, get_session_user
from common.utils import json_response, sanitize_filename
from datetime import datetime

# アップロードディレクトリ
UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'uploads', 'images'
)

# 許可する拡張子
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

# 最大ファイルサイズ（5MB）
MAX_FILE_SIZE = 5 * 1024 * 1024

def upload_image():
    """画像をアップロード"""
    try:
        # 認証チェック
        session_id = get_cookie_value('session_id')
        current_user = get_session_user(session_id)
        
        if not current_user:
            return json_response({'error': '認証が必要です'}, status=401)
        
        # フォームデータを取得
        form = cgi.FieldStorage()
        
        if 'image' not in form:
            return json_response({'error': '画像ファイルが指定されていません'}, status=400)
        
        file_item = form['image']
        
        # ファイルが選択されているか確認
        if not file_item.filename:
            return json_response({'error': 'ファイルが選択されていません'}, status=400)
        
        # ファイル名をサニタイズ
        original_filename = os.path.basename(file_item.filename)
        safe_filename = sanitize_filename(original_filename)
        
        # 拡張子をチェック
        _, ext = os.path.splitext(safe_filename.lower())
        if ext not in ALLOWED_EXTENSIONS:
            return json_response({
                'error': f'許可されていないファイル形式です。使用可能: {", ".join(ALLOWED_EXTENSIONS)}'
            }, status=400)
        
        # ファイルデータを読み込み
        file_data = file_item.file.read()
        
        # ファイルサイズをチェック
        if len(file_data) > MAX_FILE_SIZE:
            return json_response({
                'error': f'ファイルサイズが大きすぎます。最大{MAX_FILE_SIZE // (1024 * 1024)}MBまでです'
            }, status=400)
        
        # タイムスタンプを追加してユニークにする
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(safe_filename)
        unique_filename = f'{name}_{timestamp}{ext}'
        
        # 保存先パス
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filepath = os.path.join(UPLOAD_DIR, unique_filename)
        
        # ファイルを保存
        with open(filepath, 'wb') as f:
            f.write(file_data)
        
        # 相対パスを返す
        relative_path = f'/uploads/images/{unique_filename}'
        
        return json_response({
            'success': True,
            'message': '画像をアップロードしました',
            'filename': unique_filename,
            'path': relative_path
        })
        
    except Exception as e:
        return json_response({
            'error': 'サーバーエラーが発生しました',
            'details': str(e)
        }, status=500)

if __name__ == '__main__':
    upload_image()
