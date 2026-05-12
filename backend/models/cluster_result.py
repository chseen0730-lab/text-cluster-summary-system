# -*- coding: utf-8 -*-
"""
聚类结果表模型：表名与字段说明。

表名：cluster_results
字段：id, task_id（外键）, cluster_index（簇序号）, text_id（外键）, score, sort_order, created_at
说明：同一 task_id 下按 cluster_index 分组即可得到各簇的文本列表。
"""
TABLE = 'cluster_results'
