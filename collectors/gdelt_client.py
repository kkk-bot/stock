"""GDELT DOC 2.1 真实新闻客户端。"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import requests


class GdeltClient:
    """封装 GDELT DOC 2.1 新闻查询。"""

    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

    def __init__(self) -> None:
        self.last_error = ""

    def _build_query_text(self, keywords: list[str] | str) -> str:
        """根据关键词构建 GDELT 查询文本。"""
        if isinstance(keywords, str):
            normalized = keywords.strip()
            return normalized or "财经"
        normalized_items = [item.strip() for item in keywords if str(item).strip()]
        if not normalized_items:
            return "财经"
        return " OR ".join(normalized_items[:5])

    def _format_seen_date(self, raw_value: Any) -> str:
        """将 GDELT seendate 转成通用时间字符串。"""
        text = str(raw_value or "").strip()
        if not text:
            return ""
        try:
            parsed = datetime.strptime(text, "%Y%m%dT%H%M%SZ")
            return parsed.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            pass
        try:
            parsed = datetime.strptime(text, "%Y%m%d%H%M%S")
            return parsed.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            return text

    def get_news(
        self,
        keywords: list[str] | str,
        market: str,
        symbol: str | None = None,
        theme: str | None = None,
        limit: int = 8,
    ) -> list[dict[str, Any]] | None:
        """按关键词获取最近 24 小时新闻并返回统一结构。"""
        self.last_error = ""
        query_text = self._build_query_text(keywords)
        params = {
            "query": query_text,
            "mode": "ArtList",
            "format": "json",
            "timespan": "24h",
            "maxrecords": max(1, min(limit, 50)),
            "sort": "HybridRel",
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0 (compatible; MultiMarketAnalyzer/1.0)"},
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            return None

        articles = payload.get("articles", []) if isinstance(payload, dict) else []
        if not articles:
            return None

        results: list[dict[str, Any]] = []
        for item in articles[: max(1, limit)]:
            title = str(item.get("title", "")).strip()
            url = str(item.get("url", "")).strip()
            domain = str(item.get("domain", "")).strip()
            source = str(item.get("sourceCollection", "")).strip() or domain or "GDELT"
            results.append(
                {
                    "title": title or "未命名新闻",
                    "source": source,
                    "publish_time": self._format_seen_date(item.get("seendate")),
                    "summary": str(item.get("socialimage", "") or item.get("url", "") or "暂无摘要").strip(),
                    "url": url,
                    "sentiment_hint": "",
                    "market": market,
                    "theme": theme or query_text,
                    "symbol": symbol or "",
                    "source_provider": "GDELT",
                    "data_source": "real",
                }
            )

        return results or None
