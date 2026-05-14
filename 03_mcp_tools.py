# ============================================================
# SECTION 3: MCP Tools + Multi-Agent
# ============================================================
#
# In Section 2 you wrote a @tool function. MCP scales that:
# an external server provides MANY tools via a standard protocol.
#
# Then we go one step further: an AGENT can be a tool too.
# Function → built-in → MCP server → agent. All just tools.
#
# Run this: python workshop/03_mcp_tools.py
# ============================================================

import _path  # noqa: F401

import urllib.request
from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from strands_tools import current_time
from src.config import get_model
from src.hooks import ToolDisplayHook

# ── Your custom tool from Section 2 ──────────────────────
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: City name (e.g., "San Francisco", "New York")

    Returns:
        Current weather conditions for the city
    """
    url = f"https://wttr.in/{city.replace(' ', '+')}?format=3"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.read().decode().strip()


# ── MCP tools from nba-stats-mcp ─────────────────────────
mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx", args=["nba-stats-mcp"])
))

model = get_model()

with mcp_client:
    mcp_tools = mcp_client.list_tools_sync()
    print(f"MCP server provided {len(mcp_tools)} tools")

    # ── Part A: Combined tool sources ─────────────────────
    # Custom tool + built-in tool + MCP tools in one agent
    all_tools = [get_weather, current_time] + mcp_tools
    print(f"Total tools available: {len(all_tools)}\n")

    agent = Agent(
        model=model,
        tools=all_tools,
        system_prompt=(
            "You are an NBA analyst agent. Use your tools to look up real-time data. "
            "Use resolve_team_id and resolve_player_id when needed."
        ),
        callback_handler=ToolDisplayHook(),
    )

    print("=" * 60)
    print("  Part A: Custom + built-in + MCP tools")
    print("=" * 60)
    print()
    response = agent(
        "What are today's NBA scores? "
        "Also what's the weather in San Francisco?"
    )
    print(f"\n{response}\n")

    # ── Part B: An agent AS a tool (multi-agent) ──────────
    # An agent can be a tool too. Create a "researcher" agent,
    # then give it to an "orchestrator" as a tool.

    researcher = Agent(
        model=model,
        tools=mcp_tools,
        system_prompt=(
            "You are an NBA data researcher. When asked a question, "
            "use your tools to look up accurate stats and scores. "
            "Return the raw data — another agent will write the content."
        ),
        name="nba_researcher",
        description="Research NBA stats, scores, and standings using real-time data tools.",
    )

    orchestrator = Agent(
        model=model,
        tools=[researcher, get_weather, current_time],
        system_prompt=(
            "You are a sports content writer. Use your researcher tool "
            "to get NBA data, then write an engaging 2-3 sentence summary. "
            "Include the weather if the user mentions a city."
        ),
        callback_handler=ToolDisplayHook(),
    )

    print("=" * 60)
    print("  Part B: Multi-agent — the orchestrator delegates to the researcher")
    print("=" * 60)
    print()
    response = orchestrator("Write a quick recap of today's NBA action")
    print(f"\n{response}\n")

# ============================================================
# TRY THIS:
# - Ask the orchestrator about weather + NBA in one question
#   — it picks which tool (researcher agent vs get_weather)
# - Change the researcher's system_prompt to focus on stats
# - Change the orchestrator's prompt to "write like a poet"
#
# Four tool sources in one list:
#   tools=[get_weather, current_time] + mcp_tools + [researcher]
#   function    + built-in    + MCP server + agent
#
# They all work the same way. The model reads each tool's
# description and decides which to call.
#
# When you're ready: python workshop/04_add_memory.py
# ============================================================
