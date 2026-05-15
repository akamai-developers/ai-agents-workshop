"""Persistent memory tools backed by SQLite.

These are the same kind of @tool you wrote in Section 2 — just with a
real persistence layer behind them. The DB lives at memory.db in the
workshop directory and survives across runs, so a fact you remember in
one process is recallable in the next.

What students take away:
  • "memory" isn't a magic Strands feature — it's a tool that reads
    and writes a store. Pick any store: SQLite, Redis, mem0, S3.
  • If you can describe the store with a docstring, the model can use it.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from strands import tool

DB_PATH = Path(__file__).resolve().parent.parent.parent / "memory.db"


def _conn() -> sqlite3.Connection:
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """CREATE TABLE IF NOT EXISTS facts (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT    NOT NULL,
            fact    TEXT    NOT NULL,
            created TEXT    NOT NULL
        )"""
    )
    db.execute("CREATE INDEX IF NOT EXISTS idx_facts_user ON facts(user_id)")
    return db


@tool
def remember_fact(user_id: str, fact: str) -> str:
    """Persist a single fact about a user. Use this whenever the user
    tells you something durable about themselves — a preference, a name,
    a favorite team, a constraint.

    Args:
        user_id: Stable identifier for the user (e.g. "alex").
        fact: A short, self-contained statement to remember.
    """
    db = _conn()
    db.execute(
        "INSERT INTO facts(user_id, fact, created) VALUES (?,?,?)",
        (user_id, fact.strip(), datetime.now(timezone.utc).isoformat()),
    )
    db.commit()
    db.close()
    return f"Stored fact for {user_id}: {fact.strip()}"


@tool
def recall_facts(user_id: str) -> str:
    """Return everything we know about a user, oldest first. Call this
    at the start of a conversation so you can personalize your reply.

    Args:
        user_id: Stable identifier for the user (e.g. "alex").
    """
    db = _conn()
    rows = db.execute(
        "SELECT fact FROM facts WHERE user_id = ? ORDER BY id ASC",
        (user_id,),
    ).fetchall()
    db.close()
    if not rows:
        return f"No facts on file for {user_id}."
    return "\n".join(f"- {fact}" for (fact,) in rows)


@tool
def forget_facts(user_id: str) -> str:
    """Delete every stored fact for a user. Use when the user explicitly
    asks to be forgotten or reset.

    Args:
        user_id: Stable identifier for the user (e.g. "alex").
    """
    db = _conn()
    cur = db.execute("DELETE FROM facts WHERE user_id = ?", (user_id,))
    db.commit()
    deleted = cur.rowcount
    db.close()
    return f"Forgot {deleted} fact(s) for {user_id}."
