# -*- coding: utf-8 -*-
"""
聚类任务业务逻辑：创建任务、列表与详情、执行聚类（调用算法）、结果写入 cluster_results。

业务流程：
1. 创建任务：校验任务名与文本 ID 归属，将 text_ids 以 JSON 字符串存入 cluster_tasks。
2. 执行任务：从 pending 变为 running，拉取文本内容调用 utils.cluster_algorithm 得到簇划分，
   写入 cluster_results（task_id, cluster_index, text_id, score），最后将任务置为 completed。
3. 列表/详情：按 user_id 过滤，详情可附带 results（按簇分组的 textIds）。
"""
import json
from database import get_connection, fetch_one, fetch_all, execute, last_rowid
from services import text_service
from services import history_service
from utils import cluster_algorithm

def create(user_id, name, text_ids, cluster_count=3, algorithm='kmeans', description=None):
    """
    创建聚类任务，状态为 pending。
    :param user_id: 用户 ID
    :param name: 任务名
    :param text_ids: 文本 ID 列表
    :param cluster_count: 簇数
    :param algorithm: 算法名
    :param description: 可选描述
    :return: dict 新任务或 (None, str 错误)
    """
    if not name or not name.strip():
        return None, '任务名称不能为空'
    if not text_ids or len(text_ids) < 1:
        return None, '请至少选择一篇文本'
    texts = text_service.get_by_ids(text_ids, user_id)
    if len(texts) != len(text_ids):
        return None, '部分文本不存在或无权访问'
    text_ids_str = json.dumps([int(x) for x in text_ids])
    with get_connection() as conn:
        execute(conn, '''
            INSERT INTO cluster_tasks (user_id, name, description, text_ids, cluster_count, algorithm, status, progress)
            VALUES (?,?,?,?,?,?,?,?)
        ''', (user_id, name.strip(), (description or '').strip(), text_ids_str, int(cluster_count), (algorithm or 'kmeans').lower(), 'pending', 0))
        task_id = last_rowid(conn)
        task = fetch_one(conn, 'SELECT * FROM cluster_tasks WHERE id = ?', (task_id,))
    history_service.add(user_id, 'cluster_create', '创建聚类任务', task_id, name.strip())
    return dict(task), None

def get_by_id(task_id, user_id=None):
    """
    查询任务详情；若传 user_id 则校验归属。
    """
    with get_connection() as conn:
        if user_id is not None:
            return fetch_one(conn, 'SELECT * FROM cluster_tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
        return fetch_one(conn, 'SELECT * FROM cluster_tasks WHERE id = ?', (task_id,))

def list_by_user(user_id, status=None, keyword=None, page=1, page_size=10):
    """
    分页列表，支持按状态、关键字筛选。
    :return: (list[dict], total)
    """
    with get_connection() as conn:
        where = 'user_id = ?'
        params = [user_id]
        if status:
            where += ' AND status = ?'
            params.append(status)
        if keyword:
            where += ' AND name LIKE ?'
            params.append('%' + keyword + '%')
        total = fetch_one(conn, 'SELECT COUNT(*) AS c FROM cluster_tasks WHERE ' + where, params)['c']
        offset = (page - 1) * page_size
        params.extend([page_size, offset])
        rows = fetch_all(conn, 'SELECT * FROM cluster_tasks WHERE ' + where + ' ORDER BY created_at DESC LIMIT ? OFFSET ?', params)
        return rows, total

def run_task(task_id, user_id):
    """
    执行聚类：更新状态为 running，调用算法，写入 cluster_results，更新状态为 completed。
    :return: (dict 任务含 results, None) 或 (None, str 错误)
    """
    task = get_by_id(task_id, user_id)
    if not task:
        return None, '任务不存在或无权访问'
    if task['status'] not in ('pending', 'failed'):
        return None, '任务已执行或执行中'
    text_ids = json.loads(task['text_ids'] or '[]')
    texts = text_service.get_by_ids(text_ids, user_id)
    if not texts:
        return None, '无有效文本'
    with get_connection() as conn:
        execute(conn, "UPDATE cluster_tasks SET status = 'running', progress = 50 WHERE id = ?", (task_id,))
    # 调用算法
    algo_result = cluster_algorithm.simple_cluster(texts, task['cluster_count'], task.get('algorithm') or 'kmeans')
    with get_connection() as conn:
        execute(conn, 'DELETE FROM cluster_results WHERE task_id = ?', (task_id,))
        for i, r in enumerate(algo_result):
            execute(conn,
                'INSERT INTO cluster_results (task_id, cluster_index, text_id, score, sort_order) VALUES (?,?,?,?,?)',
                (task_id, r['cluster_index'], r['text_id'], r.get('score'), i))
        execute(conn,
            "UPDATE cluster_tasks SET status = 'completed', progress = 100, completed_at = datetime('now','localtime') WHERE id = ?",
            (task_id,))
        task = fetch_one(conn, 'SELECT * FROM cluster_tasks WHERE id = ?', (task_id,))
    history_service.add(user_id, 'cluster_complete', '聚类完成', task_id, task['name'])
    # 组装前端需要的 results 结构
    results = get_results_by_task(task_id)
    out = dict(task)
    out['results'] = results
    return out, None

def get_results_by_task(task_id):
    """
    按任务 ID 查询聚类结果，按簇分组，含文本 ID 列表与关键词等。
    返回 list[dict]，每项含 id（簇序号）、textIds、keywords（当前实现可为空，可扩展）。
    """
    with get_connection() as conn:
        rows = fetch_all(conn, 'SELECT * FROM cluster_results WHERE task_id = ? ORDER BY cluster_index, sort_order', (task_id,))
    clusters = {}
    for r in rows:
        idx = r['cluster_index']
        if idx not in clusters:
            clusters[idx] = {'id': idx, 'textIds': [], 'keywords': []}
        clusters[idx]['textIds'].append(r['text_id'])
    return list(clusters.values())

def get_task_with_results(task_id, user_id):
    """
    获取任务详情并附带聚类结果（按簇的文本列表）。
    先校验归属，再拼接 results 字段供前端按簇展示。
    """
    task = get_by_id(task_id, user_id)
    if not task:
        return None
    task = dict(task)
    task['results'] = get_results_by_task(task_id)
    return task

def delete(task_id, user_id):
    """删除任务（级联删除结果）。"""
    with get_connection() as conn:
        cur = execute(conn, 'DELETE FROM cluster_tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
        return cur.rowcount > 0
