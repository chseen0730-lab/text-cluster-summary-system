# -*- coding: utf-8 -*-
"""
配置模块：应用运行环境与数据库等配置。

仅使用 Python 标准库，不依赖第三方配置库。
可通过环境变量覆盖：FLASK_ENV, SECRET_KEY, DATABASE_PATH, MYSQL_* 等。
数据库连接密码在 MySQL 部署时固定为 123456（见项目 database/schema.sql 说明）。
"""
import os

# 项目根目录（backend 目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 运行环境：development / production
ENV = os.environ.get('FLASK_ENV', 'development')
DEBUG = ENV == 'development'

# 安全密钥：用于会话等，生产环境应从环境变量读取
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# 数据库：使用 SQLite（仅标准库），与 MySQL schema 逻辑一致；生产可改为 MySQL（需第三方驱动）
# 数据库连接密码 123456 用于 MySQL 部署时连接，此处 SQLite 无需密码
DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.abspath(os.path.join(BASE_DIR, 'data.db')))

# MySQL 配置（当使用 MySQL 时，连接密码固定为 123456，此处仅作占位说明）
MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '123456')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'text_cluster_summary')

# Token 有效期（秒）
TOKEN_EXPIRE_SECONDS = 7 * 24 * 3600  # 7 天

# 分页默认值
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# 以下为配置项说明，不参与运行：
# - FLASK_ENV：development 时 DEBUG 为 True，便于开发；生产环境设为 production。
# - SECRET_KEY：生产环境必须通过环境变量设置，用于会话等安全相关。
# - DATABASE_PATH：SQLite 文件路径；使用 MySQL 时需在连接层读取 MYSQL_* 并连接，密码 123456。
# - TOKEN_EXPIRE_SECONDS：登录 Token 有效时长，默认 7 天。
# - 列表接口统一支持 page、limit（或 pageSize），由 api 层从 request.args 读取并传入 service。
