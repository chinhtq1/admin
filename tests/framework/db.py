"""PostgreSQL/TimescaleDB helper (psycopg 3, same version as ingest/tools)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

from framework import REPO_ROOT
from framework.wait import wait_for_value

INIT_SQL = REPO_ROOT / "infra" / "db" / "init.sql"


class Db:
    """Autocommit connection with small query helpers. Use as a context manager."""

    def __init__(self, dsn: str, *, connect_timeout: int = 5) -> None:
        self.dsn = dsn
        self.conn = psycopg.connect(dsn, autocommit=True, connect_timeout=connect_timeout, row_factory=dict_row)

    def __enter__(self) -> Db:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self.conn.close()

    def rows(self, sql: str, params: Sequence[Any] | dict[str, Any] | None = None) -> list[dict[str, Any]]:
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            return list(cur.fetchall()) if cur.description else []

    def scalar(self, sql: str, params: Sequence[Any] | dict[str, Any] | None = None) -> Any:
        with self.conn.cursor(row_factory=psycopg.rows.tuple_row) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return None if row is None else row[0]

    def execute(self, sql: str, params: Sequence[Any] | dict[str, Any] | None = None) -> None:
        with self.conn.cursor() as cur:
            cur.execute(sql, params)

    def wait_for_rows(
        self,
        sql: str,
        params: Sequence[Any] | dict[str, Any] | None = None,
        *,
        min_rows: int = 1,
        timeout: float = 30.0,
        interval: float = 0.5,
    ) -> list[dict[str, Any]]:
        return wait_for_value(
            lambda: self.rows(sql, params),
            lambda r: len(r) >= min_rows,
            timeout=timeout,
            interval=interval,
            desc=f">= {min_rows} rows for: {sql.strip()[:120]}",
        )

    def apply_sql_file(self, path: Path = INIT_SQL) -> None:
        self.execute(path.read_text(encoding="utf-8"))

    def tables(self) -> set[str]:
        return {
            r["table_name"]
            for r in self.rows("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        }
