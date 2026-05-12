# -*- coding: utf-8 -*-
"""
摘要算法封装：仅使用 Python 标准库实现抽取式摘要。

无第三方库，采用首句/首段抽取与拼接，便于后续替换为生成式模型。
- extractive_summary(texts, max_chars)：对多段文本每段取首句，拼接后截断至 max_chars。
- summarize_single(text, max_chars)：对单段文本取首句或前 max_chars 字，用于单文本摘要。
"""
import re

def extractive_summary(texts, max_chars=500):
    """
    对多段文本生成抽取式摘要：优先每段首句，再按长度限制截断拼接。
    :param texts: list[str]，多段正文
    :param max_chars: 摘要最大字符数
    :return: str
    """
    if not texts:
        return ''
    sentences = []
    for t in texts:
        t = (t or '').strip()
        if not t:
            continue
        # 简单分句：按。！？\n 分割，取第一句
        first = re.split(r'[。！？\n]', t, 1)[0].strip()
        if first:
            sentences.append(first + '。' if not first.endswith('。') else first)
    combined = ''.join(sentences)
    if len(combined) <= max_chars:
        return combined
    return combined[:max_chars].rstrip() + '…'

def summarize_single(text, max_chars=200):
    """
    对单段文本生成简短摘要：取首句或前 max_chars 字。
    :param text: 字符串
    :param max_chars: 最大字符数
    :return: str
    """
    if not text:
        return ''
    text = text.strip()
    first = re.split(r'[。！？\n]', text, 1)[0].strip()
    if first:
        s = first + '。' if not first.endswith('。') else first
    else:
        s = text
    if len(s) <= max_chars:
        return s
    return s[:max_chars].rstrip() + '…'
