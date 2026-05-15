# ============================================================
# SECTION 5 — Heartbeat (production shape)
# ============================================================
# Up to now the agent was always THE controller. This is wrong
# for any agent that loops. The production NBA Discord bot uses
# a 5-phase pattern where Python is the controller and the LLM
# is only used when it's actually needed:
#
#   1. CONTEXT       (Python, no LLM)  — fetch + read state
#   2. PRE-CHECK     (Python boolean)  — is there ANY work?
#   3. REASON        (LLM, JSON out)   — which actions should run?
#   4. EXECUTE       (Python + LLM)    — one focused prompt each
#   5. STATE         (SQLite)          — idempotency log
#
# Why this matters:
#   • Most ticks have nothing to do — Phase 2 short-circuits
#     before the LLM is ever called. Saves GPU. Saves latency.
#   • Phase 3 returns STRUCTURED data (JSON), not prose. Python
#     dispatches on it. No regex-parsing a paragraph for "POST:".
#   • Each executor in Phase 4 has its own focused prompt — the
#     agent isn't trying to plan AND write in one shot.
#   • Phase 5 is a UNIQUE constraint in SQLite. Crash mid-tick
#     and the next tick won't double-post.
#
# This file mirrors src/heartbeat.py from the real bot, trimmed
# to ~150 lines so we can read it together.
#
# Run:  python 05_heartbeat.py
# ============================================================

import _path  # noqa: F401

import json
import sqlite3
import time
import urllib.request
from datetime import datetime
from pathlib import Path

from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.tools.mcp import MCPClient

from src.config import get_model
from src.hooks import LoggingHook


# ============================================================
# PHASE 5 first — the state layer everything else uses
# ============================================================
# Bridge from §4:
#   §4 was MEMORY THE AGENT READS — facts table, exposed via
#   @tool functions, the LLM calls them.
#   §5 is MEMORY THE CONTROLLER READS — heartbeat_log table,
#   plain Python helpers, the Python code calls them directly.
#   Same memory.db file. Different table. Different layer.
#
# Why no @tool here? Because the controller isn't reasoning
# about persistence — it knows it always wants idempotency.
# Wrapping these in @tool would just be the LLM asking
# permission from itself.
#
# Notice (job_type, job_key) is the PRIMARY KEY — INSERT OR
# IGNORE gives us exactly-once on the log side.

DB = Path(__file__).resolve().parent / "memory.db"


def _conn() -> sqlite3.Connection:
    db = sqlite3.connect(DB)
    db.execute("""
        CREATE TABLE IF NOT EXISTS heartbeat_log (
            job_type  TEXT    NOT NULL,
            job_key   TEXT    NOT NULL,
            posted_at INTEGER NOT NULL,
            PRIMARY KEY (job_type, job_key)
        )
    """)
    return db


def already_posted(job_type: str, key: str) -> bool:
    with _conn() as db:
        return db.execute(
            "SELECT 1 FROM heartbeat_log WHERE job_type=? AND job_key=?",
            (job_type, key),
        ).fetchone() is not None


def mark_posted(job_type: str, key: str) -> None:
    with _conn() as db:
        db.execute(
            "INSERT OR IGNORE INTO heartbeat_log VALUES (?,?,?)",
            (job_type, key, int(time.time())),
        )
        db.commit()


# ============================================================
# PHASE 1 — Build context (no LLM)
# ============================================================
# Direct HTTP to the NBA scoreboard endpoint. We don't need the
# LLM to know which games exist today — that's deterministic data.
#
# If the live API is unreachable (firewall on the code-server
# pod, NBA outage, or it's an NBA off-day) we fall back to a
# hardcoded fixture so the workshop still runs.

SCOREBOARD_URL = (
    "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
)

# Two finals + one in-progress — enough to show new_finals AND
# the Phase 2 dedup behavior across ticks.
FALLBACK_GAMES = [
    {"id": "0022501101", "away": "GSW", "home": "LAL",
     "away_score": 108, "home_score": 102,
     "status": "Final", "is_final": True},
    {"id": "0022501102", "away": "DEN", "home": "MIN",
     "away_score": 117, "home_score": 104,
     "status": "Final", "is_final": True},
    {"id": "0022501103", "away": "OKC", "home": "DAL",
     "away_score": 0,   "home_score": 0,
     "status": "8:30 PM ET", "is_final": False},
]


def fetch_scoreboard() -> list[dict]:
    try:
        req = urllib.request.Request(
            SCOREBOARD_URL, headers={"User-Agent": "ai-agents-workshop/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        games = [
            {
                "id": g["gameId"],
                "away": g["awayTeam"]["teamTricode"],
                "home": g["homeTeam"]["teamTricode"],
                "away_score": g["awayTeam"]["score"],
                "home_score": g["homeTeam"]["score"],
                "status": g.get("gameStatusText", "").strip(),
                "is_final": "final" in g.get("gameStatusText", "").lower(),
            }
            for g in data.get("scoreboard", {}).get("games", [])
        ]
        if games:
            return games
        print("  (live scoreboard returned 0 games — using fallback fixture)")
    except Exception as e:
        print(f"  (live scoreboard unreachable: {e} — using fallback fixture)")
    return [dict(g) for g in FALLBACK_GAMES]


def build_context() -> dict:
    games = fetch_scoreboard()
    today = datetime.now().strftime("%Y-%m-%d")
    return {
        "today": today,
        "hour": datetime.now().hour,
        "games": games,
        "new_finals": [
            g for g in games
            if g["is_final"] and not already_posted("highlight", g["id"])
        ],
        "preview_posted": already_posted("preview", today),
    }


# ============================================================
# PHASE 2 — Pre-check gate (no LLM)
# ============================================================
# Cheap boolean check. If False, we skip Phases 3-5 entirely —
# no LLM call, no Discord traffic, just sleep til the next tick.

def has_work(ctx: dict) -> bool:
    if ctx["new_finals"]:
        return True
    if 9 <= ctx["hour"] < 14 and ctx["games"] and not ctx["preview_posted"]:
        return True
    return False


# ============================================================
# PHASE 3 — Reason: LLM as a router, JSON output
# ============================================================
# This is the ONLY place we ask the LLM "what should we do?"
# Output is structured (JSON array), not prose. Python dispatches.

HEARTBEAT_DECISIONS = """
You are the controller for an NBA reporting bot.
Given the current state, decide which actions to run RIGHT NOW.

Available actions:
  - {"action": "postgame_highlight", "game_id": "<id>"}
      Post a 2-3 sentence recap of a newly-final game.
      Emit ONE of these per newly-final game.
  - {"action": "gameday_preview"}
      Post today's matchups. Only between 9 AM and 2 PM,
      and only if not already posted today.

Return ONLY a JSON array of action objects.
If nothing should run, return exactly: HEARTBEAT_OK
"""


def reason_about_actions(agent: Agent, ctx: dict) -> list[dict]:
    prompt = (
        f"{HEARTBEAT_DECISIONS}\n\n"
        f"## Current state\n"
        f"  today: {ctx['today']}\n"
        f"  current hour (24h): {ctx['hour']}\n"
        f"  games on the board today: {len(ctx['games'])}\n"
        f"  newly-final games (not yet highlighted):\n"
        + (
            "\n".join(
                f"    - id={g['id']}  {g['away']} {g['away_score']} @ "
                f"{g['home']} {g['home_score']}"
                for g in ctx["new_finals"]
            ) or "    (none)"
        )
        + f"\n  gameday_preview already posted today: {ctx['preview_posted']}\n\n"
        "What actions should run right now?"
    )
    response = str(agent(prompt)).strip()
    if "HEARTBEAT_OK" in response:
        return []
    start, end = response.find("["), response.rfind("]") + 1
    if start == -1 or end <= start:
        return []
    try:
        return [a for a in json.loads(response[start:end]) if "action" in a]
    except json.JSONDecodeError:
        return []


# ============================================================
# PHASE 4 — Executors: one focused prompt per action
# ============================================================
# Each executor knows EXACTLY what to do and asks the LLM only
# for the writing — not the planning. After success, mark_posted
# closes the idempotency loop.

def exec_postgame_highlight(agent: Agent, ctx: dict, game_id: str) -> None:
    game = next((g for g in ctx["games"] if g["id"] == game_id), None)
    if not game:
        return
    response = str(agent(
        f"Write a 2-3 sentence Discord post-game highlight.\n"
        f"Final: {game['away']} {game['away_score']} - "
        f"{game['home']} {game['home_score']}.\n"
        f"Use your tools to fetch the box score and pull out the top "
        f"performer. Bold the winning team. No game IDs."
    ))
    print(f"\n🚨 [postgame_highlight {game['away']}@{game['home']}]\n{response}\n")
    mark_posted("highlight", game_id)


def exec_gameday_preview(agent: Agent, ctx: dict) -> None:
    matchups = "\n".join(
        f"  {g['away']} @ {g['home']} — {g['status']}" for g in ctx["games"]
    )
    response = str(agent(
        f"Write a Discord game-day preview for today's matchups:\n"
        f"{matchups}\n"
        f"Two sentences total. Flag any standout matchup. No IDs."
    ))
    print(f"\n📋 [gameday_preview]\n{response}\n")
    mark_posted("preview", ctx["today"])


EXECUTORS = {
    "postgame_highlight": exec_postgame_highlight,
    "gameday_preview": lambda agent, ctx, **_: exec_gameday_preview(agent, ctx),
}


# ============================================================
# THE LOOP
# ============================================================
# In production: while True with sleep(60). Here we run 2 ticks
# so students can see Phase 2 short-circuit on tick 2 (because
# tick 1's mark_posted wrote everything to heartbeat_log).

NUM_TICKS = 2
SECONDS_BETWEEN = 5


nba_mcp = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="nba-stats-mcp", args=[])
))

with nba_mcp:
    nba_tools = nba_mcp.list_tools_sync()
    agent = Agent(
        model=get_model(),
        tools=nba_tools,
        # Inject today's date — the LLM doesn't know it, and the NBA
        # tools need it to fetch the right day's games.
        system_prompt=(
            f"You are a knowledgeable NBA reporter. Today's date is "
            f"{datetime.now():%Y-%m-%d}. When a tool needs a date, use "
            "today's date unless told otherwise. Be concise."
        ),
        hooks=[LoggingHook(verbose=False)],
    )

    for tick in range(1, NUM_TICKS + 1):
        print("\n" + "=" * 60)
        print(f"  TICK {tick}/{NUM_TICKS}")
        print("=" * 60)

        ctx = build_context()                         # Phase 1
        if not has_work(ctx):                         # Phase 2
            print("  HEARTBEAT_OK — nothing to do, skipped LLM entirely.")
        else:
            print("  Phase 2: work detected. Asking the agent what to do…")
            actions = reason_about_actions(agent, ctx)  # Phase 3
            print(f"  Phase 3: agent decided → {[a['action'] for a in actions]}")
            for action in actions:                    # Phase 4
                name = action.pop("action")
                EXECUTORS[name](agent, ctx, **action)
            agent.messages.clear()  # don't accumulate context across ticks

        if tick < NUM_TICKS:
            print(f"\n  (sleeping {SECONDS_BETWEEN}s…)")
            time.sleep(SECONDS_BETWEEN)


# ============================================================
# TRY THIS
#
#   1. Run twice. Tick 2 of the second run should print
#      "HEARTBEAT_OK" because tick 1 already marked everything
#      posted. That's the idempotency log doing its job.
#
#   2. Delete memory.db and run again — tick 1 reprocesses
#      everything, because the log is empty.
#
#   3. Add a new action, e.g. weekly_standings:
#        a. Document it inside HEARTBEAT_DECISIONS
#        b. Add an entry to EXECUTORS
#        c. Add a trigger to has_work()
#      Three places, one feature.
#
#   4. Replace the print() in each executor with a real
#      `urllib.request.urlopen(discord_webhook, ...)` call.
#      You now have a Discord bot.
#
#   5. Wrap the whole `for tick` loop in `while True` with
#      `sleep(60)` and a try/except for any KeyboardInterrupt.
#      You're running production now.
#
# Reference implementation (asyncio, Discord, ~880 lines):
#   https://github.com/labeveryday/nba-discord-agent/blob/main/src/heartbeat.py
#   https://github.com/labeveryday/nba-discord-agent/blob/main/src/HEARTBEAT.md
# ============================================================
