"""持仓补仓计算占位模块。"""

from __future__ import annotations

from typing import Any

from collectors.mock_data import get_mock_recovery_result


def calculate_recovery_plan(
    previous_nav: float,
    estimated_change_pct: float,
    holding_cost: float,
    holding_share: float,
    purchase_fee_rate: float,
    mode: str,
) -> dict[str, Any]:
    """返回补仓辅助计算占位结果。"""
    mock_result = get_mock_recovery_result()
    mock_result["input_summary"] = {
        "昨日单位净值": previous_nav,
        "当日预计涨跌幅": estimated_change_pct,
        "当前持有成本价": holding_cost,
        "当前持有份额": holding_share,
        "申购费率": purchase_fee_rate,
        "模式选择": mode,
    }
    return mock_result
