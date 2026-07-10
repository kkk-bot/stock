const features = [
  "A股 / 港股 / 美股 / 黄金多市场分析",
  "真实数据优先，失败后回退示例数据",
  "新闻情绪分析与短期判断",
  "基金与资产快捷分析",
  "持仓补仓辅助计算",
  "本地 SQLite 分析记录",
];

const markets = ["A股", "港股", "美股", "黄金", "基金"];

export default function Home() {
  return (
    <main className="shell">
      <section className="hero">
        <div className="eyebrow">Multi-market Research Console</div>
        <h1>多市场投资分析工具</h1>
        <p className="lead">
          一个基于 Python、Streamlit 与 SQLite 的轻量投研工作台，用于整理行情、新闻情绪、短期判断和持仓补仓参考。
        </p>
        <div className="actions">
          <a className="primary" href="https://stock-analysis-kk.streamlit.app/" target="_blank" rel="noreferrer">
            打开 Streamlit 应用
          </a>
          <a className="secondary" href="#run-locally">
            查看本地运行方式
          </a>
        </div>
      </section>

      <section className="panel grid">
        <div>
          <h2>支持市场</h2>
          <div className="chips">
            {markets.map((market) => (
              <span key={market}>{market}</span>
            ))}
          </div>
        </div>
        <div>
          <h2>核心能力</h2>
          <ul className="feature-list">
            {features.map((feature) => (
              <li key={feature}>{feature}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="panel" id="run-locally">
        <h2>本地运行</h2>
        <p>
          当前完整分析功能仍由 Streamlit 应用承载。如果需要在本机运行，请在项目目录执行：
        </p>
        <pre>
          <code>{`pip install -r requirements.txt
streamlit run app.py`}</code>
        </pre>
      </section>

      <section className="notice">
        本工具仅提供信息整理与辅助分析，不构成投资建议，市场有风险，投资需谨慎。
      </section>
    </main>
  );
}
