#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ログインページ (CGI)
"""

import os
import sys
import traceback


def setup_cgi():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir
    if not os.path.isdir(os.path.join(project_root, "cgi-bin")):
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
    cgi_bin = os.path.join(project_root, "cgi-bin")
    if cgi_bin not in sys.path:
        sys.path.insert(0, cgi_bin)
    try:
        import common.utils  # noqa: F401
    except Exception:
        pass


HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ログイン - 手順書管理システム</title>
    <link rel="stylesheet" href="./static/css/style.css">
</head>
<body>
    <div class="container" style="max-width: 400px; margin-top: 5rem;">
        <div class="card">
            <h1 class="card-title" style="text-align: center; margin-bottom: 2rem;">
                手順書管理システム
            </h1>

            <form id="loginForm">
                <div class="form-group">
                    <label for="email">メールアドレス</label>
                    <input type="email" id="email" name="email" required>
                </div>

                <div class="form-group">
                    <label for="password">パスワード</label>
                    <input type="password" id="password" name="password" required>
                </div>

                <button type="submit" class="btn btn-primary" style="width: 100%;">
                    ログイン
                </button>
            </form>

            <div id="errorMessage" style="margin-top: 1rem;"></div>
        </div>

        <div style="text-align: center; margin-top: 1rem; color: #666;">
            <p>初期管理者アカウント:</p>
            <p>Email: admin@example.com / Password: admin123</p>
        </div>
    </div>

    <script src="./static/js/api.js"></script>
    <script>
        const loginForm = document.getElementById('loginForm');
        const errorMessage = document.getElementById('errorMessage');

        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const data = await AuthAPI.login(email, password);

                if (data.success) {
                    window.location.href = './index.py';
                }
            } catch (error) {
                errorMessage.innerHTML = `<div class="alert alert-error">${error.message}</div>`;
            }
        });
    </script>
</body>
</html>
"""


def render():
    print("Content-Type: text/html; charset=utf-8")
    print()
    print(HTML)


if __name__ == "__main__":
    try:
        setup_cgi()
        render()
    except Exception:
        print("Content-Type: text/plain; charset=utf-8")
        print()
        traceback.print_exc()
