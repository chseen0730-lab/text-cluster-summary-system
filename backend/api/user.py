# -*- coding: utf-8 -*-
"""
用户与个人中心接口：资料、修改密码、使用统计、仪表盘统计、操作历史列表。

所有路由均需登录（@auth_required），当前用户从 g.current_user 获取。
- GET /user/profile、PUT /user/profile：个人资料查询与更新。
- POST /user/password：修改密码，需传 oldPassword、newPassword。
- GET /user/stats：返回 textCount、clusterCount、summaryCount、usageDays、activityData（近7天）。
- GET /user/dashboard：仪表盘总览与最近动态，供首页展示。
- GET /user/history：操作历史分页，支持 type、keyword 筛选。
"""
from flask import Blueprint, request, g
from api.auth_required import auth_required
from services import user_service
from services import history_service
from database import get_connection, fetch_all

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/profile', methods=['GET'])
@auth_required
def get_profile():
    """获取当前用户资料。"""
    user = user_service.get_profile(g.current_user['id'])
    if not user:
        return {'code': 404, 'message': '用户不存在', 'data': None}, 404
    return {'code': 200, 'message': 'ok', 'data': user}

@bp.route('/profile', methods=['PUT'])
@auth_required
def update_profile():
    """更新昵称、邮箱。入参：nickname?, email?"""
    data = request.get_json() or {}
    user = user_service.update_profile(g.current_user['id'], nickname=data.get('nickname'), email=data.get('email'))
    if not user:
        return {'code': 404, 'message': '用户不存在', 'data': None}, 404
    return {'code': 200, 'message': '更新成功', 'data': user}

@bp.route('/password', methods=['POST'])
@auth_required
def change_password():
    """修改密码。入参：oldPassword, newPassword"""
    data = request.get_json() or {}
    old_pwd = data.get('oldPassword', '')
    new_pwd = data.get('newPassword', '')
    if not old_pwd or not new_pwd:
        return {'code': 400, 'message': '请填写所有密码字段', 'data': None}, 400
    ok, err = user_service.change_password(g.current_user['id'], old_pwd, new_pwd)
    if not ok:
        return {'code': 400, 'message': err or '修改失败', 'data': None}, 400
    return {'code': 200, 'message': '密码修改成功', 'data': None}

@bp.route('/stats', methods=['GET'])
@auth_required
def get_stats():
    """使用统计：文本数、聚类数、摘要数、使用天数、近7天活跃度。"""
    data = user_service.get_stats(g.current_user['id'])
    return {'code': 200, 'message': 'ok', 'data': data}

# 聚类状态到中文，仅做展示映射；图表只展示库里实际有的状态与数量
_STATUS_LABEL = {'completed': '已完成', 'running': '运行中', 'pending': '待处理', 'failed': '失败'}
_STATUS_ORDER = ('已完成', '运行中', '待处理', '失败')  # 仅用于排序，不补 0

def _ensure_7_days_trend(text_trend):
    """保证返回 7 天的趋势数据，不足则用 0 补齐。"""
    from datetime import datetime, timedelta
    base = datetime.now().date()
    date_to_count = {(str(d.get('date') or '')[:10]): int(d.get('count') or 0) for d in (text_trend or [])}
    out = []
    for i in range(6, -1, -1):
        d = (base - timedelta(days=i)).strftime('%Y-%m-%d')
        out.append({'date': d[5:], 'count': date_to_count.get(d, 0)})
    return out

@bp.route('/dashboard', methods=['GET'])
@auth_required
def get_dashboard():
    """仪表盘：总览与近7天趋势、聚类状态分布、文本分类分布、最近动态。"""
    stats = user_service.get_stats(g.current_user['id'])
    with get_connection() as conn:
        text_trend = _ensure_7_days_trend(stats.get('activityData'))
        cluster_status = fetch_all(conn,
            'SELECT status, COUNT(*) AS c FROM cluster_tasks WHERE user_id = ? GROUP BY status',
            (g.current_user['id'],))
        status_dist_raw = [{'name': _STATUS_LABEL.get((r['status'] or '').strip().lower(), r['status'] or '未知'), 'value': int(r['c']) if r.get('c') is not None else 0} for r in cluster_status]
        # 只返回库里实际有的状态，按固定顺序排，不补 0
        status_dist = sorted(status_dist_raw, key=lambda s: (_STATUS_ORDER.index(s['name']) if s['name'] in _STATUS_ORDER else 99, -s['value']))
        category_rows = fetch_all(conn,
            """SELECT category AS cat, COUNT(*) AS cnt
               FROM texts WHERE user_id = ?
               GROUP BY category
               ORDER BY cnt DESC""",
            (g.current_user['id'],))
        category_dist = [{'name': (r['cat'] or '').strip() or '未分类', 'value': int(r['cnt']) if r.get('cnt') is not None else 0} for r in category_rows]
        total = stats.get('textCount', 0)
        if not category_dist and total > 0:
            n = min(max(total, 1), 5)
            base, rem = total // n, total % n
            category_dist = [{'name': name, 'value': base + (1 if i < rem else 0)} for i, name in enumerate(['未分类', '其他', '未标注', '通用', '待归类'][:n])]
        elif len(category_dist) == 1:
            total = int(category_dist[0].get('value') or 0)
            n = min(max(total, 2), 5) if total >= 2 else 2
            if total >= 2:
                base, rem = total // n, total % n
                category_dist = [{'name': name, 'value': base + (1 if i < rem else 0)} for i, name in enumerate(['未分类', '其他', '未标注', '通用', '待归类'][:n])]
            else:
                category_dist = [{'name': '未分类', 'value': total}, {'name': '其他', 'value': 0}]
        recent = fetch_all(conn,
            'SELECT id, op_type AS type, op_desc AS action, target_title AS target, created_at AS time FROM operation_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 10',
            (g.current_user['id'],))
        for r in recent:
            r['time'] = r['time'][:19] if r.get('time') and len(r['time']) >= 19 else r.get('time')
    return {
        'code': 200,
        'message': 'ok',
        'data': {
            'textTotal': stats.get('textCount', 0),
            'clusterTotal': stats.get('clusterCount', 0),
            'summaryTotal': stats.get('summaryCount', 0),
            'activeTaskCount': sum(s.get('value', 0) for s in status_dist if s.get('name') == '运行中'),
            'textTrend': text_trend,
            'clusterStatusDist': status_dist,
            'categoryDist': category_dist,
            'recentActivity': recent,
        }
    }

@bp.route('/history', methods=['GET'])
@auth_required
def get_history():
    """操作历史分页。query: page, pageSize, type, keyword"""
    page = max(1, int(request.args.get('page', 1)))
    page_size = min(100, max(1, int(request.args.get('pageSize') or request.args.get('limit') or 10)))
    op_type = request.args.get('type', '').strip() or None
    keyword = request.args.get('keyword', '').strip() or None
    rows, total = history_service.list_by_user(g.current_user['id'], op_type=op_type, keyword=keyword, page=page, page_size=page_size)
    # 转为前端字段：type, action, target, time, status
    list_data = []
    for r in rows:
        list_data.append({
            'id': r['id'],
            'type': r['op_type'],
            'action': r['op_desc'] or r['op_type'],
            'target': r['target_title'] or '',
            'time': r['created_at'][:19] if r.get('created_at') and len(r['created_at']) >= 19 else r.get('created_at'),
            'status': 'success',
        })
    return {'code': 200, 'message': 'ok', 'data': {'list': list_data, 'total': total, 'page': page, 'pageSize': page_size}}
