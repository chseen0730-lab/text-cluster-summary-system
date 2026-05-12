# -*- coding: utf-8 -*-
"""
用户业务逻辑：个人资料查询与更新、修改密码、使用统计（文本数、聚类数、摘要数、近7天活跃度）。
"""
from database import get_connection, fetch_one, fetch_all, execute
from utils.auth import hash_password
from services import history_service

def get_profile(user_id):
    """
    获取用户资料（不含密码）。
    :return: dict 或 None
    """
    with get_connection() as conn:
        row = fetch_one(conn, 'SELECT id, username, nickname, email, role, created_at FROM users WHERE id = ?', (user_id,))
        if not row:
            return None
        return _row_to_user(row)

def update_profile(user_id, nickname=None, email=None):
    """
    更新昵称、邮箱。
    :return: dict 更新后用户信息或 None
    """
    with get_connection() as conn:
        row = fetch_one(conn, 'SELECT id, username, nickname, email, role, created_at FROM users WHERE id = ?', (user_id,))
        if not row:
            return None
        updates = []
        params = []
        if nickname is not None:
            updates.append('nickname = ?')
            params.append(nickname.strip())
        if email is not None:
            updates.append('email = ?')
            params.append(email.strip())
        if updates:
            params.append(user_id)
            execute(conn, 'UPDATE users SET ' + ', '.join(updates) + ', updated_at = datetime("now","localtime") WHERE id = ?', params)
            row = fetch_one(conn, 'SELECT id, username, nickname, email, role, created_at FROM users WHERE id = ?', (user_id,))
        return _row_to_user(dict(row))

def change_password(user_id, old_password, new_password):
    """
    修改密码：校验旧密码后更新哈希。
    :return: (True, None) 或 (False, str 错误信息)
    """
    with get_connection() as conn:
        row = fetch_one(conn, 'SELECT salt, password_hash FROM users WHERE id = ?', (user_id,))
        if not row:
            return False, '用户不存在'
        if not __verify(old_password, row['salt'], row['password_hash']):
            return False, '当前密码错误'
        salt = row['salt']
    new_hash = hash_password(new_password, salt)
    with get_connection() as conn:
        execute(conn, 'UPDATE users SET password_hash = ?, updated_at = datetime("now","localtime") WHERE id = ?', (new_hash, user_id))
    return True, None

def __verify(password, salt, stored_hash):
    from utils.auth import verify_password
    return verify_password(password, salt, stored_hash)

def get_stats(user_id):
    """
    获取用户使用统计：文本数、聚类任务数、摘要数、使用天数、近7天活跃度。
    :return: dict
    """
    with get_connection() as conn:
        text_count = fetch_one(conn, 'SELECT COUNT(*) AS c FROM texts WHERE user_id = ?', (user_id,))['c']
        cluster_count = fetch_one(conn, 'SELECT COUNT(*) AS c FROM cluster_tasks WHERE user_id = ?', (user_id,))['c']
        summary_count = fetch_one(conn, 'SELECT COUNT(*) AS c FROM summaries WHERE user_id = ?', (user_id,))['c']
        first_op = fetch_one(conn, 'SELECT MIN(created_at) AS d FROM operation_history WHERE user_id = ?', (user_id,))
        first_date = first_op['d'][:10] if first_op and first_op['d'] else None
    # 使用天数：从首次操作到今天
    usage_days = 0
    if first_date:
        from datetime import datetime
        try:
            d0 = datetime.strptime(first_date[:10], '%Y-%m-%d')
            usage_days = max(0, (datetime.now() - d0).days) + 1
        except Exception:
            usage_days = 1
    activity_data = history_service.activity_by_days(user_id, 7)
    # 补齐 7 天日期，无记录为 0；日期统一为 YYYY-MM-DD 再比较
    from datetime import datetime, timedelta
    base = datetime.now().date()
    filled = []
    for i in range(6, -1, -1):
        d = (base - timedelta(days=i)).strftime('%Y-%m-%d')
        c = next((a['count'] for a in activity_data if (str(a.get('date') or '')[:10] == d)), 0)
        filled.append({'date': d, 'count': int(c) if c is not None else 0})
    return {
        'textCount': text_count,
        'clusterCount': cluster_count,
        'summaryCount': summary_count,
        'usageDays': usage_days,
        'activityData': filled,
    }

def _row_to_user(row):
    """将 users 表行转为前端格式。"""
    created = row.get('created_at')
    if created:
        created = created[:10] if len(created) >= 10 else created
    return {
        'id': row['id'],
        'username': row['username'],
        'nickname': row.get('nickname') or row['username'],
        'email': row.get('email') or '',
        'role': row.get('role') or 'user',
        'createdAt': created,
    }
