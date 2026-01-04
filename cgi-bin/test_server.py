#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Webサーバー自動判定テストスクリプト
"""

import sys
import os

# cgi-bin共通モジュールにパスを追加
sys.path.insert(0, os.path.dirname(__file__))

from common.webserver import detect_web_server, get_server_config, setup_server_environment, print_server_info

def main():
    """メイン処理"""
    # CGIヘッダー出力
    print("Content-Type: text/html; charset=utf-8\n")
    
    print("""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Webサーバー自動判定テスト</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .info { background: #f0f8ff; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .warning { background: #fff3cd; padding: 10px; margin: 10px 0; border-radius: 5px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Webサーバー自動判定テスト</h1>
""")
    
    try:
        # Webサーバーを判定
        server_type = detect_web_server()
        config = get_server_config()
        
        print(f"<div class='info'>検出されたWebサーバー: <strong>{server_type}</strong></div>")
        
        # 設定情報を表示
        print("<h2>サーバー設定</h2>")
        print("<table>")
        print("<tr><th>設定項目</th><th>値</th></tr>")
        for key, value in config.items():
            print(f"<tr><td>{key}</td><td>{value}</td></tr>")
        print("</table>")
        
        # 環境変数を表示
        print("<h2>環境変数</h2>")
        print("<table>")
        print("<tr><th>変数名</th><th>値</th></tr>")
        env_vars = ['SERVER_SOFTWARE', 'SERVER_NAME', 'SERVER_PROTOCOL', 
                   'REQUEST_METHOD', 'GATEWAY_INTERFACE', 'SCRIPT_NAME',
                   'QUERY_STRING', 'REMOTE_ADDR', 'HTTP_USER_AGENT']
        
        for var in env_vars:
            value = os.environ.get(var, '未設定')
            print(f"<tr><td>{var}</td><td>{value}</td></tr>")
        print("</table>")
        
        # セットアップ実行
        print("<h2>環境セットアップ</h2>")
        setup_result = setup_server_environment()
        print(f"<div class='success'>セットアップ完了: {setup_result}</div>")
        
        # Python情報
        print("<h2>Python情報</h2>")
        print("<table>")
        print("<tr><th>項目</th><th>値</th></tr>")
        print(f"<tr><td>バージョン</td><td>{sys.version}</td></tr>")
        print(f"<tr><td>プラットフォーム</td><td>{sys.platform}</td></tr>")
        print(f"<tr><td>実行パス</td><td>{sys.executable}</td></tr>")
        print(f"<tr><td>標準出力エンコーディング</td><td>{sys.stdout.encoding}</td></tr>")
        print("</table>")
        
        # テスト結果
        print("<h2>テスト結果</h2>")
        if server_type in ['apache', 'iis']:
            print(f"<div class='success'>✅ {server_type.upper()}環境が正しく検出されました</div>")
        elif server_type == 'none':
            print("<div class='warning'>⚠️ コマンドラインからの実行を検出しました</div>")
        else:
            print("<div class='warning'>⚠️ Webサーバーを特定できませんでした</div>")
        
    except Exception as e:
        print(f"<div class='warning'>エラーが発生しました: {e}</div>")
    
    print("""
    <hr>
    <p><a href="../index.html">トップページに戻る</a></p>
</body>
</html>
""")

if __name__ == '__main__':
    main()
