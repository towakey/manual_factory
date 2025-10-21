# -*- coding: utf-8 -*-
"""
Manual Factory - Main Application
手順書作成システムのメインアプリケーション
"""
import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.exceptions import HTTPException
import config
from app.database import init_db, get_db
from app.models import User, Manual, ManualStep, ManualHistory, AccessLog
from app.auth import login_required, admin_required, get_current_user, login_user, logout_user, is_admin
from app.utils import save_uploaded_file, delete_uploaded_file, sanitize_html, parse_tags, format_tags, get_client_ip

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config)

# Initialize database
try:
    init_db()
except Exception as e:
    print(f"Database initialization error: {e}")


# Template context processor
@app.context_processor
def inject_user():
    """Inject current user into all templates"""
    return {
        'current_user': get_current_user(),
        'is_admin': is_admin()
    }


# Error handlers
@app.errorhandler(404)
def not_found(e):
    """404 error handler"""
    return render_template('error.html', error_code=404, error_message='ページが見つかりません'), 404


@app.errorhandler(500)
def internal_error(e):
    """500 error handler"""
    return render_template('error.html', error_code=500, error_message='サーバーエラーが発生しました'), 500


@app.errorhandler(403)
def forbidden(e):
    """403 error handler"""
    return render_template('error.html', error_code=403, error_message='アクセスが拒否されました'), 403


# ==================== Authentication Routes ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('メールアドレスとパスワードを入力してください', 'error')
            return render_template('login.html')
        
        user = User.find_by_email(email)
        
        if user and User.verify_password(user, password):
            if not user['is_active']:
                flash('このアカウントは無効化されています', 'error')
                return render_template('login.html')
            
            login_user(user)
            flash('ログインしました', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('メールアドレスまたはパスワードが正しくありません', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('ログアウトしました', 'success')
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    user = get_current_user()
    
    if request.method == 'POST':
        name = request.form.get('name')
        department = request.form.get('department')
        
        if not name:
            flash('名前を入力してください', 'error')
            return render_template('profile.html', user=user)
        
        User.update(user['id'], name=name, department=department)
        session['user_name'] = name
        flash('プロフィールを更新しました', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=user)


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        user = get_current_user()
        
        if not User.verify_password(user, current_password):
            flash('現在のパスワードが正しくありません', 'error')
            return render_template('change_password.html')
        
        if len(new_password) < config.PASSWORD_MIN_LENGTH:
            flash(f'パスワードは{config.PASSWORD_MIN_LENGTH}文字以上である必要があります', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('新しいパスワードが一致しません', 'error')
            return render_template('change_password.html')
        
        User.update_password(user['id'], new_password)
        flash('パスワードを変更しました', 'success')
        return redirect(url_for('profile'))
    
    return render_template('change_password.html')


# ==================== User Management Routes (Admin) ====================

@app.route('/admin/users')
@admin_required
def admin_users():
    """User management page"""
    users = User.get_all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/create', methods=['GET', 'POST'])
@admin_required
def admin_create_user():
    """Create user page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        department = request.form.get('department')
        
        if not name or not email or not password:
            flash('必須項目を入力してください', 'error')
            return render_template('admin/user_form.html')
        
        if len(password) < config.PASSWORD_MIN_LENGTH:
            flash(f'パスワードは{config.PASSWORD_MIN_LENGTH}文字以上である必要があります', 'error')
            return render_template('admin/user_form.html')
        
        existing_user = User.find_by_email(email)
        if existing_user:
            flash('このメールアドレスは既に使用されています', 'error')
            return render_template('admin/user_form.html')
        
        User.create(name, email, password, role, department)
        flash('ユーザーを作成しました', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/user_form.html', user=None)


@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    """Edit user page"""
    user = User.find_by_id(user_id)
    if not user:
        flash('ユーザーが見つかりません', 'error')
        return redirect(url_for('admin_users'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role')
        department = request.form.get('department')
        is_active = request.form.get('is_active') == 'on'
        
        if not name or not email:
            flash('必須項目を入力してください', 'error')
            return render_template('admin/user_form.html', user=user)
        
        User.update(user_id, name=name, email=email, role=role, department=department, is_active=1 if is_active else 0)
        flash('ユーザー情報を更新しました', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/user_form.html', user=user)


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """Delete user"""
    current_user = get_current_user()
    if current_user['id'] == user_id:
        flash('自分自身を削除することはできません', 'error')
        return redirect(url_for('admin_users'))
    
    User.soft_delete(user_id)
    flash('ユーザーを削除しました', 'success')
    return redirect(url_for('admin_users'))


# ==================== Manual Routes ====================

@app.route('/')
@login_required
def index():
    """Home page - redirect to manuals list"""
    return redirect(url_for('manuals_list'))


@app.route('/manuals')
@login_required
def manuals_list():
    """Manuals list page"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    tags = request.args.get('tags', '')
    status = request.args.get('status', '')
    author_id = request.args.get('author_id', '', type=str)
    
    current_user = get_current_user()
    
    # Build query parameters
    search_params = {}
    if keyword:
        search_params['keyword'] = keyword
    if tags:
        search_params['tags'] = tags
    if status:
        search_params['status'] = status
    
    # Non-admin users can only see published manuals or their own
    if not is_admin():
        if author_id:
            author_id = current_user['id']
        else:
            search_params['status'] = 'published'
    elif author_id:
        search_params['author_id'] = int(author_id)
    
    # Search manuals
    offset = (page - 1) * config.ITEMS_PER_PAGE
    manuals = Manual.search(
        **search_params,
        limit=config.ITEMS_PER_PAGE,
        offset=offset
    )
    
    # Count total
    total = Manual.count(
        status=search_params.get('status'),
        author_id=search_params.get('author_id')
    )
    total_pages = (total + config.ITEMS_PER_PAGE - 1) // config.ITEMS_PER_PAGE
    
    # Get all users for filter (admin only)
    users = User.get_all() if is_admin() else []
    
    return render_template(
        'manuals/list.html',
        manuals=manuals,
        page=page,
        total_pages=total_pages,
        keyword=keyword,
        tags=tags,
        status=status,
        author_id=author_id,
        users=users
    )


@app.route('/manuals/<int:manual_id>')
@login_required
def manual_detail(manual_id):
    """Manual detail page"""
    manual = Manual.find_by_id(manual_id)
    
    if not manual:
        flash('手順書が見つかりません', 'error')
        return redirect(url_for('manuals_list'))
    
    current_user = get_current_user()
    
    # Check permission
    if manual['status'] == 'draft' and manual['author_id'] != current_user['id'] and not is_admin():
        flash('この手順書を閲覧する権限がありません', 'error')
        return redirect(url_for('manuals_list'))
    
    # Get steps
    steps = ManualStep.get_by_manual(manual_id)
    
    # Get author
    author = User.find_by_id(manual['author_id'])
    
    # Get history
    history = ManualHistory.get_by_manual(manual_id, limit=10)
    
    # Log access
    AccessLog.create(manual_id, current_user['id'], get_client_ip(request))
    
    # Get access count
    access_count = AccessLog.count_by_manual(manual_id)
    
    return render_template(
        'manuals/detail.html',
        manual=manual,
        steps=steps,
        author=author,
        history=history,
        access_count=access_count
    )


@app.route('/manuals/create', methods=['GET', 'POST'])
@login_required
def manual_create():
    """Create manual page"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        tags = request.form.get('tags', '')
        status = request.form.get('status', 'draft')
        visibility = request.form.get('visibility', 'public')
        
        if not title:
            flash('タイトルを入力してください', 'error')
            return render_template('manuals/form.html', manual=None, steps=[])
        
        current_user = get_current_user()
        
        # Sanitize description
        description = sanitize_html(description)
        
        # Create manual
        manual_id = Manual.create(title, description, tags, status, visibility, current_user['id'])
        
        # Create steps
        step_count = int(request.form.get('step_count', 0))
        for i in range(1, step_count + 1):
            step_title = request.form.get(f'step_title_{i}')
            step_content = request.form.get(f'step_content_{i}')
            step_notes = request.form.get(f'step_notes_{i}', '')
            
            if not step_title or not step_content:
                continue
            
            # Handle image upload
            image_path = None
            image_file = request.files.get(f'step_image_{i}')
            if image_file and image_file.filename:
                image_path = save_uploaded_file(image_file, 'manual')
            
            # Sanitize content
            step_content = sanitize_html(step_content)
            step_notes = sanitize_html(step_notes) if step_notes else None
            
            ManualStep.create(manual_id, i, step_title, step_content, step_notes, image_path)
        
        # Create history
        ManualHistory.create(manual_id, current_user['id'], 'created')
        
        flash('手順書を作成しました', 'success')
        return redirect(url_for('manual_detail', manual_id=manual_id))
    
    return render_template('manuals/form.html', manual=None, steps=[])


@app.route('/manuals/<int:manual_id>/edit', methods=['GET', 'POST'])
@login_required
def manual_edit(manual_id):
    """Edit manual page"""
    manual = Manual.find_by_id(manual_id)
    
    if not manual:
        flash('手順書が見つかりません', 'error')
        return redirect(url_for('manuals_list'))
    
    current_user = get_current_user()
    
    # Check permission
    if manual['author_id'] != current_user['id'] and not is_admin():
        flash('この手順書を編集する権限がありません', 'error')
        return redirect(url_for('manual_detail', manual_id=manual_id))
    
    steps = ManualStep.get_by_manual(manual_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        tags = request.form.get('tags', '')
        status = request.form.get('status', 'draft')
        visibility = request.form.get('visibility', 'public')
        
        if not title:
            flash('タイトルを入力してください', 'error')
            return render_template('manuals/form.html', manual=manual, steps=steps)
        
        # Sanitize description
        description = sanitize_html(description)
        
        # Update manual
        Manual.update(manual_id, title=title, description=description, tags=tags, status=status, visibility=visibility)
        
        # Delete existing steps
        ManualStep.delete_by_manual(manual_id)
        
        # Create new steps
        step_count = int(request.form.get('step_count', 0))
        for i in range(1, step_count + 1):
            step_title = request.form.get(f'step_title_{i}')
            step_content = request.form.get(f'step_content_{i}')
            step_notes = request.form.get(f'step_notes_{i}', '')
            
            if not step_title or not step_content:
                continue
            
            # Handle image upload
            image_path = None
            image_file = request.files.get(f'step_image_{i}')
            if image_file and image_file.filename:
                image_path = save_uploaded_file(image_file, 'manual')
            else:
                # Keep existing image if not replaced
                existing_image = request.form.get(f'existing_image_{i}')
                if existing_image:
                    image_path = existing_image
            
            # Sanitize content
            step_content = sanitize_html(step_content)
            step_notes = sanitize_html(step_notes) if step_notes else None
            
            ManualStep.create(manual_id, i, step_title, step_content, step_notes, image_path)
        
        # Create history
        ManualHistory.create(manual_id, current_user['id'], 'updated')
        
        flash('手順書を更新しました', 'success')
        return redirect(url_for('manual_detail', manual_id=manual_id))
    
    return render_template('manuals/form.html', manual=manual, steps=steps)


@app.route('/manuals/<int:manual_id>/delete', methods=['POST'])
@login_required
def manual_delete(manual_id):
    """Delete manual"""
    manual = Manual.find_by_id(manual_id)
    
    if not manual:
        flash('手順書が見つかりません', 'error')
        return redirect(url_for('manuals_list'))
    
    current_user = get_current_user()
    
    # Check permission
    if manual['author_id'] != current_user['id'] and not is_admin():
        flash('この手順書を削除する権限がありません', 'error')
        return redirect(url_for('manual_detail', manual_id=manual_id))
    
    # Delete manual (soft delete)
    Manual.soft_delete(manual_id)
    
    # Create history
    ManualHistory.create(manual_id, current_user['id'], 'deleted')
    
    flash('手順書を削除しました', 'success')
    return redirect(url_for('manuals_list'))


# ==================== Static Files Routes ====================

@app.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(config.UPLOAD_FOLDER, filename)


# ==================== Run Application ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
