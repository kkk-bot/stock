"""Google News RSS 轻量新闻客户端。"""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import quote_plus

import requests


class GoogleNewsRSSClient:
    """封装 Google News RSS 请求与解析逻辑。"""

    BASE_URL = "https://news.google.com/rss/search"

    def __init__(self, language: str = "zh-CN", region: str = "CN") -> None:
        self.language = language
        self.region = region

    def _build_query_text(self, keywords: list[str] | str) -> str:
        """根据关键词构建搜索文本。"""
        if isinstance(keywords, str):
            normalized = keywords.strip()
            return normalized or "财经"
        normalized_items = [item.strip() for item in keywords if str(item).strip()]
        if not normalized_items:
            return "财经"
        return " OR ".join(normalized_items[:4])

    def _strip_html(self, raw_text: str) -> str:
        """移除 HTML 标签并做基础清理。"""
        if not raw_text:
            return ""
        text = html.unescape(raw_text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _parse_source_text(self, item: ET.Element, title: str) -> str:
        """优先从 source 节点读取来源，缺失时从标题兜底推断。"""
        source_element = item.find("source")
        if source_element is not None and (source_element.text or "").strip():
            return source_element.text.strip()
        if " - " in title:
            return title.split(" - ")[-1].strip()
        return "Google News RSS"

    def get_news(
        self,
        keywords: list[str] | str,
        market: str,
        symbol: str | None = None,
        theme: str | None = None,
        limit: int = 8,
    ) -> list[dict[str, Any]] | None:
        """按关键词获取新闻并返回统一结构。"""
        query_text = self._build_query_text(keywords)
        query = quote_plus(query_text)
        request_url = (
            f"{self.BASE_URL}?q={query}&hl={self.language}&gl={self.region}&ceid={self.region}:{self.language}"
        )

        try:
            response = requests.get(
                request_url,
                timeout=8,
                headers={"User-Agent": "Mozilla/5.0 (compatible; MultiMarketAnalyzer/1.0)"},
            )
            response.raise_for_status()
            root = ET.fromstring(response.text)
        except Exception:
            return None

        channel = root.find("channel")
        if channel is None:
            return None

        news_items: list[dict[str, Any]] = []
        for item in channel.findall("item")[: max(1, limit)]:
            title = (item.findtext("title") or "").strip()
            description = self._strip_html(item.findtext("description") or "")
            link = (item.findtext("link") or "").strip()
            publish_time = (item.findtext("pubDate") or "").strip()
            source = self._parse_source_text(item, title)
            cleaned_title = title.strip()
            if " - " in cleaned_title:
                cleaned_title = cleaned_title.rsplit(" - ", 1)[0].strip()

            news_items.append(
                {
                    "title": cleaned_title or "未命名新闻",
                    "source": source,
                    "publish_time": publish_time,
                    "summary": description or "暂无摘要",
                    "url": link,
                    "sentiment_hint": "",
                    "market": market,
                    "theme": theme or query_text,
                    "symbol": symbol or "",
                    "source_provider": "Google News RSS",
                    "data_source": "real",
                }
            )

        return news_items or None
