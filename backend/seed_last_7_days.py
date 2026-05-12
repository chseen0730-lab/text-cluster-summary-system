# -*- coding: utf-8 -*-
"""为 admin 补齐近 7 天操作记录，并使每天数量有差异（趋势更明显）。与 app 使用同一数据库。"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import DATABASE_PATH
import database
from datetime import datetime, timedelta

# 近 7 天每天目标条数：[今天, 昨天, ..., 7天前]，使折线图有明显起伏
TARGETS_PER_DAY = [8, 6, 4, 5, 4, 3, 2]

def main():
    config = {'DATABASE_PATH': DATABASE_PATH}
    database.init_database(config)
    with database.get_connection() as conn:
        admin = database.fetch_one(conn, "SELECT id FROM users WHERE username = 'admin'")
        if not admin:
            print('No admin user found.')
            return
        admin_id = admin['id']
        base = datetime.now().date()
        inserted_total = 0
        for i in range(6, -1, -1):
            d = base - timedelta(days=i)
            date_str = d.strftime('%Y-%m-%d')
            cnt = database.fetch_one(conn, '''
                SELECT COUNT(*) AS c FROM operation_history
                WHERE user_id = ? AND date(created_at) = ?
            ''', (admin_id, date_str))
            n = cnt['c'] if cnt else 0
            target = TARGETS_PER_DAY[i] if i < len(TARGETS_PER_DAY) else 5
            to_add = max(0, target - n)
            for j in range(to_add):
                created_at = date_str + ' 10:%02d:00' % ((j + 1) % 60)
                database.execute(conn, '''
                    INSERT INTO operation_history (user_id, op_type, op_desc, target_id, target_title, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (admin_id, 'text_upload', '上传文本', None, '历史数据', created_at))
                inserted_total += 1
        print('OK: inserted', inserted_total, 'rows. DB:', DATABASE_PATH)
        rows = database.fetch_all(conn, '''
            SELECT date(created_at) AS d, COUNT(*) AS c FROM operation_history
            WHERE user_id = ? AND date(created_at) >= date('now','localtime','-6 days')
            GROUP BY date(created_at) ORDER BY d
        ''', (admin_id,))
        print('Last 7 days:', [(r['d'], r['c']) for r in rows])

if __name__ == '__main__':
    main()
