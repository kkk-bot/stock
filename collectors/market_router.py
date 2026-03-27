"""多市场数据路由与 fallback 逻辑。"""

from __future__ import annotations

from typing import Any

from collectors.alpha_vantage_client import AlphaVantageClient
from collectors.mock_data import get_mock_asset_detail, get_mock_kline, get_mock_related_news
from collectors.tushare_client import TushareClient
from collectors.twelve_data_client import TwelveDataClient


tushare_client = TushareClient()
alpha_client = AlphaVantageClient()
twelve_client = TwelveDataClient()


def get_asset_detail(market: str, symbol: str, asset_meta: dict[str, Any]) -> dict[str, Any]:
    """按市场获取资产详情，失败自动回退到 mock。"""
    real_result = None
    fallback_used = False

    if market == "A股":
        real_result = tushare_client.get_asset_detail(market, symbol, asset_meta)
    elif market == "港股":
        real_result = tushare_client.get_asset_detail(market, symbol, asset_meta)
        if real_result is None:
            fallback_used = True
            real_result = twelve_client.get_asset_detail(market, symbol, asset_meta)
    elif market == "美股":
        real_result = alpha_client.get_asset_detail(market, symbol, asset_meta)
        if real_result is None:
            fallback_used = True
            real_result = twelve_client.get_asset_detail(market, symbol, asset_meta)
    elif market == "黄金":
        real_result = alpha_client.get_asset_detail(market, symbol, asset_meta)
        if real_result is None:
            fallback_used = True
            real_result = twelve_client.get_asset_detail(market, symbol, asset_meta)

    if real_result:
        real_result["fallback_used"] = fallback_used
        return real_result

    mock_result = get_mock_asset_detail(market, symbol)
    mock_result["fallback_used"] = True
    return mock_result


def get_kline(market: str, symbol: str, asset_meta: dict[str, Any], interval: str = "1day") -> list[dict[str, Any]]:
    """按市场获取 K 线，失败自动回退到 mock。"""
    real_rows = None
    if market == "A股":
        real_rows = tushare_client.get_kline(market, symbol, interval, asset_meta)
    elif market == "港股":
        real_rows = tushare_client.get_kline(market, symbol, interval, asset_meta)
        if real_rows is None:
            real_rows = twelve_client.get_kline(symbol, interval)
    elif market == "美股":
        real_rows = alpha_client.get_kline(market, symbol, interval, asset_meta)
        if real_rows is None:
            real_rows = twelve_client.get_kline(symbol, interval)
    elif market == "黄金":
        real_rows = alpha_client.get_kline(market, symbol, interval, asset_meta)
        if real_rows is None:
            real_rows = twelve_client.get_kline(symbol, interval)

    if real_rows:
        return real_rows
    return get_mock_kline(market, symbol, interval)


def get_related_news(market: str, symbol: str, theme: str | None = None) -> list[dict[str, Any]]:
    """获取相关新闻，优先 Alpha Vantage，失败回退 mock。"""
    real_news = alpha_client.get_related_news(symbol, theme)
    if real_news:
        return real_news
    return get_mock_related_news(market, symbol, theme or "")
