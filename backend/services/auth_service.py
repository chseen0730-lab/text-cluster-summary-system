# -*- coding: utf-8 -*-
"""
认证业务逻辑：注册、登录、登出（Token 入库与失效）。
密码哈希与 Token 生成使用 utils.auth。
"""
import json
import secrets
from datetime import datetime, timedelta
from database import get_connection, fetch_one, fetch_all, execute, last_rowid
from utils.auth import hash_password, verify_password, generate_token

def register(username, password, nickname=None, email=None):
    """
    注册新用户。
    :return: (dict 用户信息, str token) 或 (None, str 错误信息)
    """
    username = (username or '').strip()
    if len(username) < 3 or len(username) > 20:
        return None, '用户名长度需为 3-20 个字符'
    if not password or len(password) < 6:
        return None, '密码长度不能少于 6 个字符'
    salt = 'salt_' + secrets.token_hex(8)
    password_hash = hash_password(password, salt)
    with get_connection() as conn:
        existing = fetch_one(conn, 'SELECT id FROM users WHERE username = ?', (username,))
        if existing:
            return None, '用户名已存在'
        execute(conn,
            'INSERT INTO users (username, password_hash, salt, nickname, email, role) VALUES (?,?,?,?,?,?)',
            (username, password_hash, salt, (nickname or username).strip(), (email or '').strip(), 'user'))
        uid = last_rowid(conn)
        user = fetch_one(conn, 'SELECT id, username, nickname, email, role, created_at FROM users WHERE id = ?', (uid,))
    return _user_row_to_response(user), None

def login(username, password, token_expire_seconds):
    """
    登录：校验密码后生成 token 并入库。
    :return: (dict 用户信息, str token) 或 (None, str 错误信息)
    """
    username = (username or '').strip()
    with get_connection() as conn:
        row = fetch_one(conn, 'SELECT id, username, password_hash, salt, nickname, email, role, created_at FROM users WHERE username = ?', (username,))
        if not row:
            return None, '用户名或密码错误'
        if not verify_password(password, row['salt'], row['password_hash']):
            return None, '用户名或密码错误'
        user = dict(row)
    token = generate_token()
    expires_at = (datetime.utcnow() + timedelta(seconds=token_expire_seconds)).strftime('%Y-%m-%d %H:%M:%S')
    with get_connection() as conn:
        execute(conn, 'INSERT INTO auth_tokens (user_id, token, expires_at) VALUES (?,?,?)', (user['id'], token, expires_at))
    resp_user = _user_row_to_response(user)
    return resp_user, token

def logout(token):
    """
    登出：删除该 token 记录。
    """
    with get_connection() as conn:
        execute(conn, 'DELETE FROM auth_tokens WHERE token = ?', (token,))

def get_user_by_token(token):
    """
    根据 token 获取当前用户（并校验未过期）。
    :return: dict 用户信息或 None
    """
    with get_connection() as conn:
        row = fetch_one(conn,
            'SELECT u.id, u.username, u.nickname, u.email, u.role, u.created_at FROM users u JOIN auth_tokens t ON u.id = t.user_id WHERE t.token = ? AND datetime(t.expires_at) > datetime("now")',
            (token,))
        if not row:
            return None
        return _user_row_to_response(dict(row))

def _user_row_to_response(row):
    """
    将数据库行转为前端需要的用户对象（含 createdAt）。
    不包含 password_hash、salt 等敏感字段。
    """
    if not row:
        return None
    created = row.get('created_at')
    if created:
        created = created[:10] if len(created) >= 10 else created
    return {
        'id': row['id'],
        'username': row['username'],
        'nickname': row.get('nickname') or row['username'],
        'email': row.get('email') or '',
        'role': row.get('role') or 'user',
        'createdAt': created,
    }
