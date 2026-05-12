# -*- coding: utf-8 -*-
"""
数据库模块：使用 Python 标准库 sqlite3 实现数据持久化。

职责：
- 与 MySQL schema 表结构、字段名保持一致，便于迁移至 MySQL（需第三方驱动）。
- 提供连接获取、执行与查询封装；无第三方依赖。
- 应用启动时根据配置创建 SQLite 表（若不存在）。

使用方式：
- 在 app 中调用 init_database(config) 完成初始化。
- 业务层通过 get_connection() 获取连接，配合 execute/fetch_one/fetch_all 使用。
"""
import sqlite3
import os
import threading
from contextlib import contextmanager

# 当前配置在 app 启动时注入
_config = None

def init_database(config):
    """初始化数据库配置并创建表（若不存在）。"""
    global _config
    _config = config
    os.makedirs(os.path.dirname(config.get('DATABASE_PATH', 'data.db')) or '.', exist_ok=True)
    with get_connection() as conn:
        _create_tables(conn)

def _create_tables(conn):
    """创建 SQLite 表结构（与 MySQL schema 对应）。"""
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        nickname TEXT,
        email TEXT,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    );
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

    CREATE TABLE IF NOT EXISTS auth_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT NOT NULL UNIQUE,
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_tokens_user_id ON auth_tokens(user_id);
    CREATE INDEX IF NOT EXISTS idx_tokens_expires ON auth_tokens(expires_at);

    CREATE TABLE IF NOT EXISTS texts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL DEFAULT '',
        content TEXT NOT NULL,
        word_count INTEGER NOT NULL DEFAULT 0,
        category TEXT,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_texts_user_id ON texts(user_id);
    CREATE INDEX IF NOT EXISTS idx_texts_created_at ON texts(created_at);
    CREATE INDEX IF NOT EXISTS idx_texts_category ON texts(category);

    CREATE TABLE IF NOT EXISTS cluster_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        text_ids TEXT NOT NULL,
        cluster_count INTEGER NOT NULL DEFAULT 3,
        algorithm TEXT NOT NULL DEFAULT 'kmeans',
        status TEXT NOT NULL DEFAULT 'pending',
        progress INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        completed_at TEXT,
        updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON cluster_tasks(user_id);
    CREATE INDEX IF NOT EXISTS idx_tasks_status ON cluster_tasks(status);
    CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON cluster_tasks(created_at);

    CREATE TABLE IF NOT EXISTS cluster_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        cluster_index INTEGER NOT NULL,
        text_id INTEGER NOT NULL,
        score REAL,
        sort_order INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (task_id) REFERENCES cluster_tasks(id) ON DELETE CASCADE,
        FOREIGN KEY (text_id) REFERENCES texts(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_results_task_id ON cluster_results(task_id);
    CREATE INDEX IF NOT EXISTS idx_results_text_id ON cluster_results(text_id);

    CREATE TABLE IF NOT EXISTS summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        source_type TEXT NOT NULL,
        source_id INTEGER NOT NULL,
        title TEXT NOT NULL DEFAULT '',
        content TEXT NOT NULL,
        word_count INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_summaries_user_id ON summaries(user_id);
    CREATE INDEX IF NOT EXISTS idx_summaries_source ON summaries(source_type, source_id);
    CREATE INDEX IF NOT EXISTS idx_summaries_created_at ON summaries(created_at);

    CREATE TABLE IF NOT EXISTS operation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        op_type TEXT NOT NULL,
        op_desc TEXT,
        target_id INTEGER,
        target_title TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_history_user_id ON operation_history(user_id);
    CREATE INDEX IF NOT EXISTS idx_history_op_type ON operation_history(op_type);
    CREATE INDEX IF NOT EXISTS idx_history_created_at ON operation_history(created_at);
    """)

_local = threading.local()

@contextmanager
def get_connection():
    """获取数据库连接（上下文管理器），自动提交或回滚。"""
    path = _config.get('DATABASE_PATH', 'data.db') if _config else 'data.db'
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def execute(conn, sql, params=None):
    """执行一条 SQL（INSERT/UPDATE/DELETE）。返回 cursor。"""
    params = params or ()
    return conn.execute(sql, params)

def fetch_one(conn, sql, params=None):
    """查询单行，返回 dict 或 None。"""
    params = params or ()
    cur = conn.execute(sql, params)
    row = cur.fetchone()
    return dict(row) if row else None

def fetch_all(conn, sql, params=None):
    """查询多行，返回 list[dict]。"""
    params = params or ()
    cur = conn.execute(sql, params)
    return [dict(r) for r in cur.fetchall()]

def last_rowid(conn):
    """返回最后插入的自增 ID。"""
    return conn.execute('SELECT last_insert_rowid()').fetchone()[0]

# 设计说明：
# - 本模块使用 sqlite3 实现持久化，与规划中 MySQL 表名、字段名保持一致，便于将 schema.sql 在 MySQL 执行后，
#   通过更换连接层（如使用 pymysql）迁移至 MySQL，数据库连接密码按规划固定为 123456。
# - 所有写操作均在 with get_connection() 内完成，由上下文管理器统一 commit/rollback，避免连接泄漏。
# - row_factory 设为 sqlite3.Row，fetch_one/fetch_all 返回 dict 便于业务层使用。
#
# 表与规划对应关系：
# - users：用户账号、密码哈希、盐、昵称、邮箱、角色、创建/更新时间。
# - auth_tokens：当前有效 Token，含 user_id、过期时间，登出时删除对应记录。
# - texts：用户文本，含 title、content、word_count、category、status。
# - cluster_tasks：聚类任务，含 name、text_ids（JSON）、cluster_count、algorithm、status、progress。
# - cluster_results：聚类结果，task_id、cluster_index、text_id、score、sort_order。
# - summaries：摘要，source_type（text/cluster）、source_id、title、content、word_count。
# - operation_history：操作历史，op_type、op_desc、target_id、target_title，支撑历史列表与近7天统计。
