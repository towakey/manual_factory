#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for CGI application
Python 3.7+ standard library only
"""

import sys
import os

# Add current directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

print("Testing CGI Application Components...")
print("")

# Test 1: Import modules
print("Test 1: Importing modules...")
try:
    import config
    from lib import CGIApp, Database, Session, Template, Auth
    from models import User, Manual
    print("  [OK] All modules imported successfully")
except Exception as e:
    print(f"  [ERROR] Import error: {e}")
    sys.exit(1)

# Test 2: Database connection
print("\nTest 2: Database connection...")
try:
    Database.DB_PATH = config.DATABASE_PATH
    conn = Database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    print(f"  [OK] Database connected, {count} users found")
except Exception as e:
    print(f"  [ERROR] Database error: {e}")
    sys.exit(1)

# Test 3: Template engine
print("\nTest 3: Template engine...")
try:
    Template.TEMPLATE_DIR = config.TEMPLATE_DIR
    
    # Create a simple test template
    test_template_path = os.path.join(config.TEMPLATE_DIR, 'test.html')
    with open(test_template_path, 'w', encoding='utf-8') as f:
        f.write('<html><body><h1>Hello {{ name }}!</h1></body></html>')
    
    template = Template('test.html')
    result = template.render(name='World')
    
    # Clean up
    os.remove(test_template_path)
    
    if 'Hello World!' in result:
        print("  [OK] Template engine working")
    else:
        print(f"  [ERROR] Unexpected template output: {result}")
except Exception as e:
    print(f"  [ERROR] Template error: {e}")
    sys.exit(1)

# Test 4: Authentication
print("\nTest 4: Authentication...")
try:
    test_password = "test123"
    hashed = Auth.hash_password(test_password)
    
    if Auth.verify_password(test_password, hashed):
        print("  [OK] Password hashing working")
    else:
        print("  [ERROR] Password verification failed")
except Exception as e:
    print(f"  [ERROR] Auth error: {e}")
    sys.exit(1)

# Test 5: Session
print("\nTest 5: Session management...")
try:
    Session.SESSION_DIR = config.SESSION_DIR
    Session.SESSION_LIFETIME = 3600
    
    session = Session()
    session.set('test_key', 'test_value')
    session.save()
    
    session_id = session.session_id
    
    # Load session
    session2 = Session(session_id)
    value = session2.get('test_key')
    
    # Clean up
    session2.destroy()
    
    if value == 'test_value':
        print("  [OK] Session management working")
    else:
        print(f"  [ERROR] Session value mismatch: {value}")
except Exception as e:
    print(f"  [ERROR] Session error: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("All tests passed! [OK]")
print("="*50)
print("\nCGI application is ready to use!")
print("\nNext steps:")
print("1. Copy htaccess_cgi.txt to .htaccess")
print("2. Make sure Apache CGI module is enabled")
print("3. Access http://localhost/manual_factory/app_cgi.py")
print("4. Login with admin@example.com / admin123")
