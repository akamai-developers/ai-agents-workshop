# SOLUTION — Section 3: MCP and "agents as tools".
#
# Mental model:
#     function   built-in   MCP server   agent
#         \         \           |          /
#          → all are interchangeable items in tools=[...]

import _path  # noqa: F401

import urllib.request
from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from strands_tools import current_time

from src.config import get_model
from src.hooks import LoggingHook


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    url = f"https://wttr.in/{city.replace(' ', '+')}?format=3"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.read().decode().strip()


# stdio_client launches nba-stats-mcp as a subprocess and speaks to it
# over stdin/stdout. The MCPClient context manager keeps that subprocess
# alive for the duration of the `with` block.
nba_mcp = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="nba-stats-mcp", args=[])
))

model = get_model()

with nba_mcp:
    # MCP tools arrive as a list, ready to drop into tools=[...].
    nba_tools = nba_mcp.list_tools_sync()

    # ── Part A: three tool sources, one agent ──────────────────
    agent = Agent(
        model=model,
        tools=[get_weather, current_time, *nba_tools],
        system_prompt="You are an NBA analyst. Use tools for any live data.",
        hooks=[LoggingHook()],
    )
    print(agent("What NBA games are today? And the weather in SF?"))

    # ── Part B: agents as tools ────────────────────────────────
    # The researcher has the NBA tools. The writer does NOT —
    # it only has the researcher (and weather). When the writer
    # needs facts it calls researcher AS A TOOL.
    #
    # This keeps each agent's context window focused: the writer
    # never sees 20 NBA tools it'll never use.
    researcher = Agent(
        model=model,
        tools=nba_tools,
        system_prompt="Look up NBA data. Return raw facts.",
        name="nba_researcher",
        description="Looks up live NBA scores, stats, and standings.",
    )

    writer = Agent(
        model=model,
        tools=[researcher, get_weather],   # researcher is just another tool
        system_prompt=(
            "You are a sports writer. Use nba_researcher for facts, "
            "then write a 2-3 sentence post."
        ),
        hooks=[LoggingHook()],
    )
    print(writer("Write a quick recap of tonight's NBA action."))
