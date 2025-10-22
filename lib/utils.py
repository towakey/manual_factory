"""
Utility functions
Python 3.7+ standard library only
"""

import os
import secrets
import html
from pathlib import Path


def sanitize_html(text):
    """Sanitize HTML content"""
    if not text:
        return ''
    return html.escape(text)


def save_uploaded_file(file_data, filename, upload_folder):
    """Save uploaded file"""
    if not file_data or not filename:
        return None
    
    # Generate secure filename
    ext = Path(filename).suffix.lower()
    safe_filename = f'{secrets.token_hex(16)}{ext}'
    
    # Create upload folder if not exists
    os.makedirs(upload_folder, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_folder, safe_filename)
    with open(file_path, 'wb') as f:
        f.write(file_data)
    
    return safe_filename


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def format_datetime(dt_string):
    """Format datetime string for display"""
    if not dt_string:
        return ''
    # Simple format - just return as is for now
    return dt_string[:19]  # YYYY-MM-DD HH:MM:SS
