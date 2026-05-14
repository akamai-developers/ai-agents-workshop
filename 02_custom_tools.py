# ============================================================
# SECTION 2: Built-in Tools + Custom Tools
# ============================================================
#
# Strands ships with built-in tools (current_time, shell, etc.)
# You can also write your own with the @tool decorator.
# The agent decides which tools to call based on your question.
#
# Run this: python workshop/02_custom_tools.py
# ============================================================

import _path  # noqa: F401

import urllib.request
from strands import Agent, tool
from strands_tools import current_time
from src.config import get_model
from src.hooks import ToolDisplayHook


# ── A custom tool — a real API call with @tool ────────────
# The docstring IS the tool description. The agent reads it
# to decide when to call it. This tool makes a real HTTP
# request to get live weather data.

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


# ── Create an agent with both tool types ──────────────────
# Custom tool (get_weather) + built-in tool (current_time)
# Both go in the same tools list.

agent = Agent(
    model=get_model(),
    tools=[get_weather, current_time],
    system_prompt="You are a helpful assistant. Use your tools when relevant.",
    callback_handler=ToolDisplayHook(),
)

print("=" * 60)
print("  Custom tool + built-in tool in one agent")
print("  Watch which tools the agent chooses!")
print("=" * 60)
print()

response = agent("What's the weather in Stanford, California right now? And what time is it?")
print(f"\n{response}\n")

# ============================================================
# TRY THIS:
# - "What's the weather in Tokyo?" (calls your custom tool)
# - "What time is it?" (calls built-in current_time)
# - "Who is Michael Jordan?" (no tool needed — training data)
# - Write your OWN @tool function — anything you want:
#
#   @tool
#   def get_dad_joke() -> str:
#       """Get a random dad joke."""
#       import urllib.request, json
#       req = urllib.request.Request(
#           "https://icanhazdadjoke.com/",
#           headers={"Accept": "application/json"}
#       )
#       with urllib.request.urlopen(req) as r:
#           return json.loads(r.read())["joke"]
#
# The @tool decorator is all you need. Write a function,
# add a docstring, and the agent knows when to use it.
#
# When you're ready: python workshop/03_mcp_tools.py
# ============================================================
