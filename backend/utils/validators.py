# -*- coding: utf-8 -*-
"""
入参合法性校验：仅使用 Python 标准库，供 api 层在调用 service 前做统一校验。
校验失败返回 (False, 错误信息)，成功返回 (True, None)。
"""

def check_username(username):
    """
    校验用户名：非空、长度 3-20。
    :return: (True, None) 或 (False, str)
    """
    if not username or not isinstance(username, str):
        return False, '请输入用户名'
    u = username.strip()
    if len(u) < 3:
        return False, '用户名长度不能少于 3 个字符'
    if len(u) > 20:
        return False, '用户名长度不能超过 20 个字符'
    return True, None

def check_password(password, min_len=6):
    """
    校验密码：非空、长度至少 min_len。
    :return: (True, None) 或 (False, str)
    """
    if not password:
        return False, '请输入密码'
    if isinstance(password, str) and len(password) < min_len:
        return False, '密码长度不能少于 {} 个字符'.format(min_len)
    return True, None

def check_page_params(page, page_size, max_page_size=100):
    """
    校验分页参数：page >= 1，page_size 在 1..max_page_size。
    :return: (page, page_size) 已规范化的整数
    """
    try:
        p = max(1, int(page))
    except (TypeError, ValueError):
        p = 1
    try:
        ps = int(page_size)
        if ps < 1:
            ps = 10
        if ps > max_page_size:
            ps = max_page_size
    except (TypeError, ValueError):
        ps = 10
    return p, ps

def check_positive_int(value, name='ID'):
    """
    校验为正整数，用于路径参数 id。
    :return: (int, None) 或 (None, str 错误信息)
    """
    try:
        v = int(value)
        if v < 1:
            return None, '{} 必须为正整数'.format(name)
        return v, None
    except (TypeError, ValueError):
        return None, '{} 格式无效'.format(name)
