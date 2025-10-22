# Manual Factory - CGI版

## 概要
Manual FactoryのCGI版は、**Python 3.7+の標準ライブラリのみ**を使用して実装されたWebアプリケーションです。
外部依存関係を一切必要とせず、XAMPPなどのApache環境で動作します。

## 🎉 特徴

### ✅ Python標準ライブラリのみ
- Flask、Pillow、bleachなどの外部ライブラリ不要
- `pip install` 不要
- Python 3.7以上があればすぐに動作

### 🚀 自作CGIフレームワーク
- **ルーティングシステム** - URLパターンマッチング
- **リクエスト/レスポンス処理** - CGI環境での HTTP 処理
- **セッション管理** - ファイルベースのセッション
- **認証システム** - SHA-256ベースのパスワードハッシュ化
- **テンプレートエンジン** - シンプルだが強力なテンプレート機能
- **データベース層** - SQLiteラッパー

### 📦 標準ライブラリの使用例
- `http.cookies` - Cookie管理
- `urllib.parse` - URL/クエリパース
- `sqlite3` - データベース
- `hashlib` + `secrets` - セキュアな認証
- `json` - セッションデータ
- `html` - HTMLエスケープ
- `pathlib` - ファイル操作

## システム要件

### 必須
- Python 3.7以上
- Apache (XAMPP推奨)
- CGIモジュール有効化

### 不要
- 外部Pythonパッケージ
- Node.js
- CDN接続

## セットアップ

### 1. Python確認
```cmd
python --version
```
Python 3.7以上であることを確認

### 2. データベース初期化
```cmd
cd c:\xampp\htdocs\manual_factory
python init_db_cgi.py
```

### 3. テスト実行
```cmd
python test_cgi.py
```
すべてのテストがパスすることを確認

### 4. Apache設定確認
XAMPPのApacheでCGIが有効になっているか確認：
- `httpd.conf` で `LoadModule cgi_module modules/mod_cgi.so` が有効
- `.htaccess` が配置されている（自動作成済み）

### 5. アクセス
ブラウザで以下にアクセス：
```
http://localhost/manual_factory/app_cgi.py
```

## デフォルトログイン情報

```
メールアドレス: admin@example.com
パスワード: admin123
```

**⚠️ 初回ログイン後、必ずパスワードを変更してください**

## プロジェクト構造

```
manual_factory/
├── app_cgi.py              # メインCGIスクリプト
├── config.py               # 設定ファイル
├── init_db_cgi.py         # データベース初期化
├── test_cgi.py            # テストスクリプト
├── schema.sql             # データベーススキーマ
├── .htaccess              # Apache設定
│
├── lib/                   # 自作フレームワーク
│   ├── cgi_app.py        # CGIアプリケーション
│   ├── request.py        # リクエスト処理
│   ├── response.py       # レスポンス処理
│   ├── router.py         # ルーティング
│   ├── session.py        # セッション管理
│   ├── auth.py           # 認証システム
│   ├── template.py       # テンプレートエンジン
│   ├── database.py       # データベース層
│   └── utils.py          # ユーティリティ
│
├── models/                # データモデル
│   ├── user.py
│   ├── manual.py
│   ├── manual_step.py
│   ├── manual_history.py
│   └── access_log.py
│
├── templates/             # HTMLテンプレート
│   ├── cgi_login.html
│   ├── cgi_manuals_list.html
│   ├── cgi_manual_detail.html
│   ├── cgi_manual_form.html
│   └── cgi_users_list.html
│
├── data/                  # データディレクトリ
│   ├── manual_factory.db # SQLiteデータベース
│   └── sessions/         # セッションファイル
│
├── uploads/              # アップロードファイル
└── static/               # 静的ファイル
    ├── css/
    └── js/
```

## 主な機能

### ✅ 実装済み
- ✅ ユーザー認証（ログイン/ログアウト）
- ✅ セッション管理
- ✅ 手順書一覧表示
- ✅ 手順書詳細表示
- ✅ 手順書作成（ステップ、画像、備考）
- ✅ 手順書削除
- ✅ ユーザー管理（管理者のみ）
- ✅ 検索機能
- ✅ アクセスログ
- ✅ 閲覧履歴

### 🔄 制限事項（CGI版）
- 画像アップロードは可能だが、リサイズ機能なし（標準ライブラリに画像処理機能がないため）
- PDF出力は印刷機能を使用（ブラウザの機能）
- リッチテキストエディタなし（シンプルなテキストエリア）

## 技術詳細

### テンプレートエンジン
シンプルだが強力なテンプレート機能：

```html
<!-- 変数 -->
{{ variable }}

<!-- 条件分岐 -->
{% if condition %}
    <p>True</p>
{% endif %}

<!-- ループ -->
{% for item in items %}
    <li>{{ item.name }}</li>
{% endfor %}

<!-- フィルター -->
{{ text|safe }}
{{ count|default:"0" }}
```

### セッション管理
- ファイルベース（data/sessions/）
- セキュアなセッションID生成
- 自動有効期限管理
- Cookie経由での識別

### 認証
- SHA-256 + ソルトによるパスワードハッシュ化
- `secrets`モジュールでセキュアなトークン生成
- タイミング攻撃対策（`secrets.compare_digest`）

### データベース
- SQLite3（標準ライブラリ）
- Row Factoryでdict形式の結果
- 自動コネクション管理

## トラブルシューティング

### CGIが動作しない
1. Apache設定を確認
```apache
# httpd.confで確認
LoadModule cgi_module modules/mod_cgi.so
```

2. .htaccessが正しく配置されているか確認

3. Pythonパスを確認
```cmd
which python
# または
where python
```

### 500 Internal Server Error
1. Apacheのエラーログを確認
```cmd
c:\xampp\apache\logs\error.log
```

2. app_cgi.pyの実行権限を確認（Linuxの場合）
```bash
chmod +x app_cgi.py
```

3. Pythonのエラーを確認
```cmd
python app_cgi.py
```

### セッションが保存されない
data/sessions/ ディレクトリの書き込み権限を確認

### 画像アップロードが失敗する
uploads/ ディレクトリの書き込み権限を確認

## 開発者向け

### 新しいルートの追加

```python
@app.route('/example', methods=['GET', 'POST'])
@login_required
def example_handler(request, response, session):
    # 処理
    response.body = render_template('example.html', data=data)
    return response
```

### 新しいモデルの追加

```python
class MyModel:
    @staticmethod
    def create(field1, field2):
        query = "INSERT INTO my_table (field1, field2) VALUES (?, ?)"
        return Database.execute(query, (field1, field2))
    
    @staticmethod
    def find_all():
        query = "SELECT * FROM my_table"
        return Database.execute(query, fetch_all=True)
```

### テンプレートの追加

`templates/` ディレクトリに `.html` ファイルを作成：

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ heading }}</h1>
    {% for item in items %}
        <p>{{ item }}</p>
    {% endfor %}
</body>
</html>
```

## パフォーマンス

### CGI版の特性
- リクエストごとにPythonプロセスが起動
- 小規模〜中規模のアクセスに適している
- 大規模アクセスの場合はWSGI版への移行を推奨

### 最適化のヒント
- セッションクリーンアップを定期実行
- データベースインデックスの最適化
- 静的ファイルのキャッシュ設定

## セキュリティ

### 実装済みのセキュリティ対策
- ✅ パスワードハッシュ化（SHA-256 + ソルト）
- ✅ セッション管理（セキュアなID生成）
- ✅ HTMLエスケープ（XSS対策）
- ✅ SQLインジェクション対策（プリペアドステートメント）
- ✅ CSRF対策（要実装：フォームトークン）
- ✅ 認証・認可チェック

### 推奨事項
- HTTPSの使用
- 定期的なパスワード変更
- セッション有効期限の適切な設定
- アップロードファイルの検証強化

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## サポート

問題が発生した場合は、以下を確認してください：
1. `test_cgi.py` を実行してすべてのテストがパスするか確認
2. Apacheのエラーログを確認
3. Pythonバージョンが3.7以上であることを確認

## まとめ

Manual Factory CGI版は、**外部依存関係ゼロ**で動作する手順書管理システムです。
Python標準ライブラリのみを使用し、シンプルながら実用的なWebアプリケーションを実現しています。

**Python 3.7+ の標準ライブラリだけで、こんなことができます！** 🎉
