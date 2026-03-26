"""新闻情绪分析模块。"""

from __future__ import annotations

from typing import Any

from collectors.news_fetcher import fetch_related_news


def analyze_news_sentiment(query: str) -> dict[str, Any]:
    """基于 mock 新闻情绪标签生成情绪总结。"""
    news_items = fetch_related_news(query)
    if not news_items:
        return {
            "label": "暂无数据",
            "score": 0.0,
            "summary": "当前没有可用于情绪分析的新闻数据。",
            "counts": {"positive": 0, "neutral": 0, "negative": 0},
        }

    score_map = {"positive": 1.0, "neutral": 0.5, "negative": 0.0}
    counts = {"positive": 0, "neutral": 0, "negative": 0}
    total_score = 0.0
    for item in news_items:
        hint = item.get("sentiment_hint", "neutral")
        counts[hint] = counts.get(hint, 0) + 1
        total_score += score_map.get(hint, 0.5)

    avg_score = round(total_score / len(news_items), 2)
    if avg_score >= 0.7:
        label = "偏积极"
        summary = "相关新闻以偏正向信号为主，短期情绪较活跃，但依然需要留意波动回撤。"
    elif avg_score >= 0.45:
        label = "中性"
        summary = "正负信息交织，市场情绪偏观望，短期更可能处于震荡整理阶段。"
    else:
        label = "偏谨慎"
        summary = "负面扰动相对更多，短期情绪偏弱，后续需要观察风险释放和资金回流情况。"

    return {
        "label": label,
        "score": avg_score,
        "summary": summary,
        "counts": counts,
    }
