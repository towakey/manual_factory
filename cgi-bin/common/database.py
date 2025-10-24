#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
データベース接続モジュール
"""

import sqlite3
import os
from contextlib import contextmanager

# データベースパス
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'manual_factory.db')

@contextmanager
def get_db_connection():
    """データベース接続を取得（コンテキストマネージャー）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 列名でアクセス可能にする
    # テキストデータをUTF-8文字列として取得
    conn.text_factory = str
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_query(query, params=None):
    """クエリを実行して結果を返す"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()

def execute_update(query, params=None):
    """更新クエリを実行"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.lastrowid
