# -*- coding: utf-8 -*-
"""
摘要业务逻辑：按来源（单文本或聚类任务）生成摘要、列表、删除。

- source_type 为 text 时，source_id 为文本 ID，调用抽取式摘要对单篇正文生成简短摘要。
- source_type 为 cluster 时，source_id 为聚类任务 ID，汇总该任务下所有文本内容后生成摘要。
- 摘要内容与字数入库，供前端列表与详情展示；删除时校验归属。
"""
from database import get_connection, fetch_one, fetch_all, execute, last_rowid
from services import text_service
from services import cluster_service
from services import history_service
from utils import summary_algorithm
import json

def generate(user_id, source_type, source_id, title=None):
    """
    根据来源生成摘要并入库。
    :param source_type: 'text' 或 'cluster'
    :param source_id: 文本 ID 或聚类任务 ID
    :param title: 可选标题
    :return: (dict 摘要, None) 或 (None, str 错误)
    """
    if source_type not in ('text', 'cluster'):
        return None, '来源类型无效'
    content = ''
    if source_type == 'text':
        text = text_service.get_by_id(source_id, user_id)
        if not text:
            return None, '文本不存在或无权访问'
        content = summary_algorithm.summarize_single(text.get('content') or text.get('title', ''), 300)
        title = title or (text.get('title', '')[:50] + '-摘要')
    else:
        task = cluster_service.get_by_id(source_id, user_id)
        if not task:
            return None, '聚类任务不存在或无权访问'
        text_ids = json.loads(task.get('text_ids') or '[]')
        texts = text_service.get_by_ids(text_ids, user_id)
        contents = [t.get('content') or t.get('title', '') for t in texts]
        content = summary_algorithm.extractive_summary(contents, 500)
        title = title or (task.get('name', '')[:50] + '-摘要')
    word_count = len(content)
    with get_connection() as conn:
        execute(conn,
            'INSERT INTO summaries (user_id, source_type, source_id, title, content, word_count) VALUES (?,?,?,?,?,?)',
            (user_id, source_type, source_id, (title or '摘要').strip(), content, word_count))
        sid = last_rowid(conn)
        row = fetch_one(conn, 'SELECT * FROM summaries WHERE id = ?', (sid,))
    history_service.add(user_id, 'summary_create', '生成摘要', sid, title)
    return dict(row), None

def get_by_id(summary_id, user_id=None):
    """查询摘要；可校验归属。"""
    with get_connection() as conn:
        if user_id is not None:
            return fetch_one(conn, 'SELECT * FROM summaries WHERE id = ? AND user_id = ?', (summary_id, user_id))
        return fetch_one(conn, 'SELECT * FROM summaries WHERE id = ?', (summary_id,))

def list_by_user(user_id, keyword=None, source_type=None, source_id=None, page=1, page_size=10):
    """分页列表。"""
    with get_connection() as conn:
        where = 'user_id = ?'
        params = [user_id]
        if keyword:
            where += ' AND (title LIKE ? OR content LIKE ?)'
            params.extend(['%' + keyword + '%', '%' + keyword + '%'])
        if source_type:
            where += ' AND source_type = ?'
            params.append(source_type)
        if source_id is not None:
            where += ' AND source_id = ?'
            params.append(source_id)
        total = fetch_one(conn, 'SELECT COUNT(*) AS c FROM summaries WHERE ' + where, params)['c']
        offset = (page - 1) * page_size
        params.extend([page_size, offset])
        rows = fetch_all(conn, 'SELECT * FROM summaries WHERE ' + where + ' ORDER BY created_at DESC LIMIT ? OFFSET ?', params)
        return rows, total

def delete(summary_id, user_id):
    """删除摘要。"""
    with get_connection() as conn:
        cur = execute(conn, 'DELETE FROM summaries WHERE id = ? AND user_id = ?', (summary_id, user_id))
        return cur.rowcount > 0
