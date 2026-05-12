# -*- coding: utf-8 -*-
"""
操作历史表模型：表名与字段说明。

表名：operation_history
字段：id, user_id, op_type, op_desc, target_id, target_title, created_at
说明：op_type 如 text_upload, cluster_create, cluster_complete, summary_create；供历史列表与统计。
"""
TABLE = 'operation_history'
