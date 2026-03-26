"""基金相关新闻采集占位模块。"""

from __future__ import annotations

from typing import Any

from collectors.mock_data import get_mock_fund_analysis


def fetch_related_news(query: str) -> list[dict[str, Any]]:
    """获取基金相关新闻占位数据。"""
    return get_mock_fund_analysis(query)["news"]
