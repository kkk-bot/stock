# 轻量版基金分析工具

这是一个面向支付宝基金用户的轻量版基金分析工具原型，用于整理基金信息、展示新闻情绪分析占位结果，并提供持仓补仓计算的第一阶段页面框架。

当前版本为第一阶段，仅完成项目骨架、可运行页面、SQLite 初始化逻辑与 mock data 占位，不接入真实基金接口、真实新闻源或复杂预测逻辑。

## 免责声明

本工具仅提供信息整理与辅助分析，不构成投资建议，市场有风险，投资需谨慎。

## 第一阶段已实现内容

- 完整项目骨架与模块拆分
- 可运行的 Streamlit 单页应用
- 基金分析页签占位内容
- 持仓补仓计算页签占位内容
- SQLite 初始化逻辑与基础表结构
- mock data 模拟基金信息、新闻、情绪与判断结果
- 基础异常处理与中文界面

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
├── collectors/
│   ├── __init__.py
│   ├── fund_info.py
│   ├── news_fetcher.py
│   └── mock_data.py
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
- 当前 `data/app.db` 会在首次运行应用时自动初始化创建。
- 当前页面展示内容主要来自 `collectors/mock_data.py`。

## 安装方式

请确保本地 Python 版本为 3.11 或以上。

```bash
pip install -r requirements.txt
```

## 运行方式

```bash
streamlit run app.py
```

启动后，浏览器会打开本地 Streamlit 页面，当前可体验：
- 基金分析页签的 mock 数据展示流程
- 持仓补仓计算页签的占位输入与结果展示

## 当前数据说明

当前版本全部使用 mock data，仅用于界面演示、流程打通与后续扩展准备。

后续阶段可逐步补充：
- 真实基金信息采集
- 真实新闻抓取与整理
- 情绪分析模型
- 更完整的补仓辅助计算逻辑

## 稳定性说明

第一阶段优先目标是确保：
- 项目结构清晰
- 页面可以正常启动
- 数据库初始化逻辑可运行
- 缺少真实数据时也能完整展示流程

## 不构成投资建议

本工具仅提供信息整理与辅助分析，不构成投资建议，市场有风险，投资需谨慎。
