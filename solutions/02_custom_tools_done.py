# SOLUTION — Section 2: @tool turns any function into something
# the agent can call. The docstring is the tool's API contract —
# the model reads it to decide whether to call.

import _path  # noqa: F401

import urllib.request
from strands import Agent, tool
from strands_tools import current_time     # built-in, ships with strands_tools

from src.config import get_model
from src.hooks import LoggingHook


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: City name, e.g. "San Francisco"
    """
    # wttr.in is a free, no-key HTTP weather API. We use stdlib urllib
    # so there are no extra deps to install.
    url = f"https://wttr.in/{city.replace(' ', '+')}?format=3"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.read().decode().strip()


# Custom and built-in tools live in the same list. The agent picks
# whichever fits the request — or none if it can answer from training.
agent = Agent(
    model=get_model(),
    tools=[get_weather, current_time],
    system_prompt="You are a helpful assistant. Use your tools for live data.",
    hooks=[LoggingHook()],   # prints each tool call so you can SEE the loop
)

print(agent("What's the weather at Stanford right now? And what time is it?"))
