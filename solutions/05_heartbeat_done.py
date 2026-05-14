# SOLUTION: Section 5 — The Heartbeat Pattern
# Run this if you're stuck: python workshop/solutions/05_heartbeat_done.py

import _path  # noqa: F401

from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.tools.mcp import MCPClient
from src.config import get_model
from src.hooks import ToolDisplayHook

HEARTBEAT_CRITERIA = """
You are an autonomous NBA reporting agent running on a heartbeat timer.

Every time you're triggered, you should:
1. Check the current NBA scoreboard using your tools
2. For each game, decide if it's worth reporting
3. Write a short post for anything interesting

POSTING RULES:
- Post a recap for any game that just finished (Final)
- Post a highlight if a live game with a notable performance
- Skip games that aren't interesting yet
- Keep each post to 2-3 sentences with key stats

FORMAT:
- Start posts with "POST:" and skips with "SKIP:"
"""

mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx", args=["nba-stats-mcp"])
))

with mcp_client:
    tools = mcp_client.list_tools_sync()

    agent = Agent(
        model=get_model(),
        tools=tools,
        system_prompt=HEARTBEAT_CRITERIA,
        callback_handler=ToolDisplayHook(),
    )

    response = agent(
        "Heartbeat tick. Check the current NBA scoreboard and "
        "decide what's worth reporting. Review each game."
    )
    print(f"\n{response}\n")
