// Manual Factory - Main JavaScript

// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });
});

// Confirm delete actions
function confirmDelete(message) {
    return confirm(message || '本当に削除しますか？この操作は取り消せません。');
}

// Add step to manual form
let stepCounter = 1;

function addStep() {
    stepCounter++;
    const stepsContainer = document.getElementById('steps-container');
    const stepHtml = `
        <div class="step-item" id="step-${stepCounter}">
            <div class="flex justify-between items-center mb-2">
                <h3>ステップ ${stepCounter}</h3>
                <button type="button" class="btn btn-danger btn-sm" onclick="removeStep(${stepCounter})">削除</button>
            </div>
            <div class="form-group">
                <label class="form-label">タイトル</label>
                <input type="text" name="step_title_${stepCounter}" class="form-control" required>
            </div>
            <div class="form-group">
                <label class="form-label">内容</label>
                <textarea name="step_content_${stepCounter}" class="form-control" rows="4" required></textarea>
            </div>
            <div class="form-group">
                <label class="form-label">備考</label>
                <textarea name="step_notes_${stepCounter}" class="form-control" rows="2" placeholder="補足情報や注意事項など（任意）"></textarea>
            </div>
            <div class="form-group">
                <label class="form-label">画像</label>
                <input type="file" name="step_image_${stepCounter}" class="form-control" accept="image/*">
            </div>
        </div>
    `;
    stepsContainer.insertAdjacentHTML('beforeend', stepHtml);
    updateStepCount();
}

function removeStep(stepId) {
    const stepElement = document.getElementById(`step-${stepId}`);
    if (stepElement) {
        stepElement.remove();
        updateStepCount();
    }
}

function updateStepCount() {
    const steps = document.querySelectorAll('.step-item');
    document.getElementById('step_count').value = steps.length;
    
    // Renumber steps
    steps.forEach((step, index) => {
        const title = step.querySelector('h3');
        if (title) {
            title.textContent = `ステップ ${index + 1}`;
        }
    });
}

// Image preview
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById(previewId);
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Search with enter key
function setupSearchForm() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                document.getElementById('search-form').submit();
            }
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    setupSearchForm();
    
    // Set initial step count if form exists
    const stepCountInput = document.getElementById('step_count');
    if (stepCountInput) {
        updateStepCount();
    }
});

// Form validation
function validateManualForm() {
    const title = document.querySelector('input[name="title"]');
    if (!title || !title.value.trim()) {
        alert('タイトルを入力してください');
        return false;
    }
    
    const steps = document.querySelectorAll('.step-item');
    if (steps.length === 0) {
        alert('少なくとも1つのステップを追加してください');
        return false;
    }
    
    return true;
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert('クリップボードにコピーしました');
    }, function() {
        alert('コピーに失敗しました');
    });
}
