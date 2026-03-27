"""Tushare 客户端封装。"""

from __future__ import annotations

from typing import Any

from config import TUSHARE_TOKEN

try:
    import tushare as ts
except ImportError:  # pragma: no cover - 缺少依赖时走 fallback
    ts = None


class TushareClient:
    """封装 Tushare 请求逻辑。"""

    def __init__(self, token: str | None = None) -> None:
        self.token = token or TUSHARE_TOKEN
        self.pro = None
        if ts and self.token:
            try:
                ts.set_token(self.token)
                self.pro = ts.pro_api(self.token)
            except Exception:
                self.pro = None

    @property
    def is_available(self) -> bool:
        """判断当前客户端是否可用。"""
        return self.pro is not None

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """安全转换为浮点数。"""
        try:
            if value in (None, "", "None"):
                return default
            return float(value)
        except Exception:
            return default

    def _build_asset_detail(
        self,
        market: str,
        asset_meta: dict[str, Any],
        latest: Any,
        previous_close: float,
        source_provider: str,
    ) -> dict[str, Any]:
        """统一构造资产详情，缺字段时自动补默认值。"""
        close_price = self._safe_float(latest.get("close"))
        change = close_price - previous_close
        pct_change = self._safe_float(latest.get("pct_chg"))
        if pct_change == 0 and previous_close:
            pct_change = change / previous_close * 100
        return {
            "symbol": asset_meta["symbol"],
            "name": asset_meta["name"],
            "market": market,
            "asset_type": asset_meta["asset_type"],
            "theme": asset_meta["theme"],
            "price": close_price,
            "change": round(change, 4),
            "pct_change": round(pct_change, 4),
            "volume": self._safe_float(latest.get("vol")),
            "turnover": self._safe_float(latest.get("amount")),
            "amplitude": self._safe_float(latest.get("swing")),
            "risk_level": asset_meta["risk_level"],
            "description": asset_meta["description"],
            "source_provider": source_provider,
            "data_source": "real",
            "updated_at": str(latest.get("trade_date", "")),
        }

    def get_asset_detail(self, market: str, symbol: str, asset_meta: dict[str, Any]) -> dict[str, Any] | None:
        """获取资产详情，失败时返回 None。"""
        if not self.is_available:
            return None

        try:
            if market == "A股":
                return self._get_a_share_detail(symbol, asset_meta)
            if market == "港股":
                return self._get_hk_detail(symbol, asset_meta)
        except Exception:
            return None
        return None

    def get_kline(self, market: str, symbol: str, interval: str, asset_meta: dict[str, Any]) -> list[dict[str, Any]] | None:
        """获取 K 线数据，失败时返回 None。"""
        if not self.is_available:
            return None
        try:
            if market == "A股":
                return self._get_a_share_kline(symbol, interval)
            if market == "港股":
                return self._get_hk_kline(symbol, interval)
        except Exception:
            return None
        return None

    def _get_a_share_detail(self, symbol: str, asset_meta: dict[str, Any]) -> dict[str, Any] | None:
        """获取 A 股或指数详情。"""
        latest_df = self.pro.index_daily(ts_code=symbol, limit=2)
        if latest_df is None or latest_df.empty:
            latest_df = self.pro.fund_daily(ts_code=symbol, limit=2)
        if latest_df is None or latest_df.empty:
            return None

        latest = latest_df.iloc[0]
        previous_close = self._safe_float(
            latest.get("pre_close"),
            self._safe_float(latest_df.iloc[1].get("close")) if len(latest_df) > 1 else self._safe_float(latest.get("close")),
        )
        return self._build_asset_detail("A股", asset_meta, latest, previous_close, "Tushare")

    def _get_hk_detail(self, symbol: str, asset_meta: dict[str, Any]) -> dict[str, Any] | None:
        """获取港股详情。"""
        latest_df = self.pro.hk_daily(ts_code=symbol, limit=2)
        if latest_df is None or latest_df.empty:
            return None
        latest = latest_df.iloc[0]
        prev_close = self._safe_float(
            latest_df.iloc[1].get("close") if len(latest_df) > 1 else latest.get("close"),
            self._safe_float(latest.get("close")),
        )
        return self._build_asset_detail("港股", asset_meta, latest, prev_close, "Tushare")

    def _get_a_share_kline(self, symbol: str, interval: str) -> list[dict[str, Any]] | None:
        """获取 A 股 K 线。"""
        interval_method_map = {
            "1day": self.pro.index_daily,
            "1week": getattr(self.pro, "index_weekly", None),
            "1month": getattr(self.pro, "index_monthly", None),
        }
        method = interval_method_map.get(interval)
        if method is None:
            method = self.pro.index_daily
        data_frame = method(ts_code=symbol, limit=60)
        if data_frame is None or data_frame.empty:
            data_frame = self.pro.fund_daily(ts_code=symbol, limit=60)
        if data_frame is None or data_frame.empty:
            return None

        rows: list[dict[str, Any]] = []
        for _, row in data_frame.sort_values("trade_date").iterrows():
            rows.append(
                {
                    "datetime": str(row.get("trade_date")),
                    "open": self._safe_float(row.get("open")),
                    "high": self._safe_float(row.get("high")),
                    "low": self._safe_float(row.get("low")),
                    "close": self._safe_float(row.get("close")),
                    "volume": self._safe_float(row.get("vol")),
                    "source_provider": "Tushare",
                    "data_source": "real",
                }
            )
        return rows

    def _get_hk_kline(self, symbol: str, interval: str) -> list[dict[str, Any]] | None:
        """获取港股 K 线。"""
        data_frame = self.pro.hk_daily(ts_code=symbol, limit=60)
        if data_frame is None or data_frame.empty:
            return None

        rows: list[dict[str, Any]] = []
        for _, row in data_frame.sort_values("trade_date").iterrows():
            rows.append(
                {
                    "datetime": str(row.get("trade_date")),
                    "open": self._safe_float(row.get("open")),
                    "high": self._safe_float(row.get("high")),
                    "low": self._safe_float(row.get("low")),
                    "close": self._safe_float(row.get("close")),
                    "volume": self._safe_float(row.get("vol")),
                    "source_provider": "Tushare",
                    "data_source": "real",
                }
            )
        return rows
