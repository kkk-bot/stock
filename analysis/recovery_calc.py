"""持仓补仓计算模块。"""

from __future__ import annotations

from typing import Any

import pandas as pd


def _round(value: float) -> float:
    """统一数值保留四位小数。"""
    return round(value, 4)


def _format_percent(decimal_value: float) -> str:
    """将小数转为百分比文本。"""
    return f"{decimal_value * 100:.2f}%"


def validate_recovery_inputs(
    previous_nav: float,
    estimated_change_pct: float,
    holding_cost: float,
    holding_share: float,
    purchase_fee_rate: float,
) -> list[str]:
    """校验补仓计算的基础输入。"""
    errors: list[str] = []
    if previous_nav <= 0:
        errors.append("昨日单位净值必须大于 0。")
    if holding_cost <= 0:
        errors.append("当前持有成本价必须大于 0。")
    if holding_share <= 0:
        errors.append("当前持有份额必须大于 0。")
    if purchase_fee_rate < 0:
        errors.append("申购费率不能为负数。")
    if previous_nav * (1 + estimated_change_pct / 100) <= 0:
        errors.append("按预计涨跌幅计算后的实时净值必须大于 0，请检查输入。")
    return errors


def calculate_position_status(
    previous_nav: float,
    estimated_change_pct: float,
    holding_cost: float,
    holding_share: float,
) -> dict[str, float]:
    """计算当前持仓状态。"""
    current_nav = previous_nav * (1 + estimated_change_pct / 100)
    total_cost = holding_cost * holding_share
    market_value = current_nav * holding_share
    total_profit = market_value - total_cost
    profit_rate = total_profit / total_cost if total_cost else 0.0
    return {
        "实时净值": _round(current_nav),
        "当前市值": _round(market_value),
        "持仓总成本": _round(total_cost),
        "当前总盈亏": _round(total_profit),
        "当前盈亏率": profit_rate,
    }


def _calculate_added_shares(invest_amount: float, current_nav: float, fee_rate_decimal: float) -> float:
    """根据补仓金额计算新增份额。"""
    net_amount = invest_amount * (1 - fee_rate_decimal)
    return 0.0 if current_nav <= 0 else net_amount / current_nav


def _build_risk_notices(invest_amount: float, current_market_value: float) -> list[str]:
    """根据补仓金额生成风险提示。"""
    notices = ["本工具仅提供辅助计算，请结合个人现金流、风险承受能力与仓位规划综合判断。"]
    if invest_amount > current_market_value:
        notices.append("高风险：补仓金额已超过当前持仓市值。")
    elif invest_amount > current_market_value * 0.5:
        notices.append("补仓金额较大，请注意仓位风险。")
    return notices


def _build_scenario_analysis(
    current_nav: float,
    total_shares: float,
    total_cost: float,
    rebound_list: list[float] | None = None,
) -> pd.DataFrame:
    """生成默认反弹情景分析表格。"""
    rebound_list = rebound_list or [3, 5, 8, 10]
    rows: list[dict[str, Any]] = []
    for rebound in rebound_list:
        future_nav = current_nav * (1 + rebound / 100)
        future_value = future_nav * total_shares
        future_profit = future_value - total_cost
        rows.append(
            {
                "反弹情景": f"{rebound}%",
                "未来净值": _round(future_nav),
                "未来总市值": _round(future_value),
                "未来总盈亏": _round(future_profit),
            }
        )
    return pd.DataFrame(rows)


def calculate_by_amount(
    current_nav: float,
    holding_cost: float,
    holding_share: float,
    fee_rate_decimal: float,
    invest_amount: float,
) -> dict[str, Any]:
    """模式1：输入补仓金额，计算补仓后的成本与份额。"""
    if invest_amount <= 0:
        raise ValueError("补仓金额必须大于 0。")

    current_total_cost = holding_cost * holding_share
    added_shares = _calculate_added_shares(invest_amount, current_nav, fee_rate_decimal)
    total_shares = holding_share + added_shares
    total_cost = current_total_cost + invest_amount
    average_cost = total_cost / total_shares
    break_even_rise = average_cost / current_nav - 1

    return {
        "补仓金额": _round(invest_amount),
        "新增份额": _round(added_shares),
        "补仓后总份额": _round(total_shares),
        "补仓后平均成本": _round(average_cost),
        "补仓后总成本": _round(total_cost),
        "从当前净值回本所需涨幅": _format_percent(break_even_rise),
        "scenario_analysis": _build_scenario_analysis(current_nav, total_shares, total_cost),
        "risk_notices": _build_risk_notices(invest_amount, current_nav * holding_share),
    }


def calculate_by_target_cost(
    current_nav: float,
    holding_cost: float,
    holding_share: float,
    fee_rate_decimal: float,
    target_average_cost: float,
) -> dict[str, Any]:
    """模式2：输入目标平均成本，反推需要补仓的金额。"""
    if target_average_cost <= 0:
        raise ValueError("目标平均成本必须大于 0。")

    current_total_cost = holding_cost * holding_share
    if target_average_cost >= holding_cost:
        return {
            "需要补仓多少钱": 0.0,
            "补仓后总份额": _round(holding_share),
            "补仓后平均成本": _round(holding_cost),
            "说明": "目标平均成本不低于当前持仓成本，当前已经满足或无需补仓。",
        }

    min_reachable_cost = current_nav / (1 - fee_rate_decimal)
    if target_average_cost <= min_reachable_cost:
        raise ValueError("该目标平均成本过低，按当前净值和申购费率无法通过补仓达到。")

    numerator = target_average_cost * holding_share - current_total_cost
    denominator = 1 - target_average_cost * (1 - fee_rate_decimal) / current_nav
    if abs(denominator) < 1e-10:
        raise ValueError("当前参数下无法反推出合理补仓金额，请调整目标平均成本。")

    invest_amount = numerator / denominator
    if invest_amount <= 0:
        return {
            "需要补仓多少钱": 0.0,
            "补仓后总份额": _round(holding_share),
            "补仓后平均成本": _round(holding_cost),
            "说明": "当前持仓已接近目标平均成本，无需额外补仓。",
        }

    added_shares = _calculate_added_shares(invest_amount, current_nav, fee_rate_decimal)
    total_shares = holding_share + added_shares
    total_cost = current_total_cost + invest_amount
    average_cost = total_cost / total_shares
    return {
        "需要补仓多少钱": _round(invest_amount),
        "补仓后总份额": _round(total_shares),
        "补仓后平均成本": _round(average_cost),
        "说明": "结果基于当前实时净值与申购费率反推，仅供参考。",
    }


def calculate_by_target_profit(
    current_nav: float,
    holding_cost: float,
    holding_share: float,
    fee_rate_decimal: float,
    target_profit_amount: float,
    rebound_pct: float,
) -> dict[str, Any]:
    """模式3：输入目标总盈亏金额与预期反弹幅度，反推补仓金额。"""
    if rebound_pct <= 0:
        raise ValueError("预期反弹幅度必须大于 0。")

    current_total_cost = holding_cost * holding_share
    future_nav = current_nav * (1 + rebound_pct / 100)
    base_future_profit = future_nav * holding_share - current_total_cost
    growth_factor = (1 - fee_rate_decimal) * (1 + rebound_pct / 100) - 1
    if growth_factor <= 0:
        raise ValueError("在当前费率和反弹幅度下，补仓无法改善目标收益，请提高预期反弹幅度。")

    invest_amount = (target_profit_amount - base_future_profit) / growth_factor
    if invest_amount < 0:
        invest_amount = 0.0

    added_shares = _calculate_added_shares(invest_amount, current_nav, fee_rate_decimal)
    total_shares = holding_share + added_shares
    total_cost = current_total_cost + invest_amount
    average_cost = total_cost / total_shares
    break_even_rise = average_cost / current_nav - 1

    return {
        "需要补仓多少钱": _round(invest_amount),
        "补仓后平均成本": _round(average_cost),
        "补仓后总份额": _round(total_shares),
        "回本所需涨幅": _format_percent(break_even_rise),
        "scenario_analysis": _build_scenario_analysis(current_nav, total_shares, total_cost),
        "risk_notices": _build_risk_notices(invest_amount, current_nav * holding_share),
        "说明": "目标总盈亏金额输入 0，表示在设定反弹幅度下刚好回本。",
    }


def calculate_recovery_plan(
    previous_nav: float,
    estimated_change_pct: float,
    holding_cost: float,
    holding_share: float,
    purchase_fee_rate: float,
    mode: str,
    mode_value: float,
    rebound_pct: float | None = None,
) -> dict[str, Any]:
    """根据不同补仓模式返回完整计算结果。"""
    errors = validate_recovery_inputs(
        previous_nav=previous_nav,
        estimated_change_pct=estimated_change_pct,
        holding_cost=holding_cost,
        holding_share=holding_share,
        purchase_fee_rate=purchase_fee_rate,
    )
    if errors:
        raise ValueError("；".join(errors))

    fee_rate_decimal = purchase_fee_rate / 100
    position_status = calculate_position_status(
        previous_nav=previous_nav,
        estimated_change_pct=estimated_change_pct,
        holding_cost=holding_cost,
        holding_share=holding_share,
    )
    current_nav = position_status["实时净值"]

    if mode == "模式1：输入补仓金额":
        mode_result = calculate_by_amount(
            current_nav=current_nav,
            holding_cost=holding_cost,
            holding_share=holding_share,
            fee_rate_decimal=fee_rate_decimal,
            invest_amount=mode_value,
        )
    elif mode == "模式2：输入目标平均成本":
        mode_result = calculate_by_target_cost(
            current_nav=current_nav,
            holding_cost=holding_cost,
            holding_share=holding_share,
            fee_rate_decimal=fee_rate_decimal,
            target_average_cost=mode_value,
        )
    elif mode == "模式3：目标盈亏 + 预期反弹":
        mode_result = calculate_by_target_profit(
            current_nav=current_nav,
            holding_cost=holding_cost,
            holding_share=holding_share,
            fee_rate_decimal=fee_rate_decimal,
            target_profit_amount=mode_value,
            rebound_pct=rebound_pct or 0.0,
        )
    else:
        raise ValueError("暂不支持当前模式。")

    return {
        "position_status": position_status,
        "mode_result": mode_result,
        "input_summary": {
            "昨日单位净值": previous_nav,
            "当日预计涨跌幅": estimated_change_pct,
            "当前持有成本价": holding_cost,
            "当前持有份额": holding_share,
            "申购费率": purchase_fee_rate,
            "模式选择": mode,
            "模式输入值": mode_value,
            "预期反弹幅度": rebound_pct,
        },
    }
