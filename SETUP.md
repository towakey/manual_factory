# セットアップ手順

## 自動セットアップツール（推奨）

各環境用の自動セットアップツールを用意しています。これらのツールを使用すると、必要な設定を自動的に行います。

### Windows (XAMPP/Apache)

```powershell
cd C:\xampp\htdocs\manual_factory
python setup_windows.py
```

**機能:**
- Pythonバージョンチェック
- 必要なディレクトリの作成
- データベースの初期化
- CGIスクリプトのshebang自動設定
- .htaccessファイルの作成
- Apache起動状態の確認

### Linux (Apache)

```bash
cd /var/www/html/manual_factory
chmod +x setup_linux.sh
./setup_linux.sh
```

**機能:**
- Pythonとパッケージのチェック
- Apache2、SQLite3のインストール（必要な場合）
- CGIモジュールの有効化
- ディレクトリとパーミッションの設定
- データベースの初期化
- Apacheサイト設定の作成
- Apache再起動

### Windows (IIS)

**管理者権限で実行してください:**

```powershell
cd C:\inetpub\wwwroot\manual_factory
PowerShell -ExecutionPolicy Bypass -File setup_iis.ps1
```

**機能:**
- 管理者権限チェック
- IIS機能のインストール
- ディレクトリとパーミッションの設定
- データベースの初期化
- IISハンドラーマッピング設定
- web.configの作成
- IIS再起動

---

## 手動セットアップ（詳細）

自動セットアップツールを使用しない場合や、カスタム設定が必要な場合は以下の手順に従ってください。

## Windowsでの設定（XAMPP使用）

### 1. Pythonのインストール確認

```powershell
python --version
```

Python 3.7以上がインストールされていることを確認してください。

### 2. データベース初期化

```powershell
cd C:\xampp\htdocs\manual_factory\database
python init_db.py
```

プロンプトで `yes` と入力してデータベースを作成します。

### 3. アップロードディレクトリ作成

```powershell
cd C:\xampp\htdocs\manual_factory
mkdir uploads\images
```

### 4. Apache設定

#### 方法A: httpd.confを編集

`C:\xampp\apache\conf\httpd.conf` を開き、以下を追加：

```apache
# CGI実行を有効化
<Directory "C:/xampp/htdocs/manual_factory">
    Options +ExecCGI
    AddHandler cgi-script .py
    AllowOverride All
    Require all granted
</Directory>

<Directory "C:/xampp/htdocs/manual_factory/cgi-bin">
    Options +ExecCGI
    SetHandler cgi-script
    Require all granted
</Directory>
```

#### 方法B: .htaccessを使用

`C:\xampp\htdocs\manual_factory` に `.htaccess` ファイルを作成：

```apache
Options +ExecCGI
AddHandler cgi-script .py
DirectoryIndex index.html

<Directory "cgi-bin">
    Options +ExecCGI
    SetHandler cgi-script
</Directory>
```

### 5. CGIスクリプトの修正（必要な場合）

Windowsでは、各CGIスクリプトの先頭行（shebang）を修正する必要がある場合があります。

`cgi-bin/api/` 内の各`.py`ファイルの1行目を以下のように変更：

```python
#!C:/Python39/python.exe
```

※ Pythonのインストールパスに合わせて調整してください。

または、環境変数PATHにPythonが含まれている場合：

```python
#!/usr/bin/env python
```

### 6. Apache再起動

XAMPPコントロールパネルから:
1. Apacheの「Stop」ボタンをクリック
2. 「Start」ボタンをクリックして再起動

### 7. 動作確認

ブラウザで以下にアクセス：

```
http://localhost/manual_factory/login.html
```

初期管理者アカウントでログイン：
- Email: admin@example.com
- Password: admin123

## IISでの設定（Windowsサーバー）

### 1. Python CGI Handler の設定

IISマネージャーを開き、以下の手順で設定：

1. サイトを選択
2. 「ハンドラーマッピング」を開く
3. 「スクリプトマップの追加」をクリック
4. 以下を入力：
   - 要求パス: `*.py`
   - 実行可能ファイル: `C:\Python39\python.exe %s %s`
   - 名前: `Python CGI`

### 2. CGI有効化

1. 「Windows の機能の有効化または無効化」を開く
2. 「インターネット インフォメーション サービス」→「World Wide Web サービス」→「アプリケーション開発機能」
3. 「CGI」にチェックを入れる

### 3. ディレクトリ権限

`manual_factory` フォルダに IIS_IUSRS の読み取り・実行権限を付与します。

## Linux（Apache）での設定

### 1. 必要なパッケージのインストール

```bash
sudo apt-get update
sudo apt-get install apache2 python3 python3-pip sqlite3
```

### 2. Apache CGI モジュール有効化

```bash
sudo a2enmod cgi
```

### 3. サイト設定

`/etc/apache2/sites-available/manual_factory.conf` を作成：

```apache
<VirtualHost *:80>
    ServerName manual-factory.local
    DocumentRoot /var/www/html/manual_factory

    <Directory /var/www/html/manual_factory>
        Options +ExecCGI
        AddHandler cgi-script .py
        AllowOverride All
        Require all granted
    </Directory>

    <Directory /var/www/html/manual_factory/cgi-bin>
        Options +ExecCGI
        SetHandler cgi-script
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/manual_factory_error.log
    CustomLog ${APACHE_LOG_DIR}/manual_factory_access.log combined
</VirtualHost>
```

サイトを有効化：

```bash
sudo a2ensite manual_factory
sudo systemctl restart apache2
```

### 4. パーミッション設定

```bash
cd /var/www/html/manual_factory
chmod +x cgi-bin/api/*.py
chmod 755 database uploads
chown -R www-data:www-data database uploads
```

### 5. データベース初期化

```bash
cd /var/www/html/manual_factory/database
python3 init_db.py
```

## トラブルシューティング

### エラー: Internal Server Error (500)

Apacheのエラーログを確認：

**Windows (XAMPP):**
```
C:\xampp\apache\logs\error.log
```

**Linux:**
```bash
sudo tail -f /var/log/apache2/error.log
```

よくある原因：
1. Pythonのパス（shebang）が間違っている
2. CGIスクリプトに実行権限がない
3. CGI実行が有効になっていない
4. ファイルエンコーディングの問題

### エラー: データベースにアクセスできない

1. データベースファイルが存在するか確認
2. データベースディレクトリの権限を確認
3. パスが正しいか確認（`common/database.py` の `DB_PATH`）

### CGIスクリプトがダウンロードされる

- Apache設定でCGIハンドラーが正しく設定されているか確認
- `.py` 拡張子が CGI として処理されるように設定されているか確認

### セッションが保持されない

- Cookieが正しく設定されているか確認
- ブラウザがCookieを受け入れているか確認
- HTTPSでない場合、Secure属性を外す

## 本番環境での注意事項

### セキュリティ

1. **管理者パスワードの変更**
   - 初期パスワード `admin123` を必ず変更

2. **HTTPS の使用**
   - 本番環境では必ずHTTPSを使用
   - Let's Encrypt等で無料の証明書を取得可能

3. **エラーメッセージの制限**
   - 本番環境ではスタックトレースを表示しない
   - エラーログはファイルに記録

4. **ファイルアップロードの制限**
   - 画像サイズ、拡張子の制限を厳密に
   - アップロード先のディレクトリをWebルート外に配置

### バックアップ

定期的にデータベースをバックアップ：

```bash
# Windowsの場合
copy database\manual_factory.db database\manual_factory_backup_%DATE%.db

# Linuxの場合
cp database/manual_factory.db database/manual_factory_backup_$(date +%Y%m%d).db
```

### パフォーマンス

- データベースファイルは定期的に最適化
- アップロード画像は定期的にクリーンアップ
- セッションテーブルの期限切れレコードを削除

```sql
-- 期限切れセッションの削除
DELETE FROM sessions WHERE expires_at <= datetime('now', 'localtime');

-- データベース最適化
VACUUM;
```
