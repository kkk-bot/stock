"""项目基础配置与环境变量读取。"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - 缺少依赖时允许降级运行
    def load_dotenv(*args: object, **kwargs: object) -> bool:
        """缺少 python-dotenv 时的兜底函数。"""
        return False


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "app.db"
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

APP_TITLE = "多市场真实数据投资分析工具"
DISCLAIMER_TEXT = "本工具仅提供信息整理与辅助分析，不构成投资建议，市场有风险，投资需谨慎。"

TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN", "").strip()
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "").strip()
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY", "").strip()

DEFAULT_MARKETS = ["A股", "港股", "美股", "黄金"]
DEFAULT_INTERVAL_OPTIONS = {
    "日K": "1day",
    "周K": "1week",
    "月K": "1month",
}
