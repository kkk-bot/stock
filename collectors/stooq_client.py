"""Stooq 免费日线数据客户端。"""

from __future__ import annotations

from io import StringIO
from typing import Any

import pandas as pd
import requests


class StooqClient:
    """读取 Stooq 日线 CSV，作为美股无 API Key fallback。"""

    BASE_URL = "https://stooq.com/q/d/l/"

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
        """将美股代码转换为 Stooq symbol。"""
        normalized = str(symbol or "").strip().lower()
        if not normalized:
            return ""
        if "." not in normalized:
            return f"{normalized}.us"
        return normalized

    def _fetch_daily_dataframe(self, symbol: str) -> pd.DataFrame | None:
        """获取 Stooq 日线 CSV。"""
        self.last_error = ""
        stooq_symbol = self._normalize_symbol(symbol)
        if not stooq_symbol:
            return None
        try:
            response = requests.get(
                self.BASE_URL,
                params={"s": stooq_symbol, "i": "d"},
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0 (compatible; MultiMarketAnalyzer/1.0)"},
            )
            response.raise_for_status()
            if "No data" in response.text or not response.text.strip():
                self.last_error = f"Stooq 无数据：{stooq_symbol}"
                return None
            dataframe = pd.read_csv(StringIO(response.text))
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            return None

        required_columns = {"Date", "Open", "High", "Low", "Close", "Volume"}
        if dataframe.empty or not required_columns.issubset(dataframe.columns):
            self.last_error = f"Stooq 返回字段异常：{stooq_symbol}"
            return None
        return dataframe.sort_values("Date").reset_index(drop=True)

    def _rows_from_dataframe(self, dataframe: pd.DataFrame) -> list[dict[str, Any]]:
        """转换为统一 K 线结构。"""
        rows: list[dict[str, Any]] = []
        for _, row in dataframe.iterrows():
            rows.append(
                {
                    "datetime": str(row.get("Date", "")),
                    "open": self._safe_float(row.get("Open")),
                    "high": self._safe_float(row.get("High")),
                    "low": self._safe_float(row.get("Low")),
                    "close": self._safe_float(row.get("Close")),
                    "volume": self._safe_float(row.get("Volume")),
                    "source_provider": "Stooq",
                    "data_source": "real",
                }
            )
        return rows

    def _resample_rows(self, rows: list[dict[str, Any]], interval: str) -> list[dict[str, Any]]:
        """将日线聚合为周线或月线。"""
        if interval == "1day" or not rows:
            return rows
        dataframe = pd.DataFrame(rows).copy()
        dataframe["date"] = pd.to_datetime(dataframe["datetime"], errors="coerce")
        dataframe = dataframe.dropna(subset=["date"]).set_index("date").sort_index()
        if dataframe.empty:
            return rows

        rule = "W-FRI" if interval == "1week" else "M" if interval == "1month" else None
        if rule is None:
            return rows
        resampled = dataframe.resample(rule).agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )
        resampled = resampled.dropna(subset=["open", "high", "low", "close"])
        output_rows: list[dict[str, Any]] = []
        for date_index, row in resampled.iterrows():
            output_rows.append(
                {
                    "datetime": date_index.strftime("%Y-%m-%d"),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]),
                    "source_provider": "Stooq",
                    "data_source": "real",
                }
            )
        return output_rows

    def get_kline(self, symbol: str, interval: str = "1day", limit: int = 120) -> list[dict[str, Any]] | None:
        """获取美股 K 线。"""
        dataframe = self._fetch_daily_dataframe(symbol)
        if dataframe is None or dataframe.empty:
            return None
        rows = self._rows_from_dataframe(dataframe)
        rows = self._resample_rows(rows, interval)
        return rows[-limit:] if rows else None

    def get_asset_detail(self, market: str, symbol: str, asset_meta: dict[str, Any]) -> dict[str, Any] | None:
        """基于最新日线构造美股资产详情。"""
        rows = self.get_kline(symbol, "1day", limit=2)
        if not rows:
            return None
        latest = rows[-1]
        previous = rows[-2] if len(rows) > 1 else latest
        latest_close = self._safe_float(latest.get("close"))
        previous_close = self._safe_float(previous.get("close"), latest_close)
        change = latest_close - previous_close
        pct_change = 0.0 if previous_close == 0 else change / previous_close * 100
        amplitude = 0.0 if previous_close == 0 else (
            self._safe_float(latest.get("high")) - self._safe_float(latest.get("low"))
        ) / previous_close * 100
        return {
            "symbol": str(symbol or "").strip().upper(),
            "name": asset_meta.get("name", str(symbol or "").strip().upper()),
            "market": market,
            "asset_type": asset_meta.get("asset_type", "美股资产"),
            "theme": asset_meta.get("theme", "美股市场"),
            "price": round(latest_close, 4),
            "change": round(change, 4),
            "pct_change": round(pct_change, 4),
            "volume": self._safe_float(latest.get("volume")),
            "turnover": 0.0,
            "amplitude": round(amplitude, 4),
            "risk_level": asset_meta.get("risk_level", "未知"),
            "description": asset_meta.get("description", "基于 Stooq 日线数据生成的美股行情。"),
            "source_provider": "Stooq",
            "data_source": "real",
            "updated_at": str(latest.get("datetime", "")),
        }
