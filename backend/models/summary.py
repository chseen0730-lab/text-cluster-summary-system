# -*- coding: utf-8 -*-
"""
摘要表模型：表名与字段说明。

表名：summaries
字段：id, user_id, source_type（text/cluster）, source_id, title, content, word_count, created_at, updated_at
说明：source_type+source_id 区分来源为单篇文本或某聚类任务。
"""
TABLE = 'summaries'
