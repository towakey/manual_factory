#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test real template file
"""

import sys
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Load real template
with open('templates/cgi_manuals_list.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Test for loop pattern
pattern = r'{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}(.*?){%\s*endfor\s*%}'
matches = list(re.finditer(pattern, content, flags=re.DOTALL))

print(f"Found {len(matches)} for loop(s) in actual template")

for i, match in enumerate(matches, 1):
    print(f"\nFor loop {i}:")
    print(f"  {match.group(1)} in {match.group(2)}")
    print(f"  Start: char {match.start()}")
    print(f"  End: char {match.end()}")
    print(f"  Content length: {len(match.group(3))}")

# Count template tags
for_count = content.count('{% for')
endfor_count = content.count('{% endfor')
if_count = content.count('{% if')
endif_count = content.count('{% endif')

print("\nTag counts:")
print("  {{% for: {}".format(for_count))
print("  {{% endfor: {}".format(endfor_count))
print("  {{% if: {}".format(if_count))
print("  {{% endif: {}".format(endif_count))
