# クイックスタートガイド

手順書管理システムを最速で起動するためのガイドです。

## 前提条件

- Python 3.7以上がインストールされていること
- Webサーバー（Apache または IIS）が利用可能であること

## ステップ1: リポジトリの配置

### Windows (XAMPP)
```
C:\xampp\htdocs\manual_factory\
```

### Linux (Apache)
```
/var/www/html/manual_factory/
```

### Windows (IIS)
```
C:\inetpub\wwwroot\manual_factory\
```

## ステップ2: 自動セットアップの実行

### Windows (XAMPP/Apache)

コマンドプロンプトまたはPowerShellを開き：

```powershell
cd C:\xampp\htdocs\manual_factory
python setup_windows.py
```

**注意事項:**
- Apacheが起動していなくても実行可能です
- セットアップ後、XAMPPコントロールパネルからApacheを再起動してください

### Linux (Apache)

ターミナルを開き：

```bash
cd /var/www/html/manual_factory
chmod +x setup_linux.sh
./setup_linux.sh
```

**注意事項:**
- sudo権限が必要な場合があります
- Apache2とSQLite3が自動インストールされます

### Windows (IIS)

PowerShellを**管理者として実行**し：

```powershell
cd C:\inetpub\wwwroot\manual_factory
PowerShell -ExecutionPolicy Bypass -File setup_iis.ps1
```

**注意事項:**
- 必ず管理者権限で実行してください
- IIS機能が自動的にインストールされます

## ステップ3: Webサーバーの起動/再起動

### Windows (XAMPP)
1. XAMPPコントロールパネルを開く
2. Apacheの「Stop」→「Start」をクリック

### Linux (Apache)
```bash
sudo systemctl restart apache2
```

### Windows (IIS)
```powershell
iisreset
```

## ステップ4: ブラウザでアクセス

### Windows (XAMPP)
```
http://localhost/manual_factory/login.html
```

### Linux (Apache)
```
http://localhost/manual_factory/login.html
```
または
```
http://manual-factory.local/login.html
```

### Windows (IIS)
```
http://localhost/manual_factory/login.html
```

## ステップ5: ログイン

初期管理者アカウントでログイン：

- **Email:** admin@example.com
- **Password:** admin123

⚠️ **ログイン後、すぐにパスワードを変更してください！**

## パスワード変更方法

1. ログイン後、右上のユーザー名をクリック
2. 「ユーザー管理」をクリック
3. 管理者ユーザーの「編集」をクリック
4. 新しいパスワードを入力して保存

## よくある質問

### Q: セットアップツールが「Python が見つかりません」と表示される

**A:** Pythonがインストールされているか、環境変数PATHに追加されているか確認してください。

```powershell
# Pythonのバージョン確認
python --version

# または
python3 --version
```

### Q: ブラウザで500エラーが表示される

**A:** 以下を確認してください：

1. CGIが有効になっているか
2. Pythonパス（shebang）が正しいか
3. ファイルに実行権限があるか（Linux）
4. Apacheのエラーログを確認

**エラーログの場所:**
- Windows (XAMPP): `C:\xampp\apache\logs\error.log`
- Linux: `/var/log/apache2/error.log`
- Windows (IIS): イベントビューアー

### Q: データベースエラーが発生する

**A:** データベースを再初期化してください：

```powershell
cd database
python init_db.py
```

yesと入力してデータベースを再作成します。

### Q: 画像がアップロードできない

**A:** アップロードディレクトリが存在し、書き込み権限があるか確認してください：

```powershell
# Windows
mkdir uploads\images

# Linux
mkdir -p uploads/images
sudo chown -R www-data:www-data uploads
```

### Q: Apacheが起動しない（XAMPP）

**A:** 
1. ポート80が他のアプリケーションで使用されていないか確認
2. Skype等がポート80を使用している場合は無効化
3. XAMPPコントロールパネルの「Logs」ボタンでエラーを確認

## 次のステップ

セットアップが完了したら：

1. **ユーザーの追加** - 管理画面から一般ユーザーを作成
2. **手順書の作成** - 「新規作成」ボタンから最初の手順書を作成
3. **タグの設定** - 手順書を分類するためのタグを設定
4. **公開範囲の設定** - 手順書の公開範囲を設定

## サポート

問題が解決しない場合は、以下のドキュメントを参照してください：

- `README.md` - プロジェクト全体の説明
- `SETUP.md` - 詳細なセットアップ手順
- `requirements_plan.md` - 要件定義書

---

お疲れ様でした！手順書管理システムの利用を開始できます。
