"""Alpha Vantage 客户端封装。"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

from config import ALPHA_VANTAGE_API_KEY


class AlphaVantageClient:
    """封装 Alpha Vantage 请求逻辑。"""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or ALPHA_VANTAGE_API_KEY

    @property
    def is_available(self) -> bool:
        """判断当前客户端是否可用。"""
        return bool(self.api_key)

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """安全转换为浮点数。"""
        try:
            if value in (None, "", "None"):
                return default
            return float(str(value).replace("%", ""))
        except Exception:
            return default

    def _safe_str(self, value: Any, default: str = "") -> str:
        """安全转换为字符串。"""
        if value in (None, "None"):
            return default
        return str(value)

    def _request(self, params: dict[str, Any]) -> dict[str, Any]:
        """发起请求并返回 JSON。"""
        if not self.is_available:
            raise ValueError("未配置 Alpha Vantage API Key。")
        response = requests.get(self.BASE_URL, params={**params, "apikey": self.api_key}, timeout=8)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Alpha Vantage 返回格式异常。")
        if "Note" in payload or "Error Message" in payload or "Information" in payload:
            raise ValueError(str(payload))
        return payload

    def get_asset_detail(self, market: str, symbol: str, asset_meta: dict[str, Any]) -> dict[str, Any] | None:
        """获取美股或黄金详情。"""
        try:
            if market == "美股":
                payload = self._request({"function": "GLOBAL_QUOTE", "symbol": symbol})
                quote = payload.get("Global Quote", {})
                if not quote:
                    return None
                price = self._safe_float(quote.get("05. price"))
                change = self._safe_float(quote.get("09. change"))
                pct_change = self._safe_float(quote.get("10. change percent"))
                return {
                    "symbol": symbol,
                    "name": asset_meta["name"],
                    "market": market,
                    "asset_type": asset_meta["asset_type"],
                    "theme": asset_meta["theme"],
                    "price": price,
                    "change": change,
                    "pct_change": pct_change,
                    "volume": self._safe_float(quote.get("06. volume")),
                    "turnover": 0.0,
                    "amplitude": 0.0,
                    "risk_level": asset_meta["risk_level"],
                    "description": asset_meta["description"],
                    "source_provider": "Alpha Vantage",
                    "data_source": "real",
                    "updated_at": self._safe_str(quote.get("07. latest trading day")),
                }
            if market == "黄金":
                return self._get_gold_detail(asset_meta)
        except Exception:
            return None
        return None

    def get_kline(self, market: str, symbol: str, interval: str, asset_meta: dict[str, Any]) -> list[dict[str, Any]] | None:
        """获取 K 线数据。"""
        try:
            if market == "美股":
                function_map = {"1day": "TIME_SERIES_DAILY", "1week": "TIME_SERIES_WEEKLY", "1month": "TIME_SERIES_MONTHLY"}
                payload = self._request({"function": function_map.get(interval, "TIME_SERIES_DAILY"), "symbol": symbol})
                series_key = next((key for key in payload.keys() if "Time Series" in key), None)
                if not series_key:
                    return None
                return self._parse_series(payload[series_key], "Alpha Vantage")
            if market == "黄金":
                function_map = {"1day": "FX_DAILY", "1week": "FX_WEEKLY", "1month": "FX_MONTHLY"}
                payload = self._request(
                    {
                        "function": function_map.get(interval, "FX_DAILY"),
                        "from_symbol": "XAU",
                        "to_symbol": "USD",
                    }
                )
                series_key = next((key for key in payload.keys() if "Time Series FX" in key), None)
                if not series_key:
                    return None
                return self._parse_series(payload[series_key], "Alpha Vantage")
        except Exception:
            return None
        return None

    def get_related_news(self, symbol: str, theme: str | None = None) -> list[dict[str, Any]] | None:
        """获取相关新闻（兼容旧签名）。"""
        return self.get_news(symbol=symbol, theme=theme)

    def _format_publish_time(self, raw_value: Any) -> str:
        """格式化发布时间。"""
        text = self._safe_str(raw_value)
        if not text:
            return ""
        try:
            parsed = datetime.strptime(text, "%Y%m%dT%H%M%S")
            return parsed.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return text

    def get_news(
        self,
        symbol: str | None = None,
        theme: str | None = None,
        market: str | None = None,
        limit: int = 8,
    ) -> list[dict[str, Any]] | None:
        """获取 Alpha Vantage 新闻并映射到统一字段。"""
        try:
            params: dict[str, Any] = {"function": "NEWS_SENTIMENT", "limit": max(1, min(limit, 50))}
            symbol_text = (symbol or "").strip().upper()
            if symbol_text in {"NVDA", "QQQ", "GLD"}:
                params["tickers"] = symbol_text
            else:
                params["keywords"] = theme or symbol_text or "macro"
            payload = self._request(params)
            news_feed = payload.get("feed", [])
            if not news_feed:
                return None
            results: list[dict[str, Any]] = []
            for item in news_feed:
                results.append(
                    {
                        "title": self._safe_str(item.get("title"), "未命名新闻"),
                        "source": self._safe_str(item.get("source"), "Alpha Vantage"),
                        "publish_time": self._format_publish_time(item.get("time_published")),
                        "summary": self._safe_str(item.get("summary"), "暂无摘要"),
                        "url": self._safe_str(item.get("url")),
                        "sentiment_hint": "",
                        "market": market or "",
                        "theme": theme or "",
                        "symbol": symbol or "",
                        "source_provider": "Alpha Vantage",
                        "data_source": "real",
                    }
                )
            return results
        except Exception:
            return None

    def _get_gold_detail(self, asset_meta: dict[str, Any]) -> dict[str, Any] | None:
        """获取黄金详情。"""
        klines = self.get_kline("黄金", "XAUUSD", "1day", asset_meta)
        if not klines or len(klines) < 2:
            return None
        latest = klines[-1]
        previous = klines[-2]
        latest_close = self._safe_float(latest.get("close"))
        previous_close = self._safe_float(previous.get("close"))
        change = latest_close - previous_close
        pct_change = 0.0 if previous_close == 0 else change / previous_close * 100
        return {
            "symbol": "XAUUSD",
            "name": asset_meta["name"],
            "market": "黄金",
            "asset_type": asset_meta["asset_type"],
            "theme": asset_meta["theme"],
            "price": latest_close,
            "change": round(change, 4),
            "pct_change": round(pct_change, 4),
            "volume": self._safe_float(latest.get("volume")),
            "turnover": 0.0,
            "amplitude": round(self._safe_float(latest.get("high")) - self._safe_float(latest.get("low")), 4),
            "risk_level": asset_meta["risk_level"],
            "description": asset_meta["description"],
            "source_provider": "Alpha Vantage",
            "data_source": "real",
            "updated_at": self._safe_str(latest.get("datetime")),
        }

    def _parse_series(self, raw_series: dict[str, dict[str, Any]], provider_name: str) -> list[dict[str, Any]]:
        """解析时序数据。"""
        rows: list[dict[str, Any]] = []
        for datetime_key, values in sorted(raw_series.items()):
            rows.append(
                {
                    "datetime": datetime_key,
                    "open": self._safe_float(values.get("1. open", values.get("open"))),
                    "high": self._safe_float(values.get("2. high", values.get("high"))),
                    "low": self._safe_float(values.get("3. low", values.get("low"))),
                    "close": self._safe_float(values.get("4. close", values.get("close"))),
                    "volume": self._safe_float(values.get("5. volume", values.get("volume"))),
                    "source_provider": provider_name,
                    "data_source": "real",
                }
            )
        return rows
