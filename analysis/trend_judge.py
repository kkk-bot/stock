"""短期趋势判断模块。"""

from __future__ import annotations

from typing import Any

from analysis.sentiment import analyze_news_sentiment
from collectors.fund_info import fetch_fund_info


def judge_short_term_trend(query: str) -> dict[str, Any]:
    """结合基金属性和新闻情绪给出短期判断。"""
    fund = fetch_fund_info(query)
    if not fund:
        return {"label": "暂无判断", "reason": "当前未找到基金信息，无法生成短期判断。"}

    sentiment = analyze_news_sentiment(query)
    score = sentiment.get("score", 0.0)
    fund_type = fund.get("fund_type", "")
    market = fund.get("market", "")

    if fund_type == "债券型":
        return {
            "label": "偏稳",
            "reason": "债券基金通常以稳健波动为主，即便有情绪变化，整体走势也更偏平缓。",
        }
    if score >= 0.7:
        return {
            "label": "偏涨",
            "reason": f"近期新闻偏积极，{market}相关风险偏好有修复迹象，短线更容易出现反弹延续。",
        }
    if score >= 0.45:
        return {
            "label": "震荡",
            "reason": "当前消息面多空交织，方向尚不够一致，更适合按震荡思路观察后续信号。",
        }
    return {
        "label": "偏弱",
        "reason": "当前负面扰动占优，短期修复动力仍有限，走势可能继续偏弱或反复震荡。",
    }
