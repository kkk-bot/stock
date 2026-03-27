"""短期趋势判断模块。"""

from __future__ import annotations

from typing import Any


def _contains_strength_hint(description: str) -> bool:
    """判断基金描述是否偏强。"""
    strength_keywords = ["景气", "弹性", "修复", "增长", "走强", "回暖", "利好"]
    return any(keyword in description for keyword in strength_keywords)


def _contains_weakness_hint(description: str) -> bool:
    """判断基金描述是否偏弱。"""
    weakness_keywords = ["承压", "波动", "压力", "不确定", "风险"]
    return any(keyword in description for keyword in weakness_keywords)


def judge_short_term_trend(
    fund_info: dict[str, Any],
    sentiment_summary: dict[str, Any],
    news_count: int | None = None,
) -> dict[str, Any]:
    """根据基金信息和新闻情绪结果给出短期判断与原因说明。"""
    if not fund_info:
        return {
            "trend_label": "暂无判断",
            "reason_text": "当前未找到基金信息，无法生成短期判断。",
            "confidence_hint": "低",
            "reasons": ["缺少基金基础信息。"],
        }

    positive_count = sentiment_summary.get("positive_count", 0)
    neutral_count = sentiment_summary.get("neutral_count", 0)
    negative_count = sentiment_summary.get("negative_count", 0)
    average_score = sentiment_summary.get("average_sentiment_score", 0.0)
    keyword_frequency = sentiment_summary.get("keyword_frequency", {})
    news_count = news_count if news_count is not None else sentiment_summary.get("news_count", 0)

    description = str(fund_info.get("description", ""))
    positive_bias = _contains_strength_hint(description)
    negative_bias = _contains_weakness_hint(description)

    bearish_keyword_hits = sum(
        keyword_frequency.get(keyword, 0)
        for keyword in ["风险上升", "承压", "流出", "下滑", "波动加大", "监管压力", "出口限制"]
    )

    reasons: list[str] = []
    if positive_count >= negative_count + 2 or average_score >= 0.28 or (positive_bias and average_score >= 0.12):
        trend_label = "偏涨"
        reasons.append("近期正面新闻数量较多，板块情绪偏暖。")
        if average_score >= 0.28:
            reasons.append("平均情绪分数较高，短期资金偏好有修复迹象。")
        if positive_bias:
            reasons.append("基金所处方向具备一定景气或修复特征，容易形成情绪共振。")
    elif negative_count >= positive_count + 2 or average_score <= -0.22 or bearish_keyword_hits >= 2:
        trend_label = "偏弱"
        reasons.append("近期负面新闻偏多，相关板块短期承压。")
        if average_score <= -0.22:
            reasons.append("平均情绪分数偏低，市场更关注风险而非进攻。")
        if bearish_keyword_hits >= 2 or negative_bias:
            reasons.append("新闻中多次出现承压、流出或风险上升等词，偏弱信号更集中。")
    else:
        trend_label = "震荡"
        reasons.append("正负面消息接近，短期缺少明确方向。")
        if neutral_count > 0:
            reasons.append("中性新闻占比不低，市场更可能维持观察与反复博弈。")
        reasons.append("当前更适合按震荡思路看待，等待新的催化。")

    score_gap = abs(positive_count - negative_count)
    if news_count <= 2:
        confidence_hint = "低"
    elif score_gap >= 2 and abs(average_score) >= 0.25 and news_count >= 4:
        confidence_hint = "高"
    else:
        confidence_hint = "中"

    reason_text = " ".join(reasons[:3])
    return {
        "trend_label": trend_label,
        "reason_text": reason_text,
        "confidence_hint": confidence_hint,
        "reasons": reasons[:3],
    }
