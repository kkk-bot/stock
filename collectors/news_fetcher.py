"""统一新闻获取接口。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import re
from typing import Any

from collectors.alpha_vantage_client import AlphaVantageClient
from collectors.bing_news_rss import BingNewsRSSClient
from collectors.gdelt_client import GdeltClient
from collectors.google_news_rss import GoogleNewsRSSClient
from collectors.sec_edgar_client import SecEdgarClient


alpha_client = AlphaVantageClient()
google_news_client = GoogleNewsRSSClient()
bing_news_client = BingNewsRSSClient()
gdelt_client = GdeltClient()
sec_edgar_client = SecEdgarClient()

FINANCIAL_RELEVANCE_KEYWORDS = [
    "北向资金",
    "恒生科技",
    "沪深300",
    "科技股",
    "华尔街",
    "纳斯达克",
    "标普",
    "道琼斯",
    "美股期货",
    "股票期货",
    "芯片股",
    "半导体股票",
    "美联储",
    "资金流入",
    "资金流出",
    "非农",
    "财报",
    "半导体",
    "新能源",
    "医药",
    "白酒",
    "消费",
    "降息",
    "加息",
    "通胀",
    "基金",
    "etf",
    "指数",
    "大盘",
    "市场",
    "收盘",
    "板块",
    "资金",
    "港股",
    "美股",
    "黄金",
    "金价",
    "纳指",
    "ai",
    "nasdaq",
    "s&p 500",
    "dow jones",
    "wall street",
    "us stock market",
    "stock futures",
    "us equities",
    "tech stocks",
    "semiconductor",
    "semiconductors",
    "chip stocks",
    "stocks",
    "markets",
    "earnings",
    "fed",
]

STRONG_FINANCIAL_KEYWORDS = {
    "北向资金",
    "恒生科技",
    "沪深300",
    "科技股",
    "华尔街",
    "纳斯达克",
    "标普",
    "道琼斯",
    "美股期货",
    "股票期货",
    "芯片股",
    "半导体股票",
    "美联储",
    "资金流入",
    "资金流出",
    "非农",
    "财报",
    "半导体",
    "新能源",
    "医药",
    "白酒",
    "消费",
    "降息",
    "加息",
    "通胀",
    "港股",
    "美股",
    "黄金",
    "金价",
    "纳指",
    "nasdaq",
    "s&p 500",
    "dow jones",
    "wall street",
    "us stock market",
    "stock futures",
    "us equities",
    "tech stocks",
    "semiconductor",
    "semiconductors",
    "chip stocks",
    "earnings",
    "fed",
}

OBVIOUSLY_IRRELEVANT_KEYWORDS = [
    "青少年",
    "安全教育",
    "校园",
    "研学",
    "旅游",
    "文旅",
    "招聘",
    "专场招聘",
    "青年就业",
    "志愿服务",
    "社区活动",
    "城市活动",
    "公益活动",
    "培训班",
    "开学",
    "招生",
]

THEME_EXPANSION_RULES: list[tuple[list[str], list[str]]] = [
    (
        ["恒生科技", "港股科技", "香港科技股", "恒生科技指数"],
        ["恒生科技", "港股科技", "香港科技股", "恒生科技指数", "科网股", "科技股"],
    ),
    (
        ["恒生互联网", "港股互联网", "香港互联网股"],
        ["恒生互联网", "港股互联网", "香港互联网股", "科网股", "互联网平台"],
    ),
    (
        ["高端制造", "先进制造", "制造升级", "制造业升级", "高端装备"],
        ["高端制造", "先进制造", "制造业", "制造业升级", "工业升级", "高端装备", "机器人", "自动化", "设备", "新材料", "产业升级", "制造业景气"],
    ),
    (
        ["新能源", "光伏", "锂电", "储能", "新能源车"],
        ["新能源", "锂电", "光伏", "储能", "新能源车"],
    ),
    (
        ["半导体", "芯片", "晶圆", "国产替代"],
        ["半导体", "芯片", "晶圆", "国产替代", "设备"],
    ),
    (
        ["医药", "医疗", "创新药", "生物科技"],
        ["医药", "医疗", "创新药", "集采", "审批", "生物科技"],
    ),
    (
        ["现金流", "高股息", "红利", "价值风格", "防御风格"],
        ["现金流", "红利", "高股息", "价值风格", "防御风格", "富时", "公募基金", "风格轮动", "资金流向"],
    ),
    (
        ["美股科技", "纳指", "纳斯达克", "AI芯片", "海外成长"],
        [
            "美股科技",
            "纳斯达克",
            "纳指",
            "华尔街",
            "科技股",
            "芯片股",
            "半导体",
            "英伟达",
            "NVIDIA",
            "Nvidia",
            "Apple",
            "Microsoft",
            "Nasdaq",
            "Wall Street",
            "US stock market",
            "US equities",
            "tech stocks",
            "semiconductor",
        ],
    ),
]

THEME_STOPWORDS = {"综合", "成长", "基金观察", "宽基", "蓝筹", "海外成长", "低波动"}


def _normalize_theme_text(theme: str | list[str] | None) -> str:
    """规范化主题字段。"""
    if isinstance(theme, list):
        return " / ".join(str(item).strip() for item in theme if str(item).strip())
    return str(theme or "").strip()


def _dedupe_keywords(keywords: list[str]) -> list[str]:
    """按顺序去重关键词。"""
    return list(dict.fromkeys(keyword for keyword in keywords if str(keyword).strip()))


def _shorten_text(text: str, max_length: int = 220) -> str:
    """截断过长调试文本，避免页面被请求错误撑开。"""
    normalized = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(normalized) <= max_length:
        return normalized
    return f"{normalized[:max_length]}..."


def _split_text_keywords(text: str) -> list[str]:
    """从主题或简介中拆出关键词。"""
    parts = re.split(r"[、/,，；;｜|\s]+", str(text or "").strip())
    return [part.strip() for part in parts if len(part.strip()) >= 2 and part.strip() not in THEME_STOPWORDS]


def _extract_theme_keywords(asset_detail: dict[str, Any]) -> list[str]:
    """从基金/资产基础信息中提取主题关键词并做行业扩展。"""
    name_text = str(asset_detail.get("name", "")).strip()
    theme_text = _normalize_theme_text(asset_detail.get("theme"))
    description_text = str(asset_detail.get("description", "")).strip()
    aliases = asset_detail.get("aliases", []) or []
    searchable_text = " ".join(
        [
            name_text,
            theme_text,
            description_text,
            *[str(alias).strip() for alias in aliases if str(alias).strip()],
        ]
    )

    theme_keywords: list[str] = []
    theme_keywords.extend(_split_text_keywords(theme_text))
    theme_keywords.extend(_split_text_keywords(description_text))

    for triggers, expansions in THEME_EXPANSION_RULES:
        if any(trigger in searchable_text for trigger in triggers):
            theme_keywords.extend(expansions)

    return _dedupe_keywords(theme_keywords)


def _clean_asset_name(name: str) -> str:
    """清洗基金或资产名称，便于生成更宽松的新闻匹配词。"""
    cleaned = str(name or "").strip()
    for suffix in ("ETF联接C", "ETF联接A", "ETF联接", "联接C", "联接A", "ETF", "A", "C"):
        if cleaned.endswith(suffix) and len(cleaned) > len(suffix) + 1:
            cleaned = cleaned[: -len(suffix)].strip()
            break
    return cleaned


def _asset_alias_keywords(symbol: str, name: str) -> list[str]:
    """为常见美股/ETF补充中英文新闻别名。"""
    symbol_text = str(symbol or "").strip().upper()
    name_text = str(name or "").strip()
    alias_map = {
        "NVDA": ["NVDA", "NVIDIA", "Nvidia", "英伟达", "AI芯片", "芯片股"],
        "QQQ": ["QQQ", "纳斯达克100", "纳指100", "Nasdaq 100", "Nasdaq", "美股科技ETF"],
        "AAPL": ["AAPL", "Apple", "苹果"],
        "MSFT": ["MSFT", "Microsoft", "微软"],
        "TSLA": ["TSLA", "Tesla", "特斯拉"],
        "AMZN": ["AMZN", "Amazon", "亚马逊"],
    }
    aliases = alias_map.get(symbol_text, [])
    if "英伟达" in name_text or "NVIDIA" in name_text.upper():
        aliases.extend(alias_map["NVDA"])
    return _dedupe_keywords(aliases)


def _build_relevance_profile(asset_detail: dict[str, Any]) -> dict[str, list[str]]:
    """根据资产信息构造搜索词与相关性关键词。"""
    asset_name = str(asset_detail.get("name", "")).strip()
    cleaned_name = _clean_asset_name(asset_name)
    symbol = str(asset_detail.get("symbol", "")).strip()
    aliases = [str(alias).strip() for alias in asset_detail.get("aliases", []) if str(alias).strip()]
    aliases.extend(_asset_alias_keywords(symbol, asset_name))
    theme_keywords = _extract_theme_keywords(asset_detail)

    exact_keywords = _dedupe_keywords(
        [
            asset_name,
            cleaned_name,
            symbol,
            *aliases,
        ]
    )
    medium_keywords = _dedupe_keywords(theme_keywords + aliases + _split_text_keywords(asset_detail.get("description", "")))
    search_keywords = _dedupe_keywords(
        [keyword for keyword in exact_keywords + medium_keywords if keyword and len(keyword) >= 2]
    )[:8]
    return {
        "exact_keywords": exact_keywords,
        "medium_keywords": medium_keywords,
        "search_keywords": search_keywords,
        "theme_keywords": theme_keywords,
    }


def _get_local_now() -> datetime:
    """获取运行环境本地时区下的当前时间。"""
    return datetime.now().astimezone()


def _parse_publish_time_to_local_datetime(publish_time: str) -> datetime | None:
    """尽量解析新闻发布时间，并转换到本地时间。"""
    normalized_text = str(publish_time or "").strip()
    if not normalized_text:
        return None

    try:
        parsed_dt = parsedate_to_datetime(normalized_text)
        if parsed_dt.tzinfo is None:
            parsed_dt = parsed_dt.replace(tzinfo=_get_local_now().tzinfo)
        return parsed_dt.astimezone()
    except Exception:
        pass

    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d",
        "%Y-%m-%d %H:%M:%S %Z",
        "%Y%m%dT%H%M%SZ",
        "%Y%m%d%H%M%S",
    ):
        try:
            parsed_dt = datetime.strptime(normalized_text, fmt)
            if normalized_text.endswith("UTC") or normalized_text.endswith("Z"):
                parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
            else:
                parsed_dt = parsed_dt.replace(tzinfo=_get_local_now().tzinfo)
            return parsed_dt
        except Exception:
            continue

    try:
        parsed_dt = datetime.fromisoformat(normalized_text.replace("Z", "+00:00"))
        if parsed_dt.tzinfo is None:
            parsed_dt = parsed_dt.replace(tzinfo=_get_local_now().tzinfo)
        return parsed_dt.astimezone()
    except Exception:
        return None


def _extract_keywords(market: str, symbol: str | None, theme: str | None) -> list[str]:
    """根据市场与资产提取更稳定的新闻搜索关键词。"""
    symbol_text = (symbol or "").strip().upper()
    theme_text = (theme or "").strip()
    symbol_keyword_map: dict[str, list[str]] = {
        "000001.SH": ["上证指数", "A股大盘", "沪市行情"],
        "510300.SH": ["沪深300", "沪深300ETF", "A股蓝筹"],
        "00700.HK": ["腾讯控股", "港股科技", "香港科技股"],
        "03033.HK": ["恒生科技", "恒生科技指数", "港股科技"],
        "NVDA": ["NVDA", "英伟达", "美股科技"],
        "QQQ": ["QQQ", "纳斯达克100", "美股科技ETF"],
        "XAUUSD": ["现货黄金", "国际金价", "黄金市场"],
        "GLD": ["黄金ETF", "GLD", "SPDR Gold Shares"],
    }
    if symbol_text in symbol_keyword_map:
        return symbol_keyword_map[symbol_text]
    if market == "美股" and not symbol_text:
        return ["S&P 500", "Nasdaq", "Wall Street", "US stock market"]
    if market == "基金" and theme_text:
        return [item.strip() for item in theme_text.replace("/", " ").split() if item.strip()][:4] or [theme_text]
    if theme_text:
        return [item.strip() for item in theme_text.replace("/", " ").split() if item.strip()][:4] or [theme_text]
    market_default_map = {
        "A股": ["A股", "沪深股市"],
        "港股": ["港股", "香港股市"],
        "美股": ["美股", "纳斯达克"],
        "黄金": ["黄金", "国际金价"],
    }
    return market_default_map.get(market, ["财经"])


def _get_us_market_news_keyword_groups(theme: str) -> list[list[str]]:
    """为美股市场总览生成更合理的英文新闻关键词组。"""
    theme_text = (theme or "").strip()
    base_groups = [
        ["S&P 500", "US stock market"],
        ["Nasdaq", "US equities"],
        ["Dow Jones", "Wall Street"],
        ["Nvidia", "Microsoft", "Apple", "Amazon"],
    ]
    if "科技" in theme_text or "纳指" in theme_text:
        return [
            ["Nasdaq", "US stock market"],
            ["Wall Street", "US equities"],
            ["Nvidia", "Microsoft", "Apple", "Amazon"],
        ]
    return base_groups


def _collect_google_news_batches(
    keyword_groups: list[list[str]],
    market: str,
    symbol: str | None,
    theme: str | None,
    limit_per_group: int = 4,
) -> dict[str, Any]:
    """按多组关键词聚合 Google News RSS，并在函数内完成去重。"""
    merged_items: list[dict[str, Any]] = []
    source_errors: list[str] = []
    for keywords in keyword_groups:
        rss_news = google_news_client.get_news(
            keywords=keywords,
            market=market,
            symbol=symbol,
            theme=theme,
            limit=limit_per_group,
        ) or []
        if not rss_news and google_news_client.last_error:
            source_errors.append(f"Google News RSS：{google_news_client.last_error}")
        merged_items.extend(
            _normalize_news_item(item, market, symbol, theme, "Google News RSS", "real")
            for item in rss_news
        )
    return {"items": _dedupe_news_items(merged_items), "source_errors": _dedupe_keywords(source_errors)}


def _fetch_news_with_fallback(
    keywords: list[str] | str,
    market: str,
    symbol: str | None,
    theme: str | None,
    limit: int,
    include_gdelt: bool = True,
) -> dict[str, Any]:
    """聚合多个真实新闻源，后续统一做时间与相关性筛选。"""
    source_errors: list[str] = []
    merged_items: list[dict[str, Any]] = []
    rss_items = google_news_client.get_news(
        keywords=keywords,
        market=market,
        symbol=symbol,
        theme=theme,
        limit=limit,
    ) or []
    if not rss_items and google_news_client.last_error:
        source_errors.append(f"Google News RSS：{google_news_client.last_error}")
    merged_items.extend(rss_items)

    bing_items = bing_news_client.get_news(
        keywords=keywords,
        market=market,
        symbol=symbol,
        theme=theme,
        limit=limit,
    ) or []
    if not bing_items and bing_news_client.last_error:
        source_errors.append(f"Bing News RSS：{bing_news_client.last_error}")
    merged_items.extend(bing_items)

    if include_gdelt and not merged_items:
        gdelt_items = gdelt_client.get_news(
            keywords=keywords,
            market=market,
            symbol=symbol,
            theme=theme,
            limit=limit,
        ) or []
        if not gdelt_items and gdelt_client.last_error:
            source_errors.append(f"GDELT：{gdelt_client.last_error}")
        merged_items.extend(gdelt_items)
    return {"items": _dedupe_news_items(merged_items), "source_errors": _dedupe_keywords(source_errors)}


def _build_layered_keyword_groups(
    market: str,
    exact_keywords: list[str] | None,
    medium_keywords: list[str] | None,
    search_keywords: list[str] | None,
) -> list[list[str]]:
    """按“主题优先、精确词补充、兜底词覆盖”生成真实新闻查询组。

    新闻处理顺序仍保持：先抓候选真实新闻，再按最近 24 小时过滤，
    最后按相关性排序筛选。这里仅扩展“抓候选”的入口，避免因为
    基金全名/代码过窄而漏掉真实的行业与板块新闻。
    """
    exact_group = _dedupe_keywords(exact_keywords or [])[:4]
    medium_group = _dedupe_keywords(medium_keywords or [])[:5]
    search_group = _dedupe_keywords(search_keywords or [])[:5]

    if market == "基金":
        ordered_groups = [medium_group, exact_group, search_group]
    else:
        ordered_groups = [search_group, medium_group, exact_group]

    deduped_groups: list[list[str]] = []
    seen_group_keys: set[tuple[str, ...]] = set()
    for group in ordered_groups:
        cleaned_group = [keyword for keyword in group if len(str(keyword).strip()) >= 2]
        group_key = tuple(cleaned_group)
        if cleaned_group and group_key not in seen_group_keys:
            deduped_groups.append(cleaned_group)
            seen_group_keys.add(group_key)
    return deduped_groups[:3]


def _collect_rss_news_batches(
    keyword_groups: list[list[str]],
    market: str,
    symbol: str | None,
    theme: str | None,
    limit_per_group: int = 4,
) -> dict[str, Any]:
    """按多组关键词聚合 RSS 新闻，并在 Google/Bing 之间做真实源回退。"""
    merged_items: list[dict[str, Any]] = []
    source_errors: list[str] = []
    for index, keywords in enumerate(keyword_groups):
        rss_result = _fetch_news_with_fallback(
            keywords=keywords,
            market=market,
            symbol=symbol,
            theme=theme,
            limit=limit_per_group,
            # GDELT 免费接口容易限流。多组查询时只在第一组尝试一次，
            # 其余组使用 Google/Bing RSS，避免把正常页面拖成“请求失败”。
            include_gdelt=index == 0,
        )
        source_errors.extend(rss_result["source_errors"])
        merged_items.extend(
            _normalize_news_item(
                item,
                market,
                symbol,
                theme,
                str(item.get("source_provider", "真实新闻聚合")),
                "real",
            )
            for item in rss_result["items"]
        )
    return {"items": _dedupe_news_items(merged_items), "source_errors": _dedupe_keywords(source_errors)}


def _normalize_news_item(
    item: dict[str, Any],
    market: str,
    symbol: str | None,
    theme: str | None,
    source_provider: str,
    data_source: str,
) -> dict[str, Any]:
    """统一新闻字段结构，避免页面层处理差异。"""
    return {
        "title": str(item.get("title", "未命名新闻")).strip() or "未命名新闻",
        "source": str(item.get("source", source_provider)).strip() or source_provider,
        "publish_time": str(item.get("publish_time", "")).strip(),
        "summary": str(item.get("summary", "暂无摘要")).strip() or "暂无摘要",
        "url": str(item.get("url", "")).strip(),
        "sentiment_hint": str(item.get("sentiment_hint", "")).strip(),
        "market": market,
        "theme": _normalize_theme_text(theme),
        "symbol": (symbol or "").strip(),
        "source_provider": source_provider,
        "data_source": data_source,
    }


def _has_meaningful_news_fields(item: dict[str, Any]) -> bool:
    """过滤缺少基本可追溯字段的新闻。"""
    title = str(item.get("title", "")).strip()
    source = str(item.get("source", "")).strip()
    publish_time = str(item.get("publish_time", "")).strip()
    url = str(item.get("url", "")).strip()
    return bool(title and (source or publish_time or url))


def _dedupe_news_items(news_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """按 URL 或 标题+时间 去重。"""
    seen_urls: set[str] = set()
    seen_title_time: set[tuple[str, str]] = set()
    deduped: list[dict[str, Any]] = []
    for item in news_items:
        url = str(item.get("url", "")).strip()
        title = str(item.get("title", "")).strip()
        publish_time = str(item.get("publish_time", "")).strip()
        title_time_key = (title, publish_time)

        if url and url in seen_urls:
            continue
        if not url and title_time_key in seen_title_time:
            continue
        if url:
            seen_urls.add(url)
        seen_title_time.add(title_time_key)
        deduped.append(item)
    return deduped


def _match_relevance_keywords(item: dict[str, Any], related_keywords: list[str] | None = None) -> dict[str, Any]:
    """提取新闻中命中的金融关键词与主题关键词。"""
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    matched_base_keywords: list[str] = []
    for keyword in sorted(FINANCIAL_RELEVANCE_KEYWORDS, key=len, reverse=True):
        normalized_keyword = keyword.lower()
        if normalized_keyword in text:
            matched_base_keywords.append(keyword)

    matched_theme_keywords: list[str] = []
    for keyword in sorted(related_keywords or [], key=len, reverse=True):
        normalized_keyword = keyword.lower()
        if normalized_keyword in text:
            matched_theme_keywords.append(keyword)

    strong_base_matches = [keyword for keyword in matched_base_keywords if keyword in STRONG_FINANCIAL_KEYWORDS]
    matched_keywords = _dedupe_keywords(matched_theme_keywords + matched_base_keywords)
    is_relevant = bool(matched_theme_keywords or strong_base_matches or len(matched_base_keywords) >= 2)
    if matched_theme_keywords:
        reason = f"命中当前基金主题/行业关键词：{', '.join(_dedupe_keywords(matched_theme_keywords))}"
    elif strong_base_matches:
        reason = f"命中高相关金融关键词：{', '.join(_dedupe_keywords(strong_base_matches))}"
    elif len(matched_base_keywords) >= 2:
        reason = f"命中多项金融关键词：{', '.join(_dedupe_keywords(matched_base_keywords))}"
    else:
        reason = "未命中当前基金主题关键词，也未命中足够的金融相关关键词"

    return {
        "is_relevant": is_relevant,
        "matched_keywords": matched_keywords,
        "matched_base_keywords": _dedupe_keywords(matched_base_keywords),
        "matched_theme_keywords": _dedupe_keywords(matched_theme_keywords),
        "reason": reason,
    }


def _score_news_relevance(
    item: dict[str, Any],
    exact_keywords: list[str] | None = None,
    medium_keywords: list[str] | None = None,
) -> dict[str, Any]:
    """对候选新闻做轻量相关性打分，允许中相关新闻保留。"""
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    exact_matches: list[str] = []
    medium_matches: list[str] = []
    base_matches: list[str] = []
    irrelevant_matches: list[str] = []
    score = 0.0
    title_text = str(item.get("title", "")).lower()

    for keyword in sorted(exact_keywords or [], key=len, reverse=True):
        normalized_keyword = keyword.lower()
        if len(normalized_keyword) >= 2 and normalized_keyword in text:
            exact_matches.append(keyword)
            score += 1.0 if len(keyword) >= 4 else 0.7

    for keyword in sorted(medium_keywords or [], key=len, reverse=True):
        normalized_keyword = keyword.lower()
        if len(normalized_keyword) >= 2 and normalized_keyword in text and keyword not in exact_matches:
            medium_matches.append(keyword)
            score += 0.45 if len(keyword) >= 4 else 0.3

    for keyword in sorted(FINANCIAL_RELEVANCE_KEYWORDS, key=len, reverse=True):
        normalized_keyword = keyword.lower()
        if normalized_keyword in text:
            base_matches.append(keyword)
            score += 0.18 if keyword in STRONG_FINANCIAL_KEYWORDS else 0.08

    for keyword in sorted(OBVIOUSLY_IRRELEVANT_KEYWORDS, key=len, reverse=True):
        normalized_keyword = keyword.lower()
        if normalized_keyword in title_text:
            irrelevant_matches.append(keyword)

    if irrelevant_matches and not exact_matches and score < 0.9:
        return {
            "is_relevant": False,
            "relevance_score": round(score, 3),
            "relevance_level": "低相关",
            "relevance_matched_keywords": _dedupe_keywords(exact_matches + medium_matches + base_matches),
            "relevance_exact_keywords": _dedupe_keywords(exact_matches),
            "relevance_theme_keywords": _dedupe_keywords(medium_matches),
            "relevance_base_keywords": _dedupe_keywords(base_matches),
            "relevance_irrelevant_keywords": _dedupe_keywords(irrelevant_matches),
            "relevance_reason": f"标题命中明显非投研场景词：{', '.join(_dedupe_keywords(irrelevant_matches[:4]))}",
        }

    matched_keywords = _dedupe_keywords(exact_matches + medium_matches + base_matches)
    if exact_matches:
        relevance_level = "强相关"
        reason = f"命中基金名称/代码/核心策略：{', '.join(_dedupe_keywords(exact_matches[:6]))}"
    elif medium_matches:
        relevance_level = "中相关"
        reason = f"命中基金主题/风格/板块：{', '.join(_dedupe_keywords(medium_matches[:8]))}"
    elif len(base_matches) >= 2:
        relevance_level = "中相关"
        reason = f"命中多项金融辅助关键词：{', '.join(_dedupe_keywords(base_matches[:8]))}"
    else:
        relevance_level = "低相关"
        reason = "仅命中极少量通用词，参考意义有限"

    return {
        "is_relevant": bool(exact_matches or medium_matches or score >= 0.35),
        "relevance_score": round(score, 3),
        "relevance_level": relevance_level,
        "relevance_matched_keywords": matched_keywords,
        "relevance_exact_keywords": _dedupe_keywords(exact_matches),
        "relevance_theme_keywords": _dedupe_keywords(medium_matches),
        "relevance_base_keywords": _dedupe_keywords(base_matches),
        "relevance_irrelevant_keywords": _dedupe_keywords(irrelevant_matches),
        "relevance_reason": reason,
    }


def _rank_and_filter_relevant_news(
    news_items: list[dict[str, Any]],
    exact_keywords: list[str] | None = None,
    medium_keywords: list[str] | None = None,
) -> dict[str, Any]:
    """先为新闻打相关性分，再保留较相关的真实新闻。"""
    filtered_items: list[dict[str, Any]] = []
    filtered_out_count = 0
    for item in news_items:
        relevance_result = _score_news_relevance(
            item,
            exact_keywords=exact_keywords,
            medium_keywords=medium_keywords,
        )
        if not relevance_result["is_relevant"]:
            filtered_out_count += 1
            continue
        filtered_items.append({**item, **relevance_result})
    filtered_items.sort(key=lambda item: item.get("relevance_score", 0), reverse=True)
    return {"items": filtered_items[:8], "filtered_out_count": filtered_out_count}


def _filter_recent_24h_news(news_items: list[dict[str, Any]]) -> dict[str, Any]:
    """只保留最近 24 小时内的新闻。

    顺序约定：
    1. 先从真实来源抓取候选新闻
    2. 再按最近 24 小时窗口做时间过滤
    3. 最后再进入相关性打分、排序与筛选
    """
    local_now = _get_local_now()
    time_window_start = local_now - timedelta(hours=24)
    filtered_items: list[dict[str, Any]] = []
    for item in news_items:
        publish_datetime = _parse_publish_time_to_local_datetime(item.get("publish_time", ""))
        within_last_24h = bool(publish_datetime and time_window_start <= publish_datetime <= local_now)
        if within_last_24h:
            filtered_items.append(
                {
                    **item,
                    "publish_time_local": publish_datetime.strftime("%Y-%m-%d %H:%M:%S %Z") if publish_datetime else "",
                    "within_last_24h": within_last_24h,
                }
            )
    return {
        "items": filtered_items,
        "current_time_local": local_now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "time_window_start": time_window_start.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "filtered_out_count": max(len(news_items) - len(filtered_items), 0),
    }


def get_related_news(
    market: str,
    symbol: str | None = None,
    theme: str | None = None,
    related_keywords: list[str] | None = None,
    search_keywords: list[str] | None = None,
    exact_keywords: list[str] | None = None,
    return_meta: bool = False,
) -> list[dict[str, Any]] | dict[str, Any]:
    """统一新闻获取入口，只返回真实新闻结果。

    处理顺序固定为：
    1. 抓取候选真实新闻
    2. 过滤掉缺少基本可追溯字段的新闻
    3. 按最近 24 小时过滤
    4. 再做相关性打分、排序和保留
    """
    symbol_text = (symbol or "").strip()
    theme_text = _normalize_theme_text(theme)
    real_news: list[dict[str, Any]] = []
    source_errors: list[str] = []

    try:
        if market == "基金":
            keywords = search_keywords or _extract_keywords(market, symbol_text, theme_text)
            keyword_groups = _build_layered_keyword_groups(
                market=market,
                exact_keywords=exact_keywords,
                medium_keywords=related_keywords,
                search_keywords=keywords,
            )
            rss_result = _collect_rss_news_batches(
                keyword_groups=keyword_groups or [keywords],
                market=market,
                symbol=symbol_text,
                theme=theme_text,
                limit_per_group=6,
            )
            rss_news = rss_result["items"]
            source_errors.extend(rss_result["source_errors"])
            real_news = [
                _normalize_news_item(
                    item,
                    market,
                    symbol_text,
                    theme_text,
                    str(item.get("source_provider", "Google News RSS")),
                    "real",
                )
                for item in rss_news
            ]
        if market in {"A股", "港股"}:
            keywords = search_keywords or _extract_keywords(market, symbol_text, theme_text)
            keyword_groups = _build_layered_keyword_groups(
                market=market,
                exact_keywords=exact_keywords,
                medium_keywords=related_keywords,
                search_keywords=keywords,
            )
            rss_result = _collect_rss_news_batches(
                keyword_groups=keyword_groups or [keywords],
                market=market,
                symbol=symbol_text,
                theme=theme_text,
                limit_per_group=6,
            )
            rss_news = rss_result["items"]
            source_errors.extend(rss_result["source_errors"])
            real_news = [
                _normalize_news_item(
                    item,
                    market,
                    symbol_text,
                    theme_text,
                    str(item.get("source_provider", "Google News RSS")),
                    "real",
                )
                for item in rss_news
            ]
        elif market == "美股":
            if symbol_text:
                av_news = alpha_client.get_news(
                    symbol=symbol_text,
                    theme=theme_text,
                    market=market,
                    limit=8,
                ) or []
                if not av_news and alpha_client.last_error:
                    source_errors.append(f"Alpha Vantage：{alpha_client.last_error}")
                sec_news = sec_edgar_client.get_recent_filings(
                    ticker=symbol_text,
                    market=market,
                    theme=theme_text or "公司公告",
                    limit=4,
                ) or []
                if not sec_news and sec_edgar_client.last_error:
                    source_errors.append(f"SEC EDGAR：{sec_edgar_client.last_error}")
                keywords = search_keywords or _extract_keywords(market, symbol_text, theme_text)
                keyword_groups = _build_layered_keyword_groups(
                    market=market,
                    exact_keywords=exact_keywords,
                    medium_keywords=related_keywords,
                    search_keywords=keywords,
                )
                google_result = _collect_rss_news_batches(
                    keyword_groups=keyword_groups or [keywords],
                    market=market,
                    symbol=symbol_text,
                    theme=theme_text,
                    limit_per_group=5,
                )
                source_errors.extend(google_result["source_errors"])
                merged_news = av_news + sec_news + google_result["items"]
            else:
                av_news = alpha_client.get_news(
                    theme="US stock market OR Nasdaq OR Wall Street",
                    market=market,
                    limit=8,
                ) or []
                if not av_news and alpha_client.last_error:
                    source_errors.append(f"Alpha Vantage：{alpha_client.last_error}")
                google_result = _collect_rss_news_batches(
                    keyword_groups=_get_us_market_news_keyword_groups(theme_text),
                    market=market,
                    symbol=symbol_text,
                    theme=theme_text,
                    limit_per_group=4,
                )
                source_errors.extend(google_result["source_errors"])
                google_overview_news = google_result["items"]
                merged_news = av_news + google_overview_news
            real_news = [
                _normalize_news_item(
                    item,
                    market,
                    symbol_text,
                    theme_text,
                    str(item.get("source_provider", "Alpha Vantage")),
                    "real",
                )
                for item in merged_news
            ]
        elif market == "黄金":
            av_news = alpha_client.get_news(
                symbol=symbol_text if symbol_text in {"GLD"} else None,
                theme=theme_text or "黄金",
                market=market,
                limit=8,
            ) or []
            if not av_news and alpha_client.last_error:
                source_errors.append(f"Alpha Vantage：{alpha_client.last_error}")
            if av_news:
                real_news = [
                    _normalize_news_item(item, market, symbol_text, theme_text, "Alpha Vantage", "real")
                    for item in av_news
                ]
            else:
                keywords = search_keywords or _extract_keywords(market, symbol_text, theme_text)
                keyword_groups = _build_layered_keyword_groups(
                    market=market,
                    exact_keywords=exact_keywords,
                    medium_keywords=related_keywords,
                    search_keywords=keywords,
                )
                rss_result = _collect_rss_news_batches(
                    keyword_groups=keyword_groups or [keywords],
                    market=market,
                    symbol=symbol_text,
                    theme=theme_text,
                    limit_per_group=6,
                )
                rss_news = rss_result["items"]
                source_errors.extend(rss_result["source_errors"])
                real_news = [
                    _normalize_news_item(
                        item,
                        market,
                        symbol_text,
                        theme_text,
                        str(item.get("source_provider", "Google News RSS")),
                        "real",
                    )
                    for item in rss_news
                ]
    except Exception as exc:
        source_errors.append(f"新闻聚合：{type(exc).__name__}: {exc}")
        real_news = []

    valid_real_news = [item for item in real_news if _has_meaningful_news_fields(item)]
    # 先保留所有候选真实新闻，再按最近 24 小时过滤，避免跨天新闻被过早丢弃。
    recent_news_result = _filter_recent_24h_news(valid_real_news)
    # 时间窗口过滤之后，再进入相关性评分、排序与筛选。
    relevance_result = _rank_and_filter_relevant_news(
        recent_news_result["items"],
        exact_keywords=exact_keywords,
        medium_keywords=related_keywords,
    )
    relevant_recent_news = _dedupe_news_items(relevance_result["items"])
    if return_meta:
        return {
            "items": relevant_recent_news,
            "filtered_out_count": relevance_result["filtered_out_count"],
            "time_filtered_count": recent_news_result["filtered_out_count"],
            "current_time_local": recent_news_result["current_time_local"],
            "time_window_start": recent_news_result["time_window_start"],
            "raw_candidate_count": len(real_news),
            "valid_candidate_count": len(valid_real_news),
            "recent_candidate_count": len(recent_news_result["items"]),
            "source_errors": _dedupe_keywords(source_errors),
        }
    return relevant_recent_news


def get_asset_news(asset_detail: dict[str, Any]) -> dict[str, Any]:
    """为页面层提供真实新闻列表与来源汇总。"""
    market = str(asset_detail.get("market", "")).strip()
    symbol = str(asset_detail.get("symbol", "")).strip()
    theme = _normalize_theme_text(asset_detail.get("theme"))
    relevance_profile = _build_relevance_profile(asset_detail)
    news_result = get_related_news(
        market=market,
        symbol=symbol,
        theme=theme,
        related_keywords=relevance_profile["medium_keywords"],
        search_keywords=relevance_profile["search_keywords"],
        exact_keywords=relevance_profile["exact_keywords"],
        return_meta=True,
    )
    news_items = news_result.get("items", [])
    provider_names = sorted({str(item.get("source_provider", "真实新闻")) for item in news_items if item.get("title")})
    source_errors = news_result.get("source_errors", [])
    raw_candidate_count = int(news_result.get("raw_candidate_count", 0))
    valid_candidate_count = int(news_result.get("valid_candidate_count", 0))
    recent_candidate_count = int(news_result.get("recent_candidate_count", 0))
    source_provider = " + ".join(provider_names) if provider_names else ("真实新闻源请求失败" if source_errors and raw_candidate_count == 0 else "暂未获取到真实新闻")
    data_source = "real" if news_items else "unavailable"
    fallback_used = False
    notice = ""
    if not news_items:
        if source_errors and raw_candidate_count == 0:
            notice = "真实新闻源请求失败，当前未能获取新闻。以下判断主要基于净值走势或板块方向，情绪判断可信度较低。"
        else:
            notice = "最近24小时内暂无高相关金融新闻，以下判断主要基于净值走势或板块方向，情绪判断可信度较低。"
    theme_debug = ", ".join(relevance_profile["theme_keywords"][:12]) or "暂无"
    relevance_debug = (
        f"当前系统时间：{news_result.get('current_time_local', _get_local_now().strftime('%Y-%m-%d %H:%M:%S %Z'))}"
        f"；最近24小时窗口起点：{news_result.get('time_window_start', '')}"
        f"；当前识别主题/策略关键词：{theme_debug}"
        f"；候选新闻 {raw_candidate_count} 条，有效候选 {valid_candidate_count} 条，"
        f"最近24小时候选 {recent_candidate_count} 条，展示 {len(news_items)} 条。"
        f"；因超出24小时窗口过滤 {int(news_result.get('time_filtered_count', 0))} 条，"
        f"因相关性不足过滤 {int(news_result.get('filtered_out_count', 0))} 条。"
    )
    if source_errors and not news_items:
        readable_errors = [_shorten_text(error) for error in source_errors[:3]]
        relevance_debug = f"{relevance_debug} 新闻源错误：{' | '.join(readable_errors)}"
    return {
        "items": news_items,
        "source_provider": source_provider,
        "data_source": data_source,
        "fallback_used": fallback_used,
        "notice": notice,
        "relevance_keywords": relevance_profile["theme_keywords"],
        "search_keywords": relevance_profile["search_keywords"],
        "filtered_out_count": news_result.get("filtered_out_count", 0),
        "time_filtered_count": news_result.get("time_filtered_count", 0),
        "current_time_local": news_result.get("current_time_local", ""),
        "time_window_start": news_result.get("time_window_start", ""),
        "raw_candidate_count": raw_candidate_count,
        "valid_candidate_count": valid_candidate_count,
        "recent_candidate_count": recent_candidate_count,
        "source_errors": source_errors,
        "relevance_debug": relevance_debug,
    }
