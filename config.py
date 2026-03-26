"""项目基础配置。"""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "app.db"

APP_TITLE = "轻量版基金分析工具"
DISCLAIMER_TEXT = "本工具仅提供信息整理与辅助分析，不构成投资建议，市场有风险，投资需谨慎。"
