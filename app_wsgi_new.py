#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Manual Factory - WSGI Application
Python 3.7+ standard library only
Simple routing without query parameter handlers
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
# Authentication Routes
# ============================================================================

@app.route('/', methods=['GET', 'POST'])
def index(request, response, session):
    """Home page / Login"""
    user_id = session.get('user_id')
    
    # If logged in, redirect to manuals
    if user_id and request.method == 'GET':
        response.redirect('/manuals')
        return response
    
    # Handle login
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = User.find_by_email(email)
        
        if user and User.verify_password(user, password):
            session.set('user_id', user['id'])
            session.set('user_name', user['name'])
            session.set('is_admin', user['role'] == 'admin')
            response.redirect('/manuals')
            return response
        else:
            error = 'メールアドレスまたはパスワードが正しくありません'
            response.body = render_template('cgi_login.html', error=error)
            return response
    
    # Show login form
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
    page = int(request.args.get('page', 1))
    keyword = request.args.get('keyword', '')
    tags = request.args.get('tags', '')
    status = request.args.get('status', '')
    
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
    total_count = Manual.count(
        keyword=keyword if keyword else None,
        tags=tags if tags else None,
        status=status if status else None
    )
    
    total_pages = (total_count + config.ITEMS_PER_PAGE - 1) // config.ITEMS_PER_PAGE
    
    response.body = render_template('cgi_manuals_list.html',
        manuals=manuals,
        page=page,
        total_pages=total_pages,
        keyword=keyword,
        tags=tags,
        status=status,
        user_name=session.get('user_name'),
        is_admin=session.get('is_admin')
    )
    return response


@app.route('/manual/<int:manual_id>', methods=['GET'])
@login_required
def manual_detail(request, response, session, manual_id):
    """Show manual detail"""
    manual = Manual.find_by_id(manual_id)
    
    if not manual:
        response.set_status(404)
        response.body = render_template('cgi_error.html',
            error='マニュアルが見つかりません',
            user_name=session.get('user_name'),
            is_admin=session.get('is_admin')
        )
        return response
    
    # Get steps
    steps = ManualStep.find_by_manual_id(manual_id)
    
    # Log access
    AccessLog.create(
        user_id=session.get('user_id'),
        manual_id=manual_id,
        action='view'
    )
    
    response.body = render_template('cgi_manual_detail.html',
        manual=manual,
        steps=steps,
        user_name=session.get('user_name'),
        is_admin=session.get('is_admin')
    )
    return response


@app.route('/manual/create', methods=['GET', 'POST'])
@login_required
def manual_create(request, response, session):
    """Create new manual"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        tags = request.form.get('tags', '').strip()
        status = request.form.get('status', 'draft')
        
        if not title:
            error = 'タイトルを入力してください'
            response.body = render_template('cgi_manual_form.html',
                error=error,
                title=title,
                description=description,
                tags=tags,
                status=status,
                user_name=session.get('user_name'),
                is_admin=session.get('is_admin')
            )
            return response
        
        # Create manual
        manual_id = Manual.create(
            title=title,
            description=description,
            tags=tags,
            status=status,
            created_by=session.get('user_id')
        )
        
        response.redirect(f'/manual/{manual_id}')
        return response
    
    # Show form
    response.body = render_template('cgi_manual_form.html',
        user_name=session.get('user_name'),
        is_admin=session.get('is_admin')
    )
    return response


@app.route('/manual/<int:manual_id>/edit', methods=['GET', 'POST'])
@login_required
def manual_edit(request, response, session, manual_id):
    """Edit manual"""
    manual = Manual.find_by_id(manual_id)
    
    if not manual:
        response.set_status(404)
        response.body = render_template('cgi_error.html',
            error='マニュアルが見つかりません',
            user_name=session.get('user_name'),
            is_admin=session.get('is_admin')
        )
        return response
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        tags = request.form.get('tags', '').strip()
        status = request.form.get('status', 'draft')
        
        if not title:
            error = 'タイトルを入力してください'
            response.body = render_template('cgi_manual_form.html',
                error=error,
                manual=manual,
                title=title,
                description=description,
                tags=tags,
                status=status,
                user_name=session.get('user_name'),
                is_admin=session.get('is_admin')
            )
            return response
        
        # Update manual
        Manual.update(
            manual_id=manual_id,
            title=title,
            description=description,
            tags=tags,
            status=status,
            updated_by=session.get('user_id')
        )
        
        response.redirect(f'/manual/{manual_id}')
        return response
    
    # Show form
    response.body = render_template('cgi_manual_form.html',
        manual=manual,
        user_name=session.get('user_name'),
        is_admin=session.get('is_admin')
    )
    return response


@app.route('/manual/<int:manual_id>/delete', methods=['POST'])
@login_required
def manual_delete(request, response, session, manual_id):
    """Delete manual"""
    manual = Manual.find_by_id(manual_id)
    
    if manual:
        Manual.delete(manual_id)
    
    response.redirect('/manuals')
    return response


# ============================================================================
# User Management Routes (Admin Only)
# ============================================================================

@app.route('/users', methods=['GET'])
@admin_required
def users_list(request, response, session):
    """List users"""
    users = User.find_all()
    
    response.body = render_template('cgi_users_list.html',
        users=users,
        user_name=session.get('user_name'),
        is_admin=session.get('is_admin')
    )
    return response


@app.route('/user/create', methods=['GET', 'POST'])
@admin_required
def user_create(request, response, session):
    """Create new user"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'user')
        
        if not email or not name or not password:
            error = 'すべての項目を入力してください'
            response.body = render_template('cgi_user_form.html',
                error=error,
                email=email,
                name=name,
                role=role,
                user_name=session.get('user_name'),
                is_admin=session.get('is_admin')
            )
            return response
        
        # Check if email exists
        existing_user = User.find_by_email(email)
        if existing_user:
            error = 'このメールアドレスは既に使用されています'
            response.body = render_template('cgi_user_form.html',
                error=error,
                email=email,
                name=name,
                role=role,
                user_name=session.get('user_name'),
                is_admin=session.get('is_admin')
            )
            return response
        
        # Create user
        User.create(email=email, name=name, password=password, role=role)
        
        response.redirect('/users')
        return response
    
    # Show form
    response.body = render_template('cgi_user_form.html',
        user_name=session.get('user_name'),
        is_admin=session.get('is_admin')
    )
    return response


# ============================================================================
# WSGI Application Entry Point
# ============================================================================

# This is the WSGI application callable
application = app

# For development/testing
if __name__ == '__main__':
    import sys
    from wsgiref.simple_server import make_server
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    host = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
    
    print(f"Starting WSGI server on http://{host}:{port}/")
    print("Press Ctrl+C to stop")
    
    httpd = make_server(host, port, app)
    httpd.serve_forever()
