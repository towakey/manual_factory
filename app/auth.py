# -*- coding: utf-8 -*-
"""
Authentication utilities
"""
from functools import wraps
from flask import session, redirect, url_for, flash, request
from app.models import User


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('ログインが必要です', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('ログインが必要です', 'error')
            return redirect(url_for('login'))
        
        user = User.find_by_id(session['user_id'])
        if not user or user['role'] != 'admin':
            flash('管理者権限が必要です', 'error')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get currently logged in user"""
    if 'user_id' in session:
        return User.find_by_id(session['user_id'])
    return None


def login_user(user):
    """Log in a user"""
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_role'] = user['role']
    session.permanent = True


def logout_user():
    """Log out the current user"""
    session.clear()


def is_admin():
    """Check if current user is admin"""
    return session.get('user_role') == 'admin'
