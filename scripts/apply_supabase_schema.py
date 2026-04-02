# -*- coding: utf-8 -*-
"""Aplica sql/supabase_schema.sql usando DIRECT_URL (una vez)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def split_sql(sql: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    for line in sql.splitlines():
        s = line.strip()
        if not s or s.startswith("--"):
            continue
        buf.append(line)
        if s.endswith(";"):
            parts.append("\n".join(buf))
            buf = []
    if buf:
        parts.append("\n".join(buf))
    return [p.strip() for p in parts if p.strip()]


def main() -> int:
    url = (os.environ.get("DIRECT_URL") or "").strip() or (os.environ.get("DATABASE_URL") or "").strip()
    if not url:
        print("Falta DIRECT_URL o DATABASE_URL en .env", file=sys.stderr)
        return 1
    sql_path = ROOT / "sql" / "supabase_schema.sql"
    if not sql_path.is_file():
        print("No existe", sql_path, file=sys.stderr)
        return 1
    raw = sql_path.read_text(encoding="utf-8")
    statements = split_sql(raw)
    import psycopg

    try:
        with psycopg.connect(url, autocommit=True) as conn:
            with conn.cursor() as cur:
                for stmt in statements:
                    cur.execute(stmt)
        print("Esquema aplicado:", len(statements), "sentencias.")
        return 0
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
