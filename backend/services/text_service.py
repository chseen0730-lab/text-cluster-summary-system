# -*- coding: utf-8 -*-
"""
文本业务逻辑：解析、入库、查询、更新、删除。

入参合法性在 api 层做基础校验，此处做存在性与归属校验。
- 所有写操作（创建、更新、删除）均校验 user_id，确保用户只能操作自己的文本。
- 字数 word_count 在创建与更新 content 时自动计算。
- 列表支持按 keyword（标题/内容模糊）、category 筛选，分页使用 page、page_size。
"""
import json
from database import get_connection, fetch_one, fetch_all, execute, last_rowid

def create(user_id, title, content, category=None):
    """
    创建一条文本记录。
    :param user_id: 用户 ID
    :param title: 标题
    :param content: 正文
    :param category: 可选分类
    :return: dict 新记录（含 id, created_at 等）
    """
    word_count = len((content or '').strip())
    with get_connection() as conn:
        execute(conn,
            'INSERT INTO texts (user_id, title, content, word_count, category, status) VALUES (?,?,?,?,?,?)',
            (user_id, (title or '').strip(), (content or '').strip(), word_count, (category or '').strip() or None, 'active'))
        row_id = last_rowid(conn)
        return fetch_one(conn, 'SELECT * FROM texts WHERE id = ?', (row_id,))

def get_by_id(text_id, user_id=None):
    """
    按 ID 查询文本；若传 user_id 则校验归属。
    :return: dict 或 None
    """
    with get_connection() as conn:
        if user_id is not None:
            return fetch_one(conn, 'SELECT * FROM texts WHERE id = ? AND user_id = ?', (text_id, user_id))
        return fetch_one(conn, 'SELECT * FROM texts WHERE id = ?', (text_id,))

def list_by_user(user_id, keyword=None, category=None, page=1, page_size=10):
    """
    分页查询用户的文本列表，支持关键字、分类筛选。
    :return: (list[dict], total_count)
    """
    with get_connection() as conn:
        where = 'user_id = ?'
        params = [user_id]
        if keyword:
            where += ' AND (title LIKE ? OR content LIKE ?)'
            params.extend(['%' + keyword + '%', '%' + keyword + '%'])
        if category:
            where += ' AND category = ?'
            params.append(category)
        total = fetch_one(conn, 'SELECT COUNT(*) AS c FROM texts WHERE ' + where, params)['c']
        offset = (page - 1) * page_size
        params.extend([page_size, offset])
        rows = fetch_all(conn,
            'SELECT * FROM texts WHERE ' + where + ' ORDER BY created_at DESC LIMIT ? OFFSET ?', params)
        return rows, total

def update(text_id, user_id, title=None, content=None, category=None):
    """
    更新文本；仅允许归属用户更新。
    :return: dict 更新后记录或 None
    """
    with get_connection() as conn:
        row = fetch_one(conn, 'SELECT * FROM texts WHERE id = ? AND user_id = ?', (text_id, user_id))
        if not row:
            return None
        updates = []
        params = []
        if title is not None:
            updates.append('title = ?')
            params.append(title.strip())
        if content is not None:
            updates.append('content = ?')
            params.append(content.strip())
            updates.append('word_count = ?')
            params.append(len(content.strip()))
        if category is not None:
            updates.append('category = ?')
            params.append(category.strip() or None)
        if not updates:
            return row
        params.append(text_id)
        execute(conn, 'UPDATE texts SET ' + ', '.join(updates) + ', updated_at = datetime("now","localtime") WHERE id = ?', params)
        return fetch_one(conn, 'SELECT * FROM texts WHERE id = ?', (text_id,))

def delete(text_id, user_id):
    """
    删除文本；仅允许归属用户删除。
    :return: bool 是否删除了记录
    """
    with get_connection() as conn:
        cur = execute(conn, 'DELETE FROM texts WHERE id = ? AND user_id = ?', (text_id, user_id))
        return cur.rowcount > 0

def get_by_ids(text_ids, user_id):
    """
    按 ID 列表批量查询，且归属当前用户。
    :param text_ids: list[int]
    :return: list[dict]
    """
    if not text_ids:
        return []
    placeholders = ','.join('?' * len(text_ids))
    with get_connection() as conn:
        return fetch_all(conn,
            'SELECT * FROM texts WHERE id IN (' + placeholders + ') AND user_id = ?',
            list(text_ids) + [user_id])

def batch_delete(text_ids, user_id):
    """
    批量删除；仅删除归属当前用户的记录。
    :return: int 删除条数
    """
    if not text_ids:
        return 0
    placeholders = ','.join('?' * len(text_ids))
    with get_connection() as conn:
        cur = execute(conn, 'DELETE FROM texts WHERE id IN (' + placeholders + ') AND user_id = ?', list(text_ids) + [user_id])
        return cur.rowcount
