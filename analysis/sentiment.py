"""轻量新闻情绪分析模块。"""

from __future__ import annotations

from typing import Any


POSITIVE_KEYWORDS: dict[str, float] = {
    "大涨": 1.6,
    "上涨": 1.0,
    "上行": 0.8,
    "政策支持": 1.2,
    "超预期": 1.1,
    "增加": 0.45,
    "增长": 0.8,
    "扩大": 0.45,
    "回购": 1.0,
    "反弹": 0.9,
    "突破": 0.9,
    "订单增加": 1.1,
    "订单": 0.6,
    "降息预期": 1.0,
    "流入": 0.9,
    "利好": 1.0,
    "强劲": 1.0,
    "创新高": 1.1,
    "突破新高": 1.2,
    "回暖": 0.7,
    "修复": 0.7,
    "走强": 0.8,
    "改善": 0.7,
    "活跃": 0.45,
    "提升": 0.5,
    "份额增加": 0.7,
    "规模增长": 0.8,
    "获资金关注": 0.9,
    "资金关注": 0.6,
    "关注度提升": 0.65,
    "回升": 0.55,
    "增持": 0.8,
    "看好": 0.7,
    "需求回升": 0.8,
    "盈利改善": 0.85,
    "成交回暖": 0.75,
    "景气度": 0.7,
    "国产替代": 0.9,
    "获批": 0.8,
    "销量增长": 0.9,
    "资金回流": 0.8,
    "避险": 0.5,
    "稳健": 0.5,
}

NEGATIVE_KEYWORDS: dict[str, float] = {
    "大跌": 1.8,
    "下滑": 0.9,
    "下挫": 1.4,
    "暴跌": 1.2,
    "跳水": 1.7,
    "处罚": 1.1,
    "减持": 0.9,
    "减少": 0.45,
    "缩水": 0.7,
    "违约": 1.2,
    "亏损": 1.0,
    "监管压力": 1.0,
    "地缘冲突": 1.5,
    "战争": 1.7,
    "增派部队": 1.8,
    "制裁": 1.5,
    "流出": 0.9,
    "利空": 1.0,
    "承压": 0.8,
    "走弱": 0.7,
    "波动": 0.3,
    "波动加大": 0.9,
    "风险": 0.35,
    "风险上升": 1.0,
    "压力加大": 0.8,
    "出口限制": 1.0,
    "库存压力": 0.8,
    "不确定性": 0.7,
    "回落": 0.6,
    "压力": 0.6,
    "扰动": 0.5,
    "疲弱": 0.7,
    "拖累": 0.65,
    "担忧": 0.45,
}

LABEL_TEXT_MAP = {"positive": "偏多", "neutral": "中性", "negative": "偏空"}


def _extract_keyword_score(text: str, keyword_weights: dict[str, float]) -> tuple[float, list[str]]:
    """计算文本中命中的关键词分值。"""
    score = 0.0
    matched_keywords: list[str] = []
    for keyword, weight in keyword_weights.items():
        if keyword in text:
            score += weight
            matched_keywords.append(keyword)
    return score, matched_keywords


def _normalize_score(raw_score: float) -> float:
    """将原始分数压缩到 -1 到 1 区间。"""
    if raw_score > 0:
        return round(min(raw_score / 4.2, 1.0), 3)
    return round(max(raw_score / 4.2, -1.0), 3)


def _score_to_label(score: float) -> str:
    """根据分数映射情绪标签。"""
    if score >= 0.12:
        return "positive"
    if score <= -0.12:
        return "negative"
    return "neutral"


def analyze_news_sentiment(news_item: dict[str, Any]) -> dict[str, Any]:
    """分析单条新闻情绪并返回分数、标签和命中关键词。"""
    title = str(news_item.get("title", ""))
    summary = str(news_item.get("summary", ""))
    sentiment_hint = str(news_item.get("sentiment_hint", "")).strip().lower()

    # 标题与摘要都参与分析，但标题权重更高。
    combined_text = f"{title} {summary}".strip()

    title_positive_score, title_positive_keywords = _extract_keyword_score(title, POSITIVE_KEYWORDS)
    title_negative_score, title_negative_keywords = _extract_keyword_score(title, NEGATIVE_KEYWORDS)
    summary_positive_score, summary_positive_keywords = _extract_keyword_score(summary, POSITIVE_KEYWORDS)
    summary_negative_score, summary_negative_keywords = _extract_keyword_score(summary, NEGATIVE_KEYWORDS)

    raw_score = (
        title_positive_score * 2.2
        + summary_positive_score
        - title_negative_score * 2.2
        - summary_negative_score
    )
    matched_keywords = list(
        dict.fromkeys(
            title_positive_keywords
            + title_negative_keywords
            + summary_positive_keywords
            + summary_negative_keywords
        )
    )

    if not matched_keywords and sentiment_hint in LABEL_TEXT_MAP:
        hint_score_map = {"positive": 0.3, "neutral": 0.0, "negative": -0.3}
        sentiment_score = hint_score_map[sentiment_hint]
        sentiment_label = sentiment_hint
    else:
        sentiment_score = _normalize_score(raw_score)
        sentiment_label = _score_to_label(sentiment_score)

    if not matched_keywords and combined_text:
        matched_keywords = []

    return {
        "sentiment_score": sentiment_score,
        "sentiment_label": sentiment_label,
        "sentiment_text": LABEL_TEXT_MAP[sentiment_label],
        "matched_keywords": matched_keywords,
    }


def analyze_news_list(news_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """对新闻列表逐条进行情绪分析。"""
    analyzed_items: list[dict[str, Any]] = []
    for item in news_list:
        analyzed_result = analyze_news_sentiment(item)
        analyzed_items.append({**item, **analyzed_result})
    return analyzed_items


def _ensure_analyzed_items(news_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """如果新闻已包含情绪字段则直接使用，避免重复分析。"""
    if not news_list:
        return []
    if all("sentiment_label" in item and "sentiment_score" in item for item in news_list):
        return news_list
    return analyze_news_list(news_list)


def summarize_sentiment(news_list: list[dict[str, Any]]) -> dict[str, Any]:
    """汇总新闻列表的整体情绪结果。"""
    analyzed_items = _ensure_analyzed_items(news_list)
    if not analyzed_items:
        return {
            "positive_count": 0,
            "neutral_count": 0,
            "negative_count": 0,
            "average_sentiment_score": 0.0,
            "overall_conclusion": "中性",
            "keyword_frequency": {},
            "summary_text": "暂无新闻数据，无法形成有效情绪结论。",
        }

    positive_count = sum(1 for item in analyzed_items if item["sentiment_label"] == "positive")
    neutral_count = sum(1 for item in analyzed_items if item["sentiment_label"] == "neutral")
    negative_count = sum(1 for item in analyzed_items if item["sentiment_label"] == "negative")
    average_score = round(sum(item["sentiment_score"] for item in analyzed_items) / len(analyzed_items), 3)

    keyword_frequency: dict[str, int] = {}
    for item in analyzed_items:
        for keyword in item.get("matched_keywords", []):
            keyword_frequency[keyword] = keyword_frequency.get(keyword, 0) + 1

    if average_score >= 0.2 or positive_count >= negative_count + 2:
        overall_conclusion = "偏多"
        summary_text = "正面关键词命中更多，新闻整体偏暖，短期情绪相对占优。"
    elif average_score <= -0.2 or negative_count >= positive_count + 2:
        overall_conclusion = "偏空"
        summary_text = "负面关键词出现更频繁，板块情绪偏谨慎，短期仍需控制节奏。"
    else:
        overall_conclusion = "中性"
        summary_text = "正负信息相互交织，市场缺少明确单边信号，整体更像震荡观察阶段。"

    return {
        "positive_count": positive_count,
        "neutral_count": neutral_count,
        "negative_count": negative_count,
        "average_sentiment_score": average_score,
        "overall_conclusion": overall_conclusion,
        "keyword_frequency": keyword_frequency,
        "summary_text": summary_text,
        "news_count": len(analyzed_items),
    }
