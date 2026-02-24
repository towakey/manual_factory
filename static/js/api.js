// API通信用のユーティリティ

const path = window.location.pathname;

function detectAppRoot(pathname) {
    const patterns = [
        /\/index\.py$/,
        /\/login\.py$/,
        /\/manuals\/(create|edit|view)\.py$/,
        /\/users\/index\.py$/
    ];

    for (const pattern of patterns) {
        if (pattern.test(pathname)) {
            const base = pathname.replace(pattern, '');
            return base || '';
        }
    }

    return '';
}

const APP_ROOT = detectAppRoot(path);
const API_BASE = `${APP_ROOT}/cgi-bin/api`;

// APIリクエストを送信
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}/${endpoint}`;
    
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    };
    
    const config = { ...defaultOptions, ...options };
    
    // GETリクエストの場合はbodyを削除
    if (config.method === 'GET') {
        delete config.body;
    }
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'リクエストに失敗しました');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// 認証API
const AuthAPI = {
    login: async (email, password) => {
        return apiRequest('auth_login.py', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    },
    
    logout: async () => {
        return apiRequest('auth_logout.py', {
            method: 'POST'
        });
    },
    
    getCurrentUser: async () => {
        return apiRequest('auth_me.py');
    }
};

// ユーザーAPI
const UserAPI = {
    list: async (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`users_list.py?${query}`);
    },
    
    create: async (userData) => {
        return apiRequest('users_create.py', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    },
    
    update: async (userId, userData) => {
        return apiRequest(`users_update.py?id=${userId}`, {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    },
    
    delete: async (userId) => {
        return apiRequest(`users_delete.py?id=${userId}`, {
            method: 'POST'
        });
    }
};

// 手順書API
const ManualAPI = {
    list: async (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`manuals_list.py?${query}`);
    },
    
    get: async (manualId) => {
        return apiRequest(`manuals_get.py?id=${manualId}`);
    },
    
    create: async (manualData) => {
        return apiRequest('manuals_create.py', {
            method: 'POST',
            body: JSON.stringify(manualData)
        });
    },
    
    update: async (manualId, manualData) => {
        return apiRequest(`manuals_update.py?id=${manualId}`, {
            method: 'POST',
            body: JSON.stringify(manualData)
        });
    },
    
    delete: async (manualId) => {
        return apiRequest(`manuals_delete.py?id=${manualId}`, {
            method: 'POST'
        });
    },
    
    uploadImage: async (imageFile) => {
        const formData = new FormData();
        formData.append('image', imageFile);
        
        const response = await fetch(`${API_BASE}/upload_image.py`, {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || '画像のアップロードに失敗しました');
        }
        
        return data;
    }
};

// アラート表示
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // 5秒後に自動削除
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// エラーハンドリング
function handleError(error) {
    console.error('Error:', error);
    showAlert(error.message || 'エラーが発生しました', 'error');
}

// 認証チェック
async function checkAuth() {
    try {
        const data = await AuthAPI.getCurrentUser();
        return data.user;
    } catch (error) {
        // 認証エラーの場合はログインページにリダイレクト
        const loginPath = `${APP_ROOT}/login.py`;
        if (window.location.pathname !== loginPath) {
            window.location.href = loginPath;
        }
        return null;
    }
}
