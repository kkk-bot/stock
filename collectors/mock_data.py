"""提供第二阶段使用的基金与新闻 mock 数据。"""

from __future__ import annotations

from typing import Any


MOCK_FUNDS: list[dict[str, Any]] = [
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
    "510300": [
        {
            "title": "大盘蓝筹获资金关注，核心宽基ETF成交回暖",
            "source": "模拟证券日报",
            "publish_time": "2026-03-26 09:10",
            "summary": "市场风险偏好回升后，金融与消费权重股活跃，宽基ETF成交额有所提升。",
            "url": "https://example.com/news/510300-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "宏观数据平稳，机构称核心资产估值处于合理区间",
            "source": "模拟基金观察",
            "publish_time": "2026-03-25 14:20",
            "summary": "多家机构认为蓝筹板块短期震荡后仍具配置价值，但上行节奏或偏温和。",
            "url": "https://example.com/news/510300-2",
            "sentiment_hint": "neutral",
        },
        {
            "title": "权重股分化明显，指数上行仍需成交量配合",
            "source": "模拟市场速递",
            "publish_time": "2026-03-24 18:00",
            "summary": "银行与消费表现稳定，但部分周期股回落，市场对持续上攻仍保持谨慎。",
            "url": "https://example.com/news/510300-3",
            "sentiment_hint": "neutral",
        },
    ],
    "161017": [
        {
            "title": "中盘成长方向回暖，中证500相关基金活跃度提升",
            "source": "模拟量化周刊",
            "publish_time": "2026-03-26 10:05",
            "summary": "中小盘风格在震荡市中表现出更强弹性，部分增强策略基金受关注。",
            "url": "https://example.com/news/161017-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "机构提示中盘风格波动加大，建议控制节奏",
            "source": "模拟基金评论",
            "publish_time": "2026-03-25 11:40",
            "summary": "成长赛道存在轮动加速现象，追涨风险上升。",
            "url": "https://example.com/news/161017-2",
            "sentiment_hint": "negative",
        },
        {
            "title": "政策预期改善带动先进制造与中盘个股修复",
            "source": "模拟财经头条",
            "publish_time": "2026-03-24 15:30",
            "summary": "受益于政策预期改善，先进制造和专精特新方向获得部分增量资金。",
            "url": "https://example.com/news/161017-3",
            "sentiment_hint": "positive",
        },
    ],
    "012969": [
        {
            "title": "国产替代预期升温，半导体设备订单受到关注",
            "source": "模拟芯片日报",
            "publish_time": "2026-03-26 08:50",
            "summary": "设备与材料环节订单预期改善，市场重新评估国产化链条盈利弹性。",
            "url": "https://example.com/news/012969-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "芯片板块高波动延续，短线资金分歧加大",
            "source": "模拟电子产业观察",
            "publish_time": "2026-03-25 13:10",
            "summary": "部分个股冲高回落，显示短期市场仍在博弈景气度兑现节奏。",
            "url": "https://example.com/news/012969-2",
            "sentiment_hint": "neutral",
        },
        {
            "title": "AI 算力需求扩张，先进制程与封装链条受益",
            "source": "模拟科技研报",
            "publish_time": "2026-03-24 20:00",
            "summary": "AI 服务器需求带动高端芯片和先进封装关注度提升。",
            "url": "https://example.com/news/012969-3",
            "sentiment_hint": "positive",
        },
        {
            "title": "全球半导体库存去化仍需时间，行业复苏节奏不一",
            "source": "模拟国际电子报",
            "publish_time": "2026-03-23 17:30",
            "summary": "海外需求恢复节奏存在差异，部分细分环节仍面临库存调整压力。",
            "url": "https://example.com/news/012969-4",
            "sentiment_hint": "negative",
        },
    ],
    "013048": [
        {
            "title": "新能源车销量延续增长，产业链景气度预期改善",
            "source": "模拟汽车财经",
            "publish_time": "2026-03-26 09:35",
            "summary": "终端销量增长带动市场对动力电池与零部件龙头的关注度回升。",
            "url": "https://example.com/news/013048-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "储能与锂电材料价格趋稳，行业盈利修复受期待",
            "source": "模拟新能源快讯",
            "publish_time": "2026-03-25 16:10",
            "summary": "材料价格波动趋缓后，市场关注中游制造环节利润率改善空间。",
            "url": "https://example.com/news/013048-2",
            "sentiment_hint": "positive",
        },
        {
            "title": "海外贸易不确定性升温，新能源出口链短期承压",
            "source": "模拟宏观风向",
            "publish_time": "2026-03-24 10:45",
            "summary": "若外部政策扰动扩大，新能源出海链条可能面临估值压力。",
            "url": "https://example.com/news/013048-3",
            "sentiment_hint": "negative",
        },
        {
            "title": "政策支持持续释放，充电基础设施建设提速",
            "source": "模拟产业政策观察",
            "publish_time": "2026-03-23 18:20",
            "summary": "新能源配套设施扩张提升行业中长期需求预期。",
            "url": "https://example.com/news/013048-4",
            "sentiment_hint": "positive",
        },
    ],
    "003095": [
        {
            "title": "创新药板块迎来估值修复，资金回流医药赛道",
            "source": "模拟医药投资报",
            "publish_time": "2026-03-26 10:20",
            "summary": "创新药和医疗服务方向整体回暖，部分龙头公司获得机构增持。",
            "url": "https://example.com/news/003095-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "医保谈判预期再起，医药板块情绪仍有扰动",
            "source": "模拟健康产业周刊",
            "publish_time": "2026-03-25 12:05",
            "summary": "政策端不确定性仍可能影响部分细分方向的盈利预期。",
            "url": "https://example.com/news/003095-2",
            "sentiment_hint": "neutral",
        },
        {
            "title": "医疗服务需求恢复，连锁医疗机构业绩获关注",
            "source": "模拟行业观察",
            "publish_time": "2026-03-24 09:55",
            "summary": "线下医疗服务客流改善，为板块基本面修复提供支撑。",
            "url": "https://example.com/news/003095-3",
            "sentiment_hint": "positive",
        },
    ],
    "161130": [
        {
            "title": "AI 龙头财报超预期，纳指相关基金净值弹性显现",
            "source": "模拟海外市场日报",
            "publish_time": "2026-03-26 07:30",
            "summary": "大型科技公司财报表现强劲，推动纳斯达克指数再度走强。",
            "url": "https://example.com/news/161130-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "美联储降息节奏仍存分歧，成长股估值敏感",
            "source": "模拟美股快评",
            "publish_time": "2026-03-25 21:10",
            "summary": "利率路径不确定性使高估值科技股波动加剧。",
            "url": "https://example.com/news/161130-2",
            "sentiment_hint": "neutral",
        },
        {
            "title": "半导体与云计算板块同步走强，纳指权重股再获追捧",
            "source": "模拟国际科技报",
            "publish_time": "2026-03-24 22:40",
            "summary": "AI 基础设施投资继续扩张，带动芯片和云服务公司股价表现。",
            "url": "https://example.com/news/161130-3",
            "sentiment_hint": "positive",
        },
        {
            "title": "美元与长端利率回升，海外成长资产面临短期压力",
            "source": "模拟全球资产观察",
            "publish_time": "2026-03-23 20:15",
            "summary": "若利率上行延续，科技成长股估值可能承压。",
            "url": "https://example.com/news/161130-4",
            "sentiment_hint": "negative",
        },
    ],
    "006479": [
        {
            "title": "全球科技龙头加码 AI 资本开支，成长基金受关注",
            "source": "模拟全球基金周报",
            "publish_time": "2026-03-26 06:50",
            "summary": "AI 投资周期延续，带动海外成长股基金市场热度上升。",
            "url": "https://example.com/news/006479-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "美股科技股短期高位震荡，机构建议关注估值消化",
            "source": "模拟华尔街简报",
            "publish_time": "2026-03-25 20:00",
            "summary": "在连续上涨后，部分科技龙头出现震荡整固迹象。",
            "url": "https://example.com/news/006479-2",
            "sentiment_hint": "neutral",
        },
        {
            "title": "海外流动性预期改善，成长资产风险偏好回升",
            "source": "模拟海外资产评论",
            "publish_time": "2026-03-24 19:45",
            "summary": "若通胀回落趋势延续，海外成长板块有望继续获得资金流入。",
            "url": "https://example.com/news/006479-3",
            "sentiment_hint": "positive",
        },
    ],
    "000123": [
        {
            "title": "债市收益率小幅回落，纯债基金净值表现平稳",
            "source": "模拟固收日报",
            "publish_time": "2026-03-26 11:00",
            "summary": "利率债表现稳健，纯债基金整体波动较小。",
            "url": "https://example.com/news/000123-1",
            "sentiment_hint": "positive",
        },
        {
            "title": "机构提示信用利差变化，债券配置以稳为主",
            "source": "模拟债市观察",
            "publish_time": "2026-03-25 15:55",
            "summary": "债券基金虽相对稳健，但仍需关注信用环境与流动性波动。",
            "url": "https://example.com/news/000123-2",
            "sentiment_hint": "neutral",
        },
        {
            "title": "避险情绪回升，固收类产品申购需求增加",
            "source": "模拟理财快讯",
            "publish_time": "2026-03-24 13:25",
            "summary": "部分资金从高波动权益资产转向债券及固收增强方向。",
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
