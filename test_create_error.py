#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Get error details from POST /manual/create
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

response.read()  # Consume response
conn.close()

if not session_cookie:
    print("Failed to get session cookie")
    exit(1)

print(f"Session: {session_cookie}")
print()

# Step 2: Create manual
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

print(f"Status: {response.status}")
print()
print("Response body:")
print("=" * 60)
body = response.read().decode('utf-8')
print(body)
print("=" * 60)

conn.close()
