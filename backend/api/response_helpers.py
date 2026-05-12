# -*- coding: utf-8 -*-
"""
统一响应封装：保证所有接口返回格式为 { code, message, data }。
便于前端统一处理与全局异常时格式一致。
"""

def success(data=None, message='ok'):
    """
    成功响应。
    :param data: 业务数据，可为 None
    :param message: 提示文案
    :return: (dict, int) 响应体与 200 状态码
    """
    return {'code': 200, 'message': message, 'data': data}, 200

def fail(code=400, message='请求参数错误', data=None):
    """
    业务失败响应。
    :param code: 业务码，常用 400 参数错误、401 未登录、404 不存在
    :param message: 错误说明
    :param data: 可选，通常为 None
    :return: (dict, int) 响应体与建议的 HTTP 状态码
    """
    return {'code': code, 'message': message, 'data': data or None}, (code if code in (401, 404, 403) else 400)
