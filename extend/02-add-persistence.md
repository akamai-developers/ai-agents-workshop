# Challenge 2: Production-Grade Persistence

> §5 gave you `heartbeat_log(job_type, job_key)`. Production needs two more tables and a state machine.

## What You Saw in the Workshop

§4 gave you a `facts` table for user memory the agent reads/writes:

```sql
CREATE TABLE facts (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    fact    TEXT NOT NULL,
    created TEXT NOT NULL
);
```

§5 added a `heartbeat_log` table for controller-level idempotency:

```sql
CREATE TABLE heartbeat_log (
    job_type  TEXT NOT NULL,
    job_key   TEXT NOT NULL,
    posted_at INTEGER NOT NULL,
    PRIMARY KEY (job_type, job_key)
);
```

That `UNIQUE (job_type, job_key)` is what makes the heartbeat exactly-once on the controller side — `INSERT OR IGNORE` is safe to retry. That alone gets you far. But two things still leak.

## What Still Breaks at Scale

1. **No per-game state machine**. The workshop heartbeat treats games as binary (final-or-not). Production needs to know "did this game transition Q3 → Q4 since my last tick?" — that's a state column with a `last_seen` timestamp.
2. **No linkage to side effects**. When the heartbeat creates a Discord thread for a game, the `thread_id` needs to outlive the Python process. Otherwise tomorrow's heartbeat can't post the postgame summary into the right thread.

## What Production Adds

```sql
-- Already in §5: idempotency log
CREATE TABLE heartbeat_log (
    job_type   TEXT NOT NULL,
    job_key    TEXT NOT NULL,
    posted_at  INTEGER NOT NULL,
    PRIMARY KEY (job_type, job_key)
);

-- NEW: per-game state machine
CREATE TABLE game_state (
    game_id    TEXT PRIMARY KEY,
    status     TEXT NOT NULL,   -- 'pregame' | 'live' | 'final'
    updated_at INTEGER NOT NULL
);

-- NEW: linkage to Discord threads (the side-effect target)
CREATE TABLE game_threads (
    game_id    TEXT PRIMARY KEY,
    thread_id  INTEGER NOT NULL,
    created_at INTEGER NOT NULL
);
```

## Build It

### Step 1 — add the new tables

Extend the `_conn()` helper in `05_heartbeat.py` so it creates all three tables. Add tiny accessor functions next to `already_posted` / `mark_posted`:

```python
def get_game_state(game_id: str) -> str | None:
    with _conn() as db:
        row = db.execute(
            "SELECT status FROM game_state WHERE game_id = ?", (game_id,)
        ).fetchone()
    return row[0] if row else None


def set_game_state(game_id: str, status: str) -> None:
    with _conn() as db:
        db.execute(
            "INSERT OR REPLACE INTO game_state VALUES (?, ?, ?)",
            (game_id, status, int(time.time())),
        )
        db.commit()
```

### Step 2 — use the state machine in `build_context`

The workshop's `new_finals` filter is naïve: "is_final AND not in heartbeat_log". The production version asks "has this game *transitioned to* final since I last looked?":

```python
def build_context() -> dict:
    games = fetch_scoreboard()
    new_finals = []
    for g in games:
        if g["is_final"] and get_game_state(g["id"]) != "final":
            new_finals.append(g)
    return {..., "new_finals": new_finals}


# inside exec_postgame_highlight, after the post succeeds:
set_game_state(game_id, "final")
mark_posted("highlight", game_id)
```

Now you can answer questions like "which games went final in the last 10 minutes?" — a state transition, not just a flag.

### Step 3 — wire up `game_threads`

When you add a `create_game_thread` action (extend/01 shows you the Discord side), the thread ID needs to outlive the Python process. Save it to `game_threads` on creation, look it up by `game_id` when the postgame_highlight executor runs:

```python
def exec_postgame_highlight(agent, ctx, game_id):
    ...
    thread_id = get_thread_id(game_id)
    target = client.get_channel(thread_id) if thread_id else default_channel
    # ...
```

### Step 4 — test the crash case

Add `raise Exception("crash!")` between the `mark_posted` and the Discord send. Re-run. The crash leaks a "posted in the log, never actually sent" entry. That's the fundamental trade-off — idempotency log + real side effect are two writes, and you can't make them atomic.

Three ways to handle it:

1. **Treat duplicates as acceptable.** Mark_posted FIRST, then post. A retry might double-post. Fine for low-stakes side effects.
2. **Mark after the side effect.** Post to Discord FIRST, then mark_posted. A crash leaves the log unmarked → the next tick reposts. Fine if Discord posts have a natural dedup key.
3. **Outbox pattern.** Stage the work in a third table (`pending_actions`), then a background worker drains the outbox. Atomicity moves to "claim outbox row" → "do side effect" → "delete outbox row". The production agent does a softer version of this.

## Reference

See `nba-discord-agent/src/heartbeat.py` and the README in `src/` for the full schema, indexes, and pruning loop (`_prune_stale_data` deletes rows older than 7 days).

## Why This Challenge Matters

§5 taught you the 5-phase shape. This challenge teaches the schema design that makes phase 5 (state) survive contact with reality. The controller code barely changes between toy and production — but the table layout determines whether you can sleep at night.

## Reference

See `nba-discord-agent/src/heartbeat.py` and `src/db.py` in the production repo for the full schema, indexes, and the outbox-pattern explanation.

## Why This Challenge Matters

§4 taught you the tool pattern. This challenge teaches you the *schema design* that makes the tool pattern survive contact with reality. The agent code barely changes between toy SQLite and production SQLite — but the table layout determines whether you can sleep at night.
