# 多市场真实数据投资分析工具

这是一个基于 Python + Streamlit + SQLite 的多市场投资分析工具，当前聚焦四类代表性资产：
- A股
- 港股
- 美股
- 黄金

系统优先尝试真实 API 获取数据，失败后自动回退到 mock data，保证页面始终可运行。

## 免责声明

本工具仅提供信息整理与辅助分析，不构成投资建议，市场有风险，投资需谨慎。

## 当前支持功能

- 真实 API 数据查询
- mock fallback
- 新闻情绪分析
- 短期判断
- 持仓补仓计算
- SQLite 本地存储
- Streamlit 网页展示
- K线图 + MA5 / MA10 / MA20 + 成交量

## 项目目录结构

```text
project/
├── app.py
├── requirements.txt
├── README.md
├── config.py
├── database.py
├── data/
│   └── app.db
├── AGENTS.md
├── collectors/
│   ├── __init__.py
│   ├── alpha_vantage_client.py
│   ├── fund_info.py
│   ├── google_news_rss.py
│   ├── market_router.py
│   ├── news_fetcher.py
│   ├── mock_data.py
│   ├── sec_edgar_client.py
│   ├── twelve_data_client.py
│   └── tushare_client.py
├── analysis/
│   ├── __init__.py
│   ├── sentiment.py
│   ├── trend_judge.py
│   └── recovery_calc.py
└── ui/
    ├── __init__.py
    └── components.py
```

说明：
- 当前 `data/app.db` 会在首次运行时自动初始化
- 真实 API 不可用时会自动回退到 `collectors/mock_data.py`

## 安装方式

请确保本地 Python 版本为 3.11 或以上。

## `.env` 配置方式

复制示例文件：

```bash
cp .env.example .env
```

在 `.env` 中填写：

```env
TUSHARE_TOKEN=
ALPHA_VANTAGE_API_KEY=
TWELVE_DATA_API_KEY=
```

## API key 配置说明

- `TUSHARE_TOKEN`：用于 A股 / 公募基金 / 港股优先查询
- `ALPHA_VANTAGE_API_KEY`：用于 美股 / 黄金 / 新闻优先查询
- `TWELVE_DATA_API_KEY`：用于 港股 / 美股 / 黄金备用行情查询

如果 key 缺失，系统会自动进入 mock fallback，并在页面提示当前显示示例数据。

```bash
pip install -r requirements.txt
```

## 运行方式

```bash
streamlit run app.py
```

启动后，浏览器会打开本地 Streamlit 页面，当前可体验：
- 多市场资产详情页
- K线图与成交量
- 新闻情绪分析与短期判断
- 持仓补仓计算
- 最近分析记录

## 数据来源说明

- A股 / 公募基金 / 国内黄金现货：优先 Tushare
- 港股：优先 Tushare，失败后 Twelve Data
- 美股：优先 Alpha Vantage，失败后 Twelve Data
- 黄金国际行情：优先 Alpha Vantage，失败后 Twelve Data
- 新闻来源（真实优先）：
- A股 / 港股：优先 Google News RSS 关键词聚合
- 美股：优先 Alpha Vantage News & Sentiment，并补充 SEC EDGAR 公告
- 黄金：优先 Alpha Vantage News & Sentiment，失败后 Google News RSS
- 新闻真实来源全部失败时：回退 mock 新闻

## fallback 机制说明

- API key 缺失：自动回退 mock
- API 请求失败 / 限流 / 超时：自动尝试备用 provider
- 备用 provider 仍失败：回退 mock
- 数据库存储失败：页面继续展示结果，但提示写库失败
- 当前新闻模块仅抓取标题 / 摘要 / 链接，不抓取复杂财经网站全文，避免重爬虫带来的不稳定风险

## 新闻来源配置说明

- `ALPHA_VANTAGE_API_KEY`：用于 Alpha Vantage 新闻接口（美股 / 黄金 / 宏观）
- Google News RSS：无需 API Key
- SEC EDGAR：无需 API Key（官方公开接口），建议遵守其访问频率规范

## 当前情绪分析逻辑说明

- 采用关键词词典 + 简单规则打分
- 标题权重高于摘要
- 每命中一个正向词加分，每命中一个负向词减分
- 原始分数会归一化到 `-1` 到 `1`
- 根据分数区间映射为 `positive / neutral / negative`
- 页面中会展示每条新闻的情绪标签、情绪分数和命中关键词

## 当前短期判断逻辑说明

- 先统计正面 / 中性 / 负面新闻数量
- 再计算平均情绪分数与整体情绪结论
- 结合基金描述中的强弱提示词，给出“偏涨 / 震荡 / 偏弱”判断
- 根据新闻数量和情绪倾向明显程度，给出低 / 中 / 高的轻量信心提示
- 原因说明由规则自动生成，尽量保持简短自然

## SQLite 存储说明

当前版本会在本地 SQLite 中保存以下内容：
- `asset_quotes`：资产实时行情与来源
- `kline_data`：K线数据与来源
- `news_articles`：新闻标题、摘要、情绪结果与数据来源
- `analysis_history`：查询词、市场、代码、短期判断、情绪摘要与时间

页面下方的“最近分析记录”会直接从本地数据库读取。

## 当前数据说明与局限性

当前版本的局限性：
- 真实数据源可能不稳定，接口变更或超时时会自动回退到 mock
- 免费 API 有额度限制
- 某些市场覆盖依赖 provider 可用性
- 情绪分析基于规则与关键词，不代表真实市场预测能力
- 新闻与情绪分析仅供参考
- 结果仅供参考，不构成投资建议

## 稳定性说明

当前版本优先目标是确保：
- 项目结构清晰
- 页面可以正常启动
- 数据库初始化逻辑可运行
- 缺少真实数据时也能完整展示流程
- 情绪分析与短期判断逻辑可解释、可运行

## 不构成投资建议

本工具仅提供信息整理与辅助分析，不构成投资建议，市场有风险，投资需谨慎。
