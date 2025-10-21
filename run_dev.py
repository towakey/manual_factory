# -*- coding: utf-8 -*-
"""
Development server runner
開発用サーバーを起動します
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import Flask app
import app as application

if __name__ == '__main__':
    print("=" * 60)
    print("Manual Factory - Development Server")
    print("=" * 60)
    print("\n起動中...")
    print(f"URL: http://localhost:5000")
    print("\n終了するには Ctrl+C を押してください\n")
    
    # Run development server
    application.app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )
