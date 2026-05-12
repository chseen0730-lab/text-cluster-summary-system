# -*- coding: utf-8 -*-
"""
用户表模型：表名与字段说明，供 services 与 database 使用。

表名：users
字段：id（主键）, username（唯一）, password_hash, salt, nickname, email, role, created_at, updated_at
说明：密码仅存哈希，盐与哈希算法与 utils.auth 一致；role 可选 admin/user/guest。
"""
TABLE = 'users'
