# -*- coding: utf-8 -*-
"""
聚类任务表模型：表名与字段说明。

表名：cluster_tasks
字段：id, user_id, name, description, text_ids（JSON 数组字符串）, cluster_count, algorithm, status, progress, created_at, completed_at, updated_at
说明：status 为 pending/running/completed/failed；progress 0-100；结果存 cluster_results。
"""
TABLE = 'cluster_tasks'
