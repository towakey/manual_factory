#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Manual Factory - WSGI Application
Python 3.7+ standard library only
"""

import sys
import os

# Add current directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import config
from lib.wsgi_app import WSGIApp, WSGIRequest, WSGIResponse
from lib import login_required, admin_required, render_template, Database, Session, Template
from models import User, Manual, ManualStep, ManualHistory, AccessLog
from lib.utils import sanitize_html, save_uploaded_file, allowed_file

# Configure application
Database.DB_PATH = config.DATABASE_PATH
Session.SESSION_DIR = config.SESSION_DIR
Session.SESSION_LIFETIME = config.SESSION_LIFETIME
Template.TEMPLATE_DIR = config.TEMPLATE_DIR

# Create app
app = WSGIApp()


# ============================================================================
# Routing Handler (Query-based and Path-based)
# ============================================================================

def route_handler(request, response, session):
    """Handle routing based on query parameters or path"""
    # Check query parameter routing first
    page = request.args.get('page', '')
    
    if page == 'manuals':
        return manuals_list(request, response, session)
    elif page == 'manual':
        manual_id = request.args.get('id')
        if manual_id:
            return manual_detail(request, response, session, manual_id)
    elif page == 'create':
        return manual_create(request, response, session)
    elif page == 'users':
        return users_list(request, response, session)
    elif page == 'user_create':
        return user_create(request, response, session)
    
    # If no valid page, redirect to home
    response.redirect('/')
    return response


# ============================================================================
# Authentication Routes
# ============================================================================

@app.route('/', methods=['GET', 'POST'])
def index(request, response, session):
    """Home page / Login"""
    # Check if there are query parameters for routing
    if request.args.get('page'):
        return route_handler(request, response, session)
    
    # Check if logout request
    if request.args.get('logout'):
        return logout(request, response, session)
    
    user_id = session.get('user_id')
    
    # If already logged in, redirect to manuals
    if user_id and request.method == 'GET':
        response.redirect('/?page=manuals')
        return response
    
    # Handle login POST
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = User.find_by_email(email)
        
        if user and User.verify_password(user, password):
            session.set('user_id', user['id'])
            session.set('user_name', user['name'])
            session.set('is_admin', user['role'] == 'admin')
            response.redirect('/?page=manuals')
            return response
        else:
            error = 'メールアドレスまたはパスワードが正しくありません'
            response.body = render_template('cgi_login.html', error=error)
            return response
    
    # Show login form (GET without query params)
    response.body = render_template('cgi_login.html')
    return response


@app.route('/logout', methods=['GET'])
def logout(request, response, session):
    """Logout"""
    session.destroy()
    response.delete_cookie('session_id')
    response.redirect('/')
    return response


# ============================================================================
# Manual Routes
# ============================================================================

@app.route('/manuals', methods=['GET'])
@login_required
def manuals_list(request, response, session):
    """List manuals"""
    page = int(request.get('page_num', 1))
    keyword = request.get('keyword', '')
    tags = request.get('tags', '')
    status = request.get('status', '')
    
    offset = (page - 1) * config.ITEMS_PER_PAGE
    
    # Search manuals
    manuals = Manual.search(
        keyword=keyword if keyword else None,
        tags=tags if tags else None,
        status=status if status else None,
        limit=config.ITEMS_PER_PAGE,
        offset=offset
    )
    
    # Get total count
    total = Manual.count(
        keyword=keyword if keyword else None,
        tags=tags if tags else None,
        status=status if status else None
    )
    
    total_pages = (total + config.ITEMS_PER_PAGE - 1) // config.ITEMS_PER_PAGE
    
    response.body = render_template('cgi_manuals_list.html',
        manuals=manuals,
        page=page,
        total_pages=total_pages,
        keyword=keyword,
        tags=tags,
        status=status,
        user_name=session.get('user_name'),
        is_admin=session.get('is_admin', False)
    )
    return response


@app.route('/manual/<manual_id>', methods=['GET'])
@login_required
def manual_detail(request, response, session, manual_id):
    """Manual detail"""
    manual = Manual.find_by_id(int(manual_id))
    
    if not manual:
        response.set_status(404)
        response.body = '<h1>404 Not Found</h1><p>手順書が見つかりません</p>'
        return response
    
    # Check permission
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)
    
    if manual['status'] == 'draft' and manual['author_id'] != user_id and not is_admin:
        response.set_status(403)
        response.body = '<h1>403 Forbidden</h1><p>この手順書を閲覧する権限がありません</p>'
        return response
    
    # Get steps
    steps = ManualStep.get_by_manual(int(manual_id))
    
    # Get author
    author = User.find_by_id(manual['author_id'])
    
    # Log access
    AccessLog.create(int(manual_id), user_id)
    
    # Get access count
    access_count = AccessLog.get_count_by_manual(int(manual_id))
    
    # Get history
    history = ManualHistory.get_by_manual(int(manual_id), limit=10)
    
    response.body = render_template('cgi_manual_detail.html',
        manual=manual,
        steps=steps,
        author=author,
        access_count=access_count,
        history=history,
        user_id=user_id,
        is_admin=is_admin,
        user_name=session.get('user_name')
    )
    return response


@app.route('/manual/create', methods=['GET', 'POST'])
@login_required
def manual_create(request, response, session):
    """Create manual"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '')
        tags = request.form.get('tags', '')
        status = request.form.get('status', 'draft')
        visibility = request.form.get('visibility', 'public')
        
        if not title:
            response.body = render_template('cgi_manual_form.html',
                error='タイトルを入力してください',
                user_name=session.get('user_name'),
                is_admin=session.get('is_admin', False)
            )
            return response
        
        user_id = session.get('user_id')
        
        # Sanitize
        description = sanitize_html(description)
        
        # Create manual
        manual_id = Manual.create(title, description, tags, status, visibility, user_id)
        
        # Create steps
        step_count = int(request.form.get('step_count', 0))
        for i in range(1, step_count + 1):
            step_title = request.form.get(f'step_title_{i}', '').strip()
            step_content = request.form.get(f'step_content_{i}', '')
            step_notes = request.form.get(f'step_notes_{i}', '')
            
            if not step_title or not step_content:
                continue
            
            # Handle image upload
            image_path = None
            if f'step_image_{i}' in request.files:
                file_data = request.files[f'step_image_{i}']
                filename = file_data.get('filename')
                
                if filename and allowed_file(filename, config.ALLOWED_EXTENSIONS):
                    image_path = save_uploaded_file(
                        file_data['content'],
                        filename,
                        config.UPLOAD_FOLDER
                    )
            
            # Sanitize
            step_content = sanitize_html(step_content)
            step_notes = sanitize_html(step_notes) if step_notes else None
            
            ManualStep.create(manual_id, i, step_title, step_content, step_notes, image_path)
        
        # Create history
        ManualHistory.create(manual_id, user_id, 'created')
        
        response.redirect(f'/manual/{manual_id}')
        return response
    
    # Show form
    response.body = render_template('cgi_manual_form.html',
        user_name=session.get('user_name'),
        is_admin=session.get('is_admin', False)
    )
    return response


@app.route('/manual/<manual_id>/delete', methods=['POST'])
@login_required
def manual_delete(request, response, session, manual_id):
    """Delete manual"""
    manual = Manual.find_by_id(int(manual_id))
    
    if not manual:
        response.redirect('/manuals')
        return response
    
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)
    
    # Check permission
    if manual['author_id'] != user_id and not is_admin:
        response.set_status(403)
        response.body = '<h1>403 Forbidden</h1>'
        return response
    
    Manual.delete(int(manual_id))
    response.redirect('/manuals')
    return response


# ============================================================================
# User Routes (Admin only)
# ============================================================================

@app.route('/users', methods=['GET'])
@admin_required
def users_list(request, response, session):
    """List users"""
    users = User.get_all()
    
    response.body = render_template('cgi_users_list.html',
        users=users,
        user_name=session.get('user_name'),
        is_admin=True
    )
    return response


@app.route('/user/create', methods=['POST'])
@admin_required
def user_create(request, response, session):
    """Create user"""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'user')
    department = request.form.get('department', '')
    
    if not name or not email or not password:
        response.redirect('/users?error=missing_fields')
        return response
    
    User.create(name, email, password, role, department)
    response.redirect('/users')
    return response


# WSGI application entry point
application = app

# For running with wsgiref
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    
    print(f"""
===============================================================
        Manual Factory - WSGI Application Server
             Python 3.7+ Standard Library Only
===============================================================

Server running at: http://localhost:{port}/

Default login:
  Email: admin@example.com
  Password: admin123

Press Ctrl+C to stop the server.
""")
    
    with make_server('', port, application) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
