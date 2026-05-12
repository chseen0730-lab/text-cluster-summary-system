# -*- coding: utf-8 -*-
"""
操作历史业务逻辑：写入历史、分页查询、按日统计（支撑近7天活跃度等）。

- 各业务模块在关键操作（上传文本、创建/完成聚类、生成摘要）后调用 add() 写入一条记录。
- 列表支持按 op_type、keyword 筛选，按 created_at 倒序分页。
- activity_by_days(user_id, days) 用于个人中心近 N 天每日操作次数，支撑前端图表。
"""
from datetime import datetime, timedelta
from database import get_connection, fetch_one, fetch_all, execute

def add(user_id, op_type, op_desc=None, target_id=None, target_title=None):
    """
    写入一条操作历史。
    :param user_id: 用户 ID
    :param op_type: 操作类型，如 text_upload, cluster_create, cluster_complete, summary_create
    :param op_desc: 描述
    :param target_id: 关联目标 ID
    :param target_title: 关联目标标题
    """
    with get_connection() as conn:
        execute(conn,
            'INSERT INTO operation_history (user_id, op_type, op_desc, target_id, target_title) VALUES (?,?,?,?,?)',
            (user_id, op_type, op_desc, target_id, target_title))

def list_by_user(user_id, op_type=None, keyword=None, page=1, page_size=10):
    """
    分页查询用户操作历史，支持按类型、关键字筛选。
    :return: (list[dict], total)
    """
    with get_connection() as conn:
        where = 'user_id = ?'
        params = [user_id]
        if op_type:
            where += ' AND op_type = ?'
            params.append(op_type)
        if keyword:
            where += ' AND (op_desc LIKE ? OR target_title LIKE ?)'
            params.extend(['%' + keyword + '%', '%' + keyword + '%'])
        total = fetch_one(conn, 'SELECT COUNT(*) AS c FROM operation_history WHERE ' + where, params)['c']
        offset = (page - 1) * page_size
        params.extend([page_size, offset])
        rows = fetch_all(conn,
            'SELECT * FROM operation_history WHERE ' + where + ' ORDER BY created_at DESC LIMIT ? OFFSET ?', params)
        return rows, total

def activity_by_days(user_id, days=7):
    """
    近 N 天每日操作次数，用于图表。
    :return: list[dict] 每项 { date: 'YYYY-MM-DD', count: int }
    """
    with get_connection() as conn:
        # SQLite 用 date(created_at) 分组
        rows = fetch_all(conn, '''
            SELECT date(created_at) AS d, COUNT(*) AS c
            FROM operation_history
            WHERE user_id = ? AND date(created_at) >= date('now','localtime','-''' + str(days) + ''' days')
            GROUP BY date(created_at)
            ORDER BY d
        ''', (user_id,))
        return [{'date': (str(r['d']) if r.get('d') else '')[:10], 'count': int(r['c']) if r.get('c') is not None else 0} for r in rows]
