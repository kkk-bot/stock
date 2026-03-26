"""Streamlit 应用主入口。"""

from __future__ import annotations

import streamlit as st

from analysis.recovery_calc import calculate_recovery_plan
from analysis.sentiment import analyze_news_sentiment
from analysis.trend_judge import judge_short_term_trend
from collectors.fund_info import search_fund
from collectors.news_fetcher import fetch_related_news
from config import APP_TITLE
from database import init_database
from ui.components import (
    render_disclaimer,
    render_info_card,
    render_key_metrics,
    render_message_card,
    render_news_list,
    render_section_title,
    render_tag_list,
    render_text_block,
)


def setup_page() -> None:
    """配置页面基础信息并初始化数据库。"""
    st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")
    init_database()


def render_fund_analysis_tab() -> None:
    """渲染基金分析页签内容。"""
    st.markdown("输入基金代码或基金名称，点击按钮查看内置示例基金的完整 mock 分析结果。")
    query = st.text_input("基金代码或基金名称", placeholder="例如：510300、纳指、半导体、新能源")

    if st.button("开始分析", use_container_width=True):
        try:
            search_result = search_fund(query)
            if not search_result.get("success"):
                render_message_card(search_result.get("message", ""), kind="warning")
                return

            fund = search_result["fund"]
            news_items = fetch_related_news(fund["fund_code"])
            sentiment_result = analyze_news_sentiment(fund["fund_code"])
            trend_result = judge_short_term_trend(fund["fund_code"])

            render_message_card(search_result.get("message", ""), kind="success")

            summary_col, detail_col = st.columns([1.15, 0.85])
            with summary_col:
                render_section_title("基金基础信息")
                render_info_card(
                    {
                        "基金名称": fund["fund_name"],
                        "基金代码": fund["fund_code"],
                        "基金类型": fund["fund_type"],
                        "相关市场": fund["market"],
                        "风险等级": fund["risk_level"],
                        "最近简要描述": fund["description"],
                    }
                )
            with detail_col:
                render_section_title("所属板块 / 主题")
                render_tag_list(fund.get("themes", []))

            render_section_title("相关新闻列表")
            render_news_list(news_items)

            render_text_block(
                "情绪总结",
                f"{sentiment_result.get('label', '暂无')}（情绪分值：{sentiment_result.get('score', 0)}）\n\n"
                f"{sentiment_result.get('summary', '暂无情绪总结。')}",
            )
            render_text_block("短期判断", trend_result.get("label", "暂无判断"))
            render_text_block("原因说明", trend_result.get("reason", "暂无原因说明"))
        except Exception as exc:  # pragma: no cover - UI 兜底异常处理
            render_message_card(f"分析过程中发生异常：{exc}", kind="error")
    else:
        st.info("点击“开始分析”后，将展示基金信息、相关新闻、情绪总结与短期判断。")


def render_recovery_tab() -> None:
    """渲染持仓补仓计算页签内容。"""
    st.markdown("填写持仓参数后，可根据不同补仓模式得到实际计算结果。")

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

    if st.button("开始计算", key="recovery_calc", use_container_width=True):
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

            position_status = result.get("position_status", {})
            render_section_title("当前持仓状态")
            render_key_metrics(
                {
                    "实时净值": f"{position_status.get('实时净值', 0):.4f}",
                    "当前市值": f"{position_status.get('当前市值', 0):,.2f}",
                    "持仓总成本": f"{position_status.get('持仓总成本', 0):,.2f}",
                    "当前总盈亏": f"{position_status.get('当前总盈亏', 0):,.2f}",
                    "当前盈亏率": f"{position_status.get('当前盈亏率', 0) * 100:.2f}%",
                }
            )

            mode_result = result.get("mode_result", {})
            render_section_title("计算结果")
            render_info_card(
                {key: value for key, value in mode_result.items() if key not in {"scenario_analysis", "risk_notices"}}
            )

            scenario_analysis = mode_result.get("scenario_analysis")
            if scenario_analysis is not None:
                render_section_title("情景分析")
                st.dataframe(scenario_analysis, use_container_width=True, hide_index=True)

            render_section_title("风险提示")
            for notice in mode_result.get("risk_notices", ["当前模式暂无额外风险提示。"]):
                st.markdown(f"- {notice}")

            with st.expander("查看本次输入摘要"):
                st.json(result.get("input_summary", {}), expanded=False)
        except Exception as exc:  # pragma: no cover - UI 兜底异常处理
            render_message_card(f"计算过程中发生异常：{exc}", kind="error")
    else:
        st.info("点击“开始计算”后，将展示当前持仓状态、补仓结果、情景分析与风险提示。")


def main() -> None:
    """应用主函数。"""
    setup_page()
    st.title(APP_TITLE)
    render_disclaimer()

    tab_analysis, tab_recovery = st.tabs(["基金分析", "持仓补仓计算"])

    with tab_analysis:
        render_disclaimer()
        render_fund_analysis_tab()

    with tab_recovery:
        render_disclaimer()
        render_recovery_tab()


if __name__ == "__main__":
    main()
