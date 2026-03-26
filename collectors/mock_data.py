"""提供第一阶段使用的 mock 数据。"""

from __future__ import annotations

from typing import Any


def get_mock_fund_analysis(query: str) -> dict[str, Any]:
    """返回基金分析页面需要的 mock 数据。"""
    normalized_query = query.strip() or "示例基金"
    return {
        "basic_info": {
            "基金代码": "000001",
            "基金名称": f"{normalized_query}成长混合A",
            "基金类型": "混合型",
            "风险等级": "中高风险",
            "近一年收益": "+8.36%",
        },
        "themes": ["新能源", "人工智能", "高端制造"],
        "news": [
            {
                "title": "板块回暖带动成长风格基金关注度提升",
                "source": "模拟财经早报",
                "published_at": "2026-03-25 09:00",
            },
            {
                "title": "市场情绪修复，资金重新布局科技主题",
                "source": "模拟基金观察",
                "published_at": "2026-03-25 13:30",
            },
            {
                "title": "短线震荡延续，基金配置建议关注仓位节奏",
                "source": "模拟市场速递",
                "published_at": "2026-03-26 08:20",
            },
        ],
        "sentiment": {
            "label": "中性偏积极",
            "score": 0.63,
            "summary": "相关新闻整体偏正向，但仍夹杂震荡与波动预期，适合继续观察。",
        },
        "trend": {
            "label": "震荡偏涨",
            "reason": "板块热度回升、资金关注度提升，但短期仍需警惕波动反复。",
        },
    }


def get_mock_recovery_result() -> dict[str, Any]:
    """返回补仓计算页面需要的 mock 结果。"""
    return {
        "result_text": "示例结果：若按当前参数进行补仓，可在后续阶段展示预计摊薄成本与参考补仓金额。",
        "scenario_analysis": [
            "情景一：若当日小幅下跌，可观察是否接近计划补仓区间。",
            "情景二：若当日快速反弹，可减少追高式补仓频率。",
            "情景三：若继续震荡，可分批执行并控制总仓位。",
        ],
        "risk_notice": "补仓无法保证回本，过度加仓可能放大波动风险，请结合个人资金安排谨慎决策。",
    }
