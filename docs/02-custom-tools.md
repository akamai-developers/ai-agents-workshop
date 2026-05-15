# Section 2: Custom Tools + Built-ins

[← First Agent](01-your-first-agent.md) · [Index](README.md) · [Next → MCP + Multi-Agent](03-mcp-and-multi-agent.md)

> A tool is a function. You write it, the agent decides when to call it.

## What You'll Learn

- How to write a custom tool with the `@tool` decorator
- How to use built-in tools from `strands_tools`
- How the agent reads docstrings and decides which tool to call

## The Key Idea

A tool is a Python function decorated with `@tool`. The docstring is the tool's description — the LLM reads it to decide when to use it. You don't write routing logic. The model reasons about which tool fits the question.

```python
from strands import tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # Makes a real HTTP request to wttr.in
    ...
```

Strands also ships with built-in tools like `current_time` from `strands_tools`. You can mix custom and built-in tools in one agent:

```python
from strands_tools import current_time

agent = Agent(tools=[get_weather, current_time])
```

## Run It

```
python 02_custom_tools.py
```

## Expected Output

```
============================================================
  Custom @tool + built-in tool — watch which one the agent picks
============================================================

  ↳ [agent] tool call #1: get_weather
      {
        "city": "Stanford"
      }
  ↳ [agent] tool call #2: current_time

The weather at Stanford is ☁️ 61°F right now, and the current
time in California is 5:07 PM PDT.
```

The agent called YOUR function (`get_weather`) and a built-in (`current_time`). You wrote 5 lines of Python and the agent knew when to use it.

`LoggingHook` (in `src/hooks.py`) is what prints those `↳ tool call #N` lines — it subscribes to Strands' `BeforeToolCallEvent` so you can SEE the agent loop instead of trusting that something happened.

## Try This

- Ask "What's the weather in Tokyo?" — calls your custom tool
- Ask "What time is it?" — calls the built-in `current_time`
- Ask "Who is Michael Jordan?" — no tool needed, uses training data
- Write your own `@tool` — a dad joke API, a coin flipper, anything

## What Just Happened

You wrote a Python function with `@tool`, gave it to an agent alongside a built-in tool, and the agent decided which to call based on your question. The docstring is the tool's API description. No routing code. Just a function and a decorator.

Next: [MCP Tools + Multi-Agent](03-mcp-and-multi-agent.md)
