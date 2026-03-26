"""SQLite 数据库连接与初始化逻辑。"""

from __future__ import annotations

import sqlite3
from contextlib import closing

from config import DATA_DIR, DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """创建并返回 SQLite 数据库连接。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    """初始化数据库及基础表结构。"""
    create_funds_table_sql = """
    CREATE TABLE IF NOT EXISTS funds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fund_code TEXT NOT NULL UNIQUE,
        fund_name TEXT NOT NULL,
        theme TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    create_news_articles_table_sql = """
    CREATE TABLE IF NOT EXISTS news_articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fund_code TEXT NOT NULL,
        title TEXT NOT NULL,
        source TEXT,
        published_at TEXT,
        sentiment_label TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute(create_funds_table_sql)
        cursor.execute(create_news_articles_table_sql)
        connection.commit()
