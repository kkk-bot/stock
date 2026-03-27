"""统一新闻获取接口。"""

from __future__ import annotations

from typing import Any

from collectors.alpha_vantage_client import AlphaVantageClient
from collectors.google_news_rss import GoogleNewsRSSClient
from collectors.mock_data import get_mock_related_news
from collectors.sec_edgar_client import SecEdgarClient


alpha_client = AlphaVantageClient()
google_news_client = GoogleNewsRSSClient()
sec_edgar_client = SecEdgarClient()


def _normalize_theme_text(theme: str | list[str] | None) -> str:
    """规范化主题字段。"""
    if isinstance(theme, list):
        return " / ".join(str(item).strip() for item in theme if str(item).strip())
    return str(theme or "").strip()


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
    if theme_text:
        return [item.strip() for item in theme_text.replace("/", " ").split() if item.strip()][:4] or [theme_text]
    market_default_map = {
        "A股": ["A股", "沪深股市"],
        "港股": ["港股", "香港股市"],
        "美股": ["美股", "纳斯达克"],
        "黄金": ["黄金", "国际金价"],
    }
    return market_default_map.get(market, ["财经"])


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


def get_related_news(market: str, symbol: str | None = None, theme: str | None = None) -> list[dict[str, Any]]:
    """统一新闻获取入口，按市场路由真实来源，失败后回退 mock。"""
    symbol_text = (symbol or "").strip()
    theme_text = _normalize_theme_text(theme)
    real_news: list[dict[str, Any]] = []

    try:
        if market in {"A股", "港股"}:
            keywords = _extract_keywords(market, symbol_text, theme_text)
            rss_news = google_news_client.get_news(
                keywords=keywords,
                market=market,
                symbol=symbol_text,
                theme=theme_text,
                limit=10,
            ) or []
            real_news = [
                _normalize_news_item(item, market, symbol_text, theme_text, "Google News RSS", "real")
                for item in rss_news
            ]
        elif market == "美股":
            av_news = alpha_client.get_news(
                symbol=symbol_text,
                theme=theme_text,
                market=market,
                limit=8,
            ) or []
            sec_news = sec_edgar_client.get_recent_filings(
                ticker=symbol_text,
                market=market,
                theme=theme_text or "公司公告",
                limit=4,
            ) or []
            merged_news = av_news + sec_news
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
            if av_news:
                real_news = [
                    _normalize_news_item(item, market, symbol_text, theme_text, "Alpha Vantage", "real")
                    for item in av_news
                ]
            else:
                keywords = _extract_keywords(market, symbol_text, theme_text)
                rss_news = google_news_client.get_news(
                    keywords=keywords,
                    market=market,
                    symbol=symbol_text,
                    theme=theme_text,
                    limit=10,
                ) or []
                real_news = [
                    _normalize_news_item(item, market, symbol_text, theme_text, "Google News RSS", "real")
                    for item in rss_news
                ]
    except Exception:
        real_news = []

    deduped_real_news = _dedupe_news_items(real_news)
    if deduped_real_news:
        return deduped_real_news

    mock_news = get_mock_related_news(market, symbol_text, theme_text)
    normalized_mock_news = [
        _normalize_news_item(item, market, symbol_text, theme_text, "mock", "mock")
        for item in mock_news
    ]
    return _dedupe_news_items(normalized_mock_news)


def get_asset_news(asset_detail: dict[str, Any]) -> dict[str, Any]:
    """为页面层提供新闻列表与来源汇总。"""
    market = str(asset_detail.get("market", "")).strip()
    symbol = str(asset_detail.get("symbol", "")).strip()
    theme = _normalize_theme_text(asset_detail.get("theme"))
    news_items = get_related_news(market=market, symbol=symbol, theme=theme)
    provider_names = sorted({str(item.get("source_provider", "mock")) for item in news_items if item.get("title")})
    source_provider = " + ".join(provider_names) if provider_names else "mock"
    data_source = "real" if any(item.get("data_source") == "real" for item in news_items) else "mock"
    fallback_used = data_source != "real"
    return {
        "items": news_items,
        "source_provider": source_provider,
        "data_source": data_source,
        "fallback_used": fallback_used,
    }
