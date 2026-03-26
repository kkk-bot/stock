"""基金信息查询模块。"""

from __future__ import annotations

from typing import Any

from collectors.mock_data import get_mock_fund_by_code, search_mock_funds_by_name


def search_fund(query: str) -> dict[str, Any]:
    """按基金代码或名称查询基金，并返回统一结构。"""
    normalized_query = query.strip()
    if not normalized_query:
        return {
            "success": False,
            "message": "请输入基金代码或基金名称后再开始分析。",
            "fund": None,
            "matches": [],
        }

    fund = get_mock_fund_by_code(normalized_query)
    if fund:
        return {
            "success": True,
            "message": "已按基金代码匹配到基金。",
            "fund": fund,
            "matches": [fund],
        }

    matches = search_mock_funds_by_name(normalized_query)
    if matches:
        return {
            "success": True,
            "message": f"按名称匹配到 {len(matches)} 只基金，当前优先展示第一条结果。",
            "fund": matches[0],
            "matches": matches,
        }

    return {
        "success": False,
        "message": "未找到对应基金，请检查代码或名称，当前版本仅支持内置示例数据。",
        "fund": None,
        "matches": [],
    }


def fetch_fund_info(query: str) -> dict[str, Any] | None:
    """根据基金代码或名称获取基金基础信息。"""
    result = search_fund(query)
    return result["fund"]


def fetch_fund_themes(query: str) -> list[str]:
    """获取基金所属板块或主题。"""
    fund = fetch_fund_info(query)
    if not fund:
        return []
    return list(fund.get("themes", []))
