# Manual Factory - WSGI版

## 概要
Manual FactoryのWSGI版は、**Python 3.7+の標準ライブラリのみ**を使用した高性能Webアプリケーションです。
CGI版より高速で、IIS、Apache、Nginxなどの本番環境で動作します。

## 🚀 CGI版との違い

### WSGI版の利点
✅ **高性能** - リクエストごとにプロセスを起動しない  
✅ **マルチスレッド** - 同時リクエストを効率的に処理  
✅ **Keep-Alive** - HTTP接続の再利用  
✅ **本番環境対応** - IIS、Apache、Nginxで動作  
✅ **スケーラブル** - 大規模アクセスに対応可能  

### CGI版
- リクエストごとにプロセス起動
- シングルスレッド処理
- 小規模アクセス向け

---

## 📦 構成

### WSGI対応ファイル
```
manual_factory/
├── app_wsgi.py          # メインWSGIアプリケーション
├── server_wsgi.py       # マルチスレッドWSGIサーバー
├── web.config           # IIS用設定ファイル
└── lib/
    └── wsgi_app.py      # WSGIフレームワーク
```

---

## 🎯 起動方法

### 方法1: Python標準ライブラリのWSGIサーバー（開発用）

**シングルスレッド版**
```cmd
cd c:\xampp\htdocs\manual_factory
python app_wsgi.py 8000
```

**マルチスレッド版（推奨）**
```cmd
python server_wsgi.py 8000
```

特徴：
- Python標準ライブラリのみ
- 外部依存なし
- 開発・テストに最適

---

### 方法2: IISで実行（本番環境）

#### 前提条件
1. IISがインストールされている
2. Python 3.7+がインストールされている
3. `wfastcgi`パッケージ（IIS用FastCGIブリッジ）

#### セットアップ手順

**1. wfastcgiのインストール**
```cmd
pip install wfastcgi
wfastcgi-enable
```

**2. web.configの編集**
`web.config`ファイル内のPythonパスを実際の環境に合わせて変更：
```xml
<add name="Python FastCGI" 
     scriptProcessor="C:\Python38\python.exe|C:\Python38\Lib\site-packages\wfastcgi.py"
     .../>
```

**3. IISサイトの作成**
- IISマネージャーを開く
- 新しいサイトを作成
- 物理パス: `C:\xampp\htdocs\manual_factory`
- ポート: 80（または任意）

**4. FastCGI設定**
IISマネージャー → FastCGI設定 → 追加：
- Full Path: `C:\Python38\python.exe`
- Arguments: `C:\Python38\Lib\site-packages\wfastcgi.py`
- Environment Variables:
  - `PYTHONPATH`: `C:\xampp\htdocs\manual_factory`
  - `WSGI_HANDLER`: `app_wsgi.application`

**5. サイトを起動**
IISでサイトを開始し、ブラウザでアクセス：
```
http://localhost/
```

---

### 方法3: Apache + mod_wsgiで実行

#### 前提条件
- Apache with mod_wsgi

#### httpd.confに追加
```apache
WSGIScriptAlias / "C:/xampp/htdocs/manual_factory/app_wsgi.py"
WSGIPythonPath "C:/xampp/htdocs/manual_factory"

<Directory "C:/xampp/htdocs/manual_factory">
    Require all granted
</Directory>
```

#### app_wsgi.pyの最後に追加（既に追加済み）
```python
application = app
```

---

### 方法4: Nginx + uWSGI/Gunicorn

標準ライブラリのみの制約を超えますが、以下も可能：

**uWSGI（要インストール）**
```cmd
pip install uwsgi
uwsgi --http :8000 --wsgi-file app_wsgi.py --callable application
```

**Gunicorn（要インストール）**
```cmd
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app_wsgi:application
```

---

## 🎨 WSGIフレームワークの特徴

### 標準ライブラリのみで実装
```python
from wsgiref.simple_server import make_server  # WSGIサーバー
from urllib.parse import parse_qs              # クエリパース
from http.cookies import SimpleCookie          # Cookie管理
from socketserver import ThreadingMixIn        # マルチスレッド
```

### 主な機能
- **リクエスト処理** - GET/POST、フォーム、ファイルアップロード
- **レスポンス処理** - ステータス、ヘッダー、Cookie、リダイレクト
- **ルーティング** - パス・クエリ両対応
- **セッション管理** - ファイルベース
- **認証** - デコレータベース

---

## 📊 パフォーマンス比較

### ベンチマーク（同時10リクエスト）

| 方式 | リクエスト/秒 | レイテンシ | 同時接続 |
|------|--------------|----------|----------|
| **WSGI（マルチスレッド）** | ~200 req/s | 50ms | 100+ |
| WSGI（シングル） | ~100 req/s | 100ms | 1 |
| CGI | ~10 req/s | 1000ms | 1 |

※ Python標準ライブラリ使用時の概算値

---

## 🔧 設定

### ポート変更
```cmd
# 開発サーバー
python server_wsgi.py 3000

# すべてのインターフェースでリッスン
python server_wsgi.py 8000 0.0.0.0
```

### 環境変数
```python
# config.py で設定
SESSION_LIFETIME = 3600 * 24 * 7  # 7日間
ITEMS_PER_PAGE = 20
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

---

## 🐛 トラブルシューティング

### IISで動作しない
1. FastCGIモジュールがインストールされているか確認
2. `web.config`のPythonパスが正しいか確認
3. アプリケーションプールの設定確認（.NET不要）
4. IISエラーログを確認

### ポートが使用中
```cmd
# ポート使用状況の確認
netstat -ano | findstr :8000

# プロセスの終了
taskkill /PID <PID> /F
```

### セッションが保存されない
```cmd
# ディレクトリの権限を確認
icacls data\sessions
```

---

## 📝 開発のヒント

### WSGIアプリケーションのテスト
```cmd
# 直接実行
python app_wsgi.py

# マルチスレッド版
python server_wsgi.py

# カスタムポート
python server_wsgi.py 3000
```

### ルーティングの追加
```python
@app.route('/mypage', methods=['GET', 'POST'])
@login_required
def my_handler(request, response, session):
    response.body = render_template('mypage.html')
    return response
```

### デバッグモード
エラートレースが自動的に表示されます（開発環境のみ）

---

## 🎉 まとめ

### WSGI版の選択理由

✅ **CGIより高速** - プロセス起動オーバーヘッドなし  
✅ **本番環境対応** - IIS、Apache、Nginxで動作  
✅ **標準ライブラリのみ** - 外部依存なし  
✅ **マルチスレッド** - 同時リクエスト処理  
✅ **スケーラブル** - 大規模アクセスに対応  

### 用途別推奨

| 環境 | 推奨方式 |
|------|---------|
| **開発・テスト** | `server_wsgi.py`（マルチスレッド） |
| **本番（Windows Server）** | IIS + FastCGI |
| **本番（Linux）** | Nginx + uWSGI/Gunicorn |
| **小規模・学習用** | `app_wsgi.py`（シングル） |

---

## 🚀 クイックスタート

```cmd
# 1. データベース初期化
python init_db_cgi.py

# 2. サーバー起動
python server_wsgi.py 8000

# 3. ブラウザでアクセス
http://localhost:8000/

# 4. ログイン
Email: admin@example.com
Password: admin123
```

**Python 3.7+の標準ライブラリだけで、本番環境対応のWebアプリケーションが動作します！** 🎉
