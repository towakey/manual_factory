# -*- coding: utf-8 -*-
"""
Utility functions
"""
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import bleach
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, subfolder='manual'):
    """Save uploaded file and return the path"""
    if not file or not allowed_file(file.filename):
        return None
    
    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Create subfolder if not exists
    upload_path = os.path.join(UPLOAD_FOLDER, subfolder)
    os.makedirs(upload_path, exist_ok=True)
    
    # Save file
    filepath = os.path.join(upload_path, filename)
    file.save(filepath)
    
    # Optimize image
    try:
        img = Image.open(filepath)
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        
        # Resize if too large
        max_size = (1920, 1920)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save optimized
        img.save(filepath, optimize=True, quality=85)
    except Exception as e:
        print(f"Image optimization failed: {e}")
    
    # Return relative path
    return os.path.join(subfolder, filename).replace('\\', '/')


def delete_uploaded_file(filepath):
    """Delete uploaded file"""
    if not filepath:
        return
    
    full_path = os.path.join(UPLOAD_FOLDER, filepath)
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
        except Exception as e:
            print(f"File deletion failed: {e}")


def sanitize_html(content):
    """Sanitize HTML content"""
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 's', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'a', 'code', 'pre', 'blockquote', 'hr'
    ]
    allowed_attributes = {
        'a': ['href', 'title'],
        'code': ['class']
    }
    
    return bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )


def parse_tags(tags_string):
    """Parse comma-separated tags string"""
    if not tags_string:
        return []
    
    tags = [tag.strip() for tag in tags_string.split(',')]
    return [tag for tag in tags if tag]


def format_tags(tags_list):
    """Format tags list to comma-separated string"""
    if not tags_list:
        return ''
    
    return ', '.join(tags_list)


def get_client_ip(request):
    """Get client IP address from request"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr


def paginate(query_result, page, per_page):
    """Paginate query results"""
    total = len(query_result)
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'items': query_result[start:end],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }
