#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Windows (XAMPP/Apache) 環境用セットアップスクリプト
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# カラー出力
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

# プロジェクトルート
PROJECT_ROOT = Path(__file__).parent.resolve()

def check_python_version():
    """Pythonバージョンチェック"""
    print_header("Pythonバージョンチェック")
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print_error("Python 3.7以上が必要です")
        return False
    
    print_success("Pythonバージョン OK")
    return True

def find_python_path():
    """Pythonの実行パスを取得"""
    python_path = sys.executable
    print_info(f"Pythonパス: {python_path}")
    return python_path

def create_directories():
    """必要なディレクトリを作成"""
    print_header("ディレクトリ作成")
    
    directories = [
        PROJECT_ROOT / 'uploads' / 'images',
        PROJECT_ROOT / 'database',
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print_success(f"作成: {directory}")
    
    return True

def init_database():
    """データベースを初期化"""
    print_header("データベース初期化")
    
    db_init_script = PROJECT_ROOT / 'database' / 'init_db.py'
    
    if not db_init_script.exists():
        print_error(f"初期化スクリプトが見つかりません: {db_init_script}")
        return False
    
    try:
        # 既存のDBがある場合の確認
        db_path = PROJECT_ROOT / 'database' / 'manual_factory.db'
        if db_path.exists():
            response = input("既存のデータベースが見つかりました。再作成しますか? (yes/no): ")
            if response.lower() != 'yes':
                print_warning("データベース初期化をスキップしました")
                return True
            db_path.unlink()
        
        # データベース初期化実行
        result = subprocess.run(
            [sys.executable, str(db_init_script)],
            cwd=str(PROJECT_ROOT / 'database'),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("データベース初期化完了")
            print_info("初期管理者アカウント: admin@example.com / admin123")
            return True
        else:
            print_error(f"データベース初期化エラー: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"データベース初期化エラー: {e}")
        return False

def update_cgi_shebang(python_path):
    """CGIスクリプトのshebangを更新"""
    print_header("CGIスクリプト設定")
    
    api_dir = PROJECT_ROOT / 'cgi-bin' / 'api'
    
    if not api_dir.exists():
        print_error(f"APIディレクトリが見つかりません: {api_dir}")
        return False
    
    # Windowsパスをスラッシュに変換
    python_path_unix = python_path.replace('\\', '/')
    shebang = f'#!{python_path_unix}\n'
    
    updated_count = 0
    
    for py_file in api_dir.glob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 最初の行がshebangかチェック
            if lines and lines[0].startswith('#!'):
                lines[0] = shebang
                
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                updated_count += 1
                print_success(f"更新: {py_file.name}")
        
        except Exception as e:
            print_warning(f"スキップ: {py_file.name} - {e}")
    
    print_info(f"{updated_count}個のファイルを更新しました")
    return True

def create_htaccess():
    """htaccessファイルを作成"""
    print_header(".htaccess設定")
    
    example_file = PROJECT_ROOT / 'htaccess.example'
    htaccess_file = PROJECT_ROOT / '.htaccess'
    
    if htaccess_file.exists():
        response = input(".htaccessファイルが既に存在します。上書きしますか? (yes/no): ")
        if response.lower() != 'yes':
            print_warning(".htaccess作成をスキップしました")
            return True
    
    if example_file.exists():
        try:
            shutil.copy(example_file, htaccess_file)
            print_success(f".htaccessファイルを作成しました: {htaccess_file}")
            return True
        except Exception as e:
            print_error(f".htaccess作成エラー: {e}")
            return False
    else:
        # テンプレートがない場合は直接作成
        htaccess_content = """# Apache設定ファイル
# CGIの実行を許可
Options +ExecCGI
AddHandler cgi-script .py

# ディレクトリインデックス
DirectoryIndex index.html login.html

# エラーページ
ErrorDocument 404 /manual_factory/index.html
"""
        try:
            with open(htaccess_file, 'w', encoding='utf-8') as f:
                f.write(htaccess_content)
            print_success(f".htaccessファイルを作成しました: {htaccess_file}")
            return True
        except Exception as e:
            print_error(f".htaccess作成エラー: {e}")
            return False

def check_apache():
    """Apacheの起動状態をチェック"""
    print_header("Apache状態チェック")
    
    try:
        # Apacheプロセスをチェック
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq httpd.exe'],
            capture_output=True,
            text=True
        )
        
        if 'httpd.exe' in result.stdout:
            print_success("Apache (httpd.exe) が起動しています")
            return True
        else:
            print_warning("Apacheが起動していません")
            print_info("XAMPPコントロールパネルからApacheを起動してください")
            return False
    except Exception as e:
        print_warning(f"Apache状態チェックエラー: {e}")
        return False

def display_next_steps():
    """次のステップを表示"""
    print_header("セットアップ完了")
    
    print("次のステップ:")
    print()
    print("1. XAMPPコントロールパネルを開く")
    print("2. Apacheを再起動する")
    print("   - 「Stop」ボタンをクリック")
    print("   - 「Start」ボタンをクリック")
    print()
    print("3. ブラウザで以下にアクセス:")
    print(f"   {Colors.GREEN}http://localhost/manual_factory/login.html{Colors.END}")
    print()
    print("4. 初期管理者アカウントでログイン:")
    print(f"   Email: {Colors.BOLD}admin@example.com{Colors.END}")
    print(f"   Password: {Colors.BOLD}admin123{Colors.END}")
    print()
    print_warning("※パスワードは必ず変更してください")
    print()

def main():
    """メイン処理"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}手順書管理システム - Windows セットアップ{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    # Pythonバージョンチェック
    if not check_python_version():
        sys.exit(1)
    
    # Pythonパスを取得
    python_path = find_python_path()
    
    # ディレクトリ作成
    if not create_directories():
        print_error("ディレクトリ作成に失敗しました")
        sys.exit(1)
    
    # データベース初期化
    if not init_database():
        print_error("データベース初期化に失敗しました")
        sys.exit(1)
    
    # CGIスクリプト設定
    if not update_cgi_shebang(python_path):
        print_warning("CGIスクリプト設定に問題がありました")
    
    # .htaccess作成
    if not create_htaccess():
        print_warning(".htaccess作成に問題がありました")
    
    # Apache状態チェック
    check_apache()
    
    # 次のステップを表示
    display_next_steps()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nセットアップが中断されました")
        sys.exit(1)
    except Exception as e:
        print_error(f"エラーが発生しました: {e}")
        sys.exit(1)
