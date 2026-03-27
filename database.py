"""SQLite 数据库连接、初始化与数据落地逻辑。"""

from __future__ import annotations

import sqlite3
from contextlib import closing
from typing import Any

from config import DATA_DIR, DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """创建并返回 SQLite 数据库连接。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _ensure_column(cursor: sqlite3.Cursor, table_name: str, column_name: str, definition: str) -> None:
    """确保旧表结构中存在指定字段。"""
    existing_columns = {
        row["name"]
        for row in cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
    }
    if column_name not in existing_columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def init_database() -> None:
    """初始化多市场分析所需表结构。"""
    create_asset_quotes_sql = """
    CREATE TABLE IF NOT EXISTS asset_quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        market TEXT NOT NULL,
        name TEXT,
        price REAL,
        change REAL,
        pct_change REAL,
        volume REAL,
        turnover REAL,
        amplitude REAL,
        source_provider TEXT,
        data_source TEXT,
        updated_at TEXT,
        UNIQUE(symbol, market)
    );
    """

    create_kline_data_sql = """
    CREATE TABLE IF NOT EXISTS kline_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        market TEXT NOT NULL,
        interval TEXT NOT NULL,
        datetime TEXT NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL,
        source_provider TEXT,
        data_source TEXT,
        UNIQUE(symbol, market, interval, datetime)
    );
    """

    create_news_articles_sql = """
    CREATE TABLE IF NOT EXISTS news_articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        market TEXT,
        theme TEXT,
        title TEXT NOT NULL,
        source TEXT,
        publish_time TEXT,
        summary TEXT,
        url TEXT,
        sentiment_label TEXT,
        sentiment_score REAL,
        source_provider TEXT,
        data_source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    create_analysis_history_sql = """
    CREATE TABLE IF NOT EXISTS analysis_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_text TEXT NOT NULL,
        symbol TEXT,
        market TEXT,
        trend_label TEXT,
        confidence_hint TEXT,
        sentiment_summary TEXT,
        source_provider TEXT,
        data_source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute(create_asset_quotes_sql)
        cursor.execute(create_kline_data_sql)
        cursor.execute(create_news_articles_sql)
        cursor.execute(create_analysis_history_sql)

        _ensure_column(cursor, "news_articles", "symbol", "TEXT")
        _ensure_column(cursor, "news_articles", "market", "TEXT")
        _ensure_column(cursor, "news_articles", "theme", "TEXT")
        _ensure_column(cursor, "news_articles", "publish_time", "TEXT")
        _ensure_column(cursor, "news_articles", "summary", "TEXT")
        _ensure_column(cursor, "news_articles", "url", "TEXT")
        _ensure_column(cursor, "news_articles", "sentiment_score", "REAL")
        _ensure_column(cursor, "news_articles", "source_provider", "TEXT")
        _ensure_column(cursor, "news_articles", "data_source", "TEXT")
        _ensure_column(cursor, "analysis_history", "symbol", "TEXT")
        _ensure_column(cursor, "analysis_history", "market", "TEXT")
        _ensure_column(cursor, "analysis_history", "trend_label", "TEXT")
        _ensure_column(cursor, "analysis_history", "confidence_hint", "TEXT")
        _ensure_column(cursor, "analysis_history", "sentiment_summary", "TEXT")
        _ensure_column(cursor, "analysis_history", "source_provider", "TEXT")
        _ensure_column(cursor, "analysis_history", "data_source", "TEXT")

        cursor.execute(
            """
            DELETE FROM news_articles
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM news_articles
                GROUP BY title, publish_time
            );
            """
        )
        cursor.execute(
            """
            DELETE FROM news_articles
            WHERE url IS NOT NULL
              AND TRIM(url) <> ''
              AND id NOT IN (
                  SELECT MIN(id)
                  FROM news_articles
                  WHERE url IS NOT NULL AND TRIM(url) <> ''
                  GROUP BY url
              );
            """
        )

        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_news_unique
            ON news_articles(title, publish_time);
            """
        )
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_news_url_unique
            ON news_articles(url)
            WHERE url IS NOT NULL AND url <> '';
            """
        )
        connection.commit()


def save_asset_quote(asset_detail: dict[str, Any]) -> None:
    """保存或更新资产行情。"""
    if not asset_detail:
        return

    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO asset_quotes (
                symbol, market, name, price, change, pct_change,
                volume, turnover, amplitude, source_provider,
                data_source, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol, market) DO UPDATE SET
                name=excluded.name,
                price=excluded.price,
                change=excluded.change,
                pct_change=excluded.pct_change,
                volume=excluded.volume,
                turnover=excluded.turnover,
                amplitude=excluded.amplitude,
                source_provider=excluded.source_provider,
                data_source=excluded.data_source,
                updated_at=excluded.updated_at
            """,
            (
                asset_detail.get("symbol"),
                asset_detail.get("market"),
                asset_detail.get("name"),
                asset_detail.get("price"),
                asset_detail.get("change"),
                asset_detail.get("pct_change"),
                asset_detail.get("volume"),
                asset_detail.get("turnover"),
                asset_detail.get("amplitude"),
                asset_detail.get("source_provider"),
                asset_detail.get("data_source"),
                asset_detail.get("updated_at"),
            ),
        )
        connection.commit()


def save_kline_data(symbol: str, market: str, interval: str, kline_rows: list[dict[str, Any]]) -> None:
    """保存 K 线数据。"""
    if not kline_rows:
        return

    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        for row in kline_rows:
            cursor.execute(
                """
                INSERT OR REPLACE INTO kline_data (
                    symbol, market, interval, datetime, open, high,
                    low, close, volume, source_provider, data_source
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    symbol,
                    market,
                    interval,
                    row.get("datetime"),
                    row.get("open"),
                    row.get("high"),
                    row.get("low"),
                    row.get("close"),
                    row.get("volume"),
                    row.get("source_provider"),
                    row.get("data_source"),
                ),
            )
        connection.commit()


def save_news_articles(symbol: str, market: str, theme: str, news_items: list[dict[str, Any]]) -> None:
    """保存新闻记录。"""
    if not news_items:
        return

    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        available_columns = {
            row["name"]
            for row in cursor.execute("PRAGMA table_info(news_articles)").fetchall()
        }
        for item in news_items:
            url = str(item.get("url", "")).strip()
            title = str(item.get("title", "")).strip()
            publish_time = str(item.get("publish_time", "")).strip()

            if url:
                exists_by_url = cursor.execute(
                    "SELECT 1 FROM news_articles WHERE url = ? LIMIT 1",
                    (url,),
                ).fetchone()
                if exists_by_url:
                    continue
            if title and publish_time:
                exists_by_title_time = cursor.execute(
                    "SELECT 1 FROM news_articles WHERE title = ? AND publish_time = ? LIMIT 1",
                    (title, publish_time),
                ).fetchone()
                if exists_by_title_time:
                    continue

            value_map: dict[str, Any] = {
                "fund_code": symbol,
                "symbol": symbol,
                "market": market,
                "theme": theme,
                "title": title or item.get("title"),
                "source": item.get("source"),
                "publish_time": publish_time or item.get("publish_time"),
                "published_at": publish_time or item.get("publish_time"),
                "summary": item.get("summary"),
                "url": url or item.get("url"),
                "sentiment_label": item.get("sentiment_label"),
                "sentiment_score": item.get("sentiment_score"),
                "source_provider": item.get("source_provider"),
                "data_source": item.get("data_source"),
            }
            insert_columns = [column for column in value_map.keys() if column in available_columns]
            placeholders = ", ".join(["?"] * len(insert_columns))
            columns_sql = ", ".join(insert_columns)
            insert_values = [value_map[column] for column in insert_columns]
            cursor.execute(
                f"INSERT INTO news_articles ({columns_sql}) VALUES ({placeholders})",
                insert_values,
            )
        connection.commit()


def save_analysis_history(
    query_text: str,
    symbol: str,
    market: str,
    trend_result: dict[str, Any],
    sentiment_summary: dict[str, Any],
    source_provider: str,
    data_source: str,
) -> None:
    """保存分析历史。"""
    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO analysis_history (
                query_text, symbol, market, trend_label, confidence_hint,
                sentiment_summary, source_provider, data_source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                query_text,
                symbol,
                market,
                trend_result.get("trend_label"),
                trend_result.get("confidence_hint"),
                (
                    f"正面{sentiment_summary.get('positive_count', 0)}条 / "
                    f"中性{sentiment_summary.get('neutral_count', 0)}条 / "
                    f"负面{sentiment_summary.get('negative_count', 0)}条 / "
                    f"均分{sentiment_summary.get('average_sentiment_score', 0)} / "
                    f"结论{sentiment_summary.get('overall_conclusion', '中性')}"
                ),
                source_provider,
                data_source,
            ),
        )
        connection.commit()


def get_recent_analysis_history(limit: int = 6) -> list[dict[str, Any]]:
    """读取最近分析记录。"""
    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        rows = cursor.execute(
            """
            SELECT query_text, symbol, market, trend_label, confidence_hint,
                   source_provider, data_source, created_at
            FROM analysis_history
            ORDER BY datetime(created_at) DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
