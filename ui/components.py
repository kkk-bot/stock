"""Streamlit 页面组件封装。"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from config import DISCLAIMER_TEXT


def render_disclaimer() -> None:
    """渲染全局免责声明。"""
    st.warning(DISCLAIMER_TEXT)


def render_section_title(title: str) -> None:
    """渲染统一样式的小节标题。"""
    st.subheader(title)


def render_info_card(data: dict[str, Any]) -> None:
    """以表格方式渲染基础信息卡片。"""
    if not data:
        st.info("暂无可展示的数据。")
        return

    dataframe = pd.DataFrame(list(data.items()), columns=["字段", "内容"])
    st.dataframe(dataframe, use_container_width=True, hide_index=True)


def render_tag_list(tags: list[str]) -> None:
    """渲染主题标签列表。"""
    if not tags:
        st.info("暂无主题数据。")
        return

    st.markdown(" / ".join(f"`{tag}`" for tag in tags))


def render_news_list(news_items: list[dict[str, Any]]) -> None:
    """渲染新闻列表。"""
    if not news_items:
        st.info("暂无新闻数据。")
        return

    for item in news_items:
        with st.container(border=True):
            st.markdown(f"**{item.get('title', '未命名新闻')}**")
            st.caption(
                f"来源：{item.get('source', '未知来源')} | "
                f"时间：{item.get('publish_time', item.get('published_at', '未知时间'))}"
            )
            st.write(item.get("summary", "暂无摘要。"))
            url = item.get("url")
            if url:
                st.markdown(f"[查看链接]({url})")


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
