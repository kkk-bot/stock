"""轻量新闻情绪分析模块。"""

from __future__ import annotations

import re
from typing import Any


POSITIVE_KEYWORDS: dict[str, float] = {
    "大涨": 1.0,
    "上涨": 0.55,
    "上行": 0.35,
    "看多": 0.5,
    "看好": 0.45,
    "政策支持": 0.9,
    "支持": 0.2,
    "超预期": 0.85,
    "增加": 0.18,
    "增长": 0.25,
    "扩大": 0.18,
    "回购": 0.65,
    "反弹": 0.35,
    "突破": 0.55,
    "订单增加": 0.65,
    "订单": 0.12,
    "降息预期": 0.55,
    "流入": 0.25,
    "资金流入": 0.45,
    "利好": 0.7,
    "强劲": 0.65,
    "强势": 0.4,
    "创新高": 0.9,
    "突破新高": 0.95,
    "回暖": 0.3,
    "修复": 0.3,
    "走强": 0.3,
    "改善": 0.25,
    "活跃": 0.2,
    "提升": 0.18,
    "份额增加": 0.5,
    "规模增长": 0.55,
    "获资金关注": 0.45,
    "资金关注": 0.2,
    "关注度提升": 0.32,
    "回升": 0.22,
    "增持": 0.4,
    "需求回升": 0.45,
    "盈利改善": 0.5,
    "成交回暖": 0.4,
    "布局窗口": 0.45,
    "景气度": 0.18,
    "国产替代": 0.45,
    "获批": 0.45,
    "销量增长": 0.55,
    "资金回流": 0.45,
    "避险": 0.12,
    "稳健": 0.12,
}

NEGATIVE_KEYWORDS: dict[str, float] = {
    "加速下跌": 1.0,
    "快速下跌": 0.95,
    "大幅回落": 0.75,
    "大跌": 1.0,
    "下跌": 0.45,
    "跌近": 0.5,
    "跌超": 0.65,
    "走低": 0.35,
    "下滑": 0.4,
    "下挫": 0.8,
    "暴跌": 0.95,
    "跳水": 0.95,
    "处罚": 0.65,
    "减持": 0.5,
    "减少": 0.15,
    "缩水": 0.3,
    "违约": 0.9,
    "亏损": 0.7,
    "监管压力": 0.65,
    "地缘冲突": 0.85,
    "战争": 0.95,
    "增派部队": 0.95,
    "制裁": 0.85,
    "流出": 0.3,
    "利空": 0.75,
    "承压": 0.3,
    "走弱": 0.3,
    "波动": 0.12,
    "波动加大": 0.35,
    "风险": 0.15,
    "风险上升": 0.65,
    "压力加大": 0.4,
    "出口限制": 0.55,
    "库存压力": 0.45,
    "不确定性": 0.25,
    "回落": 0.25,
    "压力": 0.15,
    "扰动": 0.12,
    "疲弱": 0.3,
    "拖累": 0.3,
    "担忧": 0.18,
    "调整": 0.18,
    "弱势": 0.25,
}

LABEL_TEXT_MAP = {"positive": "偏多", "neutral": "中性", "negative": "偏空"}
PATTERN_WEIGHTS: list[tuple[str, str, float]] = [
    (r"涨超\s*(\d+(?:\.\d+)?)%", "涨超", 0.85),
    (r"涨近\s*(\d+(?:\.\d+)?)%", "涨近", 0.55),
    (r"跌超\s*(\d+(?:\.\d+)?)%", "跌超", -0.85),
    (r"跌近\s*(\d+(?:\.\d+)?)%", "跌近", -0.55),
]


def _extract_keyword_score(text: str, keyword_weights: dict[str, float]) -> tuple[float, list[str]]:
    """计算文本中命中的关键词分值，优先长短语，避免重复叠加子词。"""
    score = 0.0
    matched_keywords: list[str] = []
    occupied_ranges: list[tuple[int, int]] = []

    for keyword, weight in sorted(keyword_weights.items(), key=lambda item: len(item[0]), reverse=True):
        start_index = text.find(keyword)
        if start_index == -1:
            continue
        end_index = start_index + len(keyword)
        if any(not (end_index <= start or start_index >= end) for start, end in occupied_ranges):
            continue
        score += weight
        matched_keywords.append(keyword)
        occupied_ranges.append((start_index, end_index))
    return score, matched_keywords


def _extract_pattern_score(text: str) -> tuple[float, list[str]]:
    """识别涨跌幅表达式，并返回附加分值。"""
    score = 0.0
    matched_patterns: list[str] = []
    for pattern, label, base_weight in PATTERN_WEIGHTS:
        for match in re.finditer(pattern, text):
            try:
                pct_value = float(match.group(1))
            except Exception:
                pct_value = 0.0
            dynamic_weight = base_weight + (min(pct_value, 5.0) / 10.0) * (1 if base_weight > 0 else -1)
            score += dynamic_weight
            matched_patterns.append(match.group(0))
    return score, matched_patterns


def _normalize_score(raw_score: float) -> float:
    """将原始分数压缩到 -1 到 1 区间。"""
    if raw_score == 0:
        return 0.0
    normalized = raw_score / (1 + abs(raw_score))
    return round(max(min(normalized, 1.0), -1.0), 3)


def _score_to_label(score: float) -> str:
    """根据分数映射情绪标签。"""
    if score > 0.1:
        return "positive"
    if score < -0.1:
        return "negative"
    return "neutral"


def analyze_news_sentiment(news_item: dict[str, Any]) -> dict[str, Any]:
    """分析单条新闻情绪并返回分数、标签和命中关键词。"""
    title = str(news_item.get("title", ""))
    summary = str(news_item.get("summary", ""))
    sentiment_hint = str(news_item.get("sentiment_hint", "")).strip().lower()
    title_weight = 0.7
    summary_weight = 0.3

    title_positive_score, title_positive_keywords = _extract_keyword_score(title, POSITIVE_KEYWORDS)
    title_negative_score, title_negative_keywords = _extract_keyword_score(title, NEGATIVE_KEYWORDS)
    summary_positive_score, summary_positive_keywords = _extract_keyword_score(summary, POSITIVE_KEYWORDS)
    summary_negative_score, summary_negative_keywords = _extract_keyword_score(summary, NEGATIVE_KEYWORDS)
    title_pattern_score, title_patterns = _extract_pattern_score(title)
    summary_pattern_score, summary_patterns = _extract_pattern_score(summary)

    title_raw_score = title_positive_score - title_negative_score
    summary_raw_score = summary_positive_score - summary_negative_score
    raw_score = (
        title_raw_score * title_weight
        + summary_raw_score * summary_weight
        + title_pattern_score * title_weight
        + summary_pattern_score * summary_weight
    )
    matched_keywords = list(
        dict.fromkeys(
            title_positive_keywords
            + title_negative_keywords
            + summary_positive_keywords
            + summary_negative_keywords
        )
    )
    matched_patterns = list(dict.fromkeys(title_patterns + summary_patterns))

    if not matched_keywords and not matched_patterns and sentiment_hint in LABEL_TEXT_MAP:
        hint_score_map = {"positive": 0.18, "neutral": 0.0, "negative": -0.18}
        sentiment_score = hint_score_map[sentiment_hint]
        sentiment_label = sentiment_hint
        normalized_score = sentiment_score
    else:
        normalized_score = _normalize_score(raw_score)
        sentiment_score = normalized_score
        sentiment_label = _score_to_label(normalized_score)

    return {
        "sentiment_score": sentiment_score,
        "raw_score": round(raw_score, 3),
        "normalized_score": normalized_score,
        "sentiment_label": sentiment_label,
        "sentiment_text": LABEL_TEXT_MAP[sentiment_label],
        "matched_keywords": matched_keywords,
        "matched_patterns": matched_patterns,
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
