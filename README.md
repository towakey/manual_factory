# Manual Factory - 手順書作成システム

## 概要
Manual Factoryは、社内の作業手順を効率的に作成・管理・共有するためのWebアプリケーションです。

## 主な機能
- ✅ ユーザー認証とアカウント管理
- ✅ 手順書の作成・編集・削除
- ✅ ステップごとの画像付き手順書作成
- ✅ タグとキーワードによる検索機能
- ✅ 下書き/公開ステータス管理
- ✅ 閲覧ログと更新履歴の記録
- ✅ 管理者によるユーザー管理

## 技術スタック
- **バックエンド**: Python 3.x, Flask
- **データベース**: SQLite
- **フロントエンド**: HTML, CSS, JavaScript (CDN不使用)
- **認証**: Flask-Login

## セットアップ手順

### 1. 必要な環境
- Python 3.8以上
- XAMPP (Apache + Python CGI環境)

### 2. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 3. データベースの初期化
```bash
python init_db.py
```

初期管理者アカウント:
- メールアドレス: `admin@example.com`
- パスワード: `admin123`

**重要**: 初回ログイン後、必ずパスワードを変更してください。

### 4. アプリケーションの起動

#### 開発環境での起動
```bash
python app.py
```

ブラウザで `http://localhost:5000` にアクセスしてください。

#### XAMPP環境での起動
1. `.htaccess.example` をコピーして `.htaccess` を作成
2. `.htaccess` 内のPythonパスを環境に合わせて設定
3. Apacheを起動
4. ブラウザで `http://localhost/manual_factory/` にアクセス

## ディレクトリ構成
```
manual_factory/
├── app/                    # アプリケーションコア
│   ├── __init__.py
│   ├── database.py         # データベース接続
│   ├── models.py           # データモデル
│   ├── auth.py             # 認証機能
│   └── utils.py            # ユーティリティ関数
├── static/                 # 静的ファイル
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/              # HTMLテンプレート
│   ├── base.html
│   ├── login.html
│   ├── profile.html
│   ├── manuals/
│   │   ├── list.html
│   │   ├── detail.html
│   │   └── form.html
│   └── admin/
│       ├── users.html
│       └── user_form.html
├── data/                   # データベースファイル
├── uploads/                # アップロード画像
├── app.py                  # メインアプリケーション
├── config.py               # 設定ファイル
├── schema.sql              # データベーススキーマ
├── init_db.py              # 初期化スクリプト
└── requirements.txt        # 依存パッケージ

```

## 使い方

### 1. ログイン
初期管理者アカウントでログインします。

### 2. ユーザー管理 (管理者のみ)
- ナビゲーションバーの「ユーザー管理」から新規ユーザーを作成
- ユーザーの編集・削除も可能

### 3. 手順書の作成
1. 「新規作成」ボタンをクリック
2. タイトル、説明、タグを入力
3. 「ステップ追加」でステップを追加
4. 各ステップにタイトル、内容、画像を設定
5. 下書き保存または公開

### 4. 手順書の検索
- キーワード検索: タイトル・説明で検索
- タグ検索: タグでフィルタリング
- ステータス: 下書き/公開で絞り込み

## セキュリティ設定

### 本番環境での推奨設定
1. `config.py` の `SECRET_KEY` を変更
2. `SESSION_COOKIE_SECURE = True` に設定（HTTPS使用時）
3. デフォルト管理者アカウントのパスワードを変更
4. データベースファイルへのWebアクセスを制限

## トラブルシューティング

### データベースエラー
```bash
# データベースを再初期化
python init_db.py
```

### 画像アップロードエラー
- `uploads/` ディレクトリの書き込み権限を確認
- `config.py` の `MAX_CONTENT_LENGTH` を確認

### ログインできない
- ブラウザのCookieを削除
- セッション設定を確認

## ライセンス
このプロジェクトはMITライセンスの下で公開されています。

## サポート
問題が発生した場合は、Issues にてご報告ください。

## ローカル環境でのセットアップ

### 1. CGIラッパースクリプトの作成

各`.py`ファイルに対応する`.cgi`ファイルをローカルで作成してください。

**例: `index.cgi`**

```python
#!C:\Users\YOUR_USERNAME\AppData\Local\Programs\Python\Python38\python.exe
# -*- coding: utf-8 -*-
import sys
import os

# index.pyを実行
with open('index.py', 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code)
```

**重要:** 
- shebangの1行目は、ご自身の環境のPythonパスに書き換えてください
- `.cgi`ファイルは`.gitignore`に含まれており、コミットされません

### 2. `.htaccess`の作成

`.htaccess.example`を参考に、ローカル用の`.htaccess`を作成してください：

```apache
Options +ExecCGI
```

### 3. アクセス方法

ブラウザで以下のURLにアクセスします：

```
http://localhost/manual_factory/index.cgi
```

**注意:** `.py`ファイルに直接アクセスせず、必ず`.cgi`経由でアクセスしてください。

## 開発の流れ

1. **コード開発**: `.py`ファイルを編集（shebangなし）
2. **ローカルテスト**: `.cgi`経由でブラウザからアクセス
3. **コミット**: `.py`ファイルのみコミット（環境非依存）

これにより、リポジトリに環境固有の情報が含まれることはありません。