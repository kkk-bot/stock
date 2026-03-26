"""短期趋势判断占位模块。"""

from __future__ import annotations

from typing import Any

from collectors.mock_data import get_mock_fund_analysis


def judge_short_term_trend(query: str) -> dict[str, Any]:
    """返回基金短期判断占位结果。"""
    return get_mock_fund_analysis(query)["trend"]
