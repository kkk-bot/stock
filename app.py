"""Streamlit 应用主入口。"""

from __future__ import annotations

import streamlit as st

from analysis.recovery_calc import calculate_recovery_plan
from analysis.sentiment import analyze_news_sentiment
from analysis.trend_judge import judge_short_term_trend
from collectors.fund_info import fetch_fund_info, fetch_fund_themes
from collectors.news_fetcher import fetch_related_news
from config import APP_TITLE
from database import init_database
from ui.components import (
    render_disclaimer,
    render_info_card,
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
    st.markdown("输入基金代码或名称，点击按钮查看第一阶段 mock 分析结果。")
    query = st.text_input("基金代码或基金名称", placeholder="例如：000001 或 新能源")

    if st.button("开始分析", use_container_width=True):
        try:
            basic_info = fetch_fund_info(query)
            themes = fetch_fund_themes(query)
            news_items = fetch_related_news(query)
            sentiment_result = analyze_news_sentiment(query)
            trend_result = judge_short_term_trend(query)

            render_section_title("基金基础信息")
            render_info_card(basic_info)

            render_section_title("基金所属板块 / 主题")
            render_tag_list(themes)

            render_section_title("相关新闻列表")
            render_news_list(news_items)

            render_section_title("情绪分析结果")
            st.write(
                f"情绪标签：{sentiment_result.get('label', '暂无')} | "
                f"情绪分值：{sentiment_result.get('score', '暂无')}"
            )
            st.write(sentiment_result.get("summary", "暂无说明。"))

            render_text_block("短期判断", trend_result.get("label", "暂无判断"))
            render_text_block("原因说明", trend_result.get("reason", "暂无原因说明"))
        except Exception as exc:  # pragma: no cover - UI 兜底异常处理
            st.error(f"分析过程中发生异常：{exc}")
    else:
        st.info("点击“开始分析”后，将展示完整的 mock 分析流程。")


def render_recovery_tab() -> None:
    """渲染持仓补仓计算页签内容。"""
    st.markdown("填写基础参数后，可查看第一阶段补仓辅助占位结果。")

    previous_nav = st.number_input("昨日单位净值", min_value=0.0, value=1.2560, step=0.0001, format="%.4f")
    estimated_change_pct = st.number_input("当日预计涨跌幅（%）", value=-1.50, step=0.10, format="%.2f")
    holding_cost = st.number_input("当前持有成本价", min_value=0.0, value=1.4200, step=0.0001, format="%.4f")
    holding_share = st.number_input("当前持有份额", min_value=0.0, value=5000.0, step=100.0, format="%.2f")
    purchase_fee_rate = st.number_input("申购费率（%）", min_value=0.0, value=0.15, step=0.01, format="%.2f")
    mode = st.selectbox("模式选择", ["模式一：固定金额补仓", "模式二：目标成本补仓", "模式三：分批计划补仓"])

    if st.button("开始计算", key="recovery_calc", use_container_width=True):
        try:
            result = calculate_recovery_plan(
                previous_nav=previous_nav,
                estimated_change_pct=estimated_change_pct,
                holding_cost=holding_cost,
                holding_share=holding_share,
                purchase_fee_rate=purchase_fee_rate,
                mode=mode,
            )

            render_text_block("结果展示", result.get("result_text", "暂无结果。"))

            render_section_title("情景分析")
            for scenario in result.get("scenario_analysis", []):
                st.markdown(f"- {scenario}")

            render_text_block("风险提示区域", result.get("risk_notice", "暂无风险提示。"))

            with st.expander("查看本次输入摘要"):
                st.json(result.get("input_summary", {}), expanded=False)
        except Exception as exc:  # pragma: no cover - UI 兜底异常处理
            st.error(f"计算过程中发生异常：{exc}")
    else:
        st.info("点击“开始计算”后，将展示补仓辅助的占位结果与情景分析。")


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
