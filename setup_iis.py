#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IIS Setup Helper for Manual Factory
Python 3.7+ standard library only
"""

import sys
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def check_python():
    """Check Python version"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("[ERROR] Python 3.7+ is required")
        return False
    print("[OK] Python version is compatible")
    return True

def find_wfastcgi():
    """Find wfastcgi installation"""
    try:
        import wfastcgi
        wfastcgi_path = os.path.dirname(wfastcgi.__file__)
        wfastcgi_script = os.path.join(wfastcgi_path, 'wfastcgi.py')
        print(f"[OK] wfastcgi found at: {wfastcgi_script}")
        return wfastcgi_script
    except ImportError:
        print("[WARNING] wfastcgi not found")
        print("\nTo install wfastcgi, run:")
        print("  pip install wfastcgi")
        print("  wfastcgi-enable")
        return None

def generate_web_config():
    """Generate web.config with correct paths"""
    python_exe = sys.executable
    wfastcgi_path = find_wfastcgi()
    
    if not wfastcgi_path:
        print("\n[SKIP] Cannot generate web.config without wfastcgi")
        return False
    
    web_config_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <!-- FastCGI handler for Python WSGI applications -->
      <add name="Python FastCGI" 
           path="*" 
           verb="*" 
           modules="FastCgiModule" 
           scriptProcessor="{python_exe}|{wfastcgi_path}" 
           resourceType="Unspecified" 
           requireAccess="Script" />
    </handlers>
    
    <rewrite>
      <rules>
        <!-- Rewrite all requests to app_wsgi.py -->
        <rule name="Manual Factory WSGI" stopProcessing="true">
          <match url="^(.*)$" />
          <conditions>
            <add input="{{REQUEST_FILENAME}}" matchType="IsFile" negate="true" />
            <add input="{{REQUEST_FILENAME}}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="app_wsgi.py/{{R:1}}" />
        </rule>
      </rules>
    </rewrite>
    
    <!-- Environment variables for WSGI -->
    <fastCgi>
      <application fullPath="{python_exe}" 
                   arguments="{wfastcgi_path}">
        <environmentVariables>
          <environmentVariable name="PYTHONPATH" value="{BASE_DIR}" />
          <environmentVariable name="WSGI_HANDLER" value="app_wsgi.application" />
          <environmentVariable name="DJANGO_SETTINGS_MODULE" value="" />
        </environmentVariables>
      </application>
    </fastCgi>
    
    <!-- Security -->
    <security>
      <requestFiltering>
        <hiddenSegments>
          <add segment="data" />
          <add segment="lib" />
          <add segment="models" />
        </hiddenSegments>
        <fileExtensions>
          <add fileExtension=".db" allowed="false" />
          <add fileExtension=".sql" allowed="false" />
        </fileExtensions>
      </requestFiltering>
    </security>
  </system.webServer>
</configuration>
'''
    
    web_config_path = os.path.join(BASE_DIR, 'web.config')
    with open(web_config_path, 'w', encoding='utf-8') as f:
        f.write(web_config_content)
    
    print(f"[OK] web.config generated at: {web_config_path}")
    return True

def check_database():
    """Check if database exists"""
    import config
    db_path = config.DATABASE_PATH
    
    if os.path.exists(db_path):
        print(f"[OK] Database found at: {db_path}")
        return True
    else:
        print(f"[WARNING] Database not found at: {db_path}")
        print("\nTo initialize database, run:")
        print("  python init_db_cgi.py")
        return False

def print_iis_instructions():
    """Print IIS setup instructions"""
    print("\n" + "="*60)
    print("IIS Setup Instructions")
    print("="*60)
    print("\n1. IIS Manager を開く")
    print("\n2. 新しいサイトを作成:")
    print(f"   - サイト名: ManualFactory")
    print(f"   - 物理パス: {BASE_DIR}")
    print(f"   - ポート: 80 (または任意)")
    print("\n3. アプリケーションプール設定:")
    print("   - .NET CLR バージョン: マネージコードなし")
    print("   - マネージパイプラインモード: 統合")
    print("\n4. サイトを開始")
    print("\n5. ブラウザでアクセス:")
    print("   http://localhost/")
    print("\n6. ログイン:")
    print("   Email: admin@example.com")
    print("   Password: admin123")
    print("\n" + "="*60)

def main():
    """Main setup function"""
    print("="*60)
    print("Manual Factory - IIS Setup Helper")
    print("="*60)
    print()
    
    # Check Python version
    if not check_python():
        sys.exit(1)
    
    print()
    
    # Find wfastcgi
    wfastcgi_path = find_wfastcgi()
    
    print()
    
    # Generate web.config
    if wfastcgi_path:
        generate_web_config()
    
    print()
    
    # Check database
    check_database()
    
    # Print instructions
    print_iis_instructions()
    
    print("\n[INFO] Configuration details:")
    print(f"  Python: {sys.executable}")
    print(f"  Application: {BASE_DIR}")
    if wfastcgi_path:
        print(f"  wfastcgi: {wfastcgi_path}")
    print()

if __name__ == '__main__':
    main()
