#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test session persistence
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import config
from lib import Session

# Configure
Session.SESSION_DIR = config.SESSION_DIR

print("=" * 60)
print("Session Persistence Test")
print("=" * 60)
print()

# Test 1: Create session
print("Test 1: Create new session")
session1 = Session()
session1.set('user_id', 1)
session1.set('user_name', 'テストユーザー')
session1.save()
print(f"  Session ID: {session1.session_id}")
print(f"  user_id: {session1.get('user_id')}")
print(f"  user_name: {session1.get('user_name')}")
print()

# Test 2: Load same session
print("Test 2: Load existing session")
session2 = Session(session1.session_id)
print(f"  Session ID: {session2.session_id}")
print(f"  user_id: {session2.get('user_id')}")
print(f"  user_name: {session2.get('user_name')}")
print()

# Test 3: Verify persistence
if session2.get('user_id') == 1 and session2.get('user_name') == 'テストユーザー':
    print("[OK] Session data persisted correctly!")
else:
    print("[ERROR] Session data not persisted!")
    
print()

# Test 4: Session file
session_file = os.path.join(config.SESSION_DIR, f"{session1.session_id}.json")
if os.path.exists(session_file):
    print(f"[OK] Session file exists: {session_file}")
    with open(session_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"  Content: {content}")
else:
    print(f"[ERROR] Session file not found: {session_file}")
