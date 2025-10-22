#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug template rendering step by step
"""

import sys
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

template_content = """
{% for manual in manuals %}
<div>{{ manual.title }}</div>
{% if manual.status == 'published' %}
<span>公開</span>
{% endif %}
{% endfor %}
{% if not manuals %}
<p>なし</p>
{% endif %}
"""

print("Original template:")
print(template_content)
print()

# Test for loop pattern
pattern = r'{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}(.*?){%\s*endfor\s*%}'
matches = list(re.finditer(pattern, template_content, flags=re.DOTALL))

print(f"Found {len(matches)} for loop(s)")
for i, match in enumerate(matches, 1):
    print(f"\nMatch {i}:")
    print(f"  Item name: {match.group(1)}")
    print(f"  Items name: {match.group(2)}")
    print(f"  Loop content length: {len(match.group(3))} chars")
    print(f"  Content preview: {match.group(3)[:100]}...")

# Process with empty list
context = {'manuals': []}
result = re.sub(pattern, '', template_content, flags=re.DOTALL)

print("\nAfter removing for loop:")
print(result)
