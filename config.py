# -*- coding: utf-8 -*-
"""
Configuration file for Manual Factory (CGI Version)
Python 3.7+ standard library only
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'manual_factory.db')

# Session settings
SESSION_DIR = os.path.join(BASE_DIR, 'data', 'sessions')
SESSION_LIFETIME = 3600 * 24 * 7  # 7 days in seconds

# Upload settings
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Template directory
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# Pagination
ITEMS_PER_PAGE = 20

# Security
PASSWORD_MIN_LENGTH = 8

# Create necessary directories
os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'static', 'css'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'static', 'js'), exist_ok=True)
os.makedirs(TEMPLATE_DIR, exist_ok=True)
