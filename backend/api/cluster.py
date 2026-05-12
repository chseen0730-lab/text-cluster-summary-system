# -*- coding: utf-8 -*-
"""
聚类任务接口：创建、列表、详情、执行、删除、统计。

创建时必填 name、textIds（数组）；可选 clusterCount、algorithm、description。
执行聚类：POST /cluster/:id/run，将任务从 pending 变为 running 再变为 completed，并写入 cluster_results。
列表与详情均按当前用户过滤；详情含 results（按簇分组的 textIds）。
"""
from flask import Blueprint, request, g
from api.auth_required import auth_required
from services import cluster_service

bp = Blueprint('cluster', __name__, url_prefix='/cluster')

def _task_to_response(task):
    """
    将任务行转为前端格式，含 results、createdAt、completedAt、textIds 等。
    text_ids 为 JSON 字符串时解析为 textIds 数组。
    """
    if not task:
        return None
    t = dict(task)
    t['createdAt'] = t.get('created_at', '')[:19] if t.get('created_at') else ''
    t['completedAt'] = t.get('completed_at', '')[:19] if t.get('completed_at') else None
    if 'text_ids' in t and isinstance(t['text_ids'], str):
        import json
        try:
            t['textIds'] = json.loads(t['text_ids'])
        except Exception:
            t['textIds'] = []
    else:
        t['textIds'] = t.get('textIds', [])
    return t

@bp.route('', methods=['GET'])
@auth_required
def list_tasks():
    """分页列表。query: page, pageSize, status, keyword"""
    page = max(1, int(request.args.get('page', 1)))
    page_size = min(100, max(1, int(request.args.get('pageSize') or request.args.get('limit') or 10)))
    status = request.args.get('status', '').strip() or None
    keyword = request.args.get('keyword', '').strip() or None
    rows, total = cluster_service.list_by_user(g.current_user['id'], status=status, keyword=keyword, page=page, page_size=page_size)
    list_data = []
    for r in rows:
        t = _task_to_response(dict(r))
        t['results'] = cluster_service.get_results_by_task(r['id']) if r.get('status') == 'completed' else None
        list_data.append(t)
    return {'code': 200, 'message': 'ok', 'data': {'list': list_data, 'total': total, 'page': page, 'pageSize': page_size}}

@bp.route('/<int:task_id>', methods=['GET'])
@auth_required
def get_task(task_id):
    """任务详情（含聚类结果）。"""
    task = cluster_service.get_task_with_results(task_id, g.current_user['id'])
    if not task:
        return {'code': 404, 'message': '任务不存在', 'data': None}, 404
    return {'code': 200, 'message': 'ok', 'data': _task_to_response(task)}

@bp.route('', methods=['POST'])
@auth_required
def create_task():
    """创建聚类任务。入参：name, textIds, clusterCount?, algorithm?, description?"""
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    text_ids = data.get('textIds', data.get('text_ids', []))
    task, err = cluster_service.create(
        g.current_user['id'],
        name=name,
        text_ids=text_ids,
        cluster_count=int(data.get('clusterCount', data.get('cluster_count', 3))),
        algorithm=data.get('algorithm', 'kmeans'),
        description=data.get('description'),
    )
    if err:
        return {'code': 400, 'message': err, 'data': None}, 400
    return {'code': 200, 'message': '任务已创建', 'data': _task_to_response(dict(task))}

@bp.route('/<int:task_id>/run', methods=['POST'])
@auth_required
def run_task(task_id):
    """执行聚类。"""
    task, err = cluster_service.run_task(task_id, g.current_user['id'])
    if err:
        return {'code': 400, 'message': err, 'data': None}, 400
    return {'code': 200, 'message': '聚类完成', 'data': _task_to_response(task)}

@bp.route('/<int:task_id>', methods=['DELETE'])
@auth_required
def delete_task(task_id):
    """删除任务。"""
    ok = cluster_service.delete(task_id, g.current_user['id'])
    if not ok:
        return {'code': 404, 'message': '任务不存在或无权删除', 'data': None}, 404
    return {'code': 200, 'message': '删除成功', 'data': None}

@bp.route('/stats', methods=['GET'])
@auth_required
def get_stats():
    """聚类任务统计：总数、已完成、运行中、待处理。"""
    from database import get_connection, fetch_all
    with get_connection() as conn:
        rows = fetch_all(conn, 'SELECT status, COUNT(*) AS c FROM cluster_tasks WHERE user_id = ? GROUP BY status', (g.current_user['id'],))
    total = sum(r['c'] for r in rows)
    by_status = {r['status']: r['c'] for r in rows}
    return {
        'code': 200,
        'message': 'ok',
        'data': {
            'total': total,
            'completed': by_status.get('completed', 0),
            'running': by_status.get('running', 0),
            'pending': by_status.get('pending', 0),
        }
    }
