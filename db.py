# -*- coding: utf-8 -*-
"""
Capa de acceso a datos: SQLite (local) o PostgreSQL / Supabase (SaaS).
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Iterator, Optional, Sequence

# Marcador de placeholder según motor
_PG = "%s"
_SQLITE = "?"

_sqlite_path: Optional[str] = None
_pg_pool = None


def is_postgres() -> bool:
    return bool(os.environ.get("DATABASE_URL", "").strip())


def set_sqlite_path(path: str) -> None:
    global _sqlite_path
    _sqlite_path = path


def _sqlite_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_sqlite_path, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=10000")
    conn.execute("PRAGMA temp_store=MEMORY")
    return conn


def _get_pg_pool():
    global _pg_pool
    if _pg_pool is None:
        from psycopg_pool import ConnectionPool
        from psycopg.rows import dict_row

        url = os.environ["DATABASE_URL"].strip()
        _pg_pool = ConnectionPool(
            conninfo=url,
            min_size=0,
            max_size=5,
            kwargs={"row_factory": dict_row},
            timeout=30.0,
            max_idle=300.0,
        )
    return _pg_pool


@contextmanager
def get_connection() -> Iterator[Any]:
    if is_postgres():
        pool = _get_pg_pool()
        with pool.connection() as conn:
            yield conn
    else:
        conn = _sqlite_conn()
        try:
            yield conn
        finally:
            conn.close()


def q(sql: str) -> str:
    """Convierte SQL con marcadores %s al estilo del motor activo."""
    if is_postgres():
        return sql
    out = []
    i = 0
    while i < len(sql):
        if sql[i] == "%" and i + 1 < len(sql) and sql[i + 1] == "s":
            out.append(_SQLITE)
            i += 2
            continue
        out.append(sql[i])
        i += 1
    return "".join(out)


def execute(cur: Any, sql: str, params: Sequence[Any] = ()) -> Any:
    return cur.execute(q(sql), params)


def fetchone(cur: Any) -> Optional[Any]:
    return cur.fetchone()


def fetchall(cur: Any) -> list:
    return list(cur.fetchall())


def commit(conn: Any) -> None:
    conn.commit()


def is_unique_violation(exc: BaseException) -> bool:
    if isinstance(exc, sqlite3.IntegrityError):
        return "UNIQUE" in str(exc).upper()
    try:
        from psycopg.errors import UniqueViolation

        if isinstance(exc, UniqueViolation):
            return True
    except ImportError:
        pass
    name = type(exc).__name__
    if name == "IntegrityError" and "psycopg" in type(exc).__module__:
        return "unique" in str(exc).lower()
    return False


def is_foreign_violation(exc: BaseException) -> bool:
    if isinstance(exc, sqlite3.IntegrityError):
        return "FOREIGN" in str(exc).upper()
    name = type(exc).__name__
    if name == "IntegrityError" and "psycopg" in type(exc).__module__:
        return "foreign" in str(exc).lower()
    return False
