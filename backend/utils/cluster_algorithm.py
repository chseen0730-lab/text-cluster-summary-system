# -*- coding: utf-8 -*-
"""
聚类算法封装：仅使用 Python 标准库实现简单聚类逻辑。

无第三方库（如 sklearn），采用基于长度与首字符特征的简单分组，便于后续替换为更复杂模型。
- simple_cluster(texts, n_clusters)：对 texts 列表（每项含 id、content/title）分配 cluster_index。
- extract_keywords(text, top_n)：从文本中按字符切分做简单词频统计，返回前 top_n 个词（供扩展展示）。
"""
import re
from collections import defaultdict

def simple_cluster(texts, n_clusters, algorithm='kmeans'):
    """
    对多段文本进行简单聚类，返回每段文本所属簇下标。
    :param texts: list[dict]，每项含 'id' 与 'content'（或 'title'+'content'）
    :param n_clusters: 簇数量
    :param algorithm: 算法名，当前仅实现 kmeans 风格分组
    :return: list[dict]，每项 {'text_id': int, 'cluster_index': int, 'score': float}
    """
    if not texts or n_clusters <= 0:
        return []
    n_clusters = min(n_clusters, len(texts))
    # 简单特征：取标题+内容的前 50 字哈希与长度作为分组依据
    features = []
    for t in texts:
        content = (t.get('title') or '') + (t.get('content') or '')
        content = content.strip()[:200]
        # 特征 1：长度段
        length_bin = min(len(content) // 20, 9)
        # 特征 2：首字/词（简化）
        first_ch = ord(content[0]) % 10 if content else 0
        features.append((t.get('id', 0), length_bin, first_ch))
    # 简单分组：按 (length_bin * 10 + first_ch) % n_clusters 分配
    result = []
    for i, (tid, lb, fc) in enumerate(features):
        idx = (lb * 10 + fc) % n_clusters
        result.append({'text_id': tid, 'cluster_index': idx, 'score': 0.85})
    return result

def extract_keywords(text, top_n=5):
    """
    从单段文本中抽取简单“关键词”（按长度过滤后的词频）。
    仅使用标准库 re，中文按字符分割简化处理。
    :param text: 字符串
    :param top_n: 返回前 N 个
    :return: list[str]
    """
    if not text:
        return []
    # 去除标点，按非字母数字中文切分
    cleaned = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
    parts = [s for s in cleaned.split() if len(s) >= 2]
    if not parts:
        return []
    cnt = defaultdict(int)
    for w in parts:
        cnt[w] += 1
    sorted_items = sorted(cnt.items(), key=lambda x: -x[1])
    return [w for w, _ in sorted_items[:top_n]]
