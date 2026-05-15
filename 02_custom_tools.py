# ============================================================
# SECTION 2 — Built-in Tools + Custom Tools
# ============================================================
# Strands ships built-in tools (current_time, calculator, etc.).
# You can also write your own with the @tool decorator.
# The agent reads each tool's docstring and decides when to call.
#
# Run:  python 02_custom_tools.py
# ============================================================

import _path  # noqa: F401

import urllib.request
from strands import Agent, tool
from strands_tools import current_time

from src.config import get_model
from src.hooks import LoggingHook


# ── Your first custom tool ──────────────────────────────────
# The docstring IS the tool description. The model reads it to
# decide whether to call this. Treat the docstring like a UX
# surface — terse but specific.

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: City name, e.g. "San Francisco" or "New York"
    """
    url = f"https://wttr.in/{city.replace(' ', '+')}?format=3"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.read().decode().strip()


# ── Mix custom + built-in tools in one agent ─────────────────
agent = Agent(
    model=get_model(),
    tools=[get_weather, current_time],
    system_prompt=(
        "You are a helpful assistant. Use your tools when the user asks "
        "for live data — never guess weather or time."
    ),
    hooks=[LoggingHook(verbose=True)],
)

print("=" * 60)
print("  Custom @tool + built-in tool — watch which one the agent picks")
print("=" * 60)
print(agent(
    "What's the weather at Stanford right now? And what time is it in California?"
))


# ============================================================
# TRY THIS
#   - "Who is Michael Jordan?"        → no tool, training data
#   - "What's the weather in Tokyo?"  → your custom tool
#   - "What time is it in Sydney?"    → built-in current_time
#
#   Write your OWN @tool:
#
#       @tool
#       def get_dad_joke() -> str:
#           """Get a random dad joke."""
#           import urllib.request, json
#           req = urllib.request.Request(
#               "https://icanhazdadjoke.com/",
#               headers={"Accept": "application/json"},
#           )
#           with urllib.request.urlopen(req, timeout=5) as r:
#               return json.loads(r.read())["joke"]
#
#   Function + docstring is all the agent needs.
#
# Next:  python 03_mcp_tools.py
# ============================================================
