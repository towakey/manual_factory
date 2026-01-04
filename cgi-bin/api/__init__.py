#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Manual Factory API 共通ヘッダー
Webサーバー自動判定機能付き
"""

import sys
import os

# パスを追加（cgi-bin/apiから実行される場合）
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Webサーバー自動判定と環境セットアップ
from common.webserver import setup_server_environment, detect_web_server, get_server_config

# 環境セットアップを実行
server_type = setup_server_environment()

# デバッグ情報（開発時のみ）
if os.environ.get('MF_DEBUG'):
    import json
    print(f"Content-Type: text/plain; charset=utf-8\n")
    print(f"Web Server Type: {server_type}")
    print(f"Server Config: {json.dumps(get_server_config(), indent=2, ensure_ascii=False)}")
    print("\nEnvironment Variables:")
    for key in ['SERVER_SOFTWARE', 'SERVER_NAME', 'REQUEST_METHOD', 'GATEWAY_INTERFACE']:
        value = os.environ.get(key, 'Not Set')
        print(f"  {key}: {value}")
