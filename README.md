# 手順書管理システム

手順書の作成・管理・共有を行うWebアプリケーションです。

## 機能

- **認証・認可**: メール・パスワードによるログイン、管理者/一般ユーザーの権限管理
- **ユーザー管理**: ユーザーの登録・編集・削除（管理者のみ）
- **手順書作成**: ステップ形式での手順書作成、画像添付、タグ付け
- **手順書管理**: 一覧表示、検索、フィルタリング、並び替え
- **公開範囲設定**: 全体公開、部署内公開、非公開から選択可能
- **下書き保存**: 作成中の手順書を下書きとして保存可能
- **更新履歴**: 手順書の更新履歴を記録・表示
- **閲覧ログ**: 手順書の閲覧履歴を記録

## 技術スタック

- **フロントエンド**: HTML, CSS, JavaScript（Vanilla JS）
- **バックエンド**: Python 3.7+ (CGI)
- **データベース**: SQLite3
- **Webサーバー**: Apache / IIS / Nginx（FastCGI + fcgiwrap 等）

## システム要件

- Python 3.7以上
- Webサーバー: Apache / IIS / Nginx（FastCGI/CGI対応）
- ブラウザ: Chrome, Firefox, Edge等の最新版

## クイックスタート（自動セットアップ）

各環境用の自動セットアップツールを用意しています。

### Windows (XAMPP/Apache)

```powershell
cd C:\xampp\htdocs\manual_factory
python setup_windows.py
```

### Linux (Apache)

```bash
cd /var/www/html/manual_factory
chmod +x setup_linux.sh
./setup_linux.sh
```

### Windows (IIS)

**管理者権限で実行:**

```powershell
cd C:\inetpub\wwwroot\manual_factory
PowerShell -ExecutionPolicy Bypass -File setup_iis.ps1
```

セットアップツールは以下を自動実行します：
- Pythonバージョンチェック
- 必要なディレクトリの作成
- データベースの初期化
- CGIスクリプトの設定
- Webサーバー設定

## サーバー別インストール手順

CGI方式で動作します。IIS を優先想定として記載していますが、Apache / Nginx でも同様に動作します。

### IIS (Windows)

1. **IIS に CGI 機能を追加**
   - 「Windows の機能の有効化または無効化」から **インターネット インフォメーション サービス > アプリケーション開発機能 > CGI** を有効化
2. **サイトの物理パスに本リポジトリを配置**
   - 例: `C:\inetpub\wwwroot\manual_factory`
3. **ハンドラーマッピングの追加**
   - IIS マネージャー > 対象サイト > 「ハンドラーマッピング」 > 「マップの追加」
   - 要素:
     - 要求パス: `*.py`
     - 実行可能ファイル: `C:\Python39\python.exe "%s" %s`（環境に合わせて調整）
     - 名前: `Python CGI`
4. **アクセス確認**
   - `http://localhost/manual_factory/login.py`

### Apache (Windows/Linux)

1. **CGI モジュールを有効化**
   - `httpd.conf` の `LoadModule cgi_module modules/mod_cgi.so` を有効化
2. **プロジェクト配下で CGI を許可**

```apache
<Directory "C:/xampp/htdocs/manual_factory">
    Options +ExecCGI
    AddHandler cgi-script .py
    Require all granted
    DirectoryIndex index.py login.py
</Directory>
```

3. **アクセス確認**
   - `http://localhost/manual_factory/login.py`

### Nginx (Linux)

Nginx は CGI を直接実行できないため、**fcgiwrap** を使用します。

1. **fcgiwrap の導入**
   - `sudo apt install fcgiwrap` など
2. **Nginx 設定例**

```nginx
server {
    listen 80;
    server_name localhost;
    root /var/www/html/manual_factory;
    index index.py login.py;

    location ~ \.py$ {
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_pass unix:/var/run/fcgiwrap.socket;
    }
}
```

3. **実行権限付与（Linuxのみ）**
   - `chmod +x *.py manuals/*.py users/*.py cgi-bin/api/*.py`

4. **アクセス確認**
   - `http://localhost/manual_factory/login.py`

## 手動インストール手順

自動セットアップツールを使用しない場合は、以下の手順で手動セットアップできます。

### 1. リポジトリの配置

XAMPPのhtdocsフォルダにこのリポジトリを配置します。

```
C:\xampp\htdocs\manual_factory\
```

### 2. データベースの初期化

コマンドプロンプトまたはPowerShellで以下を実行します。

```powershell
cd C:\xampp\htdocs\manual_factory\database
python init_db.py
```

初期管理者アカウントが作成されます：
- Email: admin@example.com
- Password: admin123

**※本番環境では必ずパスワードを変更してください。**

### 3. アップロードディレクトリの作成

画像アップロード用のディレクトリを作成します。

```powershell
mkdir C:\xampp\htdocs\manual_factory\uploads\images
```

### 4. Webサーバー設定

上記「サーバー別インストール手順」に従って CGI を有効化してください。

### 5. Pythonパスの確認

CGIスクリプトの1行目（shebang）が正しいPythonパスを指していることを確認してください。

Windowsの場合、`cgi-bin/api/` 内の各ファイルの先頭行を以下のように変更する必要がある場合があります：

```python
#!C:/Python37/python.exe
```

または環境に合わせたPythonのパスを指定してください。

### 6. Apacheの再起動

XAMPPコントロールパネルからApacheを再起動します。

### 7. アクセス

ブラウザで以下のURLにアクセスします：

```
http://localhost/manual_factory/login.py
```

## セットアップツール

プロジェクトには以下のセットアップツールが含まれています：

- `setup_windows.py` - Windows (XAMPP/Apache) 用自動セットアップ
- `setup_linux.sh` - Linux (Apache) 用自動セットアップ
- `setup_iis.ps1` - Windows (IIS) 用自動セットアップ

各ツールの詳細は `SETUP.md` を参照してください。

## ディレクトリ構造

```
manual_factory/
├── cgi-bin/
│   ├── common/          # 共通モジュール
│   │   ├── __init__.py
│   │   ├── auth.py      # 認証・セッション管理
│   │   ├── database.py  # データベース接続
│   │   └── utils.py     # ユーティリティ関数
│   └── api/             # APIエンドポイント
│       ├── auth_*.py    # 認証API
│       ├── users_*.py   # ユーザー管理API
│       ├── manuals_*.py # 手順書管理API
│       └── upload_image.py
├── database/
│   ├── schema.sql       # データベーススキーマ
│   ├── init_db.py       # 初期化スクリプト
│   └── manual_factory.db (自動生成)
├── static/
│   ├── css/
│   │   └── style.css    # スタイルシート
│   └── js/
│       └── api.js       # API通信ライブラリ
├── manuals/             # 手順書関連ページ
│   ├── view.py          # 詳細表示
│   ├── create.py        # 作成
│   └── edit.py          # 編集
├── users/
│   └── index.py         # ユーザー管理
├── uploads/
│   └── images/          # アップロード画像
├── index.py             # 手順書一覧
├── login.py             # ログイン
└── README.md
```

## API エンドポイント

### 認証API

- `POST /cgi-bin/api/auth_login.py` - ログイン
- `POST /cgi-bin/api/auth_logout.py` - ログアウト
- `GET /cgi-bin/api/auth_me.py` - 現在のユーザー情報取得

### ユーザー管理API（管理者のみ）

- `GET /cgi-bin/api/users_list.py` - ユーザー一覧取得
- `POST /cgi-bin/api/users_create.py` - ユーザー作成
- `POST /cgi-bin/api/users_update.py?id={id}` - ユーザー更新
- `POST /cgi-bin/api/users_delete.py?id={id}` - ユーザー削除

### 手順書管理API

- `GET /cgi-bin/api/manuals_list.py` - 手順書一覧取得
- `GET /cgi-bin/api/manuals_get.py?id={id}` - 手順書詳細取得
- `POST /cgi-bin/api/manuals_create.py` - 手順書作成
- `POST /cgi-bin/api/manuals_update.py?id={id}` - 手順書更新
- `POST /cgi-bin/api/manuals_delete.py?id={id}` - 手順書削除
- `POST /cgi-bin/api/upload_image.py` - 画像アップロード

## セキュリティ

- パスワードはSHA-256でハッシュ化して保存
- セッションは24時間で自動期限切れ
- Cookie は HttpOnly, SameSite=Strict に設定
- ユーザー削除は論理削除で履歴を保持
- 画像アップロードは拡張子とサイズを制限

## トラブルシューティング

### CGIスクリプトが実行されない

1. Apacheの設定でCGIが有効になっているか確認
2. Pythonのパス（shebang）が正しいか確認
3. ファイルのパーミッションを確認（実行権限が必要）
4. Apacheのエラーログを確認: `C:\xampp\apache\logs\error.log`

### データベースエラー

1. データベースファイルが存在するか確認
2. データベースファイルへの書き込み権限があるか確認
3. `init_db.py` を再実行してデータベースを再初期化

### 画像がアップロードできない

1. `uploads/images` ディレクトリが存在するか確認
2. ディレクトリへの書き込み権限があるか確認
3. アップロードする画像のサイズが5MB以下か確認

## ライセンス

MIT License

## 開発情報

- バージョン: 1.0.0
- 最終更新: 2025年
