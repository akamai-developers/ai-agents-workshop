# Challenge 2: Add Persistence

> Track what the heartbeat has posted so it never duplicates.

## What You'll Build

Add SQLite to the heartbeat so it remembers what it has already posted across restarts.

## The Problem

The workshop heartbeat uses an in-memory `already_posted` list. Restart the script and it forgets everything. The production agent solves this with SQLite.

## Steps

### 1. Create the Database

```python
import sqlite3
from pathlib import Path

DB_PATH = "agent.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS heartbeat_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_type TEXT NOT NULL,
            job_key TEXT NOT NULL UNIQUE,
            posted_at INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def already_posted(job_type: str, key: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT 1 FROM heartbeat_log WHERE job_type = ? AND job_key = ?",
        (job_type, key),
    ).fetchone()
    conn.close()
    return row is not None

def mark_posted(job_type: str, key: str):
    import time
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR IGNORE INTO heartbeat_log (job_type, job_key, posted_at) VALUES (?, ?, ?)",
        (job_type, key, int(time.time())),
    )
    conn.commit()
    conn.close()
```

### 2. Update get_current_context()

Replace the hardcoded `already_posted` list:

```python
def get_current_context():
    context = {
        # ... existing context gathering ...
        "already_posted": _get_posted_game_ids(),
    }
    return context

def _get_posted_game_ids():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT job_key FROM heartbeat_log WHERE job_type = 'game_recap'"
    ).fetchall()
    conn.close()
    return [row[0] for row in rows]
```

### 3. Mark Games as Posted

After the heartbeat agent decides to post:

```python
result = run_heartbeat(model=model, criteria=criteria, context=context)

# Parse the result for POST decisions and mark them
for game in context["recently_finished"]:
    if game["game_id"] not in context["already_posted"]:
        if f"POST" in result:  # Simple check — production uses JSON parsing
            mark_posted("game_recap", game["game_id"])
```

### 4. Test It

Run the heartbeat twice. The second run should skip games that were posted in the first run.

## Design Principle: Idempotency

The `UNIQUE` constraint on `job_key` means `INSERT OR IGNORE` is safe to call multiple times. The heartbeat can crash and restart without duplicating posts. This is the production pattern.

## Reference

See `nba-discord-agent/src/heartbeat.py` lines 56-96 for the full SQLite schema with three tables: `heartbeat_log`, `game_threads`, and `game_state`.
