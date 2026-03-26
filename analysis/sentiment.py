"""新闻情绪分析占位模块。"""

from __future__ import annotations

from typing import Any

from collectors.mock_data import get_mock_fund_analysis


def analyze_news_sentiment(query: str) -> dict[str, Any]:
    """返回新闻情绪分析占位结果。"""
    return get_mock_fund_analysis(query)["sentiment"]
