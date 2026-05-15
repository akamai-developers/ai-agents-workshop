# Section 5: Autonomous Reasoning — The Heartbeat

[← Memory](04-conversation-memory.md) · [Index](README.md) · [Next → What's Next](06-whats-next.md)

> The LLM is a router and a writer, not a controller. Python is the controller.

## What You'll Learn

- The 5-phase heartbeat pattern used in production
- Why most heartbeat ticks shouldn't call the LLM at all
- LLM-as-router: structured JSON output instead of prose
- One focused prompt per action — not one giant prompt that does everything
- SQLite idempotency log so a crash mid-tick can't double-post

## Bridge from §4

§4 was **memory the agent reads** — `remember_fact` / `recall_facts` exposed as `@tool` functions, with the LLM deciding when to call them.

§5 is **memory the controller reads** — `already_posted` / `mark_posted`, plain Python helpers that the controller calls directly. Same `memory.db` file, different table. The controller doesn't need the LLM's permission to log idempotency, so we skip the `@tool` wrapper.

Two layers of persistence, two different abstractions.

## The Key Idea

Naïve heartbeat: "every 60 seconds, ask the agent what to do, let it figure everything out." That burns GPU 1,440 times a day even when nothing's happening, and the agent has to plan AND write in a single shot. It also has no way to guarantee it won't repeat itself.

Production heartbeat looks like this:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CONTEXT    (Python, no LLM)   fetch scoreboard,         │
│                                   read SQLite, build dict   │
│                                                             │
│ 2. PRE-CHECK  (Python boolean)   is there ANY work?         │
│                                  → No: skip everything       │
│                                                             │
│ 3. REASON     (LLM, JSON out)    "given state, what runs?" │
│                                  → [{"action": "..."}, ...] │
│                                                             │
│ 4. EXECUTE    (Python + LLM)     one focused prompt per     │
│                                  action; mark_posted on ok  │
│                                                             │
│ 5. STATE      (SQLite, UNIQUE)   heartbeat_log idempotency │
└─────────────────────────────────────────────────────────────┘
```

Each phase is small and obvious. Python orchestrates; the LLM does the parts that genuinely need reasoning (Phase 3) or natural-language generation (Phase 4).

### Phase 1 — context (no LLM)

```python
def fetch_scoreboard():
    url = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
    # direct HTTP call — we don't need the LLM to know which games exist

def build_context():
    games = fetch_scoreboard()
    return {
        "today": date.today().isoformat(),
        "games": games,
        "new_finals": [g for g in games
                       if g["is_final"] and not already_posted("highlight", g["id"])],
        "preview_posted": already_posted("preview", date.today().isoformat()),
    }
```

### Phase 2 — pre-check gate (no LLM)

```python
def has_work(ctx):
    if ctx["new_finals"]:
        return True
    if 9 <= ctx["hour"] < 14 and ctx["games"] and not ctx["preview_posted"]:
        return True
    return False
```

A boolean. Most ticks (overnight, off-season, between games) return `False` and we sleep. **The LLM doesn't get invoked at all.** That's the single biggest production win.

### Phase 3 — reason (LLM, JSON out)

```python
HEARTBEAT_DECISIONS = """
Available actions:
  - {"action": "postgame_highlight", "game_id": "<id>"}
  - {"action": "gameday_preview"}

Return ONLY a JSON array of action objects, or HEARTBEAT_OK.
"""
```

The agent gets the pre-computed state and the action menu, and emits structured data. Python parses it. **No regex-matching "POST:" out of a paragraph.**

### Phase 4 — executors (Python + focused LLM)

```python
def exec_postgame_highlight(agent, ctx, game_id):
    game = lookup(ctx, game_id)
    response = agent(
        f"Write a 2-3 sentence highlight. Final: {game['away']} ... {game['home']} ..."
        " Use your tools to fetch the box score."
    )
    print(response)
    mark_posted("highlight", game_id)
```

Each action has its own executor with a focused prompt — the agent isn't trying to plan a recap AND write it in the same call. After success, `mark_posted` writes to SQLite.

### Phase 5 — idempotency log

```sql
CREATE TABLE heartbeat_log (
    job_type  TEXT,
    job_key   TEXT,
    posted_at INTEGER,
    PRIMARY KEY (job_type, job_key)
);
```

`INSERT OR IGNORE` is the magic. Call `mark_posted` twice — second one is a no-op. The next tick's `has_work` sees the log entry and short-circuits. That's exactly-once on the controller side.

## Run It

```
python 05_heartbeat.py
```

## Expected Output

**First run, tick 1** — newly-final games exist, no log entries yet:
```
============================================================
  TICK 1/2
============================================================
  Phase 2: work detected. Asking the agent what to do…
  Phase 3: agent decided → ['postgame_highlight', 'postgame_highlight']

🚨 [postgame_highlight GSW@LAL]
**Warriors** held off the Lakers 108-102. Curry 32/8/5…

🚨 [postgame_highlight DEN@MIN]
**Nuggets** rolled past the Wolves 117-104. Jokić triple-double…

  (sleeping 5s…)
```

**Tick 2 of the same run** — Phase 5 already logged both highlights:
```
============================================================
  TICK 2/2
============================================================
  HEARTBEAT_OK — nothing to do, skipped LLM entirely.
```

That second tick is the whole point. Phase 2 saw an empty `new_finals` list (everything's in `heartbeat_log`) and short-circuited before Phase 3. **In production, that's the state of 95% of ticks.**

## Try This

1. **Run twice.** On the second run, tick 1 should also short-circuit — because run #1 already logged everything. Delete `memory.db` to reset.
2. **Add a new action.** Add `weekly_standings`:
   - Document it inside `HEARTBEAT_DECISIONS`
   - Add an entry to `EXECUTORS`
   - Add a trigger to `has_work()`
   Three places. One feature.
3. **Make it a real bot.** Replace `print(response)` in each executor with `urllib.request.urlopen(discord_webhook_url, ...)`. You now have a Discord bot.
4. **Run it for real.** Wrap the `for tick` loop in `while True: ...; time.sleep(60)`. Walk away.

## What Just Happened

You built the production heartbeat pattern. Python orchestrates: it fetches data, checks state, and decides whether to even talk to the LLM. The LLM does two things, both bounded — emit JSON (Phase 3) and write content (Phase 4). SQLite gives you exactly-once via a `UNIQUE` constraint. **The agent isn't autonomous because it loops forever — it's autonomous because the controller hands it a small, well-shaped decision each tick.**

Reference implementation (asyncio, Discord, ~880 lines):
- [`src/heartbeat.py`](https://github.com/labeveryday/nba-discord-agent/blob/main/src/heartbeat.py)
- [`src/HEARTBEAT.md`](https://github.com/labeveryday/nba-discord-agent/blob/main/src/HEARTBEAT.md)

Next: [What's Next](06-whats-next.md)
