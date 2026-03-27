"""提供第二阶段使用的基金与新闻 mock 数据。"""

from __future__ import annotations

import math
from typing import Any


MOCK_FUNDS: list[dict[str, Any]] = [
    {
        "fund_code": "012349",
        "fund_name": "天弘恒生科技ETF联接C",
        "fund_type": "QDII指数型",
        "themes": ["恒生科技", "港股科技", "香港科技股"],
        "market": "港股",
        "risk_level": "高风险",
        "description": "跟踪恒生科技指数，主要覆盖香港市场科技龙头，波动受港股科技情绪影响明显。",
    },
    {
        "fund_code": "510300",
        "fund_name": "沪深300ETF联接A",
        "fund_type": "指数型",
        "themes": ["沪深300", "宽基", "蓝筹"],
        "market": "A股",
        "risk_level": "中风险",
        "description": "跟踪沪深300指数，适合作为A股核心宽基配置参考。",
    },
    {
        "fund_code": "161017",
        "fund_name": "富国中证500指数增强",
        "fund_type": "指数增强型",
        "themes": ["中证500", "中盘成长", "宽基"],
        "market": "A股",
        "risk_level": "中高风险",
        "description": "偏中盘风格，波动较沪深300更高，适合关注成长弹性的投资者。",
    },
    {
        "fund_code": "012969",
        "fund_name": "国联安中证全指半导体ETF联接C",
        "fund_type": "行业指数型",
        "themes": ["半导体", "芯片", "国产替代"],
        "market": "A股",
        "risk_level": "高风险",
        "description": "聚焦芯片设计、设备与材料链条，板块弹性高但波动也较大。",
    },
    {
        "fund_code": "013048",
        "fund_name": "新能源车主题混合A",
        "fund_type": "主题混合型",
        "themes": ["新能源", "锂电池", "新能源车"],
        "market": "A股",
        "risk_level": "高风险",
        "description": "覆盖整车、动力电池与上游材料，受政策与销量预期影响明显。",
    },
    {
        "fund_code": "003095",
        "fund_name": "中欧医疗健康混合A",
        "fund_type": "行业混合型",
        "themes": ["医药", "创新药", "医疗服务"],
        "market": "A股",
        "risk_level": "中高风险",
        "description": "围绕医药与医疗服务布局，受研发进展与政策环境影响较大。",
    },
    {
        "fund_code": "161130",
        "fund_name": "易方达纳斯达克100指数(QDII)A",
        "fund_type": "QDII指数型",
        "themes": ["纳指100", "美股科技", "海外指数"],
        "market": "美股",
        "risk_level": "高风险",
        "description": "跟踪纳斯达克100指数，和美股科技权重股走势联动较强。",
    },
    {
        "fund_code": "006479",
        "fund_name": "广发全球精选股票(QDII)",
        "fund_type": "QDII主动股票型",
        "themes": ["美股科技", "AI", "全球成长"],
        "market": "美股",
        "risk_level": "高风险",
        "description": "以全球成长资产为主，科技龙头权重较高，波动受海外市场主导。",
    },
    {
        "fund_code": "000123",
        "fund_name": "稳健增利债券A",
        "fund_type": "债券型",
        "themes": ["债券", "固收", "低波动"],
        "market": "债券",
        "risk_level": "中低风险",
        "description": "以利率债与高等级信用债为主，适合作为权益仓位的对比参考。",
    },
]


MOCK_NEWS_BY_FUND_CODE: dict[str, list[dict[str, Any]]] = {
    "012349": [
        {
            "title": "恒生科技指数反弹，港股科技股获南向资金流入",
            "source": "模拟港股市场日报",
            "publish_time": "2026-03-26 10:00",
            "summary": "港股科技板块回暖，恒生科技指数走强，互联网与硬科技权重股表现活跃。",
            "url": "https://example.com/news/012349-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "香港科技股波动加大，恒生科技指数短线震荡",
            "source": "模拟香港财经快讯",
            "publish_time": "2026-03-25 14:20",
            "summary": "受海外利率预期扰动，香港科技股盘中波动加大，但恒生科技指数仍有资金关注。",
            "url": "https://example.com/news/012349-2",
            "sentiment_hint": "neutral",
        },
        {
            "title": "港股互联网与科技权重股回暖，恒生科技ETF关注度提升",
            "source": "模拟ETF观察",
            "publish_time": "2026-03-24 18:30",
            "summary": "恒生科技、港股科技和香港互联网股同步获得增量关注，相关 ETF 成交回升。",
            "url": "https://example.com/news/012349-3",
            "sentiment_hint": "positive",
        },
    ],
    "510300": [
        {
            "title": "大盘蓝筹获资金流入，核心宽基ETF成交回暖",
            "source": "模拟证券日报",
            "publish_time": "2026-03-26 09:10",
            "summary": "市场风险偏好回升后，金融与消费权重股活跃，宽基ETF成交额提升，资金流入与反弹信号增强。",
            "url": "https://example.com/news/510300-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "宏观数据平稳，机构称核心资产估值处于合理区间",
            "source": "模拟基金观察",
            "publish_time": "2026-03-25 14:20",
            "summary": "多家机构认为蓝筹板块短期震荡后仍具配置价值，但缺少明确突破信号，整体偏中性。",
            "url": "https://example.com/news/510300-2",
            "sentiment_hint": "neutral",
        },
        {
            "title": "权重股分化明显，指数上行仍需成交量配合",
            "source": "模拟市场速递",
            "publish_time": "2026-03-24 18:00",
            "summary": "银行与消费表现稳定，但部分周期股下滑，增量资金不足，指数短期仍有承压迹象。",
            "url": "https://example.com/news/510300-3",
            "sentiment_hint": "neutral",
        },
    ],
    "161017": [
        {
            "title": "中盘成长方向回暖，中证500相关基金活跃度提升",
            "source": "模拟量化周刊",
            "publish_time": "2026-03-26 10:05",
            "summary": "中小盘风格在震荡市中表现出更强弹性，部分增强策略基金受关注，成交活跃度回升。",
            "url": "https://example.com/news/161017-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "机构提示中盘风格波动加大，建议控制节奏",
            "source": "模拟基金评论",
            "publish_time": "2026-03-25 11:40",
            "summary": "成长赛道存在轮动加速现象，短线波动加大，追涨风险上升。",
            "url": "https://example.com/news/161017-2",
            "sentiment_hint": "negative",
        },
        {
            "title": "政策预期改善带动先进制造与中盘个股修复",
            "source": "模拟财经头条",
            "publish_time": "2026-03-24 15:30",
            "summary": "受益于政策支持预期改善，先进制造和专精特新方向获得部分增量资金流入。",
            "url": "https://example.com/news/161017-3",
            "sentiment_hint": "positive",
        },
    ],
    "012969": [
        {
            "title": "国产替代预期升温，半导体设备订单增加",
            "source": "模拟芯片日报",
            "publish_time": "2026-03-26 08:50",
            "summary": "设备与材料环节订单增加，政策支持与国产替代预期升温，市场重新评估行业弹性。",
            "url": "https://example.com/news/012969-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "芯片板块高波动延续，短线资金分歧加大",
            "source": "模拟电子产业观察",
            "publish_time": "2026-03-25 13:10",
            "summary": "部分个股冲高回落，显示短期市场仍在博弈景气度兑现节奏，板块波动加大。",
            "url": "https://example.com/news/012969-2",
            "sentiment_hint": "neutral",
        },
        {
            "title": "AI 算力需求强劲，先进制程与封装链条受益",
            "source": "模拟科技研报",
            "publish_time": "2026-03-24 20:00",
            "summary": "AI 服务器需求强劲，带动高端芯片和先进封装关注度提升，行业景气度改善。",
            "url": "https://example.com/news/012969-3",
            "sentiment_hint": "positive",
        },
        {
            "title": "全球半导体库存去化仍需时间，出口限制压力未散",
            "source": "模拟国际电子报",
            "publish_time": "2026-03-23 17:30",
            "summary": "海外需求恢复节奏存在差异，部分细分环节仍面临库存压力与出口限制带来的风险上升。",
            "url": "https://example.com/news/012969-4",
            "sentiment_hint": "negative",
        },
    ],
    "013048": [
        {
            "title": "新能源车销量延续增长，产业链景气度超预期改善",
            "source": "模拟汽车财经",
            "publish_time": "2026-03-26 09:35",
            "summary": "终端销量增长带动市场对动力电池与零部件龙头的关注度回升，行业景气度改善超预期。",
            "url": "https://example.com/news/013048-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "储能与锂电材料价格趋稳，行业盈利修复受期待",
            "source": "模拟新能源快讯",
            "publish_time": "2026-03-25 16:10",
            "summary": "材料价格波动趋缓后，市场关注中游制造环节利润率改善空间，订单增加预期升温。",
            "url": "https://example.com/news/013048-2",
            "sentiment_hint": "positive",
        },
        {
            "title": "海外贸易不确定性升温，新能源出口链短期承压",
            "source": "模拟宏观风向",
            "publish_time": "2026-03-24 10:45",
            "summary": "若外部政策扰动扩大，新能源出海链条可能面临估值压力与资金流出，短期承压。",
            "url": "https://example.com/news/013048-3",
            "sentiment_hint": "negative",
        },
        {
            "title": "政策支持持续释放，充电基础设施建设提速",
            "source": "模拟产业政策观察",
            "publish_time": "2026-03-23 18:20",
            "summary": "政策支持持续释放，新能源配套设施扩张提升行业中长期需求预期，形成利好。",
            "url": "https://example.com/news/013048-4",
            "sentiment_hint": "positive",
        },
    ],
    "003095": [
        {
            "title": "创新药板块迎来估值修复，资金回流医药赛道",
            "source": "模拟医药投资报",
            "publish_time": "2026-03-26 10:20",
            "summary": "创新药和医疗服务方向整体回暖，部分龙头公司获批进展顺利并获得资金回流。",
            "url": "https://example.com/news/003095-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "医保谈判预期再起，医药板块情绪仍有扰动",
            "source": "模拟健康产业周刊",
            "publish_time": "2026-03-25 12:05",
            "summary": "政策端不确定性仍可能影响部分细分方向的盈利预期，监管压力暂未完全消退。",
            "url": "https://example.com/news/003095-2",
            "sentiment_hint": "neutral",
        },
        {
            "title": "医疗服务需求恢复，连锁医疗机构业绩超预期",
            "source": "模拟行业观察",
            "publish_time": "2026-03-24 09:55",
            "summary": "线下医疗服务客流改善，为板块基本面修复提供支撑，部分公司业绩超预期。",
            "url": "https://example.com/news/003095-3",
            "sentiment_hint": "positive",
        },
    ],
    "161130": [
        {
            "title": "AI 龙头财报超预期，纳指相关基金净值弹性显现",
            "source": "模拟海外市场日报",
            "publish_time": "2026-03-26 07:30",
            "summary": "大型科技公司财报表现强劲，AI 与云计算需求增长，推动纳斯达克指数反弹走强。",
            "url": "https://example.com/news/161130-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "美联储降息节奏仍存分歧，成长股估值敏感",
            "source": "模拟美股快评",
            "publish_time": "2026-03-25 21:10",
            "summary": "利率路径不确定性使高估值科技股波动加大，短期情绪偏中性。",
            "url": "https://example.com/news/161130-2",
            "sentiment_hint": "neutral",
        },
        {
            "title": "半导体与云计算板块同步走强，纳指权重股再获追捧",
            "source": "模拟国际科技报",
            "publish_time": "2026-03-24 22:40",
            "summary": "AI 基础设施投资继续扩张，带动芯片和云服务公司股价表现强劲，市场风险偏好回升。",
            "url": "https://example.com/news/161130-3",
            "sentiment_hint": "positive",
        },
        {
            "title": "美元与长端利率回升，海外成长资产面临短期压力",
            "source": "模拟全球资产观察",
            "publish_time": "2026-03-23 20:15",
            "summary": "若利率上行延续，科技成长股估值可能承压，资金流出风险上升。",
            "url": "https://example.com/news/161130-4",
            "sentiment_hint": "negative",
        },
    ],
    "006479": [
        {
            "title": "全球科技龙头加码 AI 资本开支，成长基金受关注",
            "source": "模拟全球基金周报",
            "publish_time": "2026-03-26 06:50",
            "summary": "AI 投资周期延续，带动海外成长股基金市场热度上升，云计算与芯片订单增加。",
            "url": "https://example.com/news/006479-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "美股科技股短期高位震荡，机构建议关注估值消化",
            "source": "模拟华尔街简报",
            "publish_time": "2026-03-25 20:00",
            "summary": "在连续上涨后，部分科技龙头出现震荡整固迹象，短线方向暂不明朗。",
            "url": "https://example.com/news/006479-2",
            "sentiment_hint": "neutral",
        },
        {
            "title": "海外流动性预期改善，成长资产风险偏好回升",
            "source": "模拟海外资产评论",
            "publish_time": "2026-03-24 19:45",
            "summary": "若通胀回落趋势延续，降息预期升温，海外成长板块有望继续获得资金流入。",
            "url": "https://example.com/news/006479-3",
            "sentiment_hint": "positive",
        },
    ],
    "000123": [
        {
            "title": "债市收益率小幅回落，纯债基金净值表现平稳",
            "source": "模拟固收日报",
            "publish_time": "2026-03-26 11:00",
            "summary": "利率债表现稳健，降息预期抬升后债券价格走强，纯债基金整体波动较低。",
            "url": "https://example.com/news/000123-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "机构提示信用利差变化，债券配置以稳为主",
            "source": "模拟债市观察",
            "publish_time": "2026-03-25 15:55",
            "summary": "债券基金虽相对稳健，但仍需关注信用环境、违约风险和流动性波动。",
            "url": "https://example.com/news/000123-2",
            "sentiment_hint": "neutral",
        },
        {
            "title": "避险情绪回升，固收类产品申购需求增加",
            "source": "模拟理财快讯",
            "publish_time": "2026-03-24 13:25",
            "summary": "部分资金从高波动权益资产转向债券及固收增强方向，资金流入提升债券配置吸引力。",
            "url": "https://example.com/news/000123-3",
            "sentiment_hint": "positive",
        },
    ],
}


def list_mock_funds() -> list[dict[str, Any]]:
    """返回全部 mock 基金列表。"""
    return MOCK_FUNDS


def get_mock_fund_by_code(fund_code: str) -> dict[str, Any] | None:
    """按基金代码精确获取 mock 基金信息。"""
    normalized_code = fund_code.strip()
    for fund in MOCK_FUNDS:
        if fund["fund_code"] == normalized_code:
            return fund.copy()
    return None


def search_mock_funds_by_name(query: str) -> list[dict[str, Any]]:
    """按基金名称模糊搜索 mock 基金。"""
    normalized_query = query.strip().lower()
    if not normalized_query:
        return []

    matched_funds: list[dict[str, Any]] = []
    for fund in MOCK_FUNDS:
        searchable_text = f"{fund['fund_name']} {' '.join(fund['themes'])}".lower()
        if normalized_query in searchable_text:
            matched_funds.append(fund.copy())
    return matched_funds


def get_mock_news_by_fund_code(fund_code: str) -> list[dict[str, Any]]:
    """按基金代码获取对应 mock 新闻。"""
    news_items = MOCK_NEWS_BY_FUND_CODE.get(fund_code.strip(), [])
    return [item.copy() for item in news_items]


def get_mock_news_by_theme(theme: str) -> list[dict[str, Any]]:
    """按主题搜索相关新闻。"""
    normalized_theme = theme.strip().lower()
    if not normalized_theme:
        return []

    results: list[dict[str, Any]] = []
    for fund in MOCK_FUNDS:
        if any(normalized_theme in item.lower() for item in fund["themes"]):
            results.extend(get_mock_news_by_fund_code(fund["fund_code"]))
    return results


SUPPORTED_ASSETS: dict[str, list[dict[str, Any]]] = {
    "A股": [
        {
            "symbol": "000001.SH",
            "name": "上证指数",
            "asset_type": "指数",
            "theme": "A股宽基",
            "risk_level": "中风险",
            "description": "A股核心指数之一，可用于观察整体市场风险偏好。",
            "aliases": ["上证指数", "上证", "000001.SH"],
        },
        {
            "symbol": "510300.SH",
            "name": "沪深300ETF",
            "asset_type": "ETF",
            "theme": "A股宽基",
            "risk_level": "中风险",
            "description": "跟踪沪深300的代表性 ETF，可作为 A 股宽基观察样本。",
            "aliases": ["沪深300ETF", "510300", "沪深300"],
        },
    ],
    "港股": [
        {
            "symbol": "00700.HK",
            "name": "腾讯控股",
            "asset_type": "港股龙头",
            "theme": "港股科技",
            "risk_level": "高风险",
            "description": "香港市场代表性科技龙头，可反映港股科技情绪。",
            "aliases": ["腾讯控股", "腾讯", "00700.HK"],
        },
        {
            "symbol": "03033.HK",
            "name": "恒生科技ETF",
            "asset_type": "ETF",
            "theme": "恒生科技",
            "risk_level": "高风险",
            "description": "跟踪恒生科技指数，覆盖港股科技核心成分。",
            "aliases": ["恒生科技ETF", "恒生科技", "03033.HK"],
        },
    ],
    "美股": [
        {
            "symbol": "NVDA",
            "name": "NVIDIA",
            "asset_type": "美股龙头",
            "theme": "AI芯片",
            "risk_level": "高风险",
            "description": "全球 AI 芯片龙头，常作为美股科技代表样本。",
            "aliases": ["NVDA", "英伟达", "NVIDIA"],
        },
        {
            "symbol": "QQQ",
            "name": "Invesco QQQ Trust",
            "asset_type": "ETF",
            "theme": "纳指100",
            "risk_level": "高风险",
            "description": "跟踪纳斯达克 100 指数的代表性 ETF。",
            "aliases": ["QQQ", "纳指ETF", "纳指100"],
        },
    ],
    "黄金": [
        {
            "symbol": "XAUUSD",
            "name": "现货黄金",
            "asset_type": "贵金属",
            "theme": "黄金避险",
            "risk_level": "中高风险",
            "description": "国际现货黄金价格，常用于观察避险资产走势。",
            "aliases": ["现货黄金", "黄金", "XAUUSD", "XAU/USD"],
        },
        {
            "symbol": "GLD",
            "name": "SPDR Gold Shares",
            "asset_type": "黄金ETF",
            "theme": "黄金ETF",
            "risk_level": "中高风险",
            "description": "美股代表性黄金 ETF，可作为黄金相关资产参考。",
            "aliases": ["GLD", "黄金ETF"],
        },
    ],
}


MOCK_ASSET_QUOTES: dict[tuple[str, str], dict[str, Any]] = {
    ("A股", "000001.SH"): {
        "symbol": "000001.SH",
        "name": "上证指数",
        "market": "A股",
        "asset_type": "指数",
        "theme": "A股宽基",
        "price": 3218.45,
        "change": 18.22,
        "pct_change": 0.57,
        "volume": 382000000.0,
        "turnover": 486500000000.0,
        "amplitude": 1.28,
        "risk_level": "中风险",
        "description": "A股核心指数之一，可用于观察整体市场风险偏好。",
        "source_provider": "mock",
        "data_source": "mock",
        "updated_at": "2026-03-27 15:00:00",
    },
    ("A股", "510300.SH"): {
        "symbol": "510300.SH",
        "name": "沪深300ETF",
        "market": "A股",
        "asset_type": "ETF",
        "theme": "A股宽基",
        "price": 3.68,
        "change": 0.03,
        "pct_change": 0.82,
        "volume": 56200000.0,
        "turnover": 208000000.0,
        "amplitude": 1.15,
        "risk_level": "中风险",
        "description": "跟踪沪深300的代表性 ETF，可作为 A 股宽基观察样本。",
        "source_provider": "mock",
        "data_source": "mock",
        "updated_at": "2026-03-27 15:00:00",
    },
    ("港股", "00700.HK"): {
        "symbol": "00700.HK",
        "name": "腾讯控股",
        "market": "港股",
        "asset_type": "港股龙头",
        "theme": "港股科技",
        "price": 368.4,
        "change": -4.6,
        "pct_change": -1.23,
        "volume": 28500000.0,
        "turnover": 10450000000.0,
        "amplitude": 2.8,
        "risk_level": "高风险",
        "description": "香港市场代表性科技龙头，可反映港股科技情绪。",
        "source_provider": "mock",
        "data_source": "mock",
        "updated_at": "2026-03-27 16:00:00",
    },
    ("港股", "03033.HK"): {
        "symbol": "03033.HK",
        "name": "恒生科技ETF",
        "market": "港股",
        "asset_type": "ETF",
        "theme": "恒生科技",
        "price": 4.52,
        "change": 0.09,
        "pct_change": 2.03,
        "volume": 46800000.0,
        "turnover": 214000000.0,
        "amplitude": 3.4,
        "risk_level": "高风险",
        "description": "跟踪恒生科技指数，覆盖港股科技核心成分。",
        "source_provider": "mock",
        "data_source": "mock",
        "updated_at": "2026-03-27 16:00:00",
    },
    ("美股", "NVDA"): {
        "symbol": "NVDA",
        "name": "NVIDIA",
        "market": "美股",
        "asset_type": "美股龙头",
        "theme": "AI芯片",
        "price": 924.8,
        "change": 16.4,
        "pct_change": 1.81,
        "volume": 42100000.0,
        "turnover": 0.0,
        "amplitude": 2.35,
        "risk_level": "高风险",
        "description": "全球 AI 芯片龙头，常作为美股科技代表样本。",
        "source_provider": "mock",
        "data_source": "mock",
        "updated_at": "2026-03-27 09:30:00",
    },
    ("美股", "QQQ"): {
        "symbol": "QQQ",
        "name": "Invesco QQQ Trust",
        "market": "美股",
        "asset_type": "ETF",
        "theme": "纳指100",
        "price": 492.6,
        "change": 4.2,
        "pct_change": 0.86,
        "volume": 31200000.0,
        "turnover": 0.0,
        "amplitude": 1.52,
        "risk_level": "高风险",
        "description": "跟踪纳斯达克 100 指数的代表性 ETF。",
        "source_provider": "mock",
        "data_source": "mock",
        "updated_at": "2026-03-27 09:30:00",
    },
    ("黄金", "XAUUSD"): {
        "symbol": "XAUUSD",
        "name": "现货黄金",
        "market": "黄金",
        "asset_type": "贵金属",
        "theme": "黄金避险",
        "price": 2186.4,
        "change": 8.6,
        "pct_change": 0.39,
        "volume": 0.0,
        "turnover": 0.0,
        "amplitude": 15.2,
        "risk_level": "中高风险",
        "description": "国际现货黄金价格，常用于观察避险资产走势。",
        "source_provider": "mock",
        "data_source": "mock",
        "updated_at": "2026-03-27 10:00:00",
    },
    ("黄金", "GLD"): {
        "symbol": "GLD",
        "name": "SPDR Gold Shares",
        "market": "黄金",
        "asset_type": "黄金ETF",
        "theme": "黄金ETF",
        "price": 203.8,
        "change": 1.4,
        "pct_change": 0.69,
        "volume": 8400000.0,
        "turnover": 0.0,
        "amplitude": 1.08,
        "risk_level": "中高风险",
        "description": "美股代表性黄金 ETF，可作为黄金相关资产参考。",
        "source_provider": "mock",
        "data_source": "mock",
        "updated_at": "2026-03-27 09:30:00",
    },
}


MOCK_ASSET_NEWS: dict[tuple[str, str], list[dict[str, Any]]] = {
    ("A股", "000001.SH"): [
        {
            "title": "权重板块回暖，上证指数震荡走强",
            "source": "模拟A股日报",
            "publish_time": "2026-03-27 11:00:00",
            "summary": "金融与消费权重回暖，A股整体风险偏好有所修复。",
            "url": "https://example.com/a-share-1",
            "sentiment_hint": "positive",
            "source_provider": "mock",
            "data_source": "mock",
        },
        {
            "title": "A股量能仍待放大，指数上攻节奏偏温和",
            "source": "模拟盘面速递",
            "publish_time": "2026-03-27 10:00:00",
            "summary": "市场延续震荡，资金更关注结构性机会。",
            "url": "https://example.com/a-share-2",
            "sentiment_hint": "neutral",
            "source_provider": "mock",
            "data_source": "mock",
        },
    ],
    ("A股", "510300.SH"): [
        {
            "title": "沪深300ETF成交回暖，核心资产吸引增量资金",
            "source": "模拟ETF日报",
            "publish_time": "2026-03-27 11:20:00",
            "summary": "沪深300ETF跟踪标的表现稳健，宽基配置价值受到关注。",
            "url": "https://example.com/hs300-1",
            "sentiment_hint": "positive",
            "source_provider": "mock",
            "data_source": "mock",
        },
        {
            "title": "A股宽基延续震荡，沪深300ETF等待量能配合",
            "source": "模拟市场观察",
            "publish_time": "2026-03-27 10:10:00",
            "summary": "沪深300相关权重板块分化，短线仍需观察增量资金是否回流。",
            "url": "https://example.com/hs300-2",
            "sentiment_hint": "neutral",
            "source_provider": "mock",
            "data_source": "mock",
        },
    ],
    ("港股", "00700.HK"): [
        {
            "title": "港股科技股承压，腾讯控股盘中回落",
            "source": "模拟港股观察",
            "publish_time": "2026-03-27 14:00:00",
            "summary": "海外利率预期扰动下，港股科技龙头波动加大。",
            "url": "https://example.com/hk-1",
            "sentiment_hint": "negative",
            "source_provider": "mock",
            "data_source": "mock",
        },
        {
            "title": "南向资金关注港股科技，腾讯成交活跃",
            "source": "模拟港股日报",
            "publish_time": "2026-03-27 12:30:00",
            "summary": "港股科技板块情绪修复，权重龙头获得资金流入。",
            "url": "https://example.com/hk-2",
            "sentiment_hint": "positive",
            "source_provider": "mock",
            "data_source": "mock",
        },
    ],
    ("港股", "03033.HK"): [
        {
            "title": "恒生科技指数反弹，港股科技板块走强",
            "source": "模拟恒生科技快讯",
            "publish_time": "2026-03-27 14:30:00",
            "summary": "恒生科技指数和香港科技股同步反弹，港股科技情绪转暖。",
            "url": "https://example.com/hstech-1",
            "sentiment_hint": "positive",
            "source_provider": "mock",
            "data_source": "mock",
        },
        {
            "title": "港股科技波动加大，恒生科技ETF短线震荡",
            "source": "模拟ETF速递",
            "publish_time": "2026-03-27 13:00:00",
            "summary": "恒生科技指数短期受外部市场扰动，港股科技股分化明显。",
            "url": "https://example.com/hstech-2",
            "sentiment_hint": "neutral",
            "source_provider": "mock",
            "data_source": "mock",
        },
    ],
    ("美股", "NVDA"): [
        {
            "title": "AI 需求强劲，英伟达再获机构看多",
            "source": "模拟美股科技报",
            "publish_time": "2026-03-27 08:00:00",
            "summary": "AI 芯片订单增加，市场预期业绩继续超预期。",
            "url": "https://example.com/us-1",
            "sentiment_hint": "positive",
            "source_provider": "mock",
            "data_source": "mock",
        },
        {
            "title": "美股科技高位震荡，芯片龙头短线波动加大",
            "source": "模拟华尔街观察",
            "publish_time": "2026-03-27 07:30:00",
            "summary": "利率预期扰动下，美股科技股短线承压。",
            "url": "https://example.com/us-2",
            "sentiment_hint": "negative",
            "source_provider": "mock",
            "data_source": "mock",
        },
    ],
    ("美股", "QQQ"): [
        {
            "title": "纳指100维持强势，QQQ 受大型科技股带动反弹",
            "source": "模拟纳指观察",
            "publish_time": "2026-03-27 08:40:00",
            "summary": "美股科技龙头走强，QQQ 跟踪的纳指100整体表现偏暖。",
            "url": "https://example.com/qqq-1",
            "sentiment_hint": "positive",
            "source_provider": "mock",
            "data_source": "mock",
        },
        {
            "title": "利率预期扰动仍在，QQQ 短线或维持高位震荡",
            "source": "模拟美股ETF评论",
            "publish_time": "2026-03-27 07:10:00",
            "summary": "成长股估值仍较敏感，QQQ 走势更多取决于大型科技股财报与利率路径。",
            "url": "https://example.com/qqq-2",
            "sentiment_hint": "neutral",
            "source_provider": "mock",
            "data_source": "mock",
        },
    ],
    ("黄金", "XAUUSD"): [
        {
            "title": "地缘冲突升级，现货黄金维持强势",
            "source": "模拟贵金属观察",
            "publish_time": "2026-03-27 09:00:00",
            "summary": "避险资金流入，黄金价格保持高位运行。",
            "url": "https://example.com/gold-1",
            "sentiment_hint": "positive",
            "source_provider": "mock",
            "data_source": "mock",
        },
        {
            "title": "美元回升压制黄金，短线高位震荡",
            "source": "模拟黄金快讯",
            "publish_time": "2026-03-27 08:20:00",
            "summary": "黄金上行动能略有放缓，但避险需求仍在。",
            "url": "https://example.com/gold-2",
            "sentiment_hint": "neutral",
            "source_provider": "mock",
            "data_source": "mock",
        },
    ],
    ("黄金", "GLD"): [
        {
            "title": "黄金ETF获避险资金流入，GLD 维持偏强走势",
            "source": "模拟黄金ETF日报",
            "publish_time": "2026-03-27 09:15:00",
            "summary": "地缘风险与降息预期交织，黄金ETF吸引避险资金配置。",
            "url": "https://example.com/gld-1",
            "sentiment_hint": "positive",
            "source_provider": "mock",
            "data_source": "mock",
        },
        {
            "title": "美元波动影响黄金ETF，GLD 短线高位整理",
            "source": "模拟贵金属ETF评论",
            "publish_time": "2026-03-27 08:35:00",
            "summary": "黄金ETF短线受到美元回升扰动，但中期避险逻辑仍在。",
            "url": "https://example.com/gld-2",
            "sentiment_hint": "neutral",
            "source_provider": "mock",
            "data_source": "mock",
        },
    ],
}


def list_supported_assets(market: str | None = None) -> list[dict[str, Any]]:
    """返回支持的代表性资产列表。"""
    if market:
        return SUPPORTED_ASSETS.get(market, [])
    return [item for values in SUPPORTED_ASSETS.values() for item in values]


def resolve_mock_asset(market: str, query: str) -> dict[str, Any] | None:
    """按市场和输入解析资产元信息。"""
    normalized_query = query.strip().lower()
    for asset in SUPPORTED_ASSETS.get(market, []):
        aliases = [alias.lower() for alias in asset.get("aliases", [])]
        if normalized_query == asset["symbol"].lower() or normalized_query in aliases:
            return asset.copy()
    return None


def _generate_mock_kline_from_quote(quote: dict[str, Any], interval: str) -> list[dict[str, Any]]:
    """根据报价生成更接近真实行情的 mock K 线。"""
    close_price = float(quote["price"])
    base_dates = {
        "1day": [f"2026-02-{day:02d}" for day in range(1, 31)],
        "1week": [f"2026-W{week:02d}" for week in range(1, 13)],
        "1month": [f"2025-{month:02d}" for month in range(1, 13)],
    }
    date_list = base_dates.get(interval, base_dates["1day"])
    rows: list[dict[str, Any]] = []
    previous_close = close_price * 0.97
    for index, datetime_value in enumerate(date_list):
        trend_component = ((index - len(date_list) / 2) / max(len(date_list), 1)) * 0.08
        wave_component = math.sin(index * 0.72) * 0.02
        pullback_component = math.cos(index * 0.33) * 0.01
        close_factor = 1 + trend_component + wave_component + pullback_component
        close_value = round(close_price * close_factor, 4)

        open_shift = math.sin(index * 0.91) * 0.012
        open_value = round(previous_close * (1 + open_shift), 4)

        wick_factor = 0.012 + abs(math.cos(index * 0.57)) * 0.012
        high_value = round(max(open_value, close_value) * (1 + wick_factor), 4)
        low_value = round(min(open_value, close_value) * (1 - wick_factor * 0.95), 4)

        volume_base = float(quote.get("volume", 0))
        volume_factor = 0.68 + (index / max(len(date_list) - 1, 1)) * 0.55 + abs(math.sin(index * 0.64)) * 0.35
        volume_value = round(volume_base * volume_factor, 2)
        rows.append(
            {
                "datetime": datetime_value,
                "open": open_value,
                "high": high_value,
                "low": low_value,
                "close": close_value,
                "volume": volume_value,
                "source_provider": "mock",
                "data_source": "mock",
            }
        )
        previous_close = close_value
    return rows


def get_mock_asset_detail(market: str, symbol: str) -> dict[str, Any]:
    """获取 mock 资产详情。"""
    asset_detail = MOCK_ASSET_QUOTES.get((market, symbol))
    if asset_detail:
        return asset_detail.copy()

    fallback_asset = resolve_mock_asset(market, symbol)
    if fallback_asset:
        return {
            "symbol": fallback_asset["symbol"],
            "name": fallback_asset["name"],
            "market": market,
            "asset_type": fallback_asset["asset_type"],
            "theme": fallback_asset["theme"],
            "price": 0.0,
            "change": 0.0,
            "pct_change": 0.0,
            "volume": 0.0,
            "turnover": 0.0,
            "amplitude": 0.0,
            "risk_level": fallback_asset["risk_level"],
            "description": fallback_asset["description"],
            "source_provider": "mock",
            "data_source": "mock",
            "updated_at": "",
        }

    return {
        "symbol": symbol,
        "name": symbol,
        "market": market,
        "asset_type": "未知",
        "theme": "综合",
        "price": 0.0,
        "change": 0.0,
        "pct_change": 0.0,
        "volume": 0.0,
        "turnover": 0.0,
        "amplitude": 0.0,
        "risk_level": "未知",
        "description": "暂无示例资产说明。",
        "source_provider": "mock",
        "data_source": "mock",
        "updated_at": "",
    }


def get_mock_kline(market: str, symbol: str, interval: str = "1day") -> list[dict[str, Any]]:
    """获取 mock K 线。"""
    quote = get_mock_asset_detail(market, symbol)
    return _generate_mock_kline_from_quote(quote, interval)


def get_mock_related_news(market: str, symbol: str, theme: str) -> list[dict[str, Any]]:
    """获取 mock 新闻。"""
    news_items = MOCK_ASSET_NEWS.get((market, symbol), [])
    if news_items:
        return [item.copy() for item in news_items]

    matched_items: list[dict[str, Any]] = []
    for (item_market, _), values in MOCK_ASSET_NEWS.items():
        if item_market == market:
            for item in values:
                if theme and theme in f"{item.get('title', '')} {item.get('summary', '')}":
                    matched_items.append(item.copy())
    return matched_items
