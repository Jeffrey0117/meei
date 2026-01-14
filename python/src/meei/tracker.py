"""
用量追蹤模組 - SQLite 記錄每次 API 調用
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from meei.crypto import MEEI_DIR

DB_FILE = MEEI_DIR / "meei.db"


def _ensure_db():
    """確保資料庫存在並建立表格"""
    MEEI_DIR.mkdir(exist_ok=True)

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT,
                type TEXT NOT NULL,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                cost REAL DEFAULT 0,
                success INTEGER DEFAULT 1,
                latency_ms INTEGER DEFAULT 0,
                prompt TEXT,
                error TEXT
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON usage(timestamp)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_provider ON usage(provider)
        """)


@contextmanager
def get_db():
    """取得資料庫連線"""
    _ensure_db()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def track(
    provider: str,
    type: str,
    model: str = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost: float = 0,
    success: bool = True,
    latency_ms: int = 0,
    prompt: str = None,
    error: str = None,
):
    """記錄一次 API 調用"""
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO usage (
                timestamp, provider, model, type,
                input_tokens, output_tokens, total_tokens,
                cost, success, latency_ms, prompt, error
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                provider,
                model,
                type,
                input_tokens,
                output_tokens,
                input_tokens + output_tokens,
                cost,
                1 if success else 0,
                latency_ms,
                prompt[:500] if prompt else None,  # 只存前 500 字
                error,
            ),
        )
        conn.commit()


def get_usage_summary(
    days: int = 30,
    provider: str = None,
) -> Dict[str, Any]:
    """取得用量摘要"""
    since = (datetime.now() - timedelta(days=days)).isoformat()

    with get_db() as conn:
        query = """
            SELECT
                provider,
                COUNT(*) as total_requests,
                SUM(total_tokens) as total_tokens,
                SUM(cost) as total_cost,
                AVG(latency_ms) as avg_latency,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count
            FROM usage
            WHERE timestamp > ?
        """
        params = [since]

        if provider:
            query += " AND provider = ?"
            params.append(provider)

        query += " GROUP BY provider"

        rows = conn.execute(query, params).fetchall()

        return {
            "period_days": days,
            "providers": [dict(row) for row in rows],
            "total_cost": sum(row["total_cost"] or 0 for row in rows),
            "total_requests": sum(row["total_requests"] for row in rows),
        }


def get_recent_requests(limit: int = 50) -> List[Dict[str, Any]]:
    """取得最近的請求記錄"""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM usage
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [dict(row) for row in rows]


def get_daily_usage(days: int = 30) -> List[Dict[str, Any]]:
    """取得每日用量統計"""
    since = (datetime.now() - timedelta(days=days)).isoformat()

    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT
                DATE(timestamp) as date,
                COUNT(*) as requests,
                SUM(cost) as cost,
                SUM(total_tokens) as tokens
            FROM usage
            WHERE timestamp > ?
            GROUP BY DATE(timestamp)
            ORDER BY date
            """,
            (since,),
        ).fetchall()

        return [dict(row) for row in rows]
