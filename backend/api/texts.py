# -*- coding: utf-8 -*-
"""
文本管理接口：CRUD、分页列表、批量删除。

所有路由需登录。列表支持 query：page、pageSize、keyword、category。
创建时必填 content，title 可选；更新可部分字段；删除与批量删除均校验归属。
"""
from flask import Blueprint, request, g
from api.auth_required import auth_required
from services import text_service
from services import history_service

bp = Blueprint('texts', __name__, url_prefix='/texts')

def _row_to_text(row):
    """
    将数据库行转为前端格式：created_at/updated_at 转为 createdAt/updatedAt，
    并截取为 19 位日期时间字符串。
    """
    if not row:
        return None
    r = dict(row)
    r['createdAt'] = r.get('created_at', '')[:19] if r.get('created_at') else ''
    r['updatedAt'] = r.get('updated_at', '')[:19] if r.get('updated_at') else ''
    return r

@bp.route('', methods=['GET'])
@auth_required
def list_texts():
    """分页列表。query: page, pageSize, keyword, category"""
    page = max(1, int(request.args.get('page', 1)))
    page_size = min(100, max(1, int(request.args.get('pageSize') or request.args.get('limit') or 10)))
    keyword = request.args.get('keyword', '').strip() or None
    category = request.args.get('category', '').strip() or None
    rows, total = text_service.list_by_user(g.current_user['id'], keyword=keyword, category=category, page=page, page_size=page_size)
    list_data = [_row_to_text(r) for r in rows]
    return {'code': 200, 'message': 'ok', 'data': {'list': list_data, 'total': total, 'page': page, 'pageSize': page_size}}

@bp.route('/<int:text_id>', methods=['GET'])
@auth_required
def get_text(text_id):
    """单条详情。"""
    row = text_service.get_by_id(text_id, g.current_user['id'])
    if not row:
        return {'code': 404, 'message': '文本不存在', 'data': None}, 404
    return {'code': 200, 'message': 'ok', 'data': _row_to_text(row)}

@bp.route('', methods=['POST'])
@auth_required
def create_text():
    """创建文本。入参：title, content, category?"""
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    if not content:
        return {'code': 400, 'message': '正文不能为空', 'data': None}, 400
    row = text_service.create(g.current_user['id'], title=title or '未命名', content=content, category=data.get('category'))
    history_service.add(g.current_user['id'], 'text_upload', '上传文本', row['id'], row.get('title'))
    return {'code': 200, 'message': '创建成功', 'data': _row_to_text(row)}

@bp.route('/<int:text_id>', methods=['PUT'])
@auth_required
def update_text(text_id):
    """更新文本。入参：title?, content?, category?"""
    data = request.get_json() or {}
    row = text_service.update(text_id, g.current_user['id'], title=data.get('title'), content=data.get('content'), category=data.get('category'))
    if not row:
        return {'code': 404, 'message': '文本不存在或无权修改', 'data': None}, 404
    return {'code': 200, 'message': '更新成功', 'data': _row_to_text(row)}

@bp.route('/<int:text_id>', methods=['DELETE'])
@auth_required
def delete_text(text_id):
    """删除单条。"""
    ok = text_service.delete(text_id, g.current_user['id'])
    if not ok:
        return {'code': 404, 'message': '文本不存在或无权删除', 'data': None}, 404
    return {'code': 200, 'message': '删除成功', 'data': None}

@bp.route('/batch-delete', methods=['POST'])
@auth_required
def batch_delete():
    """批量删除。入参：ids: number[]"""
    data = request.get_json() or {}
    ids = data.get('ids', [])
    if not ids:
        return {'code': 400, 'message': '请选择要删除的文本', 'data': None}, 400
    n = text_service.batch_delete(ids, g.current_user['id'])
    return {'code': 200, 'message': '批量删除成功', 'data': {'deleted': n}}
