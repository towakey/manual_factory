#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test template rendering
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import config
from lib import Template

# Configure
Template.TEMPLATE_DIR = config.TEMPLATE_DIR

# Test rendering
template = Template('cgi_manuals_list.html')
html = template.render(
    user_name='テストユーザー',
    is_admin=True,
    manuals=[],  # Empty list
    page=1,
    total_pages=1,
    keyword='',
    tags='',
    status=''
)

# Check for unprocessed template tags
if '{% ' in html or ' %}' in html:
    print("[ERROR] Template tags not processed!")
    print()
    print("Unprocessed content:")
    lines = html.split('\n')
    for i, line in enumerate(lines, 1):
        if '{% ' in line or ' %}' in line:
            print(f"  Line {i}: {line.strip()}")
else:
    print("[OK] All template tags processed!")
