"""Streamlit 应用主入口。"""

from __future__ import annotations

import streamlit as st

from analysis.recovery_calc import calculate_recovery_plan
from analysis.sentiment import analyze_news_list, summarize_sentiment
from analysis.trend_judge import judge_short_term_trend
from collectors.fund_info import list_market_assets, resolve_asset_input
from collectors.market_router import get_asset_detail, get_kline
from collectors.news_fetcher import get_asset_news
from config import (
    ALPHA_VANTAGE_API_KEY,
    APP_TITLE,
    DEFAULT_INTERVAL_OPTIONS,
    DEFAULT_MARKETS,
    TUSHARE_TOKEN,
    TWELVE_DATA_API_KEY,
)
from database import (
    get_recent_analysis_history,
    init_database,
    save_analysis_history,
    save_asset_quote,
    save_kline_data,
    save_news_articles,
)
from ui.components import (
    render_analysis_history,
    render_data_source_notice,
    render_disclaimer,
    render_header,
    render_info_card,
    inject_global_styles,
    render_kline_chart,
    render_market_overview,
    render_message_card,
    render_news_list,
    render_recovery_result_panel,
    render_section_title,
    render_sentiment_summary,
    render_tag_list,
    render_trend_card,
)


def setup_page() -> None:
    """配置页面基础信息并初始化数据库。"""
    st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")
    inject_global_styles()
    init_database()


def _get_api_notice() -> str | None:
    """返回当前 API 配置提示。"""
    if not any([TUSHARE_TOKEN, ALPHA_VANTAGE_API_KEY, TWELVE_DATA_API_KEY]):
        return "未配置真实 API，当前显示示例数据。"
    return None


def render_asset_analysis_tab() -> None:
    """渲染多市场资产分析页签内容。"""
    render_section_title("查询控制区")
    st.caption("选择市场与代表资产，系统将优先获取真实数据，失败时自动回退到示例数据。")
    api_notice = _get_api_notice()
    if api_notice:
        render_message_card(api_notice, kind="warning")

    with st.container(border=True):
        control_col1, control_col2, control_col3 = st.columns([1, 1.3, 1.2])
        with control_col1:
            market = st.selectbox("市场选择", DEFAULT_MARKETS)
        market_assets = list_market_assets(market)
        asset_option_map = {f"{item['name']}（{item['symbol']}）": item["symbol"] for item in market_assets}
        selected_labels = list(asset_option_map.keys()) or ["暂无资产"]
        with control_col2:
            selected_label = st.selectbox("代表资产", selected_labels)
            default_symbol = asset_option_map.get(selected_label, "")
        with control_col3:
            manual_symbol = st.text_input("代码输入（可选）", placeholder=f"例如：{default_symbol or 'NVDA'}")

        interval_label = st.radio("图表周期", list(DEFAULT_INTERVAL_OPTIONS.keys()), horizontal=True)
        query_text = manual_symbol.strip() or default_symbol
        trigger_analysis = st.button("开始分析", key="asset_analysis", use_container_width=True)

    if trigger_analysis:
        try:
            resolved = resolve_asset_input(market, query_text)
            if not resolved.get("success"):
                render_message_card(resolved.get("message", "未找到可分析资产。"), kind="warning")
                return

            asset_meta = resolved["asset"]
            asset_detail = get_asset_detail(market, asset_meta["symbol"], asset_meta)
            kline_rows = get_kline(market, asset_meta["symbol"], asset_meta, DEFAULT_INTERVAL_OPTIONS[interval_label])
            news_result = get_asset_news(asset_detail)
            analyzed_news = analyze_news_list(news_result.get("items", []))
            sentiment_result = summarize_sentiment(analyzed_news)
            trend_result = judge_short_term_trend(asset_detail, sentiment_result, len(analyzed_news))

            render_market_overview(asset_detail)
            render_data_source_notice(
                asset_detail.get("source_provider", "mock"),
                asset_detail.get("data_source", "mock"),
                news_result.get("source_provider", "mock"),
                news_result.get("data_source", "mock"),
                bool(asset_detail.get("fallback_used") or news_result.get("fallback_used")),
            )

            render_kline_chart(kline_rows)

            detail_col, theme_col = st.columns([1.2, 0.8])
            with detail_col:
                render_section_title("资产基础信息")
                render_info_card(
                    {
                        "名称": asset_detail.get("name", "暂无数据"),
                        "代码": asset_detail.get("symbol", "暂无数据"),
                        "市场": asset_detail.get("market", "暂无数据"),
                        "资产类型": asset_detail.get("asset_type", "暂无数据"),
                        "风险等级": asset_detail.get("risk_level", "暂无数据"),
                        "简介": asset_detail.get("description", "暂无数据"),
                    }
                )
            with theme_col:
                render_section_title("主题标签")
                render_tag_list(asset_detail.get("theme", "综合"))

            render_section_title("新闻与情绪区")
            render_news_list(analyzed_news)

            render_sentiment_summary(sentiment_result)
            risk_notice = ""
            if sentiment_result.get("overall_conclusion") == "偏空":
                risk_notice = "当前新闻情绪偏空，建议控制仓位与节奏。"
            elif trend_result.get("confidence_hint") == "低":
                risk_notice = "当前信号一致性一般，建议结合更多信息再决策。"
            render_trend_card(trend_result, risk_notice=risk_notice)

            try:
                save_asset_quote(asset_detail)
                save_kline_data(asset_detail["symbol"], market, DEFAULT_INTERVAL_OPTIONS[interval_label], kline_rows)
                save_news_articles(asset_detail["symbol"], market, asset_detail.get("theme", "综合"), analyzed_news)
                save_analysis_history(
                    query_text=query_text,
                    symbol=asset_detail["symbol"],
                    market=market,
                    trend_result=trend_result,
                    sentiment_summary=sentiment_result,
                    source_provider=asset_detail.get("source_provider", "mock"),
                    data_source=asset_detail.get("data_source", "mock"),
                )
            except Exception:
                render_message_card("本次结果未成功写入本地数据库，但页面分析结果仍可正常查看。", kind="warning")

            render_section_title("最近分析记录区")
            render_analysis_history(get_recent_analysis_history(limit=6))
        except Exception as exc:  # pragma: no cover - UI 兜底异常处理
            render_message_card(f"分析过程中发生异常：{exc}", kind="error")
    else:
        st.info("点击“开始分析”后，将展示多市场行情、K线、新闻情绪与短期判断。")
        render_section_title("最近分析记录区")
        render_analysis_history(get_recent_analysis_history(limit=6))


def render_recovery_tab() -> None:
    """渲染持仓补仓计算页签内容。"""
    st.caption("填写参数后可快速评估补仓方案，输入区与结果区已拆分。")
    render_section_title("输入参数区")
    with st.container(border=True):
        base_col1, base_col2 = st.columns(2)
        with base_col1:
            previous_nav = st.number_input("昨日单位净值（元）", min_value=0.0, value=1.2560, step=0.0001, format="%.4f")
            estimated_change_pct = st.number_input("当日预计涨跌幅（%）", value=-1.50, step=0.10, format="%.2f")
            holding_cost = st.number_input("当前持有成本价（元）", min_value=0.0, value=1.4200, step=0.0001, format="%.4f")
        with base_col2:
            holding_share = st.number_input("当前持有份额（份）", min_value=0.0, value=5000.0, step=100.0, format="%.2f")
            purchase_fee_rate = st.number_input("申购费率（%）", min_value=0.0, value=0.15, step=0.01, format="%.2f")
            mode = st.radio(
                "模式选择",
                ["模式1：输入补仓金额", "模式2：输入目标平均成本", "模式3：目标盈亏 + 预期反弹"],
            )

        mode_value = 0.0
        rebound_pct = None
        if mode == "模式1：输入补仓金额":
            mode_value = st.number_input("补仓金额（元）", min_value=0.0, value=2000.0, step=100.0, format="%.2f")
        elif mode == "模式2：输入目标平均成本":
            mode_value = st.number_input("目标平均成本（元）", min_value=0.0, value=1.3200, step=0.0001, format="%.4f")
        else:
            mode_value = st.number_input("目标总盈亏金额（元）", value=0.0, step=100.0, format="%.2f")
            rebound_pct = st.number_input("预期反弹幅度（%）", min_value=0.0, value=5.0, step=0.10, format="%.2f")

        trigger_recovery_calc = st.button("开始计算", key="recovery_calc", use_container_width=True)

    if trigger_recovery_calc:
        try:
            result = calculate_recovery_plan(
                previous_nav=previous_nav,
                estimated_change_pct=estimated_change_pct,
                holding_cost=holding_cost,
                holding_share=holding_share,
                purchase_fee_rate=purchase_fee_rate,
                mode=mode,
                mode_value=mode_value,
                rebound_pct=rebound_pct,
            )

            render_section_title("结果面板")
            with st.container(border=True):
                render_recovery_result_panel(result)

            with st.expander("查看本次输入摘要"):
                st.json(result.get("input_summary", {}), expanded=False)
        except Exception as exc:  # pragma: no cover - UI 兜底异常处理
            render_message_card(f"计算过程中发生异常：{exc}", kind="error")
    else:
        st.info("点击“开始计算”后，将展示当前持仓状态、补仓结果、情景分析与风险提示。")


def main() -> None:
    """应用主函数。"""
    setup_page()
    render_header(APP_TITLE, "A股 / 港股 / 美股 / 黄金 多市场联动分析与持仓补仓辅助")
    render_disclaimer()

    tab_analysis, tab_recovery = st.tabs(["多市场分析", "持仓补仓计算"])

    with tab_analysis:
        render_asset_analysis_tab()

    with tab_recovery:
        render_recovery_tab()


if __name__ == "__main__":
    main()
