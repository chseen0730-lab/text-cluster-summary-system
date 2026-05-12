# -*- coding: utf-8 -*-
"""
认证依赖：从请求头 Authorization: Bearer <token> 解析并注入当前用户。

说明：
- 仅使用 Flask 的 request、g；无第三方库。
- get_current_user() 用于可选登录场景；auth_required 装饰器用于必须登录的接口，未登录返回 401。
- Token 存储在 auth_tokens 表中，过期由数据库查询时过滤（expires_at > now）。
"""
from functools import wraps
from flask import request, g

from services.auth_service import get_user_by_token

def get_current_user():
    """
    从当前请求中解析 Bearer Token 并返回用户信息。
    :return: dict 用户信息或 None
    """
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return None
    token = auth[7:].strip()
    return get_user_by_token(token)

def auth_required(f):
    """装饰器：要求已登录，否则返回 401。"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if not user:
            return {'code': 401, 'message': '未登录或登录已过期', 'data': None}, 401
        g.current_user = user
        return f(*args, **kwargs)
    return wrapped
