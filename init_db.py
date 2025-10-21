# -*- coding: utf-8 -*-
"""
Database initialization script
初期データベースとデフォルト管理者アカウントを作成します
"""
import sys
from app.database import init_db
from app.models import User

def main():
    """Initialize database and create default admin user"""
    print("データベースを初期化しています...")
    
    try:
        # Initialize database
        init_db()
        print("[OK] データベーススキーマを作成しました")
        
        # Check if admin user already exists
        admin = User.find_by_email('admin@example.com')
        if admin:
            print("[OK] 管理者アカウントは既に存在します")
        else:
            # Create default admin user
            User.create(
                name='管理者',
                email='admin@example.com',
                password='admin123',
                role='admin',
                department='システム管理'
            )
            print("[OK] デフォルト管理者アカウントを作成しました")
            print("\n--- ログイン情報 ---")
            print("メールアドレス: admin@example.com")
            print("パスワード: admin123")
            print("※ 初回ログイン後、必ずパスワードを変更してください")
        
        print("\n初期化が完了しました!")
        return 0
        
    except Exception as e:
        print(f"\nエラーが発生しました: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
