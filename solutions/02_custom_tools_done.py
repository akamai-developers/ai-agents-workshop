# SOLUTION: Section 2 — Custom Tools + Built-in Tools
# Run this if you're stuck: python workshop/solutions/02_custom_tools_done.py

import _path  # noqa: F401

import urllib.request
from strands import Agent, tool
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


agent = Agent(
    model=get_model(),
    tools=[get_weather, current_time],
    system_prompt="You are a helpful assistant. Use your tools when relevant.",
    callback_handler=ToolDisplayHook(),
)

response = agent("What's the weather in Stanford, California right now? And what time is it?")
print(f"\n{response}\n")
