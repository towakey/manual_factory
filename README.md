# manual_factory

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