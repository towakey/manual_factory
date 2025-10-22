#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test manual detail page access
"""

import http.client
import urllib.parse

# Step 1: Login to get session
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

# Extract session cookie
session_cookie = None
for header, value in response.getheaders():
    if header.lower() == 'set-cookie' and 'session_id=' in value:
        session_cookie = value.split(';')[0]
        break

response.read()
conn.close()

if not session_cookie:
    print("[ERROR] Failed to get session cookie")
    exit(1)

print(f"✓ Session: {session_cookie}")
print()

# Step 2: Access manual detail page
print("Test: GET /manual/1")
conn = http.client.HTTPConnection('localhost', 8000)

headers = {
    'Cookie': session_cookie
}

conn.request('GET', '/manual/1', headers=headers)
response = conn.getresponse()

print(f"Status: {response.status} {response.reason}")

if response.status == 200:
    print("✓ [OK] Manual detail page loaded successfully!")
    body = response.read().decode('utf-8')
    
    # Check for manual content
    if 'テストマニュアル' in body:
        print("✓ [OK] Manual title found in page")
    else:
        print("  [WARNING] Manual title not found")
        
elif response.status == 500:
    print("✗ [ERROR] 500 Internal Server Error")
    body = response.read().decode('utf-8')
    print("\nError details:")
    print(body)
else:
    print(f"  Status: {response.status}")
    body = response.read().decode('utf-8')
    print(body[:500])

conn.close()
