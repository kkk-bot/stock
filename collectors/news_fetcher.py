"""基金相关新闻查询模块。"""

from __future__ import annotations

from typing import Any

from collectors.fund_info import search_fund
from collectors.mock_data import get_mock_news_by_fund_code, get_mock_news_by_theme


def fetch_related_news(query: str) -> list[dict[str, Any]]:
    """按基金代码、基金名称或主题获取相关新闻。"""
    search_result = search_fund(query)
    fund = search_result.get("fund")
    if fund:
        news_items = get_mock_news_by_fund_code(fund["fund_code"])
        if news_items:
            return news_items

        theme_list = fund.get("themes", [])
        if theme_list:
            return get_mock_news_by_theme(theme_list[0])

    return get_mock_news_by_theme(query)
