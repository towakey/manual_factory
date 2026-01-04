#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Webサーバー自動判定モジュール
ApacheとIISを自動検出し、それぞれの環境に合わせた設定を行う
"""

import os
import sys

def detect_web_server():
    """
    実行中のWebサーバーを自動判定する
    
    Returns:
        str: 'apache', 'iis', 'unknown', 'none' のいずれか
    """
    # 環境変数からWebサーバー情報を取得
    server_software = os.environ.get('SERVER_SOFTWARE', '').lower()
    server_name = os.environ.get('SERVER_NAME', '').lower()
    
    # Apacheの判定
    if 'apache' in server_software or 'mod_python' in server_software:
        return 'apache'
    
    # IISの判定
    if 'microsoft-iis' in server_software or 'iis' in server_software:
        return 'iis'
    
    # その他の判定方法
    # SERVER_SIGNATUREが存在する場合（Apache特有）
    if os.environ.get('SERVER_SIGNATURE'):
        return 'apache'
    
    # IISの特有の環境変数
    if os.environ.get('IIS_UrlRewriteModule') or os.environ.get('APPL_MD_PATH'):
        return 'iis'
    
    # コマンドラインからの実行判定
    if not os.environ.get('REQUEST_METHOD'):
        return 'none'
    
    return 'unknown'

def get_server_config():
    """
    Webサーバーに応じた設定を取得
    
    Returns:
        dict: サーバー設定情報
    """
    server_type = detect_web_server()
    
    configs = {
        'apache': {
            'handler': 'cgi-script',
            'options': '+ExecCGI',
            'directory_index': ['index.html', 'index.py'],
            'error_document': '404 /index.html'
        },
        'iis': {
            'handler': 'Python',
            'script_processor': 'python.exe "%s" %s',
            'directory_index': ['index.html', 'index.py'],
            'fastcgi': True
        },
        'unknown': {
            'handler': 'cgi-script',
            'options': '+ExecCGI',
            'directory_index': ['index.html', 'index.py']
        },
        'none': {
            'development': True,
            'debug': True
        }
    }
    
    return configs.get(server_type, configs['unknown'])

def setup_server_environment():
    """
    Webサーバー環境に応じたセットアップ処理を実行
    """
    server_type = detect_web_server()
    
    if server_type == 'apache':
        # Apache固有の設定
        if sys.platform == 'win32':
            # Windows + Apacheの場合
            os.environ['PYTHONIOENCODING'] = 'utf-8'
        
    elif server_type == 'iis':
        # IIS固有の設定
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # FastCGIモードの場合の調整
        if os.environ.get('FASTCGI') == '1':
            sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    
    # 共通設定
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    return server_type

def print_server_info():
    """
    サーバー情報を出力（デバッグ用）
    """
    server_type = detect_web_server()
    config = get_server_config()
    
    print(f"Webサーバー: {server_type}")
    print(f"設定: {config}")
    
    # 環境変数のデバッグ情報
    print("\n環境変数:")
    for key in ['SERVER_SOFTWARE', 'SERVER_NAME', 'REQUEST_METHOD', 'GATEWAY_INTERFACE']:
        value = os.environ.get(key, '未設定')
        print(f"  {key}: {value}")

# モジュールとしてインポートされた場合に自動実行
if __name__ != '__main__':
    setup_server_environment()
