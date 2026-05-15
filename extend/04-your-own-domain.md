# Challenge 4: Your Own Domain

> Replace NBA with any domain you care about.

## What You'll Build

An agent for your own domain — weather, finance, fitness, cooking, or anything with accessible data.

## The Template

Every domain agent has the same three components:

### 1. Tools (Data Access)

Write tools that fetch data from your domain's APIs:

```python
from strands import tool
import urllib.request, json

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city.

    Args:
        city: City name (e.g., "San Francisco")
    """
    # Replace with your actual API. We use stdlib urllib so there are no
    # extra deps — same pattern as §2's wttr.in tool.
    url = f"https://api.weather.example/current?city={city}"
    with urllib.request.urlopen(url, timeout=5) as resp:
        data = json.loads(resp.read())
    return f"{city}: {data['temp']}°F, {data['conditions']}"
```

The docstring is critical — it's what the LLM reads to decide when to use the tool.

### 2. System Prompt (Personality)

```python
system_prompt = """You are a weather assistant. Help users plan their day
based on weather conditions. When asked about weather, use your tools to get
current data. Provide practical advice, not just raw numbers."""
```

### 3. Heartbeat Criteria (Autonomous Behavior)

```python
criteria = """
You are an autonomous weather alert agent. Review the current conditions:

- If severe weather (tornado, hurricane, extreme heat) is detected, POST an alert
- If rain is expected in the next 2 hours, POST a heads-up
- If conditions are normal, SKIP with a brief reason
- Keep alerts to 1-2 sentences
"""
```

## Checklist

- [ ] Identify your domain's data source (API, database, scraper)
- [ ] Write 2-3 `@tool` functions with clear docstrings
- [ ] Write a system prompt that defines the agent's personality
- [ ] Write heartbeat criteria for autonomous behavior
- [ ] Test: ask the agent a question — does it choose the right tool?
- [ ] Test: run the heartbeat — does it make reasonable decisions?

## Ideas

| Domain | Tools | Heartbeat |
|--------|-------|-----------|
| **Finance** | `get_stock_price`, `get_portfolio` | Alert on big price moves |
| **Fitness** | `get_workout_log`, `get_nutrition` | Daily workout recommendations |
| **News** | `search_articles`, `get_trending` | Post breaking news summaries |
| **DevOps** | `get_pod_status`, `get_metrics` | Alert on failing services |
| **Music** | `search_songs`, `get_playlist` | Recommend new releases |

## The Pattern Is Universal

The three patterns you learned — tool use, memory, autonomous reasoning — work for any domain. The NBA was the example. The pattern is the lesson.
