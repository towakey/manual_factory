#!python
# -*- coding: utf-8 -*-
"""
Manual Factory - CGI Entry Point
IIS settings modification not required
"""

import sys
import os

# Add current directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Import and run CGI application
from app_cgi import app
app.run()