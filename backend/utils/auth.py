# -*- coding: utf-8 -*-
"""
认证工具：密码哈希与校验、Token 生成与校验。
仅使用 Python 标准库 hashlib、secrets、hmac；不依赖 PyJWT。
"""
import hashlib
import secrets
from datetime import datetime, timedelta

def hash_password(password, salt):
    """
    对明文密码加盐哈希。
    :param password: 明文密码字符串
    :param salt: 盐字符串
    :return: 十六进制哈希字符串，与 MySQL SHA2(CONCAT(salt,password),256) 逻辑一致
    """
    raw = (salt + password).encode('utf-8')
    return hashlib.sha256(raw).hexdigest().lower()

def verify_password(password, salt, password_hash):
    """
    校验密码是否与存储的哈希一致。
    :param password: 用户输入的明文密码
    :param salt: 该用户的盐
    :param password_hash: 存储的密码哈希
    :return: bool
    """
    if not salt or not password_hash:
        return False
    salt = str(salt).strip()
    password_hash = str(password_hash).strip().lower()
    return hash_password(password, salt) == password_hash

def generate_token():
    """
    生成安全随机 token，用于登录态。
    :return: 可放入 Header Authorization Bearer 的字符串
    """
    return secrets.token_urlsafe(32)

def token_expires_at(expire_seconds):
    """
    计算 token 过期时间点。
    :param expire_seconds: 有效秒数
    :return: datetime
    """
    return datetime.utcnow() + timedelta(seconds=expire_seconds)

def datetime_to_str(dt):
    """将 datetime 转为 ISO 格式字符串。"""
    if dt is None:
        return None
    return dt.isoformat() if hasattr(dt, 'isoformat') else str(dt)
