# Webサーバー自動判定機能

Manual FactoryはApacheとIISを自動検出し、それぞれの環境に合わせた設定を自動的に行います。

## 対応Webサーバー

- **Apache** (Windows/Linux/macOS)
- **IIS** (Windows)
- **その他CGI対応サーバー**

## 自動判定の仕組み

以下の方法でWebサーバーを自動判定します：

1. **環境変数の確認**
   - `SERVER_SOFTWARE` の値をチェック
   - Apache: "Apache" や "mod_python" を含む
   - IIS: "Microsoft-IIS" や "IIS" を含む

2. **固有の環境変数**
   - Apache: `SERVER_SIGNATURE` の存在
   - IIS: `IIS_UrlRewriteModule` や `APPL_MD_PATH` の存在

3. **実行環境の検出**
   - コマンドライン実行かCGI実行かを判定

## 設定ファイル

### Apacheの場合
`.htaccess` を使用：
```bash
cp .htaccess.apache .htaccess
```

### IISの場合
`web.config` を使用（既に配置済み）

## 使用方法

### 1. 自動判定の確認
以下のURLにアクセスしてWebサーバーが正しく検出されているか確認：

```
http://localhost/manual_factory/cgi-bin/test_server.py
```

### 2. APIでの利用
各APIスクリプトは自動的にWebサーバーを判定し、適切な設定を適用します。

```python
from common.webserver import detect_web_server, get_server_config

server_type = detect_web_server()
config = get_server_config()
```

## 文字化け対策

Windows環境での文字化けを防ぐため、以下の対策を自動で適用：

- 標準出力のUTF-8設定
- 環境変数 `PYTHONIOENCODING=utf-8` の設定
- IIS FastCGI対応

## トラブルシューティング

### 文字化けが発生する場合
1. `.htaccess` に `SetEnv PYTHONIOENCODING utf-8` を追加
2. `web.config` に環境変数設定を確認
3. Pythonのバージョンが3.7以上であることを確認

### 500エラーが発生する場合
1. Pythonのパスを確認（IISの場合）
2. CGIの実行権限を確認
3. エラーログを確認

## 開発時のデバッグ

環境変数 `MF_DEBUG=1` を設定するとデバッグ情報が出力されます：

```bash
# Apache
SetEnv MF_DEBUG 1

# IIS
<environmentVariable name="MF_DEBUG" value="1" />

# コマンドライン
set MF_DEBUG=1
python test_server.py
```
