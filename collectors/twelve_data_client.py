"""Twelve Data 客户端封装。"""

from __future__ import annotations

from typing import Any

import requests

from config import TWELVE_DATA_API_KEY


class TwelveDataClient:
    """封装 Twelve Data 请求逻辑。"""

    BASE_URL = "https://api.twelvedata.com"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or TWELVE_DATA_API_KEY

    @property
    def is_available(self) -> bool:
        """判断当前客户端是否可用。"""
        return bool(self.api_key)

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """安全转换为浮点数。"""
        try:
            if value in (None, "", "None"):
                return default
            return float(value)
        except Exception:
            return default

    def _safe_str(self, value: Any, default: str = "") -> str:
        """安全转换为字符串。"""
        if value in (None, "None"):
            return default
        return str(value)

    def _request(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        """发起请求并返回 JSON。"""
        if not self.is_available:
            raise ValueError("未配置 Twelve Data API Key。")
        response = requests.get(f"{self.BASE_URL}/{endpoint}", params={**params, "apikey": self.api_key}, timeout=8)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Twelve Data 返回格式异常。")
        if payload.get("status") == "error":
            raise ValueError(str(payload))
        return payload

    def get_asset_detail(self, market: str, symbol: str, asset_meta: dict[str, Any]) -> dict[str, Any] | None:
        """获取港股、美股或黄金详情。"""
        try:
            payload = self._request("quote", {"symbol": symbol})
            close_price = self._safe_float(payload.get("close"))
            previous_close = self._safe_float(payload.get("previous_close"))
            change = close_price - previous_close
            pct_change = 0.0 if previous_close == 0 else change / previous_close * 100
            return {
                "symbol": symbol,
                "name": self._safe_str(payload.get("name"), asset_meta["name"]),
                "market": market,
                "asset_type": asset_meta["asset_type"],
                "theme": asset_meta["theme"],
                "price": close_price,
                "change": round(change, 4),
                "pct_change": round(pct_change, 4),
                "volume": self._safe_float(payload.get("volume")),
                "turnover": 0.0,
                "amplitude": 0.0,
                "risk_level": asset_meta["risk_level"],
                "description": asset_meta["description"],
                "source_provider": "Twelve Data",
                "data_source": "real",
                "updated_at": self._safe_str(payload.get("datetime")),
            }
        except Exception:
            return None

    def get_kline(self, symbol: str, interval: str) -> list[dict[str, Any]] | None:
        """获取 K 线数据。"""
        try:
            payload = self._request("time_series", {"symbol": symbol, "interval": interval, "outputsize": 60, "order": "asc"})
            values = payload.get("values", [])
            if not values:
                return None
            rows: list[dict[str, Any]] = []
            for value in values:
                rows.append(
                    {
                        "datetime": self._safe_str(value.get("datetime")),
                        "open": self._safe_float(value.get("open")),
                        "high": self._safe_float(value.get("high")),
                        "low": self._safe_float(value.get("low")),
                        "close": self._safe_float(value.get("close")),
                        "volume": self._safe_float(value.get("volume")),
                        "source_provider": "Twelve Data",
                        "data_source": "real",
                    }
                )
            return rows
        except Exception:
            return None
