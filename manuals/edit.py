#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手順書編集ページ (CGI)
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
    <title>手順書編集 - 手順書管理システム</title>
    <link rel="stylesheet" href="../static/css/style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>手順書管理システム</h1>
            <nav id="globalNav"></nav>
        </div>
    </header>

    <div class="container">
        <div class="card">
            <h1 class="card-title">手順書編集</h1>

            <div id="loadingMessage" class="loading">読み込み中</div>

            <form id="manualForm" style="display: none;">
                <div class="form-group">
                    <label for="title">タイトル <span style="color: red;">*</span></label>
                    <input type="text" id="title" name="title" required>
                </div>

                <div class="form-group">
                    <label for="description">説明</label>
                    <textarea id="description" name="description" rows="4"></textarea>
                </div>

                <div class="form-group">
                    <label for="visibility">公開範囲</label>
                    <select id="visibility" name="visibility">
                        <option value="public">全体公開</option>
                        <option value="department">部署内公開</option>
                        <option value="private">非公開</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="tags">タグ（カンマ区切り）</label>
                    <input type="text" id="tags" name="tags" placeholder="例: 作業手順, 初心者向け">
                </div>

                <div class="form-group">
                    <label>ステップ</label>
                    <div id="stepsContainer"></div>
                    <button type="button" class="btn btn-secondary" id="addStepBtn">ステップを追加</button>
                </div>

                <div style="display: flex; gap: 1rem; margin-top: 2rem;">
                    <button type="submit" name="action" value="draft" class="btn btn-secondary">下書き保存</button>
                    <button type="submit" name="action" value="publish" class="btn btn-success">公開</button>
                    <a href="../index.py" class="btn">キャンセル</a>
                </div>
            </form>
        </div>
    </div>

    <script src="../static/js/api.js"></script>
    <script>
        let currentUser = null;
        let manualId = null;
        let stepCounter = 0;

        // 初期化
        async function init() {
            currentUser = await checkAuth();
            if (!currentUser) return;

            const nav = document.getElementById('globalNav');
            nav.innerHTML = renderGlobalNav(currentUser, {
                home: '../index.py',
                create: '../manuals/create.py',
                users: '../users/index.py',
                login: '../login.py'
            });
            attachLogoutHandler('../login.py');

            // URLパラメータから手順書IDを取得
            const params = new URLSearchParams(window.location.search);
            manualId = params.get('id');

            if (!manualId) {
                showAlert('手順書IDが指定されていません', 'error');
                return;
            }

            await loadManual();
        }

        // 手順書を読み込み
        async function loadManual() {
            try {
                const data = await ManualAPI.get(manualId);
                const manual = data.manual;

                // 編集権限チェック
                if (manual.author_id !== currentUser.id && currentUser.role !== 'admin') {
                    showAlert('編集権限がありません', 'error');
                    setTimeout(() => {
                        window.location.href = '../index.py';
                    }, 2000);
                    return;
                }

                // フォームに値を設定
                document.getElementById('title').value = manual.title;
                document.getElementById('description').value = manual.description || '';
                document.getElementById('visibility').value = manual.visibility;

                // タグを設定
                if (manual.tags && manual.tags.length > 0) {
                    document.getElementById('tags').value = manual.tags.map(t => t.name).join(', ');
                }

                // ステップを追加
                if (manual.steps && manual.steps.length > 0) {
                    manual.steps.forEach(step => {
                        addStep(step);
                    });
                } else {
                    addStep();
                }

                document.getElementById('loadingMessage').style.display = 'none';
                document.getElementById('manualForm').style.display = 'block';

            } catch (error) {
                handleError(error);
            }
        }

        function createStepElement(stepData = null) {
            stepCounter++;
            const stepDiv = document.createElement('div');
            stepDiv.className = 'step-item';
            stepDiv.id = `step-${stepCounter}`;
            stepDiv.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <h3 class="step-heading">ステップ</h3>
                    <button type="button" class="btn btn-danger" onclick="removeStep('step-${stepCounter}')" style="padding: 0.25rem 0.75rem;">削除</button>
                </div>

                <div style="margin-bottom: 0.75rem;">
                    <button type="button" class="btn btn-secondary" onclick="insertStepAfter('step-${stepCounter}')" style="padding: 0.25rem 0.75rem;">この下にステップを追加</button>
                </div>

                <div class="form-group">
                    <label>タイトル</label>
                    <input type="text" class="step-title" placeholder="ステップのタイトル" value="${stepData ? escapeHtml(stepData.title) : ''}">
                </div>

                <div class="form-group">
                    <label>内容</label>
                    <textarea class="step-content" rows="3" placeholder="手順の詳細">${stepData ? escapeHtml(stepData.content) : ''}</textarea>
                </div>

                <div class="form-group">
                    <label>備考</label>
                    <textarea class="step-note" rows="2" placeholder="注意事項など">${stepData ? escapeHtml(stepData.note) : ''}</textarea>
                </div>

                <div class="form-group">
                    <label>画像</label>
                    <div class="step-existing-image-container"></div>
                    <input type="file" class="step-image" accept="image/*">
                    <small style="display: block; color: #666; margin-top: 0.25rem;">または下の欄をクリックして、クリップボードの画像を貼り付け</small>
                    <div class="step-image-paste-area" tabindex="0" style="margin-top: 0.5rem; padding: 0.75rem; border: 1px dashed #999; border-radius: 4px; color: #666; background: #fafafa;">
                        ここに画像を貼り付け（Ctrl+V / Cmd+V）
                    </div>
                    <input type="hidden" class="step-existing-image" value="${stepData && stepData.image_path ? stepData.image_path : ''}">
                    <div class="step-image-preview" style="margin-top: 0.5rem;"></div>
                </div>
            `;

            // 既存画像を表示
            const existingImageContainer = stepDiv.querySelector('.step-existing-image-container');
            const existingImageInput = stepDiv.querySelector('.step-existing-image');
            if (stepData && stepData.image_path) {
                const imagePath = resolveAppAssetPath(stepData.image_path);
                existingImageContainer.innerHTML = `
                    <div style="position: relative; display: inline-block; margin-bottom: 0.5rem;">
                        <img src="${imagePath}" style="max-width: 300px; border-radius: 4px;">
                        <button type="button" class="btn btn-danger remove-existing-image-btn" style="position: absolute; top: 0.25rem; right: 0.25rem; width: 1.8rem; height: 1.8rem; padding: 0; line-height: 1; border-radius: 999px;">×</button>
                    </div>
                `;

                const removeExistingImageBtn = existingImageContainer.querySelector('.remove-existing-image-btn');
                removeExistingImageBtn.addEventListener('click', function() {
                    existingImageInput.value = '';
                    existingImageContainer.innerHTML = '';
                    showAlert('既存画像を削除しました', 'success');
                });
            }

            // 画像アップロードのプレビュー
            const imageInput = stepDiv.querySelector('.step-image');
            const imagePreview = stepDiv.querySelector('.step-image-preview');
            const pasteArea = stepDiv.querySelector('.step-image-paste-area');

            function updateImagePreview(file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.innerHTML = `
                        <div style="position: relative; display: inline-block;">
                            <img src="${e.target.result}" style="max-width: 300px; border-radius: 4px;">
                            <button type="button" class="btn btn-danger remove-preview-image-btn" style="position: absolute; top: 0.25rem; right: 0.25rem; width: 1.8rem; height: 1.8rem; padding: 0; line-height: 1; border-radius: 999px;">×</button>
                        </div>
                    `;

                    const removePreviewImageBtn = imagePreview.querySelector('.remove-preview-image-btn');
                    removePreviewImageBtn.addEventListener('click', function() {
                        imagePreview.innerHTML = '';
                        imageInput.value = '';
                        stepDiv.pastedImageFile = null;
                        showAlert('選択中の画像を削除しました', 'success');
                    });
                };
                reader.readAsDataURL(file);
            }

            imageInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    stepDiv.pastedImageFile = null;
                    updateImagePreview(file);
                }
            });

            pasteArea.addEventListener('paste', function(e) {
                const items = e.clipboardData && e.clipboardData.items;
                if (!items) {
                    return;
                }

                for (const item of items) {
                    if (item.type.startsWith('image/')) {
                        const blob = item.getAsFile();
                        if (!blob) {
                            continue;
                        }

                        const pastedFile = new File([blob], `pasted_${Date.now()}.png`, { type: blob.type || 'image/png' });
                        stepDiv.pastedImageFile = pastedFile;
                        imageInput.value = '';
                        updateImagePreview(pastedFile);
                        e.preventDefault();
                        showAlert('画像を貼り付けました', 'success');
                        return;
                    }
                }
            });

            return stepDiv;
        }

        // ステップ番号を振り直し
        function renumberSteps() {
            const stepDivs = document.querySelectorAll('#stepsContainer .step-item');
            stepDivs.forEach((stepDiv, index) => {
                const heading = stepDiv.querySelector('.step-heading');
                if (heading) {
                    heading.textContent = `ステップ ${index + 1}`;
                }
            });
        }

        // ステップを追加
        function addStep(stepData = null) {
            const container = document.getElementById('stepsContainer');
            const stepDiv = createStepElement(stepData);
            container.appendChild(stepDiv);
            renumberSteps();
        }

        // 指定ステップの下にステップを追加
        function insertStepAfter(stepId) {
            const currentStep = document.getElementById(stepId);
            if (!currentStep) {
                return;
            }

            const stepDiv = createStepElement();
            currentStep.insertAdjacentElement('afterend', stepDiv);
            renumberSteps();
        }

        // ステップを削除
        function removeStep(stepId) {
            const stepDiv = document.getElementById(stepId);
            if (stepDiv) {
                stepDiv.remove();
                renumberSteps();
            }
        }

        // フォーム送信
        document.getElementById('manualForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const submitter = e.submitter;
            const action = submitter.value;

            // ローディング表示
            const loadingOverlay = document.createElement('div');
            loadingOverlay.id = 'loadingOverlay';
            loadingOverlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            `;
            loadingOverlay.innerHTML = `
                <div style="background: white; padding: 2rem; border-radius: 8px; text-align: center;">
                    <div style="margin-bottom: 1rem;">
                        <svg style="animation: spin 1s linear infinite; width: 50px; height: 50px;" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="12" cy="12" r="10" stroke="#3b82f6" stroke-width="4" stroke-linecap="round" stroke-dasharray="31.416" stroke-dashoffset="31.416"></circle>
                        </svg>
                    </div>
                    <p style="margin: 0; font-size: 1.1rem; color: #333;">${action === 'publish' ? '公開中...' : '保存中...'}</p>
                </div>
                <style>
                    @keyframes spin {
                        from { transform: rotate(0deg); }
                        to { transform: rotate(360deg); }
                    }
                </style>
            `;
            document.body.appendChild(loadingOverlay);

            // ボタンを無効化
            const buttons = document.querySelectorAll('button[type="submit"], button[type="button"]');
            buttons.forEach(btn => btn.disabled = true);

            try {
                // 基本情報を取得
                const title = document.getElementById('title').value;
                const description = document.getElementById('description').value;
                const visibility = document.getElementById('visibility').value;
                const tagsInput = document.getElementById('tags').value;

                // タグを配列に変換
                const tags = tagsInput.split(',').map(t => t.trim()).filter(t => t);

                // ステップを取得
                const steps = [];
                const stepDivs = document.querySelectorAll('[id^="step-"]');

                for (const stepDiv of stepDivs) {
                    const stepTitle = stepDiv.querySelector('.step-title').value;
                    const stepContent = stepDiv.querySelector('.step-content').value;
                    const stepNote = stepDiv.querySelector('.step-note').value;
                    const stepImageInput = stepDiv.querySelector('.step-image');
                    const existingImage = stepDiv.querySelector('.step-existing-image').value;

                    let imagePath = existingImage;

                    const uploadFile = stepImageInput.files[0] || stepDiv.pastedImageFile;

                    // 新しい画像がある場合はアップロード
                    if (uploadFile) {
                        const imageData = await ManualAPI.uploadImage(uploadFile);
                        imagePath = imageData.path;
                    }

                    steps.push({
                        title: stepTitle || `ステップ ${steps.length + 1}`,
                        content: stepContent,
                        note: stepNote,
                        image_path: imagePath
                    });
                }

                // 手順書データ
                const manualData = {
                    title: title,
                    description: description,
                    visibility: visibility,
                    is_published: action === 'publish' ? 1 : 0,
                    tags: tags,
                    steps: steps
                };

                // API呼び出し
                await ManualAPI.update(manualId, manualData);

                showAlert('手順書を更新しました', 'success');

                setTimeout(() => {
                    window.location.href = `../manuals/view.py?id=${manualId}`;
                }, 1000);

            } catch (error) {
                // エラー時はローディングを削除してボタンを再有効化
                const overlay = document.getElementById('loadingOverlay');
                if (overlay) overlay.remove();
                buttons.forEach(btn => btn.disabled = false);
                handleError(error);
            }
        });

        // ユーティリティ
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // イベントリスナー
        document.getElementById('addStepBtn').addEventListener('click', () => addStep());

        // 初期化実行
        init();
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
