# -*- coding: utf-8 -*-
"""
认证接口：注册、登录、登出。

RESTful：POST /api/auth/register, POST /api/auth/login, POST /api/auth/logout
- 注册：入参 username（必填）、password（必填）、nickname、email；成功后自动登录并返回 user+token。
- 登录：入参 username、password；成功返回 user（含 id、username、nickname、email、role、createdAt）与 token。
- 登出：需在请求头携带 Authorization: Bearer <token>，服务端使该 token 失效。
"""
from flask import Blueprint, request, current_app, jsonify
from services import auth_service

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    """
    注册新用户。
    入参：username, password, nickname?, email?
    返回：{ code, message, data: { user, token } }
    """
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    nickname = data.get('nickname', '').strip()
    email = data.get('email', '').strip()
    if not username:
        return jsonify({'code': 400, 'message': '请输入用户名', 'data': None}), 400
    if not password:
        return jsonify({'code': 400, 'message': '请输入密码', 'data': None}), 400
    user, err = auth_service.register(username, password, nickname=nickname or None, email=email or None)
    if err:
        return jsonify({'code': 400, 'message': err, 'data': None}), 400
    _, token = auth_service.login(username, password, current_app.config.get('TOKEN_EXPIRE_SECONDS', 604800))
    return jsonify({'code': 200, 'message': '注册成功', 'data': {'user': user, 'token': token}})

@bp.route('/login', methods=['POST'])
def login():
    """
    登录。
    入参：username, password
    返回：{ code, message, data: { user, token } }
    """
    try:
        data = request.get_json() or {}
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''
        if not username:
            return jsonify({'code': 400, 'message': '请输入用户名', 'data': None}), 400
        if not password:
            return jsonify({'code': 400, 'message': '请输入密码', 'data': None}), 400
        user, token_or_err = auth_service.login(username, password, current_app.config.get('TOKEN_EXPIRE_SECONDS', 604800))
        if not user:
            return jsonify({'code': 401, 'message': token_or_err or '登录失败', 'data': None}), 401
        return jsonify({'code': 200, 'message': '登录成功', 'data': {'user': user, 'token': token_or_err}})
    except Exception as e:
        current_app.logger.exception(e)
        return jsonify({'code': 500, 'message': '登录服务异常，请重试', 'data': None}), 500

@bp.route('/logout', methods=['POST'])
def logout():
    """
    登出：使当前 token 失效。
    请求头需带 Authorization: Bearer <token>
    """
    from api.auth_required import get_current_user
    user = get_current_user()
    if user:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            auth_service.logout(auth_header[7:].strip())
    return jsonify({'code': 200, 'message': '已登出', 'data': None})
