"""基金信息采集占位模块。"""

from __future__ import annotations

from typing import Any

from collectors.mock_data import get_mock_fund_analysis


def fetch_fund_info(query: str) -> dict[str, Any]:
    """根据基金代码或名称获取基金基础信息占位数据。"""
    return get_mock_fund_analysis(query)["basic_info"]


def fetch_fund_themes(query: str) -> list[str]:
    """获取基金所属板块或主题占位数据。"""
    return get_mock_fund_analysis(query)["themes"]
