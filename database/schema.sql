-- ユーザーテーブル
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user', -- 'admin' or 'user'
    department TEXT,
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT DEFAULT (datetime('now', 'localtime'))
);

-- セッションテーブル
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    expires_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 手順書テーブル
CREATE TABLE IF NOT EXISTS manuals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    author_id INTEGER NOT NULL,
    is_published INTEGER DEFAULT 0, -- 0: 下書き, 1: 公開
    visibility TEXT DEFAULT 'public', -- 'public', 'private', 'department'
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT DEFAULT (datetime('now', 'localtime')),
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (author_id) REFERENCES users(id)
);

-- 手順書ステップテーブル
CREATE TABLE IF NOT EXISTS manual_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manual_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    note TEXT,
    image_path TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (manual_id) REFERENCES manuals(id) ON DELETE CASCADE
);

-- タグテーブル
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

-- 手順書とタグの関連テーブル
CREATE TABLE IF NOT EXISTS manual_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manual_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (manual_id) REFERENCES manuals(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE(manual_id, tag_id)
);

-- 手順書更新履歴テーブル
CREATE TABLE IF NOT EXISTS manual_histories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manual_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL, -- 'created', 'updated', 'published', 'unpublished'
    description TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (manual_id) REFERENCES manuals(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 閲覧ログテーブル
CREATE TABLE IF NOT EXISTS view_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manual_id INTEGER NOT NULL,
    user_id INTEGER,
    viewed_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (manual_id) REFERENCES manuals(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_manuals_author ON manuals(author_id);
CREATE INDEX IF NOT EXISTS idx_manuals_published ON manuals(is_published);
CREATE INDEX IF NOT EXISTS idx_manual_steps_manual ON manual_steps(manual_id);
CREATE INDEX IF NOT EXISTS idx_manual_tags_manual ON manual_tags(manual_id);
CREATE INDEX IF NOT EXISTS idx_manual_tags_tag ON manual_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_manual_histories_manual ON manual_histories(manual_id);
CREATE INDEX IF NOT EXISTS idx_view_logs_manual ON view_logs(manual_id);
