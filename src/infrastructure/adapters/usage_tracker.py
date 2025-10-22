import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class APIUsage:
    id: Optional[int] = None
    timestamp: str = ""
    api_name: str = ""
    endpoint: str = ""
    request_data: Dict = None
    response_data: Dict = None
    tokens_used: int = 0
    cost_usd: float = 0.0
    session_id: str = ""
    success: bool = True
    error_message: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.request_data is None:
            self.request_data = {}
        if self.response_data is None:
            self.response_data = {}


class UsageTracker:
    def __init__(self, db_file: str = "usage_tracking.db"):
        self.db_file = Path(db_file)
        self._init_database()

    def _init_database(self):
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    api_name TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    request_data TEXT,
                    response_data TEXT,
                    tokens_used INTEGER DEFAULT 0,
                    cost_usd REAL DEFAULT 0.0,
                    session_id TEXT,
                    success BOOLEAN DEFAULT 1,
                    error_message TEXT DEFAULT ''
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON api_usage(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_api_name ON api_usage(api_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON api_usage(session_id)")

    def track_usage(self, usage: APIUsage):
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""
                INSERT INTO api_usage (
                    timestamp, api_name, endpoint, request_data, response_data,
                    tokens_used, cost_usd, session_id, success, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                usage.timestamp,
                usage.api_name,
                usage.endpoint,
                json.dumps(usage.request_data),
                json.dumps(usage.response_data),
                usage.tokens_used,
                usage.cost_usd,
                usage.session_id,
                usage.success,
                usage.error_message
            ))

    def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row

            # Estadísticas generales
            cursor = conn.execute("""
                SELECT
                    api_name,
                    COUNT(*) as total_calls,
                    SUM(cost_usd) as total_cost,
                    SUM(tokens_used) as total_tokens,
                    AVG(cost_usd) as avg_cost_per_call,
                    COUNT(CASE WHEN success = 0 THEN 1 END) as failed_calls
                FROM api_usage
                WHERE datetime(timestamp) >= datetime('now', '-{} days')
                GROUP BY api_name
                ORDER BY total_cost DESC
            """.format(days))

            api_stats = [dict(row) for row in cursor.fetchall()]

            # Estadísticas por día
            cursor = conn.execute("""
                SELECT
                    date(timestamp) as date,
                    api_name,
                    SUM(cost_usd) as daily_cost,
                    COUNT(*) as daily_calls
                FROM api_usage
                WHERE datetime(timestamp) >= datetime('now', '-{} days')
                GROUP BY date(timestamp), api_name
                ORDER BY date DESC
            """.format(days))

            daily_stats = [dict(row) for row in cursor.fetchall()]

            # Total general
            cursor = conn.execute("""
                SELECT
                    SUM(cost_usd) as total_cost,
                    COUNT(*) as total_calls,
                    SUM(tokens_used) as total_tokens
                FROM api_usage
                WHERE datetime(timestamp) >= datetime('now', '-{} days')
            """.format(days))

            totals = dict(cursor.fetchone())

            return {
                "api_stats": api_stats,
                "daily_stats": daily_stats,
                "totals": totals,
                "period_days": days
            }

    def get_session_usage(self, session_id: str) -> List[Dict]:
        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM api_usage
                WHERE session_id = ?
                ORDER BY timestamp
            """, (session_id,))
            return [dict(row) for row in cursor.fetchall()]

    def calculate_suno_cost(self, response_data: Dict) -> float:
        # Estimación de costos para SunoAPI
        # Normalmente son $0.015 por generación
        return 0.015

    def calculate_replicate_cost(self, model: str, response_data: Dict) -> float:
        # Costos estimados de Replicate por modelo
        costs = {
            "bytedance/seedream-4": 0.005,  # por imagen
            "wan-video/wan-2.2-i2v-fast": 0.02,  # por video
        }
        return costs.get(model, 0.01)

    def calculate_openai_cost(self, model: str, tokens_used: int) -> float:
        # Costos de OpenAI por token
        costs_per_1k = {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
        }
        cost_per_1k = costs_per_1k.get(model, 0.002)
        return (tokens_used / 1000) * cost_per_1k


# Singleton global
_tracker = None

def get_tracker() -> UsageTracker:
    global _tracker
    if _tracker is None:
        _tracker = UsageTracker()
    return _tracker