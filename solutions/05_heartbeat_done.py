# SOLUTION — Section 5: production-shape heartbeat.
#
# Five phases. Python is the controller. The LLM is a router
# (Phase 3) and a writer (Phase 4) — nothing more.
#
# Phase 1: Build context     (no LLM)
# Phase 2: Pre-check gate    (no LLM)
# Phase 3: Reason → JSON     (LLM, structured output)
# Phase 4: Execute actions   (Python + focused LLM prompts)
# Phase 5: State (SQLite)    (idempotency log)
#
# Mirrors src/heartbeat.py in labeveryday/nba-discord-agent.

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


# ── Phase 5 — idempotency log ───────────────────────────────────
# UNIQUE on (job_type, job_key). INSERT OR IGNORE means double-call
# is harmless; a crash mid-tick can't cause double-posting.
DB = Path(__file__).resolve().parent.parent / "memory.db"


def _conn() -> sqlite3.Connection:
    db = sqlite3.connect(DB)
    db.execute("""
        CREATE TABLE IF NOT EXISTS heartbeat_log (
            job_type  TEXT NOT NULL,
            job_key   TEXT NOT NULL,
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


# ── Phase 1 — fetch + build context (no LLM) ────────────────────
# Direct API call. The LLM doesn't need to "decide to look up
# games" — we always know what's on the board today.
SCOREBOARD_URL = (
    "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
)

# Fallback fixture for off-days, firewalled environments, or outages.
FALLBACK_GAMES = [
    {"id": "0022501101", "away": "GSW", "home": "LAL",
     "away_score": 108, "home_score": 102,
     "status": "Final", "is_final": True},
    {"id": "0022501102", "away": "DEN", "home": "MIN",
     "away_score": 117, "home_score": 104,
     "status": "Final", "is_final": True},
    {"id": "0022501103", "away": "OKC", "home": "DAL",
     "away_score": 0, "home_score": 0,
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
    except Exception:
        pass
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


# ── Phase 2 — pre-check gate (no LLM) ───────────────────────────
def has_work(ctx: dict) -> bool:
    if ctx["new_finals"]:
        return True
    if 9 <= ctx["hour"] < 14 and ctx["games"] and not ctx["preview_posted"]:
        return True
    return False


# ── Phase 3 — reason: LLM as a router, JSON output ──────────────
HEARTBEAT_DECISIONS = """
You are the controller for an NBA reporting bot.

Available actions:
  - {"action": "postgame_highlight", "game_id": "<id>"}  — one per new final
  - {"action": "gameday_preview"}                        — once/day, 9 AM–2 PM

Return ONLY a JSON array of action objects, or HEARTBEAT_OK if nothing.
"""


def reason_about_actions(agent: Agent, ctx: dict) -> list[dict]:
    prompt = (
        f"{HEARTBEAT_DECISIONS}\n\n"
        f"## State\n"
        f"  today: {ctx['today']}\n"
        f"  hour: {ctx['hour']}\n"
        f"  games today: {len(ctx['games'])}\n"
        f"  newly-final games:\n"
        + (
            "\n".join(
                f"    - id={g['id']} {g['away']} {g['away_score']} @ "
                f"{g['home']} {g['home_score']}"
                for g in ctx["new_finals"]
            ) or "    (none)"
        )
        + f"\n  preview_posted: {ctx['preview_posted']}"
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


# ── Phase 4 — executors (Python + focused LLM prompts) ──────────
def exec_postgame_highlight(agent: Agent, ctx: dict, game_id: str) -> None:
    game = next((g for g in ctx["games"] if g["id"] == game_id), None)
    if not game:
        return
    response = str(agent(
        f"Write a 2-3 sentence Discord post-game highlight.\n"
        f"Final: {game['away']} {game['away_score']} - "
        f"{game['home']} {game['home_score']}.\n"
        f"Use your tools to fetch the box score and call out the top performer."
    ))
    print(f"\n🚨 [postgame_highlight {game['away']}@{game['home']}]\n{response}\n")
    mark_posted("highlight", game_id)


def exec_gameday_preview(agent: Agent, ctx: dict) -> None:
    matchups = "\n".join(
        f"  {g['away']} @ {g['home']} — {g['status']}" for g in ctx["games"]
    )
    response = str(agent(
        f"Write a Discord game-day preview for today's matchups:\n{matchups}\n"
        "Two sentences total. Flag any standout matchup."
    ))
    print(f"\n📋 [gameday_preview]\n{response}\n")
    mark_posted("preview", ctx["today"])


EXECUTORS = {
    "postgame_highlight": exec_postgame_highlight,
    "gameday_preview": lambda agent, ctx, **_: exec_gameday_preview(agent, ctx),
}


# ── The loop ────────────────────────────────────────────────────
nba_mcp = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="nba-stats-mcp", args=[])
))

with nba_mcp:
    nba_tools = nba_mcp.list_tools_sync()
    agent = Agent(
        model=get_model(),
        tools=nba_tools,
        system_prompt="You are a knowledgeable NBA reporter. Be concise.",
        hooks=[LoggingHook(verbose=False)],
    )

    for tick in range(1, 3):
        print(f"\n--- TICK {tick} ---")
        ctx = build_context()
        if not has_work(ctx):
            print("HEARTBEAT_OK — no work, skipped LLM.")
        else:
            actions = reason_about_actions(agent, ctx)
            for action in actions:
                EXECUTORS[action.pop("action")](agent, ctx, **action)
            agent.messages.clear()
        if tick < 2:
            time.sleep(5)
