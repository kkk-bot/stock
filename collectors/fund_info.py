"""资产基础信息、代码标准化与市场总览配置模块。"""

from __future__ import annotations

import json
import re
from typing import Any

import pandas as pd
import requests

from collectors.mock_data import (
    build_mock_fund_kline_from_detail,
    get_mock_fund_by_code,
    get_mock_fund_asset_detail,
    get_mock_fund_kline,
    list_mock_funds,
    list_supported_assets,
    resolve_mock_asset,
    search_mock_funds_by_name,
)


SINGLE_ANALYSIS_MARKETS = ["基金", "A股", "港股", "美股", "黄金"]
OVERVIEW_ANALYSIS_MARKETS = ["A股", "港股", "美股", "黄金"]
MARKET_OVERVIEW_THEMES = {
    "A股": "A股大盘",
    "港股": "港股科技",
    "美股": "美股科技",
    "黄金": "黄金市场",
}

EASTMONEY_FUND_SEARCH_URL = "https://fundsuggest.eastmoney.com/FundSearch/api/FundSearchAPI.ashx"
EASTMONEY_FUND_ESTIMATE_URL = "https://fundgz.1234567.com.cn/js/{code}.js"
EASTMONEY_FUND_HISTORY_URL = "https://fund.eastmoney.com/pingzhongdata/{code}.js"


def _is_probable_fund_code(query: str) -> bool:
    """判断输入是否像基金代码，必须按字符串处理以保留前导 0。"""
    normalized_query = str(query or "").strip()
    return bool(re.fullmatch(r"\d{6}", normalized_query))


def _infer_fund_traits(fund_name: str, fund_type: str, fund_code: str) -> dict[str, Any]:
    """根据基金名称和类型推断主题、市场与描述。"""
    name_text = str(fund_name or fund_code).strip()
    fund_type_text = str(fund_type or "基金").strip()
    searchable_text = f"{name_text} {fund_type_text}"

    if any(keyword in searchable_text for keyword in ["恒生", "港股", "香港", "H股"]):
        return {
            "themes": ["恒生科技", "港股科技"] if "科技" in searchable_text else ["港股", "香港市场"],
            "market": "港股",
            "risk_level": "高风险",
            "description": f"{name_text} 主要受香港市场与港股相关板块情绪影响，当前基于可用信息进行基金分析。",
        }
    if any(keyword in searchable_text for keyword in ["纳指", "纳斯达克", "美股", "QDII", "海外"]):
        return {
            "themes": ["美股科技", "海外成长"] if any(k in searchable_text for k in ["科技", "纳指", "纳斯达克"]) else ["海外市场"],
            "market": "美股",
            "risk_level": "高风险",
            "description": f"{name_text} 与海外市场联动较强，当前基于净值与相关主题新闻输出简化分析。",
        }
    if any(keyword in searchable_text for keyword in ["黄金", "贵金属"]):
        return {
            "themes": ["黄金", "避险资产"],
            "market": "黄金",
            "risk_level": "中高风险",
            "description": f"{name_text} 主要跟踪黄金或贵金属方向，当前基于可用净值与主题信息输出分析。",
        }
    if any(keyword in searchable_text for keyword in ["债券", "纯债", "固收"]):
        return {
            "themes": ["债券", "固收"],
            "market": "债券",
            "risk_level": "中低风险",
            "description": f"{name_text} 以固收类资产为主，分析侧重净值稳定性与利率环境。",
        }
    if any(keyword in searchable_text for keyword in ["半导体", "芯片"]):
        return {
            "themes": ["半导体", "芯片"],
            "market": "A股",
            "risk_level": "高风险",
            "description": f"{name_text} 聚焦半导体产业链，分析会结合净值走势与芯片板块情绪。",
        }
    if any(keyword in searchable_text for keyword in ["新能源", "光伏", "锂电", "储能"]):
        return {
            "themes": ["新能源", "成长"],
            "market": "A股",
            "risk_level": "高风险",
            "description": f"{name_text} 主要覆盖新能源相关方向，分析会结合净值走势与行业新闻情绪。",
        }
    if any(keyword in searchable_text for keyword in ["医药", "医疗", "创新药"]):
        return {
            "themes": ["医药", "医疗"],
            "market": "A股",
            "risk_level": "中高风险",
            "description": f"{name_text} 主要覆盖医药医疗方向，分析会结合净值走势与行业情绪输出结果。",
        }
    if any(keyword in searchable_text for keyword in ["制造", "高端装备", "工业"]):
        return {
            "themes": ["高端制造", "先进制造", "成长"],
            "market": "A股",
            "risk_level": "中高风险",
            "description": f"{name_text} 偏向制造升级与成长方向，分析会结合净值走势、板块新闻与情绪结果。",
        }
    return {
        "themes": ["基金观察"],
        "market": "A股",
        "risk_level": "中风险",
        "description": f"{name_text} 已识别为基金，当前基于可用净值、阶段表现与相关新闻输出简化分析。",
    }


def _build_fund_asset_meta(
    fund_code: str,
    fund_name: str,
    fund_type: str,
    themes: list[str],
    underlying_market: str,
    risk_level: str,
    description: str,
    data_source: str = "mock",
) -> dict[str, Any]:
    """构造统一的基金资产元信息。"""
    return {
        "symbol": str(fund_code).strip(),
        "name": str(fund_name).strip() or str(fund_code).strip(),
        "asset_type": str(fund_type).strip() or "基金",
        "theme": " / ".join(theme for theme in themes if str(theme).strip()) or "基金观察",
        "risk_level": str(risk_level).strip() or "中风险",
        "description": str(description).strip() or "已识别为基金，当前基于可用信息进行简化分析。",
        "market": "基金",
        "underlying_market": str(underlying_market).strip() or "A股",
        "aliases": [str(fund_code).strip(), str(fund_name).strip(), *themes],
        "data_source": data_source,
    }


def _extract_fund_candidates(payload: Any) -> list[dict[str, str]]:
    """从公开搜索接口中尽量提取基金候选。"""
    if not payload:
        return []

    raw_items: list[Any] = []
    if isinstance(payload, dict):
        for key in ("Datas", "data", "Data", "Result"):
            value = payload.get(key)
            if isinstance(value, list):
                raw_items = value
                break
    elif isinstance(payload, list):
        raw_items = payload

    candidates: list[dict[str, str]] = []
    for item in raw_items:
        if isinstance(item, dict):
            code = str(
                item.get("CODE")
                or item.get("FCODE")
                or item.get("code")
                or item.get("fundcode")
                or ""
            ).strip()
            name = str(
                item.get("NAME")
                or item.get("SHORTNAME")
                or item.get("name")
                or item.get("fundname")
                or ""
            ).strip()
            fund_type = str(
                item.get("FundBaseType")
                or item.get("FundType")
                or item.get("TYPE")
                or item.get("category")
                or ""
            ).strip()
            if code:
                candidates.append({"fund_code": code, "fund_name": name, "fund_type": fund_type})
        elif isinstance(item, str):
            parts = [part.strip() for part in item.split(",")]
            if parts and parts[0]:
                candidates.append(
                    {
                        "fund_code": parts[0],
                        "fund_name": parts[1] if len(parts) > 1 else parts[0],
                        "fund_type": parts[3] if len(parts) > 3 else "",
                    }
                )
    return candidates


def _fetch_real_fund_candidate(query: str) -> dict[str, Any] | None:
    """尝试从轻量公开接口查询基金基础信息。"""
    normalized_query = str(query or "").strip()
    if not normalized_query:
        return None

    try:
        response = requests.get(
            EASTMONEY_FUND_SEARCH_URL,
            params={"m": "1", "key": normalized_query},
            timeout=5,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return None

    candidates = _extract_fund_candidates(payload)
    if not candidates:
        return None

    exact_code_candidate = next((item for item in candidates if item["fund_code"] == normalized_query), None)
    exact_name_candidate = next((item for item in candidates if normalized_query.lower() in item["fund_name"].lower()), None)
    selected_candidate = exact_code_candidate or exact_name_candidate or candidates[0]
    fund_traits = _infer_fund_traits(
        selected_candidate.get("fund_name", ""),
        selected_candidate.get("fund_type", ""),
        selected_candidate.get("fund_code", normalized_query),
    )
    return _build_fund_asset_meta(
        fund_code=selected_candidate.get("fund_code", normalized_query),
        fund_name=selected_candidate.get("fund_name", normalized_query),
        fund_type=selected_candidate.get("fund_type", "基金"),
        themes=fund_traits["themes"],
        underlying_market=fund_traits["market"],
        risk_level=fund_traits["risk_level"],
        description=fund_traits["description"],
        data_source="real",
    )


def _fetch_real_fund_quote(fund_code: str) -> dict[str, Any] | None:
    """尝试获取基金净值估算信息。"""
    normalized_code = str(fund_code or "").strip()
    if not _is_probable_fund_code(normalized_code):
        return None

    try:
        response = requests.get(
            EASTMONEY_FUND_ESTIMATE_URL.format(code=normalized_code),
            timeout=5,
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://fund.eastmoney.com/"},
        )
        response.raise_for_status()
        matched = re.search(r"\{.*\}", response.text)
        if not matched:
            return None
        payload = json.loads(matched.group(0))
    except Exception:
        return None

    previous_nav = float(payload.get("dwjz") or 0) if str(payload.get("dwjz", "")).strip() else 0.0
    estimated_nav = float(payload.get("gsz") or payload.get("dwjz") or 0) if str(payload.get("gsz", payload.get("dwjz", ""))).strip() else 0.0
    pct_change = float(payload.get("gszzl") or 0) if str(payload.get("gszzl", "")).strip() else 0.0
    change_value = estimated_nav - previous_nav if previous_nav else 0.0
    return {
        "fund_code": normalized_code,
        "fund_name": str(payload.get("name", normalized_code)).strip() or normalized_code,
        "price": round(estimated_nav, 4),
        "change": round(change_value, 4),
        "pct_change": round(pct_change, 4),
        "previous_nav": round(previous_nav, 4),
        "updated_at": str(payload.get("gztime") or payload.get("jzrq") or "").strip(),
        "source_provider": "Eastmoney Fund",
    }


def _resample_fund_nav_rows(rows: list[dict[str, Any]], interval: str) -> list[dict[str, Any]]:
    """将真实基金日净值聚合为周/月走势。"""
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
                "source_provider": "Eastmoney Fund NAV",
                "data_source": "real",
            }
        )
    return output_rows


def _fetch_real_fund_kline(fund_code: str, interval: str = "1day", limit: int = 120) -> list[dict[str, Any]] | None:
    """从东方财富基金页面脚本读取真实历史净值走势。"""
    normalized_code = str(fund_code or "").strip()
    if not _is_probable_fund_code(normalized_code):
        return None

    try:
        response = requests.get(
            EASTMONEY_FUND_HISTORY_URL.format(code=normalized_code),
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0", "Referer": f"https://fund.eastmoney.com/{normalized_code}.html"},
        )
        response.raise_for_status()
        matched = re.search(r"var\s+Data_netWorthTrend\s*=\s*(.*?);/\*累计净值走势", response.text, re.S)
        if not matched:
            return None
        payload = json.loads(matched.group(1))
    except Exception:
        return None

    rows: list[dict[str, Any]] = []
    previous_close = 0.0
    for item in payload:
        try:
            timestamp_ms = int(item.get("x", 0))
            nav_value = float(item.get("y", 0))
        except Exception:
            continue
        if timestamp_ms <= 0 or nav_value <= 0:
            continue
        date_text = pd.to_datetime(timestamp_ms, unit="ms").strftime("%Y-%m-%d")
        open_value = previous_close or nav_value
        high_value = max(open_value, nav_value)
        low_value = min(open_value, nav_value)
        rows.append(
            {
                "datetime": date_text,
                "open": round(open_value, 4),
                "high": round(high_value, 4),
                "low": round(low_value, 4),
                "close": round(nav_value, 4),
                "volume": 0.0,
                "source_provider": "Eastmoney Fund NAV",
                "data_source": "real",
            }
        )
        previous_close = nav_value

    if not rows:
        return None
    resampled_rows = _resample_fund_nav_rows(rows, interval)
    return resampled_rows[-limit:] if resampled_rows else None


def find_fund_candidate(query: str) -> dict[str, Any] | None:
    """查询基金候选，优先 mock，其次轻量真实接口，最后对 6 位代码做简化识别。"""
    normalized_query = str(query or "").strip()
    if not normalized_query:
        return None

    fund = get_mock_fund_by_code(normalized_query)
    if fund:
        return _fund_to_asset_meta(fund)

    matched_funds = search_mock_funds_by_name(normalized_query)
    if matched_funds:
        return _fund_to_asset_meta(matched_funds[0])

    real_candidate = _fetch_real_fund_candidate(normalized_query)
    if real_candidate:
        return real_candidate

    if _is_probable_fund_code(normalized_query):
        fund_traits = _infer_fund_traits("", "基金", normalized_query)
        return _build_fund_asset_meta(
            fund_code=normalized_query,
            fund_name=f"基金 {normalized_query}",
            fund_type="基金",
            themes=fund_traits["themes"],
            underlying_market=fund_traits["market"],
            risk_level=fund_traits["risk_level"],
            description="已识别为基金，但暂时未获取到完整资料，当前将基于可用净值与主题信息输出简化分析。",
            data_source="fallback",
        )
    return None


def detect_input_market(selected_market: str, query: str) -> str:
    """在尽量不影响原逻辑的前提下，为基金代码增加优先识别。"""
    normalized_query = str(query or "").strip()
    if selected_market != "A股" or not _is_probable_fund_code(normalized_query):
        return selected_market

    a_share_match = resolve_mock_asset("A股", normalize_symbol_input("A股", normalized_query)) or resolve_mock_asset("A股", normalized_query)
    if a_share_match:
        return selected_market

    fund_candidate = find_fund_candidate(normalized_query)
    if fund_candidate:
        return "基金"
    return selected_market


def get_fund_data(fund_code: str, asset_meta: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """基金专用数据获取函数，优先真实估值，失败后回退 mock / 简化数据。"""
    normalized_code = str(fund_code or "").strip()
    if not normalized_code:
        return None

    candidate_meta = asset_meta or find_fund_candidate(normalized_code)
    mock_detail = get_mock_fund_asset_detail(normalized_code)
    if not candidate_meta and mock_detail:
        candidate_meta = {
            "symbol": mock_detail.get("symbol", normalized_code),
            "name": mock_detail.get("name", normalized_code),
            "asset_type": mock_detail.get("asset_type", "基金"),
            "theme": mock_detail.get("theme", "基金观察"),
            "risk_level": mock_detail.get("risk_level", "中风险"),
            "description": mock_detail.get("description", "已识别为基金，当前基于可用信息进行分析。"),
        }

    real_quote = _fetch_real_fund_quote(normalized_code)
    if real_quote and candidate_meta:
        return {
            "symbol": normalized_code,
            "name": real_quote.get("fund_name") or candidate_meta.get("name") or normalized_code,
            "market": "基金",
            "asset_type": candidate_meta.get("asset_type", "基金"),
            "theme": candidate_meta.get("theme", "基金观察"),
            "price": real_quote.get("price", 0.0),
            "change": real_quote.get("change", 0.0),
            "pct_change": real_quote.get("pct_change", 0.0),
            "volume": 0.0,
            "turnover": 0.0,
            "amplitude": abs(float(real_quote.get("pct_change", 0.0) or 0.0)),
            "risk_level": candidate_meta.get("risk_level", "中风险"),
            "description": candidate_meta.get("description", "已基于可用基金数据输出简化分析。"),
            "source_provider": real_quote.get("source_provider", "Eastmoney Fund"),
            "data_source": "real",
            "updated_at": real_quote.get("updated_at", ""),
            "previous_nav": real_quote.get("previous_nav", 0.0),
            "fund_name": real_quote.get("fund_name", ""),
        }

    if mock_detail:
        return mock_detail

    if not candidate_meta:
        return None

    return {
        "symbol": normalized_code,
        "name": candidate_meta.get("name", normalized_code),
        "market": "基金",
        "asset_type": candidate_meta.get("asset_type", "基金"),
        "theme": candidate_meta.get("theme", "基金观察"),
        "price": 1.0,
        "change": 0.0,
        "pct_change": 0.0,
        "volume": 0.0,
        "turnover": 0.0,
        "amplitude": 0.0,
        "risk_level": candidate_meta.get("risk_level", "中风险"),
        "description": candidate_meta.get("description", "已识别为基金，但暂未获取到完整数据，当前基于可用信息输出简化分析。"),
        "source_provider": "mock",
        "data_source": "mock",
        "updated_at": "",
        "fallback_used": True,
    }


def get_fund_kline(fund_code: str, asset_detail: dict[str, Any], interval: str = "1day") -> list[dict[str, Any]]:
    """基金专用 K 线获取函数，优先真实历史净值，失败后回退 mock。"""
    normalized_code = str(fund_code or "").strip()
    real_rows = _fetch_real_fund_kline(normalized_code, interval)
    if real_rows:
        return real_rows
    mock_rows = get_mock_fund_kline(normalized_code, interval)
    if mock_rows:
        return mock_rows
    return build_mock_fund_kline_from_detail(asset_detail, interval)


def _fund_to_asset_meta(fund: dict[str, Any]) -> dict[str, Any]:
    """将基金信息映射为统一资产元信息。"""
    return {
        "symbol": fund["fund_code"],
        "name": fund["fund_name"],
        "asset_type": fund["fund_type"],
        "theme": " / ".join(fund.get("themes", [])),
        "risk_level": fund["risk_level"],
        "description": fund["description"],
        "market": "基金",
        "underlying_market": fund.get("market", ""),
        "aliases": [fund["fund_code"], fund["fund_name"], *fund.get("themes", [])],
    }


def list_market_assets(market: str) -> list[dict[str, Any]]:
    """返回指定市场可用的分析对象。"""
    if market == "基金":
        return [_fund_to_asset_meta(fund) for fund in list_mock_funds()]
    return list_supported_assets(market)


def normalize_symbol_input(market: str, query: str) -> str:
    """根据市场标准化用户输入代码。"""
    normalized_query = query.strip()
    if not normalized_query:
        return ""

    compact_query = normalized_query.replace(" ", "").upper()
    if market == "基金":
        return normalized_query

    if market == "A股":
        if compact_query == "000001":
            return "000001.SH"
        if compact_query.endswith((".SH", ".SZ")):
            return compact_query
        if compact_query.isdigit() and len(compact_query) == 6:
            if compact_query.startswith(("5", "6", "9")):
                return f"{compact_query}.SH"
            return f"{compact_query}.SZ"
        return compact_query

    if market == "港股":
        if compact_query.endswith(".HK"):
            code_part = compact_query.replace(".HK", "")
            if code_part.isdigit():
                return f"{code_part.zfill(5)}.HK"
            return compact_query
        if compact_query.isdigit():
            return f"{compact_query.zfill(5)}.HK"
        return compact_query

    if market == "美股":
        return compact_query

    if market == "黄金":
        gold_alias_map = {
            "GOLD": "XAUUSD",
            "黄金": "XAUUSD",
            "现货黄金": "XAUUSD",
            "XAU/USD": "XAUUSD",
            "XAUUSD": "XAUUSD",
            "黄金ETF": "GLD",
            "GLD": "GLD",
        }
        return gold_alias_map.get(compact_query, compact_query)

    return compact_query


def _build_generic_asset_meta(market: str, symbol: str) -> dict[str, Any]:
    """为未命中内置样本的输入构造通用元信息。"""
    default_theme_map = {
        "A股": "A股市场",
        "港股": "港股市场",
        "美股": "美股市场",
        "黄金": "黄金市场",
    }
    default_type_map = {
        "A股": "A股资产",
        "港股": "港股资产",
        "美股": "美股资产",
        "黄金": "黄金资产",
    }
    return {
        "symbol": symbol,
        "name": symbol,
        "asset_type": default_type_map.get(market, "未知资产"),
        "theme": default_theme_map.get(market, "综合"),
        "risk_level": "未知",
        "description": f"未命中内置样本，当前将按输入代码 {symbol} 尝试查询。",
        "market": market,
        "aliases": [symbol, f"{symbol} stock", f"{symbol} news"] if market == "美股" else [symbol],
    }


def resolve_asset_input(market: str, query: str) -> dict[str, Any]:
    """根据市场与用户输入解析单个分析对象。"""
    normalized_query = query.strip()
    if market == "基金":
        if not normalized_query:
            funds = list_market_assets("基金")
            if not funds:
                return {"success": False, "message": "当前没有可分析基金。", "asset": None, "data_source": "mock"}
            return {
                "success": True,
                "message": "未输入基金代码，当前使用默认示例基金。",
                "asset": funds[0],
                "data_source": "mock",
            }

        fund_candidate = find_fund_candidate(normalized_query)
        if fund_candidate:
            data_source = str(fund_candidate.get("data_source", "mock"))
            if fund_candidate.get("symbol") == normalized_query:
                matched_message = "已识别为基金代码。"
            else:
                matched_message = "已匹配到基金名称。"
            if data_source == "fallback":
                matched_message = "已识别为基金，但暂时未获取到完整资料，当前使用简化基金分析。"
            elif data_source == "real":
                matched_message = "已识别为基金，并获取到基础资料。"
            return {
                "success": True,
                "message": matched_message,
                "asset": fund_candidate,
                "data_source": data_source,
            }

        return {
            "success": False,
            "message": "未找到对应基金，请检查代码或名称。",
            "asset": None,
            "data_source": "mock",
        }

    normalized_symbol = normalize_symbol_input(market, normalized_query)
    if not normalized_symbol:
        assets = list_market_assets(market)
        if not assets:
            return {"success": False, "message": "当前市场暂无可分析资产。", "asset": None, "data_source": "mock"}
        default_asset = assets[0].copy()
        default_asset["market"] = market
        return {
            "success": True,
            "message": "未输入代码，当前使用默认代表性资产。",
            "asset": default_asset,
            "data_source": "mock",
        }

    matched_asset = resolve_mock_asset(market, normalized_symbol) or resolve_mock_asset(market, normalized_query)
    if matched_asset:
        matched_asset["market"] = market
        return {
            "success": True,
            "message": "已匹配到分析资产。",
            "asset": matched_asset,
            "data_source": "mock",
        }

    generic_asset = _build_generic_asset_meta(market, normalized_symbol)
    return {
        "success": True,
        "message": "未命中内置样本，当前将按输入代码尝试真实查询。",
        "asset": generic_asset,
        "data_source": "input",
    }


def get_market_overview_targets(market: str) -> list[dict[str, Any]]:
    """返回市场总览模式的代表资产。"""
    return list_market_assets(market)[:3]


def get_market_overview_theme(market: str) -> str:
    """返回市场总览模式的主题关键词。"""
    return MARKET_OVERVIEW_THEMES.get(market, "市场观察")


def build_market_overview_summary(market: str, asset_details: list[dict[str, Any]]) -> dict[str, Any]:
    """根据代表资产构造市场总览摘要。"""
    if not asset_details:
        return {
            "symbol": f"{market}_OVERVIEW",
            "name": f"{market}市场总览",
            "market": market,
            "asset_type": "市场总览",
            "theme": get_market_overview_theme(market),
            "price": 0.0,
            "change": 0.0,
            "pct_change": 0.0,
            "volume": 0.0,
            "turnover": 0.0,
            "amplitude": 0.0,
            "risk_level": "中风险",
            "description": f"{market} 市场总览暂无代表资产数据。",
            "source_provider": "mock",
            "data_source": "mock",
            "updated_at": "",
        }

    average_price = sum(float(item.get("price", 0) or 0) for item in asset_details) / len(asset_details)
    average_change = sum(float(item.get("change", 0) or 0) for item in asset_details) / len(asset_details)
    average_pct_change = sum(float(item.get("pct_change", 0) or 0) for item in asset_details) / len(asset_details)
    average_amplitude = sum(float(item.get("amplitude", 0) or 0) for item in asset_details) / len(asset_details)
    average_volume = sum(float(item.get("volume", 0) or 0) for item in asset_details)
    average_turnover = sum(float(item.get("turnover", 0) or 0) for item in asset_details)
    provider_names = sorted({str(item.get("source_provider", "mock")) for item in asset_details})
    data_sources = {str(item.get("data_source", "mock")) for item in asset_details}
    rising_count = sum(1 for item in asset_details if float(item.get("pct_change", 0) or 0) > 0)

    return {
        "symbol": f"{market}_OVERVIEW",
        "name": f"{market}市场总览",
        "market": market,
        "asset_type": "市场总览",
        "theme": get_market_overview_theme(market),
        "price": round(average_price, 4),
        "change": round(average_change, 4),
        "pct_change": round(average_pct_change, 4),
        "volume": round(average_volume, 2),
        "turnover": round(average_turnover, 2),
        "amplitude": round(average_amplitude, 4),
        "risk_level": "中高风险" if rising_count != len(asset_details) else "中风险",
        "description": f"{market} 市场总览基于 {len(asset_details)} 个代表资产生成，当前上涨资产 {rising_count} 个。",
        "source_provider": " + ".join(provider_names) if provider_names else "mock",
        "data_source": "real" if "real" in data_sources else "mock",
        "updated_at": asset_details[0].get("updated_at", ""),
        "fallback_used": any(bool(item.get("fallback_used")) for item in asset_details),
    }
