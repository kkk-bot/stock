"""资产基础信息与输入解析模块。"""

from __future__ import annotations

from typing import Any

from collectors.mock_data import list_supported_assets, resolve_mock_asset


def list_market_assets(market: str) -> list[dict[str, Any]]:
    """返回指定市场可用的代表性资产。"""
    return list_supported_assets(market)


def resolve_asset_input(market: str, query: str) -> dict[str, Any]:
    """根据市场与用户输入解析代表性资产。"""
    normalized_query = query.strip()
    if not normalized_query:
        assets = list_market_assets(market)
        if not assets:
            return {
                "success": False,
                "message": "当前市场暂无可分析资产，请稍后再试。",
                "asset": None,
                "data_source": "mock",
            }
        default_asset = assets[0].copy()
        default_asset["market"] = market
        return {
            "success": True,
            "message": "未输入代码，当前使用默认代表性资产。",
            "asset": default_asset,
            "data_source": "mock",
        }

    matched_asset = resolve_mock_asset(market, normalized_query)
    if matched_asset:
        matched_asset["market"] = market
        return {
            "success": True,
            "message": "已匹配到代表性资产。",
            "asset": matched_asset,
            "data_source": "mock",
        }

    return {
        "success": False,
        "message": "未找到对应资产，请优先使用页面提供的代表性资产代码或名称。",
        "asset": None,
        "data_source": "mock",
    }
