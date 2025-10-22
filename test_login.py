#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test login functionality and database
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import config
from lib import Database
from models import User

# Configure database
Database.DB_PATH = config.DATABASE_PATH

print("=" * 60)
print("Login Test Script")
print("=" * 60)
print()

# Test 1: Check if database exists
print("Test 1: Database file")
if os.path.exists(config.DATABASE_PATH):
    print(f"  [OK] Database exists: {config.DATABASE_PATH}")
else:
    print(f"  [ERROR] Database not found: {config.DATABASE_PATH}")
    print()
    print("Please run: python init_db_cgi.py")
    sys.exit(1)

print()

# Test 2: Check users in database
print("Test 2: Users in database")
try:
    users = User.get_all()
    if users:
        print(f"  [OK] Found {len(users)} user(s):")
        for user in users:
            print(f"    - Email: {user['email']}")
            print(f"      Name: {user['name']}")
            print(f"      Role: {user['role']}")
            print()
    else:
        print("  [WARNING] No users found")
        print()
        print("Please run: python init_db_cgi.py")
        sys.exit(1)
except Exception as e:
    print(f"  [ERROR] {e}")
    sys.exit(1)

print()

# Test 3: Test login with admin@example.com
print("Test 3: Test login")
test_email = "admin@example.com"
test_password = "admin123"

print(f"  Trying to login with:")
print(f"    Email: {test_email}")
print(f"    Password: {test_password}")
print()

user = User.find_by_email(test_email)
if user:
    print(f"  [OK] User found: {user['name']}")
    
    # Test password verification
    if User.verify_password(user, test_password):
        print(f"  [OK] Password verified!")
        print()
        print("=" * 60)
        print("Login should work!")
        print("=" * 60)
    else:
        print(f"  [ERROR] Password verification failed!")
        print()
        print("The password hash might be incorrect.")
        print("Please run: python init_db_cgi.py")
else:
    print(f"  [ERROR] User not found: {test_email}")
    print()
    print("Please run: python init_db_cgi.py")

print()
