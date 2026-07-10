"""Streamlit 应用主入口。"""

from __future__ import annotations

import streamlit as st

from analysis.recovery_calc import calculate_recovery_plan
from analysis.ollama_ai import DEFAULT_OLLAMA_BASE_URL, DEFAULT_OLLAMA_MODEL, analyze_with_ollama, list_ollama_models
from analysis.sentiment import analyze_news_list, summarize_sentiment
from analysis.trend_judge import judge_short_term_trend
from collectors.fund_info import (
    OVERVIEW_ANALYSIS_MARKETS,
    SINGLE_ANALYSIS_MARKETS,
    build_market_overview_summary,
    detect_input_market,
    get_fund_data,
    get_fund_kline,
    get_market_overview_targets,
    get_market_overview_theme,
    list_market_assets,
    resolve_asset_input,
)
from collectors.market_router import get_asset_detail, get_kline
from collectors.news_fetcher import get_asset_news
from config import (
    ALPHA_VANTAGE_API_KEY,
    APP_TITLE,
    DEFAULT_INTERVAL_OPTIONS,
    TUSHARE_TOKEN,
    TWELVE_DATA_API_KEY,
)
from database import (
    add_watchlist_asset,
    get_recent_analysis_history,
    init_database,
    list_watchlist_assets,
    remove_watchlist_asset,
    save_analysis_history,
    save_asset_quote,
    save_kline_data,
    save_news_articles,
)
from ui.components import (
    render_analysis_history,
    render_ai_analysis_result,
    render_data_source_notice,
    render_debug_panel,
    render_disclaimer,
    render_header,
    render_info_card,
    inject_global_styles,
    render_kline_chart,
    render_market_snapshot_table,
    render_market_overview,
    render_message_card,
    render_news_list,
    render_recovery_result_panel,
    render_section_title,
    render_sentiment_summary,
    render_tag_list,
    render_trend_card,
    render_watchlist_manager,
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


def _render_ollama_ai_section(
    section_key: str,
    asset_detail: dict,
    analyzed_news: list[dict],
    sentiment_result: dict,
    trend_result: dict,
    kline_rows: list[dict] | None = None,
) -> None:
    """渲染本地 Ollama AI 辅助分析区。"""
    render_section_title("AI 辅助分析（本地 Ollama）")
    result_key = f"{section_key}_ollama_result"
    with st.container(border=True):
        st.caption("该模块只在点击按钮时调用本地 Ollama API，不会改变上方规则分析结果。")
        config_col1, config_col2 = st.columns([1, 1.5])
        with config_col2:
            base_url = st.text_input("Ollama API 地址", value=DEFAULT_OLLAMA_BASE_URL, key=f"{section_key}_ollama_base_url")
        model_result = list_ollama_models(base_url)
        available_models = model_result.get("models", [])
        with config_col1:
            if available_models:
                default_index = available_models.index(DEFAULT_OLLAMA_MODEL) if DEFAULT_OLLAMA_MODEL in available_models else 0
                model = st.selectbox(
                    "Ollama 模型",
                    available_models,
                    index=default_index,
                    key=f"{section_key}_ollama_model_select",
                )
            else:
                model = st.text_input("Ollama 模型", value=DEFAULT_OLLAMA_MODEL, key=f"{section_key}_ollama_model")
        if not model_result.get("success"):
            st.caption(f"未读取到 Ollama 模型列表：{model_result.get('error', '未知错误')}。可手动填写模型名。")

        if st.button("生成 AI 分析", key=f"{section_key}_ollama_button", use_container_width=True):
            with st.spinner("正在调用本地 Ollama 生成分析..."):
                st.session_state[result_key] = analyze_with_ollama(
                    asset_detail=asset_detail,
                    news_items=analyzed_news,
                    sentiment_result=sentiment_result,
                    trend_result=trend_result,
                    kline_rows=kline_rows,
                    model=model,
                    base_url=base_url,
                )

        render_ai_analysis_result(st.session_state.get(result_key, {}))


def _render_single_asset_result(market: str, query_text: str, interval_label: str) -> None:
    """执行单个标的分析并渲染结果。"""
    if not str(query_text).strip():
        render_message_card("请先手动输入代码，或从快捷资产中选择一个常用标的。", kind="warning")
        return

    effective_market = detect_input_market(market, query_text)
    if effective_market != market:
        render_message_card(f"已将代码 {query_text.strip()} 识别为基金，当前进入基金分析分支。", kind="info")

    resolved = resolve_asset_input(effective_market, query_text)
    if not resolved.get("success"):
        render_message_card(resolved.get("message", "未找到可分析资产。"), kind="warning")
        return

    asset_meta = resolved["asset"]
    if effective_market == "基金":
        asset_detail = get_fund_data(asset_meta["symbol"], asset_meta)
        if not asset_detail:
            render_message_card("已识别为基金，但暂时未获取到完整数据。", kind="warning")
            return
        kline_rows = get_fund_kline(asset_meta["symbol"], asset_detail, DEFAULT_INTERVAL_OPTIONS[interval_label])
    else:
        asset_detail = get_asset_detail(effective_market, asset_meta["symbol"], asset_meta)
        kline_rows = get_kline(effective_market, asset_meta["symbol"], asset_meta, DEFAULT_INTERVAL_OPTIONS[interval_label])

    news_result = get_asset_news(asset_detail)
    analyzed_news = analyze_news_list(news_result.get("items", []))
    sentiment_result = summarize_sentiment(analyzed_news)
    trend_result = judge_short_term_trend(asset_detail, sentiment_result, len(analyzed_news))
    if effective_market == "基金" and trend_result.get("trend_label") == "偏涨":
        trend_result = {**trend_result, "trend_label": "偏强"}
    if not analyzed_news:
        trend_result = {
            **trend_result,
            "confidence_hint": "低",
            "reason_text": "最近24小时内暂无高相关金融新闻，当前判断主要基于净值走势、板块方向和已有基础信息。",
        }
    st.session_state["last_analyzed_asset"] = asset_detail
    st.session_state["last_analyzed_market"] = effective_market

    render_debug_panel(
        mode="单个标的分析",
        market=effective_market,
        symbol=asset_detail.get("symbol", ""),
        data_source=f"{asset_detail.get('source_provider', 'mock')} / {news_result.get('source_provider', 'mock')}",
    )
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
    if news_result.get("notice"):
        render_message_card(news_result["notice"], kind="warning")
    if news_result.get("relevance_debug"):
        st.caption(news_result["relevance_debug"])
    render_news_list(analyzed_news)
    render_sentiment_summary(sentiment_result)

    risk_notice = ""
    if sentiment_result.get("overall_conclusion") == "偏空":
        risk_notice = "当前新闻情绪偏空，建议控制仓位与节奏。"
    elif not analyzed_news:
        risk_notice = "最近24小时内暂无高相关金融新闻，以下结论主要参考净值走势与板块方向，可信度相对较低。"
    elif trend_result.get("confidence_hint") == "低":
        risk_notice = "当前信号一致性一般，建议结合更多信息再决策。"
    render_trend_card(trend_result, risk_notice=risk_notice)
    _render_ollama_ai_section(
        section_key=f"single_{asset_detail.get('market', '')}_{asset_detail.get('symbol', '')}",
        asset_detail=asset_detail,
        analyzed_news=analyzed_news,
        sentiment_result=sentiment_result,
        trend_result=trend_result,
        kline_rows=kline_rows,
    )

    try:
        save_asset_quote(asset_detail)
        save_kline_data(asset_detail["symbol"], effective_market, DEFAULT_INTERVAL_OPTIONS[interval_label], kline_rows)
        save_news_articles(asset_detail["symbol"], effective_market, asset_detail.get("theme", "综合"), analyzed_news)
        save_analysis_history(
            query_text=query_text,
            symbol=asset_detail["symbol"],
            market=effective_market,
            trend_result=trend_result,
            sentiment_summary=sentiment_result,
            source_provider=asset_detail.get("source_provider", "mock"),
            data_source=asset_detail.get("data_source", "mock"),
        )
    except Exception:
        render_message_card("本次结果未成功写入本地数据库，但页面分析结果仍可正常查看。", kind="warning")

    render_section_title("最近分析记录区")
    render_analysis_history(get_recent_analysis_history(limit=6))


def _render_market_overview_result(market: str) -> None:
    """执行市场总览分析并渲染结果。"""
    overview_targets = get_market_overview_targets(market)
    if not overview_targets:
        render_message_card("当前市场暂无可用于总览分析的代表资产。", kind="warning")
        return

    asset_details = [get_asset_detail(market, asset["symbol"], asset) for asset in overview_targets]
    summary_detail = build_market_overview_summary(market, asset_details)
    news_result = get_asset_news({"market": market, "symbol": "", "theme": get_market_overview_theme(market)})
    analyzed_news = analyze_news_list(news_result.get("items", []))
    sentiment_result = summarize_sentiment(analyzed_news)
    trend_result = judge_short_term_trend(summary_detail, sentiment_result, len(analyzed_news))
    if trend_result.get("trend_label") == "偏涨":
        trend_result = {**trend_result, "trend_label": "偏强"}
    if not analyzed_news:
        trend_result = {
            **trend_result,
            "confidence_hint": "低",
            "reason_text": "最近24小时内暂无高相关金融新闻，当前判断主要基于代表资产表现与市场方向。",
        }

    render_debug_panel(
        mode="市场总览分析",
        market=market,
        symbol=summary_detail.get("symbol", ""),
        data_source=f"{summary_detail.get('source_provider', 'mock')} / {news_result.get('source_provider', 'mock')}",
    )
    render_market_overview(summary_detail)
    render_data_source_notice(
        summary_detail.get("source_provider", "mock"),
        summary_detail.get("data_source", "mock"),
        news_result.get("source_provider", "mock"),
        news_result.get("data_source", "mock"),
        bool(summary_detail.get("fallback_used") or news_result.get("fallback_used")),
    )
    render_market_snapshot_table(asset_details)
    render_section_title("新闻与情绪区")
    if news_result.get("notice"):
        render_message_card(news_result["notice"], kind="warning")
    if news_result.get("relevance_debug"):
        st.caption(news_result["relevance_debug"])
    render_news_list(analyzed_news)
    render_sentiment_summary(sentiment_result)
    render_trend_card(
        trend_result,
        risk_notice="市场总览结论基于代表资产与相关新闻，仅用于辅助观察，不代表完整市场判断。",
    )
    _render_ollama_ai_section(
        section_key=f"overview_{market}",
        asset_detail=summary_detail,
        analyzed_news=analyzed_news,
        sentiment_result=sentiment_result,
        trend_result=trend_result,
        kline_rows=None,
    )

    try:
        for item in asset_details:
            save_asset_quote(item)
        save_news_articles(summary_detail["symbol"], market, summary_detail.get("theme", "综合"), analyzed_news)
        save_analysis_history(
            query_text=f"{market}市场总览",
            symbol=summary_detail["symbol"],
            market=market,
            trend_result=trend_result,
            sentiment_summary=sentiment_result,
            source_provider=summary_detail.get("source_provider", "mock"),
            data_source=summary_detail.get("data_source", "mock"),
        )
    except Exception:
        render_message_card("本次市场总览结果未成功写入本地数据库，但页面分析结果仍可正常查看。", kind="warning")

    render_section_title("最近分析记录区")
    render_analysis_history(get_recent_analysis_history(limit=6))


def render_asset_analysis_tab() -> None:
    """渲染多市场资产分析页签内容。"""
    render_section_title("查询控制区")
    st.caption("支持手动输入代码或使用快捷资产。若手动输入代码，系统将优先按输入代码分析；快捷资产用于保存常用基金与资产，便于快速选择。")
    api_notice = _get_api_notice()
    if api_notice:
        render_message_card(api_notice, kind="warning")

    analysis_mode = st.radio("分析模式", ["单个标的分析", "市场总览分析"], horizontal=True)

    with st.container(border=True):
        market_options = SINGLE_ANALYSIS_MARKETS if analysis_mode == "单个标的分析" else OVERVIEW_ANALYSIS_MARKETS
        watchlist_assets = list_watchlist_assets(market=None)
        control_col1, control_col2, control_col3 = st.columns([1, 1.3, 1.2])
        with control_col1:
            market = st.selectbox("市场选择", market_options)
        market_watchlist = [item for item in watchlist_assets if item.get("market") == market]
        watchlist_option_map = {
            f"{item['asset_name']}（{item['asset_code']}）": item["asset_code"]
            for item in market_watchlist
        }
        watchlist_labels = ["未选择快捷资产", *list(watchlist_option_map.keys())]
        input_key = "asset_code_input"
        selector_key = f"watchlist_selector_{market}"

        if input_key not in st.session_state:
            st.session_state[input_key] = ""

        def _fill_code_from_watchlist() -> None:
            """将快捷资产代码回填到输入框，不直接触发分析。"""
            selected = st.session_state.get(selector_key, "未选择快捷资产")
            selected_code = watchlist_option_map.get(selected, "")
            if selected_code:
                st.session_state[input_key] = selected_code

        with control_col2:
            if analysis_mode == "单个标的分析":
                st.selectbox(
                    "快捷资产（可选，点击后仅回填输入框）",
                    watchlist_labels,
                    key=selector_key,
                    on_change=_fill_code_from_watchlist,
                )
            else:
                st.markdown("**市场总览分析**")
                st.caption("该模式会直接分析当前市场，不需要输入单个代码。")
        with control_col3:
            if analysis_mode == "单个标的分析":
                manual_symbol = st.text_input("代码输入", key=input_key, placeholder="例如：012349、510300、700、NVDA、gold")
                st.caption("快捷资产只会自动填入输入框，不会直接触发分析；真正分析时仍以输入框内容为准。")
            else:
                manual_symbol = ""

        if analysis_mode == "单个标的分析":
            interval_label = st.radio("图表周期", list(DEFAULT_INTERVAL_OPTIONS.keys()), horizontal=True)
            query_text = manual_symbol.strip()
            trigger_analysis = st.button("开始分析", key="asset_analysis", use_container_width=True)
        else:
            interval_label = "日K"
            query_text = ""
            trigger_analysis = st.button("开始市场分析", key="market_overview_analysis", use_container_width=True)

    if trigger_analysis:
        try:
            if analysis_mode == "单个标的分析":
                st.session_state["last_analysis_request"] = {
                    "mode": "单个标的分析",
                    "market": market,
                    "query_text": query_text,
                    "interval_label": interval_label,
                }
                _render_single_asset_result(market, query_text, interval_label)
            else:
                st.session_state["last_analysis_request"] = {
                    "mode": "市场总览分析",
                    "market": market,
                    "query_text": "",
                    "interval_label": "日K",
                }
                _render_market_overview_result(market)
        except Exception as exc:  # pragma: no cover - UI 兜底异常处理
            render_message_card(f"分析过程中发生异常：{exc}", kind="error")
    else:
        last_request = st.session_state.get("last_analysis_request", {})
        can_restore_single = (
            last_request.get("mode") == "单个标的分析"
            and last_request.get("market") == market
            and str(last_request.get("query_text", "")).strip()
        )
        can_restore_overview = last_request.get("mode") == "市场总览分析" and last_request.get("market") == market
        if can_restore_single or can_restore_overview:
            try:
                if can_restore_single:
                    _render_single_asset_result(
                        last_request["market"],
                        last_request["query_text"],
                        last_request.get("interval_label", interval_label),
                    )
                else:
                    _render_market_overview_result(last_request["market"])
            except Exception as exc:  # pragma: no cover - UI 兜底异常处理
                render_message_card(f"恢复上一次分析结果时发生异常：{exc}", kind="error")
        else:
            st.info("选择单个标的分析或市场总览分析后，点击按钮即可生成结果。")
            render_section_title("最近分析记录区")
            render_analysis_history(get_recent_analysis_history(limit=6))

    if analysis_mode == "单个标的分析":
        latest_asset = st.session_state.get("last_analyzed_asset")
        latest_market = st.session_state.get("last_analyzed_market")
        if latest_asset and latest_market == market:
            add_button_label = f"添加到快捷资产：{latest_asset.get('name', '未命名资产')}（{latest_asset.get('symbol', '')}）"
            if st.button(add_button_label, key="add_watchlist_asset", use_container_width=True):
                if add_watchlist_asset(latest_asset):
                    st.session_state["watchlist_feedback"] = "已添加到快捷资产。"
                else:
                    st.session_state["watchlist_feedback"] = "该资产已存在于快捷资产，无需重复添加。"
                st.rerun()

        delete_code, delete_market = render_watchlist_manager(watchlist_assets, market)
        if delete_code and delete_market:
            if remove_watchlist_asset(delete_code, delete_market):
                st.session_state["watchlist_feedback"] = f"已删除快捷资产：{delete_code}"
            else:
                st.session_state["watchlist_feedback"] = f"未找到要删除的快捷资产：{delete_code}"
            st.rerun()

        feedback = st.session_state.pop("watchlist_feedback", "")
        if feedback:
            render_message_card(feedback, kind="success")


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
