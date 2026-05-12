# -*- coding: utf-8 -*-
"""
全局常量：HTTP 状态码与业务码、默认分页、任务状态等。
供 api 与 services 引用，避免魔术数字。
"""

# 业务响应码（与前端约定）
CODE_SUCCESS = 200
CODE_BAD_REQUEST = 400
CODE_UNAUTHORIZED = 401
CODE_FORBIDDEN = 403
CODE_NOT_FOUND = 404
CODE_SERVER_ERROR = 500

# 分页
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# 聚类任务状态
TASK_STATUS_PENDING = 'pending'
TASK_STATUS_RUNNING = 'running'
TASK_STATUS_COMPLETED = 'completed'
TASK_STATUS_FAILED = 'failed'

# 摘要来源类型
SOURCE_TYPE_TEXT = 'text'
SOURCE_TYPE_CLUSTER = 'cluster'

# 操作历史类型（与前端展示一致）
OP_TYPE_TEXT_UPLOAD = 'text_upload'
OP_TYPE_CLUSTER_CREATE = 'cluster_create'
OP_TYPE_CLUSTER_COMPLETE = 'cluster_complete'
OP_TYPE_SUMMARY_CREATE = 'summary_create'

# 用户角色（与 users.role 对应）
ROLE_ADMIN = 'admin'
ROLE_USER = 'user'
ROLE_GUEST = 'guest'
