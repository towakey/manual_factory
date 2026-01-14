#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IIS + CGI 動作確認用の最小テストスクリプト
- ヘッダー出力/エンコーディング確認
- 環境変数とPython実行パス確認
- DBファイル有無確認
"""

import os
import sys
import traceback


def main():
    # 必須: CGIヘッダー
    print("Content-Type: text/plain; charset=utf-8")
    print()

    print("OK: CGI test script")
    print("Python:", sys.version)
    print("Executable:", sys.executable)
    print("CWD:", os.getcwd())
    print("REQUEST_METHOD:", os.environ.get("REQUEST_METHOD", "<none>"))
    print("GATEWAY_INTERFACE:", os.environ.get("GATEWAY_INTERFACE", "<none>"))
    print("SERVER_SOFTWARE:", os.environ.get("SERVER_SOFTWARE", "<none>"))
    print()

    # DBファイルの存在確認
    project_root = os.path.dirname(os.path.dirname(__file__))
    db_path = os.path.join(project_root, "database", "manual_factory.db")
    print("DB exists:", os.path.exists(db_path), "path:", db_path)

    # webserver判定の読み込み（失敗しても続行）
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from common.webserver import setup_server_environment, detect_web_server

        server_type = setup_server_environment()
        print("detect_web_server:", detect_web_server())
        print("setup_server_environment result:", server_type)
    except Exception as e:
        print("webserver import/setup error:", e)
        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # ここで例外を握って表示しておくとIISの500原因が分かりやすい
        print("Content-Type: text/plain; charset=utf-8")
        print()
        traceback.print_exc()
