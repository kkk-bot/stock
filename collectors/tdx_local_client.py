"""通达信本地 vipdoc 日线数据读取客户端。"""

from __future__ import annotations

from pathlib import Path
import struct
from typing import Any

import pandas as pd

from config import TDX_VIPDOC_DIR


class TdxLocalClient:
    """读取通达信客户端本地 `.day` 日线文件。

    该模块只读取用户本机已存在的数据文件，不自动下载、不伪造数据。
    常见路径示例：`/path/to/tdx/vipdoc/sh/lday/sh600000.day`。
    """

    RECORD_SIZE = 32

    def __init__(self, vipdoc_dir: str | None = None) -> None:
        self.vipdoc_dir = Path(vipdoc_dir or TDX_VIPDOC_DIR).expanduser() if (vipdoc_dir or TDX_VIPDOC_DIR) else None

    @property
    def is_available(self) -> bool:
        """判断本地 vipdoc 目录是否可用。"""
        return bool(self.vipdoc_dir and self.vipdoc_dir.exists() and self.vipdoc_dir.is_dir())

    def _normalize_symbol(self, symbol: str) -> tuple[str, str] | None:
        """将项目代码转成通达信市场前缀与 6 位代码。"""
        normalized = str(symbol or "").strip().upper()
        if not normalized:
            return None

        if "." in normalized:
            code, suffix = normalized.split(".", 1)
            market_prefix = "sh" if suffix == "SH" else "sz" if suffix == "SZ" else ""
        else:
            code = normalized
            if code.startswith(("5", "6", "9")):
                market_prefix = "sh"
            elif code.startswith(("0", "1", "2", "3")):
                market_prefix = "sz"
            else:
                market_prefix = ""

        if market_prefix not in {"sh", "sz"} or not code.isdigit() or len(code) != 6:
            return None
        return market_prefix, code

    def _day_file_path(self, symbol: str) -> Path | None:
        """返回 `.day` 文件路径。"""
        if not self.is_available or self.vipdoc_dir is None:
            return None
        normalized = self._normalize_symbol(symbol)
        if not normalized:
            return None
        market_prefix, code = normalized
        return self.vipdoc_dir / market_prefix / "lday" / f"{market_prefix}{code}.day"

    def _read_day_rows(self, symbol: str) -> list[dict[str, Any]]:
        """读取通达信日线文件并转换为统一 K 线结构。"""
        file_path = self._day_file_path(symbol)
        if file_path is None or not file_path.exists():
            return []

        rows: list[dict[str, Any]] = []
        try:
            raw_data = file_path.read_bytes()
        except Exception:
            return []

        for offset in range(0, len(raw_data) - self.RECORD_SIZE + 1, self.RECORD_SIZE):
            chunk = raw_data[offset : offset + self.RECORD_SIZE]
            try:
                trade_date, open_price, high_price, low_price, close_price, amount, volume, _reserved = struct.unpack(
                    "<iiiiifii",
                    chunk,
                )
            except Exception:
                continue
            if trade_date <= 0:
                continue
            rows.append(
                {
                    "datetime": str(trade_date),
                    "open": round(open_price / 100.0, 4),
                    "high": round(high_price / 100.0, 4),
                    "low": round(low_price / 100.0, 4),
                    "close": round(close_price / 100.0, 4),
                    "volume": float(volume),
                    "turnover": float(amount),
                    "source_provider": "TDX local vipdoc",
                    "data_source": "real",
                }
            )
        return rows

    def _resample_rows(self, rows: list[dict[str, Any]], interval: str) -> list[dict[str, Any]]:
        """将日线聚合为周线或月线。"""
        if interval == "1day" or not rows:
            return rows

        dataframe = pd.DataFrame(rows).copy()
        dataframe["date"] = pd.to_datetime(dataframe["datetime"], format="%Y%m%d", errors="coerce")
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
                "turnover": "sum",
            }
        )
        resampled = resampled.dropna(subset=["open", "high", "low", "close"])
        output_rows: list[dict[str, Any]] = []
        for date_index, row in resampled.iterrows():
            output_rows.append(
                {
                    "datetime": date_index.strftime("%Y%m%d"),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]),
                    "turnover": float(row["turnover"]),
                    "source_provider": "TDX local vipdoc",
                    "data_source": "real",
                }
            )
        return output_rows

    def get_kline(self, symbol: str, interval: str = "1day", limit: int = 120) -> list[dict[str, Any]] | None:
        """读取本地 K 线数据。"""
        if not self.is_available:
            return None
        day_rows = self._read_day_rows(symbol)
        if not day_rows:
            return None
        rows = self._resample_rows(day_rows, interval)
        return rows[-limit:] if rows else None

    def get_asset_detail(self, market: str, symbol: str, asset_meta: dict[str, Any]) -> dict[str, Any] | None:
        """基于本地最新日线构造资产详情。"""
        rows = self.get_kline(symbol, "1day", limit=2)
        if not rows:
            return None
        latest = rows[-1]
        previous = rows[-2] if len(rows) > 1 else latest
        previous_close = float(previous.get("close", latest.get("close", 0)) or 0)
        close_price = float(latest.get("close", 0) or 0)
        change = close_price - previous_close
        pct_change = 0.0 if previous_close == 0 else change / previous_close * 100
        high_price = float(latest.get("high", close_price) or close_price)
        low_price = float(latest.get("low", close_price) or close_price)
        amplitude = 0.0 if previous_close == 0 else (high_price - low_price) / previous_close * 100

        return {
            "symbol": asset_meta.get("symbol", symbol),
            "name": asset_meta.get("name", symbol),
            "market": market,
            "asset_type": asset_meta.get("asset_type", "A股"),
            "theme": asset_meta.get("theme", "A股"),
            "price": round(close_price, 4),
            "change": round(change, 4),
            "pct_change": round(pct_change, 4),
            "volume": float(latest.get("volume", 0) or 0),
            "turnover": float(latest.get("turnover", 0) or 0),
            "amplitude": round(amplitude, 4),
            "risk_level": asset_meta.get("risk_level", "中高风险"),
            "description": asset_meta.get("description", "基于本地通达信 vipdoc 日线数据生成的资产信息。"),
            "source_provider": "TDX local vipdoc",
            "data_source": "real",
            "updated_at": str(latest.get("datetime", "")),
        }
