# -*- coding: utf-8 -*-
"""
应用入口：创建 Flask 应用、加载配置、初始化数据库、注册蓝图、CORS、全局异常处理。

仅使用 Flask 与 Python 标准库，无第三方扩展。
接口统一前缀 /api，响应格式 { code, message, data }；认证方式 Bearer Token。

接口一览：
- POST /api/auth/register  注册
- POST /api/auth/login     登录
- POST /api/auth/logout    登出
- GET  /api/user/profile   当前用户资料
- PUT  /api/user/profile   更新资料
- POST /api/user/password  修改密码
- GET  /api/user/stats     使用统计
- GET  /api/user/dashboard 仪表盘
- GET  /api/user/history   操作历史分页
- GET  /api/texts          文本列表
- GET  /api/texts/:id      文本详情
- POST /api/texts          创建文本
- PUT  /api/texts/:id      更新文本
- DELETE /api/texts/:id    删除文本
- POST /api/texts/batch-delete 批量删除
- GET  /api/cluster        聚类任务列表
- GET  /api/cluster/:id    任务详情
- POST /api/cluster        创建任务
- POST /api/cluster/:id/run 执行聚类
- DELETE /api/cluster/:id  删除任务
- GET  /api/cluster/stats  任务统计
- GET  /api/summary        摘要列表
- GET  /api/summary/:id    摘要详情
- POST /api/summary/generate 生成摘要
- DELETE /api/summary/:id  删除摘要
"""
import os
import sys

# 将项目根目录加入 path，便于 import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request
from config.settings import (
    DEBUG, SECRET_KEY, DATABASE_PATH, TOKEN_EXPIRE_SECONDS,
    DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE,
)
import database
from utils.auth import hash_password, verify_password

def create_app():
    """创建并配置 Flask 应用。"""
    app = Flask(__name__)
    app.config.update(
        DEBUG=DEBUG,
        SECRET_KEY=SECRET_KEY,
        DATABASE_PATH=DATABASE_PATH,
        TOKEN_EXPIRE_SECONDS=TOKEN_EXPIRE_SECONDS,
        DEFAULT_PAGE=DEFAULT_PAGE,
        DEFAULT_PAGE_SIZE=DEFAULT_PAGE_SIZE,
        MAX_PAGE_SIZE=MAX_PAGE_SIZE,
    )
    # 初始化数据库（SQLite 建表）
    config = {
        'DATABASE_PATH': app.config['DATABASE_PATH'],
    }
    database.init_database(config)
    # 种子用户：若用户表为空则插入管理员与测试账户（密码 123456）
    _seed_users_if_empty(app)
    # 确保默认账户密码一致（修复旧库或哈希逻辑变更导致的无法登录）
    _ensure_default_passwords()
    # 仅默认账户 admin 有展示数据；新建账户数据为空
    _seed_admin_data_if_empty()
    # 为 admin 补齐近 7 天操作记录，图表按日统计与之一致
    _ensure_last_7_days_activity()
    # 注册蓝图，统一加 /api 前缀
    from api.auth import bp as auth_bp
    from api.user import bp as user_bp
    from api.texts import bp as texts_bp
    from api.cluster import bp as cluster_bp
    from api.summary import bp as summary_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(texts_bp, url_prefix='/api/texts')
    app.register_blueprint(cluster_bp, url_prefix='/api/cluster')
    app.register_blueprint(summary_bp, url_prefix='/api/summary')
    # CORS：仅标准库，手动添加响应头；OPTIONS 预检直接返回
    @app.before_request
    def cors_preflight():
        if request.method == 'OPTIONS':
            return '', 204
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'code': 200, 'message': 'ok', 'data': {'status': 'up'}})
    # 全局异常捕获
    @app.errorhandler(Exception)
    def handle_error(e):
        app.logger.exception(e)
        return jsonify({'code': 500, 'message': '服务器内部错误', 'data': None}), 500
    return app

def _seed_users_if_empty(app):
    """若 users 表为空，则插入默认管理员与测试账户，密码均为 123456。"""
    with database.get_connection() as conn:
        r = database.fetch_one(conn, 'SELECT COUNT(*) AS c FROM users')
        if r and r['c'] > 0:
            return
        for username, nickname, email, role in [
            ('admin', '系统管理员', 'admin@example.com', 'admin'),
            ('test', '测试用户', 'test@example.com', 'user'),
            ('demo', '演示账户', 'demo@example.com', 'user'),
        ]:
            salt = 'salt_' + username + '_01'
            password_hash = hash_password('123456', salt)
            database.execute(conn,
                'INSERT INTO users (username, password_hash, salt, nickname, email, role) VALUES (?,?,?,?,?,?)',
                (username, password_hash, salt, nickname, email, role))

def _ensure_default_passwords():
    """确保 admin/test/demo 的密码均为 123456（修正旧库或哈希不一致）。"""
    default_accounts = ['admin', 'test', 'demo']
    with database.get_connection() as conn:
        for username in default_accounts:
            row = database.fetch_one(conn, 'SELECT id, salt, password_hash FROM users WHERE username = ?', (username,))
            if not row:
                continue
            salt = 'salt_' + username + '_01'
            password_hash = hash_password('123456', salt)
            if not verify_password('123456', salt, row['password_hash']):
                database.execute(conn, 'UPDATE users SET salt = ?, password_hash = ? WHERE username = ?',
                    (salt, password_hash, username))

def _ensure_last_7_days_activity():
    """为 admin 补齐近 7 天操作记录，使仪表盘「近7天活跃度」「文本上传趋势」每天都有数据。"""
    from datetime import datetime, timedelta
    with database.get_connection() as conn:
        admin = database.fetch_one(conn, "SELECT id FROM users WHERE username = 'admin'")
        if not admin:
            return
        admin_id = admin['id']
        base = datetime.now().date()
        # 为近 7 天每一天补足至少 2 条操作，使图表有可见高度
        for i in range(6, -1, -1):
            d = base - timedelta(days=i)
            date_str = d.strftime('%Y-%m-%d')
            cnt = database.fetch_one(conn, '''
                SELECT COUNT(*) AS c FROM operation_history
                WHERE user_id = ? AND date(created_at) = ?
            ''', (admin_id, date_str))
            n = cnt['c'] if cnt else 0
            to_add = max(0, 3 - n)
            for _ in range(to_add):
                created_at = date_str + ' 10:00:00'
                database.execute(conn, '''
                    INSERT INTO operation_history (user_id, op_type, op_desc, target_id, target_title, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (admin_id, 'text_upload', '上传文本', None, '历史数据', created_at))

def _seed_admin_data_if_empty():
    """仅当 admin（user_id=1）尚无任何文本时，为其初始化展示数据；其他账户保持为空。"""
    from datetime import datetime, timedelta
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with database.get_connection() as conn:
        admin = database.fetch_one(conn, "SELECT id FROM users WHERE username = 'admin'")
        if not admin:
            return
        admin_id = admin['id']
        cnt = database.fetch_one(conn, 'SELECT COUNT(*) AS c FROM texts WHERE user_id = ?', (admin_id,))
        if cnt and cnt['c'] > 0:
            return
        # 仅 admin 有数据：插入文本
        texts = [
            ('人工智能在教育领域的应用前景', '随着AI技术的快速发展，教育领域正在经历深刻的变革。个性化学习、智能评估、虚拟助教等应用场景逐步落地，为教育公平和质量提升带来新的可能性。', 68, '科技'),
            ('全球气候变化与可持续发展', '气候变化已成为全球最紧迫的环境挑战之一。各国政府和企业正在加速推动碳中和目标，可再生能源投资持续增长，绿色金融体系逐步完善。', 62, '环境'),
            ('数字经济时代的隐私保护挑战', '大数据和人工智能技术的广泛应用使个人隐私面临前所未有的威胁。如何在促进数据流通的同时保障用户隐私权，成为各国立法和技术研究的重点。', 65, '社会'),
            ('远程办公模式对企业管理的影响', '疫情后远程办公成为常态，企业管理模式随之转变。弹性工作制、分布式团队协作、数字化绩效管理等新实践正在重塑职场文化。', 58, '商业'),
            ('新能源汽车市场竞争格局分析', '全球新能源汽车市场持续高速增长，传统车企加速转型，新势力品牌不断涌现。电池技术突破、充电基础设施建设和智能驾驶成为竞争焦点。', 62, '商业'),
            ('社交媒体对青少年心理健康的影响', '研究表明过度使用社交媒体与青少年焦虑、抑郁等心理问题存在关联。平台责任、家长监督和数字素养教育成为社会关注焦点。', 56, '社会'),
            ('量子计算的商业化进程', '量子计算正从实验室走向商业应用。金融建模、药物研发、密码学和物流优化等领域有望率先受益，但技术成熟度和人才储备仍是瓶颈。', 60, '科技'),
            ('城市化进程中的社区治理创新', '城市化加速推进背景下，智慧社区建设、居民自治和数字治理成为基层治理现代化的重要抓手，社区服务的精细化和智能化水平不断提升。', 60, '社会'),
        ]
        for title, content, wc, cat in texts:
            database.execute(conn,
                'INSERT INTO texts (user_id, title, content, word_count, category, status) VALUES (?,?,?,?,?,?)',
                (admin_id, title, content, wc, cat, 'active'))
        # 聚类任务（已完成 2 个 + 运行中 1 个）
        database.execute(conn, '''INSERT INTO cluster_tasks (user_id, name, description, text_ids, cluster_count, algorithm, status, progress, completed_at)
            VALUES (?,?,?,?,?,?,?,?,?)''',
            (admin_id, '科技与社会话题聚类', '对科技和社会类文本进行观点聚类分析', '[1,3,6,7]', 3, 'kmeans', 'completed', 100, now))
        database.execute(conn, '''INSERT INTO cluster_tasks (user_id, name, description, text_ids, cluster_count, algorithm, status, progress, completed_at)
            VALUES (?,?,?,?,?,?,?,?,?)''',
            (admin_id, '商业领域文本分析', '针对商业类文本的聚类任务', '[4,5]', 2, 'kmeans', 'completed', 100, now))
        database.execute(conn, '''INSERT INTO cluster_tasks (user_id, name, description, text_ids, cluster_count, algorithm, status, progress, completed_at)
            VALUES (?,?,?,?,?,?,?,?,?)''',
            (admin_id, '环境与可持续发展', '环境主题文本聚类', '[2]', 2, 'kmeans', 'running', 68, None))
        # 聚类结果（任务 1 和 2）
        database.execute(conn, 'INSERT INTO cluster_results (task_id, cluster_index, text_id, score, sort_order) VALUES (1,0,1,0.92,0)', ())
        database.execute(conn, 'INSERT INTO cluster_results (task_id, cluster_index, text_id, score, sort_order) VALUES (1,0,7,0.85,1)', ())
        database.execute(conn, 'INSERT INTO cluster_results (task_id, cluster_index, text_id, score, sort_order) VALUES (1,1,3,0.90,0)', ())
        database.execute(conn, 'INSERT INTO cluster_results (task_id, cluster_index, text_id, score, sort_order) VALUES (1,1,8,0.85,1)', ())
        database.execute(conn, 'INSERT INTO cluster_results (task_id, cluster_index, text_id, score, sort_order) VALUES (1,2,6,0.91,0)', ())
        database.execute(conn, 'INSERT INTO cluster_results (task_id, cluster_index, text_id, score, sort_order) VALUES (2,0,4,0.89,0)', ())
        database.execute(conn, 'INSERT INTO cluster_results (task_id, cluster_index, text_id, score, sort_order) VALUES (2,1,5,0.87,0)', ())
        # 摘要
        database.execute(conn, '''INSERT INTO summaries (user_id, source_type, source_id, title, content, word_count)
            VALUES (?,?,?,?,?,?)''',
            (admin_id, 'cluster', 1, 'AI与技术发展观点摘要',
             '文本集中讨论了人工智能在教育领域的应用前景和量子计算的商业化进程。主要观点包括：AI技术正在推动教育变革，个性化学习和智能评估成为趋势。', 98))
        database.execute(conn, '''INSERT INTO summaries (user_id, source_type, source_id, title, content, word_count)
            VALUES (?,?,?,?,?,?)''',
            (admin_id, 'cluster', 1, '社会治理与隐私保护摘要',
             '这组文本围绕数字时代的社会治理展开讨论。数据隐私保护和基层社区智慧治理是两个核心议题。', 72))
        database.execute(conn, '''INSERT INTO summaries (user_id, source_type, source_id, title, content, word_count)
            VALUES (?,?,?,?,?,?)''',
            (admin_id, 'cluster', 2, '企业管理变革趋势',
             '远程办公模式已成为企业常态，正在深刻影响组织管理方式。弹性工作制和分布式协作带来效率提升。', 68))
        # 操作历史：分散到近 7 天，支撑仪表盘「近7天活跃度」「文本上传趋势」
        base = datetime.now().date()
        history_with_days = [
            (0, 'text_upload', '上传文本', 1, '人工智能在教育领域的应用前景'),
            (0, 'text_upload', '上传文本', 2, '全球气候变化与可持续发展'),
            (1, 'cluster_create', '创建聚类任务', 1, '科技与社会话题聚类'),
            (2, 'cluster_complete', '聚类完成', 1, '科技与社会话题聚类'),
            (2, 'summary_create', '生成摘要', 1, 'AI与技术发展观点摘要'),
            (3, 'cluster_create', '创建聚类任务', 2, '商业领域文本分析'),
            (4, 'cluster_complete', '聚类完成', 2, '商业领域文本分析'),
            (4, 'summary_create', '生成摘要', 2, '企业管理变革趋势'),
            (5, 'cluster_create', '创建聚类任务', 3, '环境与可持续发展'),
            (6, 'text_upload', '上传文本', 3, '数字经济时代的隐私保护挑战'),
            (6, 'text_upload', '上传文本', 4, '远程办公模式对企业管理的影响'),
        ]
        for days_ago, op_type, op_desc, target_id, target_title in history_with_days:
            d = base - timedelta(days=days_ago)
            created_at = d.strftime('%Y-%m-%d') + ' 10:00:00'
            database.execute(conn, '''
                INSERT INTO operation_history (user_id, op_type, op_desc, target_id, target_title, created_at)
                VALUES (?,?,?,?,?,?)
            ''', (admin_id, op_type, op_desc, target_id, target_title, created_at))

app = create_app()

# 分层说明（严格遵循步骤 1 目录结构）：
# - api/*：RESTful 接口层，负责请求解析、入参校验、调用 service、返回统一格式。
# - services/*：业务逻辑层，负责 CRUD 与业务流程，调用 database 与 utils 中的算法。
# - models/*：数据表名与字段说明，无 ORM，供 service 与 database 参考。
# - utils/*：认证（auth）、聚类/摘要算法、校验（validators）等工具。
# - database：SQLite 连接与建表，与 MySQL schema 一致；全局异常在 app 中统一捕获并返回 500。

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=DEBUG)
