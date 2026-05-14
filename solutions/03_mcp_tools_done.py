# SOLUTION: Section 3 — MCP Tools + Multi-Agent
# Run this if you're stuck: python workshop/solutions/03_mcp_tools_done.py

import _path  # noqa: F401

import urllib.request
from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from strands_tools import current_time
from src.config import get_model
from src.hooks import ToolDisplayHook

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


mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx", args=["nba-stats-mcp"])
))

model = get_model()

with mcp_client:
    mcp_tools = mcp_client.list_tools_sync()

    # Part A: Combined tools
    agent = Agent(
        model=model,
        tools=[get_weather, current_time] + mcp_tools,
        system_prompt="You are an NBA analyst. Use your tools to look up real-time data.",
        callback_handler=ToolDisplayHook(),
    )

    response = agent("What are today's NBA scores? What's the weather in SF?")
    print(f"\n{response}\n")

    # Part B: Multi-agent
    researcher = Agent(
        model=model,
        tools=mcp_tools,
        system_prompt="You are an NBA data researcher. Look up stats when asked.",
        name="nba_researcher",
        description="Research NBA stats, scores, and standings using real-time data tools.",
    )

    orchestrator = Agent(
        model=model,
        tools=[researcher, get_weather, current_time],
        system_prompt="You are a sports writer. Use your researcher for NBA data.",
        callback_handler=ToolDisplayHook(),
    )

    response = orchestrator("Write a quick recap of today's NBA action")
    print(f"\n{response}\n")
