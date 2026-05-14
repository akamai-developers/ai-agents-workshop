# ============================================================
# SECTION 5: The Heartbeat — Autonomous Reasoning
# ============================================================
#
# Everything so far is request/response. The heartbeat pattern
# makes the agent act on its own:
#   1. Check the NBA scoreboard using its tools
#   2. Apply criteria YOU wrote to decide what's worth posting
#   3. Act without being asked
#
# In production, this runs every 60 seconds on a timer.
# Here we trigger one tick so you can see the reasoning.
#
# Run this: python workshop/05_heartbeat.py
# ============================================================

import _path  # noqa: F401

from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.tools.mcp import MCPClient
from src.config import get_model
from src.hooks import LoggingHook

# ── The criteria — EDIT THIS ──────────────────────────────
# Natural language that controls agent behavior.
# The agent reads these rules and decides what to do.
# No if/else. No routing logic. Just rules in English.

HEARTBEAT_CRITERIA = """
You are an autonomous NBA reporting agent running on a heartbeat timer.

Every time you're triggered, you should:
1. Check the current NBA scoreboard using your tools
2. For each game, decide if it's worth reporting
3. Write a short post for anything interesting

POSTING RULES:
- Post a recap for any game that just finished (Final)
- Post a highlight if a live game has a notable performance
- Post a preview for any game starting within 30 minutes
- Skip games that aren't interesting yet (early in Q1, blowouts)

TONE:
- Write like an excited but knowledgeable sports commentator
- Keep each post to 2-3 sentences with key stats
- Include the score and standout players

FORMAT:
- Start each post with "POST:" followed by your content
- Start each skip with "SKIP:" followed by a brief reason
"""

# ── One heartbeat tick ────────────────────────────────────

mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx", args=["nba-stats-mcp"])
))

with mcp_client:
    tools = mcp_client.list_tools_sync()

    agent = Agent(
        model=get_model(),
        tools=tools,
        system_prompt=HEARTBEAT_CRITERIA,
        hooks=[LoggingHook(verbose=True)]
    )

    print("=" * 60)
    print("  Heartbeat tick")
    print("  Agent checking scoreboard and deciding what to post...")
    print("=" * 60)
    print()

    response = agent(
        "Heartbeat tick. Check the current NBA scoreboard and "
        "decide what's worth reporting. Review each game."
    )
    print(f"\n{response}\n")

# ============================================================
# TRY THIS:
#
# 1. Change the POSTING RULES: "Only post about Western
#    Conference games" — the agent skips Eastern Conference
#
# 2. Change the TONE: "Write like a dry statistician" or
#    "Write like a trash-talking fan"
#
# 3. Add a rule: "If any player has 30+ points, make it
#    the headline"
#
# 4. Run it in a loop (the production pattern):
#
#    import time
#    while True:
#        response = agent("Heartbeat tick. Check the scoreboard.")
#        print(response)
#        time.sleep(60)  # wait 60 seconds, then check again
#
# The production NBA Discord Agent runs this exact pattern
# 24/7 — checking the scoreboard, reasoning about what's
# worth posting, and acting autonomously.
#
# 🎉 You've completed the workshop!
#    - reference/README.md → production code walkthrough
#    - extend/ → take-home challenges
# ============================================================
