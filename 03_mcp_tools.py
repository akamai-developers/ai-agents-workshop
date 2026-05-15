# ============================================================
# SECTION 3 — MCP Tools + Multi-Agent
# ============================================================
# In Section 2 you wrote ONE custom tool. MCP scales that:
# a single MCP server exposes many tools through a standard
# protocol. We plug into nba-stats-mcp (live NBA data).
#
# Then one more step: an Agent can ITSELF be a tool. That's
# the "agents as tools" pattern.
#
# Run:  python 03_mcp_tools.py
# ============================================================

import _path  # noqa: F401

import urllib.request
from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from strands_tools import current_time

from src.config import get_model
from src.hooks import LoggingHook


# Custom tool carried over from Section 2 — proof that all
# tool types coexist on a single agent.
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: City name, e.g. "San Francisco"
    """
    url = f"https://wttr.in/{city.replace(' ', '+')}?format=3"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.read().decode().strip()


# ── Spin up the NBA MCP server over stdio ───────────────────
nba_mcp = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx", args=["nba-stats-mcp"])
))

model = get_model()

with nba_mcp:
    nba_tools = nba_mcp.list_tools_sync()
    print(f"  nba-stats-mcp exposed {len(nba_tools)} tools\n")

    # ── Part A — four tool sources, one agent ──────────────
    # function + built-in + MCP, all in one tools list.
    agent = Agent(
        model=model,
        tools=[get_weather, current_time, *nba_tools],
        system_prompt=(
            "You are an NBA analyst. Use your tools for any live data — "
            "scores, stats, weather, time. Never invent live numbers."
        ),
        hooks=[LoggingHook(verbose=False)],
    )

    print("=" * 60)
    print("  Part A — one agent, three tool sources")
    print("=" * 60)
    print(agent(
        "What NBA games are on today? And what's the weather in San Francisco?"
    ))

    # ── Part B — agents as tools ────────────────────────────
    # The "researcher" knows how to look up NBA data.
    # The "writer" is given the researcher AS A TOOL plus the
    # weather tool. The writer doesn't see nba-mcp at all — it
    # just calls the researcher when it needs facts.
    #
    # Why this matters: each agent stays focused. The writer's
    # context window doesn't fill up with 20 NBA tools it never
    # uses. The researcher doesn't need to know how to write.

    researcher = Agent(
        model=model,
        tools=nba_tools,
        system_prompt=(
            "You are an NBA data researcher. Look up the requested data with "
            "your tools and return the raw facts — scores, dates, stat lines. "
            "Do not editorialize."
        ),
        name="nba_researcher",
        description="Looks up live NBA scores, stats, and standings.",
        hooks=[LoggingHook(verbose=False)],
    )

    writer = Agent(
        model=model,
        tools=[researcher, get_weather],
        system_prompt=(
            "You are a sports content writer. When you need NBA data, call "
            "the nba_researcher tool. Then write a punchy 2-3 sentence post. "
            "If a city is mentioned, include the weather."
        ),
        name="sports_writer",
        hooks=[LoggingHook(verbose=False)],
    )

    print("\n" + "=" * 60)
    print("  Part B — writer agent delegates research to a researcher agent")
    print("=" * 60)
    print(writer("Write a quick recap of tonight's NBA action."))

# ============================================================
# TRY THIS
#   - Ask the writer: "Recap tonight's NBA action AND tell me
#     if it's going to rain in Boston." Watch it call both
#     the researcher tool and get_weather.
#   - Change the writer's system_prompt to "Write like a poet."
#   - Add a third agent — a `fact_checker` — that the writer
#     calls before publishing.
#
# Mental model:
#   function   built-in   MCP server   agent
#       \         \           |          /
#        \         \          |         /
#         \         \         |        /
#          → all of these are just `tools=[...]`
#
# Next:  python 04_add_memory.py
# ============================================================
