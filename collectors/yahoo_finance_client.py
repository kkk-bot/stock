"""Yahoo Finance 轻量行情客户端。

该客户端作为美股无 API Key 的真实行情兜底来源，只读取公开 chart JSON，
不在页面层暴露外部请求细节。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import requests


class YahooFinanceClient:
    """通过 Yahoo Finance chart 接口获取美股行情和 K 线。"""

    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

    def __init__(self) -> None:
        self.last_error = ""

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """安全转换浮点数。"""
        try:
            if value in (None, "", "None"):
                return default
            return float(value)
        except Exception:
            return default

    def _normalize_symbol(self, symbol: str) -> str:
        """规范化美股代码。"""
        return str(symbol or "").strip().upper()

    def _symbol_variants(self, symbol: str) -> list[str]:
        """生成 Yahoo Finance 可识别的美股代码候选。

        部分美股类别股在常见输入里写作 BRK.B / BF.B，但 Yahoo Finance
        chart 接口使用 BRK-B / BF-B。这里只在客户端层补候选，不改变页面主流程。
        """
        normalized = self._normalize_symbol(symbol)
        variants = [normalized] if normalized else []
        if "." in normalized:
            variants.append(normalized.replace(".", "-"))
        return list(dict.fromkeys(variants))

    def _interval_params(self, interval: str) -> tuple[str, str]:
        """将项目周期映射为 Yahoo Finance 查询参数。"""
        if interval == "1week":
            return "2y", "1wk"
        if interval == "1month":
            return "5y", "1mo"
        return "6mo", "1d"

    def _request_chart(self, symbol: str, range_value: str, interval: str) -> dict[str, Any] | None:
        """请求 Yahoo Finance chart JSON。"""
        self.last_error = ""
        symbol_variants = self._symbol_variants(symbol)
        if not symbol_variants:
            self.last_error = "Yahoo Finance symbol 为空。"
            return None

        errors: list[str] = []
        for candidate_symbol in symbol_variants:
            try:
                response = requests.get(
                    self.BASE_URL.format(symbol=candidate_symbol),
                    params={"range": range_value, "interval": interval, "includePrePost": "false"},
                    timeout=10,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; MultiMarketAnalyzer/1.0)"},
                )
                response.raise_for_status()
                payload = response.json()
            except Exception as exc:
                errors.append(f"{candidate_symbol}: {type(exc).__name__}: {exc}")
                continue

            chart = payload.get("chart", {})
            error = chart.get("error")
            if error:
                errors.append(f"{candidate_symbol}: {error}")
                continue
            results = chart.get("result") or []
            if not results:
                errors.append(f"{candidate_symbol}: 无数据")
                continue
            result = results[0]
            quote_items = (result.get("indicators") or {}).get("quote") or []
            timestamps = result.get("timestamp") or []
            if not timestamps or not quote_items:
                errors.append(f"{candidate_symbol}: K线字段为空")
                continue
            result["_resolved_symbol"] = candidate_symbol
            return result

        self.last_error = "；".join(errors) or f"Yahoo Finance 无数据：{symbol}"
        return None

    def _timestamp_to_date(self, timestamp: Any) -> str:
        """将时间戳转换为日期字符串。"""
        try:
            return datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d")
        except Exception:
            return ""

    def get_kline(self, symbol: str, interval: str = "1day", limit: int = 120) -> list[dict[str, Any]] | None:
        """获取美股 K 线数据。"""
        range_value, yahoo_interval = self._interval_params(interval)
        result = self._request_chart(symbol, range_value, yahoo_interval)
        if not result:
            return None

        timestamps = result.get("timestamp") or []
        quote_items = (result.get("indicators") or {}).get("quote") or []
        if not timestamps or not quote_items:
            self.last_error = f"Yahoo Finance K线字段为空：{symbol}"
            return None

        quote = quote_items[0]
        opens = quote.get("open") or []
        highs = quote.get("high") or []
        lows = quote.get("low") or []
        closes = quote.get("close") or []
        volumes = quote.get("volume") or []

        rows: list[dict[str, Any]] = []
        for index, timestamp in enumerate(timestamps):
            close = self._safe_float(closes[index] if index < len(closes) else None)
            if close <= 0:
                continue
            rows.append(
                {
                    "datetime": self._timestamp_to_date(timestamp),
                    "open": self._safe_float(opens[index] if index < len(opens) else close, close),
                    "high": self._safe_float(highs[index] if index < len(highs) else close, close),
                    "low": self._safe_float(lows[index] if index < len(lows) else close, close),
                    "close": close,
                    "volume": self._safe_float(volumes[index] if index < len(volumes) else 0),
                    "source_provider": "Yahoo Finance",
                    "data_source": "real",
                }
            )

        if not rows:
            self.last_error = f"Yahoo Finance 无有效K线：{symbol}"
            return None
        return rows[-limit:]

    def get_asset_detail(self, market: str, symbol: str, asset_meta: dict[str, Any]) -> dict[str, Any] | None:
        """获取美股基础行情详情。"""
        result = self._request_chart(symbol, "1mo", "1d")
        if not result:
            return None

        meta = result.get("meta") or {}
        rows = self.get_kline(symbol, "1day", limit=2)
        latest = rows[-1] if rows else {}
        previous = rows[-2] if rows and len(rows) > 1 else latest

        current_price = self._safe_float(meta.get("regularMarketPrice"), self._safe_float(latest.get("close")))
        previous_close = self._safe_float(meta.get("chartPreviousClose"), self._safe_float(previous.get("close"), current_price))
        change = current_price - previous_close
        pct_change = 0.0 if previous_close == 0 else change / previous_close * 100

        day_high = self._safe_float(meta.get("regularMarketDayHigh"), self._safe_float(latest.get("high"), current_price))
        day_low = self._safe_float(meta.get("regularMarketDayLow"), self._safe_float(latest.get("low"), current_price))
        amplitude = 0.0 if previous_close == 0 else (day_high - day_low) / previous_close * 100

        market_time = meta.get("regularMarketTime")
        updated_at = self._timestamp_to_date(market_time) if market_time else str(latest.get("datetime", ""))
        normalized_symbol = meta.get("symbol") or result.get("_resolved_symbol") or self._normalize_symbol(symbol)
        if current_price <= 0 and latest:
            current_price = self._safe_float(latest.get("close"))
        if current_price <= 0:
            self.last_error = f"Yahoo Finance 无有效价格：{normalized_symbol}"
            return None

        return {
            "symbol": normalized_symbol,
            "name": meta.get("longName") or meta.get("shortName") or asset_meta.get("name", normalized_symbol),
            "market": market,
            "asset_type": asset_meta.get("asset_type", "美股资产"),
            "theme": asset_meta.get("theme", "美股市场"),
            "price": round(current_price, 4),
            "change": round(change, 4),
            "pct_change": round(pct_change, 4),
            "volume": self._safe_float(meta.get("regularMarketVolume"), self._safe_float(latest.get("volume"))),
            "turnover": 0.0,
            "amplitude": round(amplitude, 4),
            "risk_level": asset_meta.get("risk_level", "较高"),
            "description": asset_meta.get("description", f"{normalized_symbol} 的 Yahoo Finance 公开行情数据。"),
            "source_provider": "Yahoo Finance",
            "data_source": "real",
            "updated_at": updated_at,
        }
