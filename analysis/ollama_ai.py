"""本地 Ollama AI 辅助分析模块。"""

from __future__ import annotations

import os
from typing import Any

import pandas as pd
import requests


DEFAULT_OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b").strip()


def _format_number(value: Any) -> str:
    """格式化数值，失败时返回原始文本。"""
    try:
        return f"{float(value):.4f}"
    except Exception:
        return str(value or "暂无数据")


def _build_news_digest(news_items: list[dict[str, Any]], limit: int = 6) -> str:
    """整理新闻摘要，避免把过长内容直接塞给本地模型。"""
    if not news_items:
        return "最近24小时内暂无高相关真实新闻。"

    rows: list[str] = []
    for index, item in enumerate(news_items[:limit], start=1):
        rows.append(
            "\n".join(
                [
                    f"{index}. 标题：{item.get('title', '未命名新闻')}",
                    f"   来源：{item.get('source', '未知来源')}；时间：{item.get('publish_time', '未知时间')}",
                    f"   摘要：{item.get('summary', '暂无摘要')}",
                    f"   情绪：{item.get('sentiment_text', item.get('sentiment_label', '中性'))}"
                    f"；分数：{item.get('sentiment_score', 0)}",
                ]
            )
        )
    return "\n".join(rows)


def _build_kline_digest(kline_rows: list[dict[str, Any]] | None, limit: int = 8) -> str:
    """整理最近 K 线数据摘要，并生成可供 AI 使用的图表分析。"""
    if not kline_rows:
        return "暂无可用 K 线数据。"

    dataframe = pd.DataFrame(kline_rows).copy()
    if dataframe.empty or "close" not in dataframe.columns:
        return "暂无可用 K 线数据。"

    for column in ["open", "high", "low", "close", "volume"]:
        if column not in dataframe.columns:
            dataframe[column] = 0.0
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")
    dataframe = dataframe.dropna(subset=["close"]).reset_index(drop=True)
    if dataframe.empty:
        return "暂无可用 K 线数据。"

    close_series = dataframe["close"]
    latest_close = float(close_series.iloc[-1])
    previous_close = float(close_series.iloc[-2]) if len(close_series) > 1 else latest_close
    recent_5_start = float(close_series.iloc[-6]) if len(close_series) > 5 else float(close_series.iloc[0])
    recent_20_start = float(close_series.iloc[-21]) if len(close_series) > 20 else float(close_series.iloc[0])
    high_20 = float(dataframe["high"].tail(20).max()) if "high" in dataframe else float(close_series.tail(20).max())
    low_20 = float(dataframe["low"].tail(20).min()) if "low" in dataframe else float(close_series.tail(20).min())
    ma5 = float(close_series.tail(5).mean())
    ma10 = float(close_series.tail(10).mean())
    ma20 = float(close_series.tail(20).mean())

    def _pct_change(current: float, base: float) -> float:
        return 0.0 if base == 0 else (current - base) / base * 100

    latest_change_pct = _pct_change(latest_close, previous_close)
    recent_5_pct = _pct_change(latest_close, recent_5_start)
    recent_20_pct = _pct_change(latest_close, recent_20_start)
    range_position = 0.0 if high_20 == low_20 else (latest_close - low_20) / (high_20 - low_20) * 100
    ma_relation = "均线上方"
    if latest_close < ma5 and latest_close < ma10 and latest_close < ma20:
        ma_relation = "主要均线下方"
    elif latest_close < ma5 or latest_close < ma10:
        ma_relation = "短期均线附近偏弱"
    elif latest_close > ma5 and latest_close > ma10 and latest_close > ma20:
        ma_relation = "主要均线上方"

    technical_lines = [
        "图表技术摘要：",
        f"- 最新收盘/净值：{latest_close:.4f}，上一周期变化：{latest_change_pct:+.2f}%。",
        f"- 近5周期涨跌：{recent_5_pct:+.2f}%；近20周期涨跌：{recent_20_pct:+.2f}%。",
        f"- 近20周期区间：低点 {low_20:.4f} / 高点 {high_20:.4f}，当前位置约处于区间 {range_position:.1f}% 分位。",
        f"- MA5={ma5:.4f}，MA10={ma10:.4f}，MA20={ma20:.4f}，当前价格位于{ma_relation}。",
        f"- 数据来源：{dataframe.iloc[-1].get('source_provider', '未知来源')}；最近数据日期：{dataframe.iloc[-1].get('datetime', '未知日期')}。",
    ]

    rows: list[str] = ["最近明细数据："]
    for item in kline_rows[-limit:]:
        rows.append(
            f"{item.get('datetime', '未知日期')}: "
            f"open={_format_number(item.get('open'))}, "
            f"high={_format_number(item.get('high'))}, "
            f"low={_format_number(item.get('low'))}, "
            f"close={_format_number(item.get('close'))}, "
            f"volume={_format_number(item.get('volume'))}"
        )
    return "\n".join(technical_lines + rows)


def build_ai_analysis_prompt(
    asset_detail: dict[str, Any],
    news_items: list[dict[str, Any]],
    sentiment_result: dict[str, Any],
    trend_result: dict[str, Any],
    kline_rows: list[dict[str, Any]] | None = None,
) -> str:
    """构造给 Ollama 的投资分析提示词。"""
    return f"""
你是一个谨慎的中文投资研究助手。请基于下面的真实行情、真实新闻和规则分析结果，输出辅助分析。

重要要求：
1. 不要承诺收益，不要给确定性买卖建议。
2. 如果新闻样本不足，请明确说明可信度较低。
3. 必须结合“图表技术摘要”分析趋势、均线、区间位置和短期波动，不要只复述新闻。
4. 输出必须简洁、可执行、偏投研风格。
5. 结尾必须包含：本工具仅提供信息整理与辅助分析，不构成投资建议。

资产信息：
- 名称：{asset_detail.get('name', '暂无数据')}
- 代码：{asset_detail.get('symbol', '暂无数据')}
- 市场：{asset_detail.get('market', '暂无数据')}
- 类型：{asset_detail.get('asset_type', '暂无数据')}
- 主题：{asset_detail.get('theme', '暂无数据')}
- 最新价格/净值：{asset_detail.get('price', '暂无数据')}
- 涨跌幅：{asset_detail.get('pct_change', '暂无数据')}%
- 风险等级：{asset_detail.get('risk_level', '暂无数据')}
- 简介：{asset_detail.get('description', '暂无数据')}

规则情绪汇总：
- 正面新闻数：{sentiment_result.get('positive_count', 0)}
- 中性新闻数：{sentiment_result.get('neutral_count', 0)}
- 负面新闻数：{sentiment_result.get('negative_count', 0)}
- 平均情绪分数：{sentiment_result.get('average_sentiment_score', sentiment_result.get('average_score', 0))}
- 整体情绪：{sentiment_result.get('overall_conclusion', '中性')}

规则短期判断：
- 判断：{trend_result.get('trend_label', '震荡')}
- 信心：{trend_result.get('confidence_hint', '低')}
- 原因：{trend_result.get('reason_text', '暂无原因')}

最近 K 线摘要：
{_build_kline_digest(kline_rows)}

最近24小时真实相关新闻：
{_build_news_digest(news_items)}

请按以下结构输出：
一、核心结论
二、图表/净值走势分析
三、主要利多因素
四、主要利空/风险因素
五、短期观察重点
六、适合什么类型的投资者关注
七、免责声明
""".strip()


def list_ollama_models(base_url: str | None = None, timeout: int = 3) -> dict[str, Any]:
    """读取本地 Ollama 已安装模型列表。"""
    endpoint_base = (base_url or DEFAULT_OLLAMA_BASE_URL).strip().rstrip("/")
    try:
        response = requests.get(f"{endpoint_base}/api/tags", timeout=timeout)
        response.raise_for_status()
        data = response.json()
        models = [
            str(item.get("name") or item.get("model") or "").strip()
            for item in data.get("models", [])
            if str(item.get("name") or item.get("model") or "").strip()
        ]
        return {"success": True, "models": models, "error": ""}
    except Exception as exc:
        return {"success": False, "models": [], "error": f"{type(exc).__name__}: {exc}"}


def analyze_with_ollama(
    asset_detail: dict[str, Any],
    news_items: list[dict[str, Any]],
    sentiment_result: dict[str, Any],
    trend_result: dict[str, Any],
    kline_rows: list[dict[str, Any]] | None = None,
    model: str | None = None,
    base_url: str | None = None,
    timeout: int = 90,
) -> dict[str, Any]:
    """调用本地 Ollama API 生成 AI 辅助分析。"""
    selected_model = (model or DEFAULT_OLLAMA_MODEL).strip()
    endpoint_base = (base_url or DEFAULT_OLLAMA_BASE_URL).strip().rstrip("/")
    if not selected_model:
        return {"success": False, "error": "请先填写 Ollama 模型名称。", "content": ""}
    if not endpoint_base:
        return {"success": False, "error": "请先填写 Ollama API 地址。", "content": ""}

    prompt = build_ai_analysis_prompt(
        asset_detail=asset_detail,
        news_items=news_items,
        sentiment_result=sentiment_result,
        trend_result=trend_result,
        kline_rows=kline_rows,
    )
    request_url = f"{endpoint_base}/api/generate"
    payload = {
        "model": selected_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
        },
    }

    try:
        response = requests.post(request_url, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        content = str(data.get("response", "")).strip()
        if not content:
            return {"success": False, "error": "Ollama 返回为空，请检查模型是否可用。", "content": ""}
        return {
            "success": True,
            "content": content,
            "model": selected_model,
            "base_url": endpoint_base,
            "prompt": prompt,
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": f"无法连接本地 Ollama：{endpoint_base}。请确认已运行 `ollama serve`。",
            "content": "",
        }
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Ollama 响应超时，请稍后重试或换用更轻量模型。", "content": ""}
    except Exception as exc:
        return {"success": False, "error": f"Ollama 调用失败：{type(exc).__name__}: {exc}", "content": ""}
