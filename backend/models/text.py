# -*- coding: utf-8 -*-
"""
文本表模型：表名与字段说明。

表名：texts
字段：id, user_id（外键）, title, content, word_count, category, status（active/archived）, created_at, updated_at
说明：word_count 由应用层在写入时计算；为聚类与摘要的输入数据源。
"""
TABLE = 'texts'
