"""Streamlit 页面组件封装。"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from config import DISCLAIMER_TEXT

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError:  # pragma: no cover - 缺少 plotly 时允许页面降级
    go = None
    make_subplots = None


def inject_global_styles() -> None:
    """注入轻量全局样式，提升页面层级与产品感。"""
    st.markdown(
        """
        <style>
        .main .block-container {padding-top: 1.2rem; padding-bottom: 1.4rem; max-width: 1240px;}
        .app-hero {padding: 1rem 1.1rem 0.7rem 1.1rem; border: 1px solid #dbe3f0; border-radius: 14px;
            background: linear-gradient(135deg, #f8fafc 0%, #eef3ff 100%);}
        .app-hero-title {font-size: 1.6rem; font-weight: 700; color: #0f172a; margin-bottom: 0.2rem;}
        .app-hero-sub {font-size: 0.95rem; color: #475569; margin-bottom: 0.5rem;}
        .asset-card {padding: 1rem 1.1rem; border: 1px solid #dbe3f0; border-radius: 14px; background: #ffffff;}
        .asset-head {display:flex; justify-content:space-between; gap:16px; align-items:flex-start;}
        .asset-name {font-size:1.18rem; font-weight:700; color:#0f172a;}
        .asset-meta {color:#64748b; font-size:0.88rem; margin-top: 0.1rem;}
        .asset-price {font-size:2rem; font-weight:800; line-height:1; text-align:right;}
        .asset-change {font-size:0.9rem; font-weight:600; margin-top:0.35rem; text-align:right;}
        .color-up {color:#e11d48;} .color-down {color:#059669;} .color-flat {color:#64748b;}
        .badge-wrap {display:flex; flex-wrap:wrap; gap:8px; margin: 0.2rem 0 0.4rem 0;}
        .badge-item {padding: 0.22rem 0.55rem; border-radius: 999px; font-size:0.76rem; font-weight:600;
            border:1px solid #d5deee; background:#f8fafc; color:#334155;}
        .panel-title {font-size:1.06rem; font-weight:700; color:#0f172a; margin-bottom:0.1rem;}
        .panel-subtitle {font-size:0.83rem; color:#64748b; margin-bottom:0.55rem;}
        .trend-card {padding: 1rem; border-radius: 12px; border:1px solid #dbe3f0; background:#ffffff;}
        .trend-main {font-size: 1.22rem; font-weight: 800; margin-bottom: 0.35rem;}
        .trend-meta {color:#475569; font-size:0.9rem; margin-bottom:0.35rem;}
        .news-sentiment {display:inline-block; padding:0.18rem 0.45rem; border-radius:999px; font-size:0.74rem;
            font-weight:700;}
        .s-pos {background:#ffe4ea; color:#be123c;}
        .s-neu {background:#eff3f9; color:#334155;}
        .s-neg {background:#e7fbf4; color:#065f46;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _to_float(value: Any, default: float = 0.0) -> float:
    """安全转 float。"""
    try:
        if value in (None, "", "None"):
            return default
        return float(value)
    except Exception:
        return default


def _change_class(change_value: float) -> str:
    """根据涨跌返回颜色类名。"""
    if change_value > 0:
        return "color-up"
    if change_value < 0:
        return "color-down"
    return "color-flat"


def render_header(title: str, subtitle: str) -> None:
    """渲染页面头部。"""
    st.markdown(
        f"""
        <div class="app-hero">
          <div class="app-hero-title">{title}</div>
          <div class="app-hero-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_disclaimer() -> None:
    """渲染全局免责声明。"""
    st.warning(DISCLAIMER_TEXT)


def render_section_title(title: str) -> None:
    """渲染统一样式的小节标题。"""
    st.subheader(title)


def render_info_card(data: dict[str, Any]) -> None:
    """以表格方式渲染信息卡片。"""
    if not data:
        st.info("暂无可展示的数据。")
        return
    dataframe = pd.DataFrame(list(data.items()), columns=["字段", "内容"])
    st.dataframe(dataframe, use_container_width=True, hide_index=True)


def render_tag_list(tags: list[str] | str) -> None:
    """渲染标签列表。"""
    if isinstance(tags, str):
        tags = [item.strip() for item in tags.split(",") if item.strip()]
    if not tags:
        st.info("暂无主题数据。")
        return
    st.markdown(" / ".join(f"`{tag}`" for tag in tags))


def render_market_overview(asset_detail: dict[str, Any]) -> None:
    """渲染顶部行情概览。"""
    render_section_title("顶部行情区")
    price = _to_float(asset_detail.get("price"))
    change = _to_float(asset_detail.get("change"))
    pct_change = _to_float(asset_detail.get("pct_change"))
    trend_class = _change_class(change)

    with st.container(border=True):
        st.markdown(
            f"""
            <div class="asset-card">
              <div class="asset-head">
                <div>
                  <div class="asset-name">{asset_detail.get("name", "暂无数据")}</div>
                  <div class="asset-meta">代码：{asset_detail.get("symbol", "暂无数据")} ｜ 市场：{asset_detail.get("market", "暂无数据")}</div>
                </div>
                <div>
                  <div class="asset-price {trend_class}">{price:,.4f}</div>
                  <div class="asset-change {trend_class}">{change:+,.4f} ({pct_change:+.2f}%)</div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        extra_columns = st.columns(6)
        extra_columns[0].metric("成交量", f"{_to_float(asset_detail.get('volume')):,.0f}")
        extra_columns[1].metric("成交额", f"{_to_float(asset_detail.get('turnover')):,.0f}")
        extra_columns[2].metric("振幅", f"{_to_float(asset_detail.get('amplitude')):,.2f}")
        extra_columns[3].metric("风险等级", str(asset_detail.get("risk_level", "暂无数据")))
        extra_columns[4].metric("标签", str(asset_detail.get("asset_type", "暂无数据")))
        extra_columns[5].metric("主题", str(asset_detail.get("theme", "综合"))[:14])


def render_asset_summary(asset_detail: dict[str, Any]) -> None:
    """渲染资产摘要（兼容命名）。"""
    render_market_overview(asset_detail)


def _prepare_kline_dataframe(kline_rows: list[dict[str, Any]]) -> pd.DataFrame:
    """整理 K 线数据，并补齐基础数值列。"""
    dataframe = pd.DataFrame(kline_rows).copy()
    if dataframe.empty:
        return dataframe

    dataframe["datetime"] = dataframe["datetime"].astype(str)
    for column in ["open", "high", "low", "close", "volume"]:
        if column not in dataframe.columns:
            dataframe[column] = None
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")
    dataframe = dataframe.sort_values("datetime").reset_index(drop=True)
    return dataframe


def _has_complete_ohlc(dataframe: pd.DataFrame) -> bool:
    """判断是否具备完整的 OHLC 数据。"""
    if dataframe.empty:
        return False
    required_columns = {"open", "high", "low", "close"}
    if not required_columns.issubset(dataframe.columns):
        return False
    return not dataframe[list(required_columns)].isna().any().any()


def _build_demo_ohlc(dataframe: pd.DataFrame) -> pd.DataFrame:
    """仅有收盘价时生成演示用 OHLC 数据，避免页面空白。"""
    demo_df = dataframe.copy()
    demo_df["prev_close"] = demo_df["close"].shift(1).fillna(demo_df["close"])
    body_base = (demo_df["close"] - demo_df["prev_close"]).abs().replace(0, pd.NA)
    body_base = body_base.fillna(demo_df["close"].abs() * 0.003).clip(lower=0.0001)
    demo_df["open"] = demo_df["prev_close"]
    demo_df["high"] = demo_df[["open", "close"]].max(axis=1) + body_base * 0.55
    demo_df["low"] = demo_df[["open", "close"]].min(axis=1) - body_base * 0.55
    return demo_df.drop(columns=["prev_close"])


def _get_recent_price_range(dataframe: pd.DataFrame) -> tuple[float | None, float | None]:
    """根据当前显示数据自动计算更紧凑的 Y 轴范围。"""
    if dataframe.empty:
        return None, None

    visible_df = dataframe
    price_low = visible_df["low"].min(skipna=True)
    price_high = visible_df["high"].max(skipna=True)
    if pd.isna(price_low) or pd.isna(price_high):
        price_low = visible_df["close"].min(skipna=True)
        price_high = visible_df["close"].max(skipna=True)
    if pd.isna(price_low) or pd.isna(price_high):
        return None, None

    price_span = max(price_high - price_low, abs(price_high) * 0.001, 0.0001)
    padding_ratio = 0.025 if price_span / max(abs(price_high), 0.0001) > 0.08 else 0.015
    padding = max(price_span * padding_ratio, abs(price_high) * 0.003, 0.0001)

    lower_bound = max(price_low - padding, 0.0) if price_low >= 0 else price_low - padding
    upper_bound = price_high + padding
    if lower_bound >= upper_bound:
        return None, None
    return float(lower_bound), float(upper_bound)


def render_kline_chart(kline_rows: list[dict[str, Any]]) -> None:
    """渲染 K 线图与成交量。"""
    render_section_title("图表区")
    panel = st.container(border=True)
    with panel:
        st.markdown('<div class="panel-title">价格走势与成交量</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-subtitle">支持 K 线/趋势 + MA5/MA10/MA20 + 成交量</div>', unsafe_allow_html=True)
    if not kline_rows:
        with panel:
            st.info("暂无 K 线数据。")
        return

    dataframe = _prepare_kline_dataframe(kline_rows)
    if dataframe.empty or dataframe["close"].isna().all():
        with panel:
            st.info("暂无可用于绘图的价格数据。")
        return

    has_complete_ohlc = _has_complete_ohlc(dataframe)
    with panel:
        if not has_complete_ohlc:
            st.caption("当前数据源未提供完整 OHLC，已根据收盘价生成演示蜡烛图，便于观察趋势。")
            dataframe = _build_demo_ohlc(dataframe)

    dataframe["MA5"] = dataframe["close"].rolling(5).mean()
    dataframe["MA10"] = dataframe["close"].rolling(10).mean()
    dataframe["MA20"] = dataframe["close"].rolling(20).mean()
    dataframe["is_up"] = dataframe["close"] >= dataframe["open"]

    yaxis_min, yaxis_max = _get_recent_price_range(dataframe)
    rise_color = "#e11d48"
    fall_color = "#059669"
    neutral_color = "#94a3b8"
    volume_colors = dataframe["is_up"].map({True: rise_color, False: fall_color}).tolist()
    last_row = dataframe.iloc[-1]
    previous_close = float(dataframe.iloc[-2]["close"]) if len(dataframe) > 1 else float(last_row["open"])
    last_close = float(last_row["close"])
    last_change = last_close - previous_close
    last_pct_change = 0.0 if previous_close == 0 else last_change / previous_close * 100
    last_price_color = rise_color if last_change > 0 else fall_color if last_change < 0 else neutral_color

    if go is None or make_subplots is None:
        with panel:
            st.line_chart(dataframe.set_index("datetime")[["close", "MA5", "MA10", "MA20"]], height=420)
        return

    figure = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.025,
        row_heights=[0.82, 0.18],
    )
    figure.add_trace(
        go.Candlestick(
            x=dataframe["datetime"],
            open=dataframe["open"],
            high=dataframe["high"],
            low=dataframe["low"],
            close=dataframe["close"],
            name="K线",
            increasing_line_color=rise_color,
            increasing_fillcolor=rise_color,
            decreasing_line_color=fall_color,
            decreasing_fillcolor=fall_color,
            whiskerwidth=0.5,
            opacity=0.95,
        ),
        row=1,
        col=1,
    )
    for ma_name, color, width in [("MA5", "#f59e0b", 1.4), ("MA10", "#2563eb", 1.8), ("MA20", "#7c3aed", 2.1)]:
        figure.add_trace(
            go.Scatter(
                x=dataframe["datetime"],
                y=dataframe[ma_name],
                mode="lines",
                name=ma_name,
                line={"width": width, "color": color},
                connectgaps=False,
                hovertemplate=f"{ma_name}: %{{y:.4f}}<extra></extra>",
            ),
            row=1,
            col=1,
        )
    figure.add_trace(
        go.Scatter(
            x=[last_row["datetime"]],
            y=[last_close],
            mode="markers",
            name="最新价",
            marker={
                "size": 9,
                "color": last_price_color,
                "line": {"color": "#ffffff", "width": 1.4},
            },
            hovertemplate=(
                f"最新价: {last_close:.4f}<br>"
                f"涨跌额: {last_change:+.4f}<br>"
                f"涨跌幅: {last_pct_change:+.2f}%<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )
    figure.add_trace(
        go.Bar(
            x=dataframe["datetime"],
            y=dataframe["volume"],
            name="成交量",
            marker={"color": volume_colors, "line": {"width": 0}},
            opacity=0.85,
            hovertemplate="成交量: %{y:,.0f}<extra></extra>",
        ),
        row=2,
        col=1,
    )
    figure.add_hline(
        y=last_close,
        row=1,
        col=1,
        line_width=1,
        line_dash="dot",
        line_color=last_price_color,
        opacity=0.6,
    )
    figure.add_annotation(
        x=1,
        y=last_close,
        xref="x domain",
        yref="y",
        text=f"最新价 {last_close:.4f}",
        showarrow=False,
        xanchor="left",
        yanchor="middle",
        font={"color": "#ffffff", "size": 11},
        bgcolor=last_price_color,
        bordercolor=last_price_color,
        borderpad=4,
    )

    figure.update_yaxes(
        range=[yaxis_min, yaxis_max] if yaxis_min is not None and yaxis_max is not None else None,
        row=1,
        col=1,
        gridcolor="rgba(148, 163, 184, 0.16)",
        tickformat=".4f",
        fixedrange=True,
        automargin=True,
        nticks=8,
    )
    figure.update_yaxes(
        row=2,
        col=1,
        gridcolor="rgba(148, 163, 184, 0.12)",
        separatethousands=True,
        fixedrange=True,
        automargin=True,
        nticks=4,
    )
    figure.update_xaxes(
        row=1,
        col=1,
        showgrid=False,
        showspikes=True,
        spikecolor="rgba(59, 130, 246, 0.5)",
        spikemode="across",
    )
    figure.update_xaxes(row=2, col=1, showgrid=False)
    figure.update_layout(
        height=900,
        xaxis_rangeslider_visible=False,
        margin={"l": 8, "r": 8, "t": 6, "b": 6},
        hovermode="x unified",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.01,
            "xanchor": "left",
            "x": 0,
        },
        plot_bgcolor="rgba(255, 255, 255, 0)",
        paper_bgcolor="rgba(255, 255, 255, 0)",
        font={"size": 12},
        bargap=0.15,
    )
    with panel:
        st.plotly_chart(figure, use_container_width=True)
        delta_text = f"{last_change:+.4f} ({last_pct_change:+.2f}%)"
        st.caption(f"最新价：{last_close:.4f} | 较上一周期 {delta_text}")


def render_news_list(news_items: list[dict[str, Any]]) -> None:
    """渲染新闻列表。"""
    if not news_items:
        st.info("暂无新闻数据。")
        return

    label_to_class = {"偏多": "s-pos", "中性": "s-neu", "偏空": "s-neg"}
    for item in news_items:
        with st.container(border=True):
            st.markdown(f"**{item.get('title', '未命名新闻')}**")
            st.caption(
                f"来源：{item.get('source', '未知来源')} | "
                f"时间：{item.get('publish_time', '未知时间')}"
            )
            st.write(item.get("summary", "暂无摘要。"))
            sentiment_text = str(item.get("sentiment_text", "中性"))
            sentiment_score = _to_float(item.get("sentiment_score"))
            sentiment_class = label_to_class.get(sentiment_text, "s-neu")
            st.markdown(
                f"""
                <span class="news-sentiment {sentiment_class}">{sentiment_text}</span>
                <span style="color:#64748b; font-size:0.80rem; margin-left:8px;">情绪分数 {sentiment_score:.3f}</span>
                """,
                unsafe_allow_html=True,
            )
            matched_keywords = item.get("matched_keywords", [])
            if matched_keywords:
                st.caption(f"命中关键词：{', '.join(matched_keywords)}")
            if item.get("url"):
                st.markdown(f"[查看链接]({item.get('url')})")


def render_news_cards(news_items: list[dict[str, Any]]) -> None:
    """渲染新闻卡片（兼容命名）。"""
    render_news_list(news_items)


def render_text_block(title: str, content: str) -> None:
    """渲染简单文本区域。"""
    render_section_title(title)
    st.write(content)


def render_key_metrics(metrics: dict[str, Any]) -> None:
    """渲染关键指标。"""
    if not metrics:
        st.info("暂无关键指标。")
        return
    columns = st.columns(len(metrics))
    for index, (label, value) in enumerate(metrics.items()):
        columns[index].metric(label, value)


def render_message_card(message: str, kind: str = "info") -> None:
    """渲染统一消息卡片。"""
    if not message:
        return
    if kind == "success":
        st.success(message)
    elif kind == "warning":
        st.warning(message)
    elif kind == "error":
        st.error(message)
    else:
        st.info(message)


def render_data_source_notice(quote_provider: str, quote_data_source: str, news_provider: str, news_data_source: str, fallback_used: bool) -> None:
    """渲染数据来源 Badge。"""
    fallback_text = "是" if fallback_used else "否"
    st.markdown(
        f"""
        <div class="badge-wrap">
          <span class="badge-item">行情来源：{quote_provider}（{quote_data_source}）</span>
          <span class="badge-item">新闻来源：{news_provider}（{news_data_source}）</span>
          <span class="badge-item">Fallback：{fallback_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_source_badges(quote_provider: str, quote_data_source: str, news_provider: str, news_data_source: str, fallback_used: bool) -> None:
    """渲染数据来源标签（兼容命名）。"""
    render_data_source_notice(
        quote_provider=quote_provider,
        quote_data_source=quote_data_source,
        news_provider=news_provider,
        news_data_source=news_data_source,
        fallback_used=fallback_used,
    )


def render_sentiment_summary(sentiment_result: dict[str, Any]) -> None:
    """渲染情绪汇总面板。"""
    render_section_title("情绪汇总")
    render_key_metrics(
        {
            "正面新闻数": sentiment_result.get("positive_count", 0),
            "中性新闻数": sentiment_result.get("neutral_count", 0),
            "负面新闻数": sentiment_result.get("negative_count", 0),
            "平均情绪分数": f"{_to_float(sentiment_result.get('average_sentiment_score')):.3f}",
            "整体情绪结论": sentiment_result.get("overall_conclusion", "中性"),
        }
    )
    st.caption(sentiment_result.get("summary_text", "暂无情绪总结。"))


def render_trend_card(trend_result: dict[str, Any], risk_notice: str | None = None) -> None:
    """渲染短期判断结论卡片。"""
    trend_label = str(trend_result.get("trend_label", "震荡"))
    confidence_hint = str(trend_result.get("confidence_hint", "低"))
    reason_text = str(trend_result.get("reason_text", "暂无原因说明。"))
    trend_class = "color-flat"
    if trend_label == "偏涨":
        trend_class = "color-up"
    elif trend_label == "偏弱":
        trend_class = "color-down"

    render_section_title("短期判断")
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="trend-card">
              <div class="trend-main {trend_class}">{trend_label}</div>
              <div class="trend-meta">信心提示：{confidence_hint}</div>
              <div style="font-size:0.92rem; color:#334155;">{reason_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if risk_notice:
            st.warning(risk_notice)


def render_recovery_result_panel(result: dict[str, Any]) -> None:
    """渲染补仓计算结果面板。"""
    position_status = result.get("position_status", {})
    mode_result = result.get("mode_result", {})

    render_section_title("当前持仓状态")
    render_key_metrics(
        {
            "实时净值": f"{_to_float(position_status.get('实时净值')):.4f}",
            "当前市值": f"{_to_float(position_status.get('当前市值')):,.2f}",
            "持仓总成本": f"{_to_float(position_status.get('持仓总成本')):,.2f}",
            "当前总盈亏": f"{_to_float(position_status.get('当前总盈亏')):,.2f}",
            "当前盈亏率": f"{_to_float(position_status.get('当前盈亏率')) * 100:.2f}%",
        }
    )

    render_section_title("计算结果")
    result_cols = st.columns(4)
    preferred_keys = ["新增份额", "补仓后总份额", "补仓后平均成本", "回本所需涨幅"]
    shown_count = 0
    for key in preferred_keys:
        if key in mode_result and shown_count < 4:
            result_cols[shown_count].metric(key, mode_result.get(key))
            shown_count += 1
    if shown_count == 0:
        render_info_card(
            {key: value for key, value in mode_result.items() if key not in {"scenario_analysis", "risk_notices"}}
        )

    scenario_analysis = mode_result.get("scenario_analysis")
    if scenario_analysis is not None:
        render_section_title("情景分析")
        st.dataframe(scenario_analysis, use_container_width=True, hide_index=True)

    render_section_title("风险提示")
    risk_notices = mode_result.get("risk_notices", ["当前模式暂无额外风险提示。"])
    for notice in risk_notices:
        st.warning(notice)


def render_analysis_history(history_rows: list[dict[str, Any]]) -> None:
    """渲染最近分析记录。"""
    if not history_rows:
        st.info("暂无最近分析记录。")
        return
    dataframe = pd.DataFrame(history_rows)
    dataframe = dataframe.rename(
        columns={
            "query_text": "查询时间/输入",
            "symbol": "代码",
            "market": "市场",
            "trend_label": "短期判断",
            "confidence_hint": "信心提示",
            "source_provider": "来源",
            "data_source": "数据类型",
            "created_at": "时间",
        }
    )
    st.dataframe(dataframe, use_container_width=True, hide_index=True)
