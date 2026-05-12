# -*- coding: utf-8 -*-
"""
摘要接口：生成、列表、详情、删除。

生成摘要：POST /summary/generate，入参 sourceType（text/cluster）、sourceId、可选 title。
列表支持 keyword、clusterId（即按来源聚类任务筛选）及分页。删除时校验归属。
"""
from flask import Blueprint, request, g
from api.auth_required import auth_required
from services import summary_service

bp = Blueprint('summary', __name__, url_prefix='/summary')

def _row_to_summary(row):
    """
    转为前端格式：createdAt、clusterId（当 source_type 为 cluster 时取 source_id）、clusterLabel 等。
    """
    if not row:
        return None
    r = dict(row)
    r['createdAt'] = r.get('created_at', '')[:19] if r.get('created_at') else ''
    r['clusterId'] = r.get('source_id') if r.get('source_type') == 'cluster' else None
    r['clusterLabel'] = ''
    return r

@bp.route('', methods=['GET'])
@auth_required
def list_summaries():
    """分页列表。query: page, pageSize, keyword, clusterId"""
    page = max(1, int(request.args.get('page', 1)))
    page_size = min(100, max(1, int(request.args.get('pageSize') or request.args.get('limit') or 10)))
    keyword = request.args.get('keyword', '').strip() or None
    source_type = None
    source_id = None
    cid = request.args.get('clusterId')
    if cid is not None and cid != '':
        try:
            source_id = int(cid)
            source_type = 'cluster'
        except (TypeError, ValueError):
            pass
    rows, total = summary_service.list_by_user(g.current_user['id'], keyword=keyword, source_type=source_type, source_id=source_id, page=page, page_size=page_size)
    list_data = [_row_to_summary(r) for r in rows]
    return {'code': 200, 'message': 'ok', 'data': {'list': list_data, 'total': total, 'page': page, 'pageSize': page_size}}

@bp.route('/<int:summary_id>', methods=['GET'])
@auth_required
def get_summary(summary_id):
    """单条详情。"""
    row = summary_service.get_by_id(summary_id, g.current_user['id'])
    if not row:
        return {'code': 404, 'message': '摘要不存在', 'data': None}, 404
    return {'code': 200, 'message': 'ok', 'data': _row_to_summary(row)}

@bp.route('/generate', methods=['POST'])
@auth_required
def generate():
    """生成摘要。入参：sourceType, sourceId, title?"""
    data = request.get_json() or {}
    source_type = (data.get('sourceType') or data.get('source_type') or '').strip().lower()
    source_id = data.get('sourceId') or data.get('source_id')
    if not source_type or source_id is None:
        return {'code': 400, 'message': '请选择来源类型与来源ID', 'data': None}, 400
    try:
        source_id = int(source_id)
    except (TypeError, ValueError):
        return {'code': 400, 'message': '来源ID无效', 'data': None}, 400
    row, err = summary_service.generate(g.current_user['id'], source_type=source_type, source_id=source_id, title=data.get('title'))
    if err:
        return {'code': 400, 'message': err, 'data': None}, 400
    return {'code': 200, 'message': '摘要生成成功', 'data': _row_to_summary(dict(row))}

@bp.route('/<int:summary_id>', methods=['DELETE'])
@auth_required
def delete_summary(summary_id):
    """删除摘要。"""
    ok = summary_service.delete(summary_id, g.current_user['id'])
    if not ok:
        return {'code': 404, 'message': '摘要不存在或无权删除', 'data': None}, 404
    return {'code': 200, 'message': '删除成功', 'data': None}
