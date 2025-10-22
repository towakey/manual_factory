#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test HTTP flow with session cookies
"""

import http.client
import urllib.parse

def test_login_and_create():
    """Test complete flow: login -> create manual"""
    
    print("=" * 60)
    print("HTTP Flow Test")
    print("=" * 60)
    print()
    
    # Step 1: Login
    print("Step 1: POST /login")
    conn = http.client.HTTPConnection('localhost', 8000)
    
    params = urllib.parse.urlencode({
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    conn.request('POST', '/', params, headers)
    response = conn.getresponse()
    
    print(f"  Status: {response.status} {response.reason}")
    print(f"  Headers:")
    for header, value in response.getheaders():
        print(f"    {header}: {value}")
    
    # Extract session cookie
    session_cookie = None
    for header, value in response.getheaders():
        if header.lower() == 'set-cookie':
            if 'session_id=' in value:
                # Extract session_id value
                session_cookie = value.split(';')[0]
                print(f"\n  [OK] Session cookie received: {session_cookie}")
    
    if not session_cookie:
        print("\n  [ERROR] No session cookie received!")
        conn.close()
        return
    
    conn.close()
    print()
    
    # Step 2: Access /manual/create with session
    print("Step 2: GET /manual/create (with session)")
    conn = http.client.HTTPConnection('localhost', 8000)
    
    headers = {
        'Cookie': session_cookie
    }
    
    conn.request('GET', '/manual/create', headers=headers)
    response = conn.getresponse()
    
    print(f"  Status: {response.status} {response.reason}")
    if response.status == 302:
        location = None
        for header, value in response.getheaders():
            if header.lower() == 'location':
                location = value
                print(f"  Redirect to: {location}")
        
        if location == '/':
            print("\n  [ERROR] Redirected to login! Session not working!")
        else:
            print(f"\n  [WARNING] Redirected to: {location}")
    elif response.status == 200:
        print("\n  [OK] Page loaded successfully!")
        # Check if it's the form page
        body = response.read().decode('utf-8')
        if 'タイトル' in body and '説明' in body:
            print("  [OK] Manual creation form displayed")
        else:
            print("  [WARNING] Unexpected content")
    
    conn.close()
    print()
    
    # Step 3: Create manual with session
    print("Step 3: POST /manual/create (with session)")
    conn = http.client.HTTPConnection('localhost', 8000)
    
    params = urllib.parse.urlencode({
        'title': 'テストマニュアル',
        'description': 'HTTPテスト用',
        'tags': 'test',
        'status': 'draft'
    })
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': session_cookie
    }
    
    conn.request('POST', '/manual/create', params, headers)
    response = conn.getresponse()
    
    print(f"  Status: {response.status} {response.reason}")
    print(f"  Headers:")
    for header, value in response.getheaders():
        print(f"    {header}: {value}")
    
    if response.status == 302:
        location = None
        for header, value in response.getheaders():
            if header.lower() == 'location':
                location = value
                print(f"\n  Redirect to: {location}")
        
        if location == '/':
            print("  [ERROR] Redirected to login! Session lost!")
        elif location and location.startswith('/manual/'):
            print("  [OK] Redirected to manual detail page!")
        else:
            print(f"  [INFO] Redirected to: {location}")
    
    conn.close()
    print()

if __name__ == '__main__':
    test_login_and_create()
