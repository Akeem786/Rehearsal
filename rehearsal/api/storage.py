"""SQLite persistence storage for Rehearsal evaluation runs and test history."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional
from rehearsal.api.schemas import RunSummary
from rehearsal.runner.models import EvaluationReport

logger = logging.getLogger("rehearsal.api.storage")

DEFAULT_DB_PATH = Path("rehearsal_history.sqlite3")


class EvaluationStorage:
    """Thread-safe SQLite storage repository for persisting evaluation reports."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = str(db_path or DEFAULT_DB_PATH)
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Establish a sqlite3 database connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Create database tables and indices if they do not exist."""
        create_sql = """
        CREATE TABLE IF NOT EXISTS evaluation_runs (
            run_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            domain TEXT,
            total_cases INTEGER NOT NULL,
            tool_accuracy REAL NOT NULL,
            exact_match_rate REAL NOT NULL,
            f1_score REAL NOT NULL,
            average_duration_seconds REAL NOT NULL,
            report_json TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_runs_created_at ON evaluation_runs(created_at DESC);
        """
        with self._get_connection() as conn:
            conn.executescript(create_sql)
            conn.commit()

    def save_run(
        self,
        run_id: str,
        domain: Optional[str],
        report: EvaluationReport,
        created_at: Optional[str] = None,
    ) -> RunSummary:
        """Persist an evaluation run and return its summary."""
        timestamp = created_at or datetime.now(timezone.utc).isoformat()
        report_json_str = report.to_json()

        insert_sql = """
        INSERT OR REPLACE INTO evaluation_runs (
            run_id, created_at, domain, total_cases, tool_accuracy,
            exact_match_rate, f1_score, average_duration_seconds, report_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        with self._get_connection() as conn:
            conn.execute(
                insert_sql,
                (
                    run_id,
                    timestamp,
                    domain,
                    report.total_cases,
                    report.tool_selection_accuracy,
                    report.exact_argument_match_rate,
                    report.slot_metrics.f1_score,
                    report.average_estimated_speech_duration_seconds,
                    report_json_str,
                ),
            )
            conn.commit()

        return RunSummary(
            run_id=run_id,
            created_at=timestamp,
            domain=domain,
            total_cases=report.total_cases,
            tool_accuracy=report.tool_selection_accuracy,
            exact_match_rate=report.exact_argument_match_rate,
            f1_score=report.slot_metrics.f1_score,
            average_duration_seconds=report.average_estimated_speech_duration_seconds,
        )

    def count_runs(self) -> int:
        """Return the total number of saved evaluation runs."""
        with self._get_connection() as conn:
            cur = conn.execute("SELECT COUNT(*) FROM evaluation_runs;")
            row = cur.fetchone()
            return int(row[0]) if row else 0

    def list_runs(self, limit: int = 20, offset: int = 0) -> List[RunSummary]:
        """Query recent evaluation runs ordered newest first with pagination."""
        query_sql = """
        SELECT run_id, created_at, domain, total_cases, tool_accuracy,
               exact_match_rate, f1_score, average_duration_seconds
        FROM evaluation_runs
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?;
        """
        with self._get_connection() as conn:
            cur = conn.execute(query_sql, (limit, offset))
            rows = cur.fetchall()

        summaries: List[RunSummary] = []
        for r in rows:
            summaries.append(
                RunSummary(
                    run_id=r["run_id"],
                    created_at=r["created_at"],
                    domain=r["domain"],
                    total_cases=r["total_cases"],
                    tool_accuracy=r["tool_accuracy"],
                    exact_match_rate=r["exact_match_rate"],
                    f1_score=r["f1_score"],
                    average_duration_seconds=r["average_duration_seconds"],
                )
            )
        return summaries

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve complete evaluation run report by ID, or None if not found."""
        query_sql = """
        SELECT run_id, created_at, domain, total_cases, tool_accuracy,
               exact_match_rate, f1_score, average_duration_seconds, report_json
        FROM evaluation_runs
        WHERE run_id = ?;
        """
        with self._get_connection() as conn:
            cur = conn.execute(query_sql, (run_id,))
            row = cur.fetchone()

        if not row:
            return None

        try:
            report_data = json.loads(row["report_json"])
        except Exception as exc:
            logger.error("Failed to parse stored JSON for run %s: %s", run_id, exc)
            report_data = {}

        return {
            "run_id": row["run_id"],
            "created_at": row["created_at"],
            "domain": row["domain"],
            "summary": {
                "total_cases": row["total_cases"],
                "tool_accuracy": row["tool_accuracy"],
                "exact_match_rate": row["exact_match_rate"],
                "f1_score": row["f1_score"],
                "average_duration_seconds": row["average_duration_seconds"],
            },
            "report": report_data,
        }
