#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ユーティリティ関数
"""

import json
import sys
import os
import cgi
from datetime import datetime

def json_response(data, status=200, cookies=None):
    """JSON レスポンスを出力"""
    # 標準出力をUTF-8に設定
    sys.stdout.reconfigure(encoding='utf-8')
    
    # ステータスコード
    status_messages = {
        200: 'OK',
        201: 'Created',
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        500: 'Internal Server Error'
    }
    
    status_message = status_messages.get(status, 'Unknown')
    
    # ヘッダー出力
    print(f'Status: {status} {status_message}')
    print('Content-Type: application/json; charset=utf-8')
    
    # Cookie設定
    if cookies:
        for cookie in cookies:
            print(f'Set-Cookie: {cookie}')
    
    print()  # ヘッダーと本文の区切り
    
    # JSON出力
    print(json.dumps(data, ensure_ascii=False, indent=2))

def get_request_data():
    """POSTリクエストのJSONデータを取得"""
    try:
        content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        if content_length > 0:
            request_body = sys.stdin.read(content_length)
            return json.loads(request_body)
        return {}
    except (ValueError, json.JSONDecodeError):
        return {}

def get_query_params():
    """GETクエリパラメータを取得"""
    query_string = os.environ.get('QUERY_STRING', '')
    params = {}
    
    if query_string:
        for pair in query_string.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key] = value
    
    return params

def validate_required_fields(data, required_fields):
    """必須フィールドの検証"""
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f'必須フィールドが不足しています: {", ".join(missing_fields)}'
    
    return True, None

def validate_email(email):
    """メールアドレスの簡易検証"""
    if not email or '@' not in email:
        return False
    return True

def format_datetime(dt_string):
    """日時文字列をフォーマット"""
    if not dt_string:
        return None
    try:
        dt = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%Y年%m月%d日 %H:%M')
    except ValueError:
        return dt_string

def sanitize_filename(filename):
    """ファイル名をサニタイズ"""
    # 危険な文字を除去
    unsafe_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    return filename

def save_uploaded_file(field_storage, upload_dir):
    """アップロードされたファイルを保存"""
    if not field_storage.filename:
        return None
    
    # ファイル名をサニタイズ
    original_filename = os.path.basename(field_storage.filename)
    safe_filename = sanitize_filename(original_filename)
    
    # タイムスタンプを追加してユニークにする
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(safe_filename)
    unique_filename = f'{name}_{timestamp}{ext}'
    
    # 保存先パス
    filepath = os.path.join(upload_dir, unique_filename)
    
    # ディレクトリが存在しなければ作成
    os.makedirs(upload_dir, exist_ok=True)
    
    # ファイルを保存
    with open(filepath, 'wb') as f:
        f.write(field_storage.file.read())
    
    return unique_filename
