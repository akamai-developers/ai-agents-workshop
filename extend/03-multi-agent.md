# Challenge 3: Multi-Agent Deep Dive

> Go beyond the workshop's researcher/orchestrator pattern.

## What You Saw in the Workshop

In Section 3, you created a simple multi-agent system:

```python
researcher = Agent(model=model, tools=mcp_tools, name="nba_researcher", ...)
orchestrator = Agent(model=model, tools=[researcher, get_weather, current_time], ...)
```

This challenge goes deeper.

## Build a Three-Agent Pipeline

```
Editor Agent
    │
    ├── calls nba_researcher (gets raw data)
    ├── calls fact_checker (verifies claims)
    │
    └── produces polished, fact-checked content
```

### Step 1: The Researcher (you already built this in §3)

```python
researcher = Agent(
    model=model, tools=nba_tools,
    name="nba_researcher",
    description="Looks up live NBA scores, stats, and standings.",
    system_prompt="You are a data researcher. Return raw facts and stats.",
)
```

### Step 2: A Fact Checker

```python
fact_checker = Agent(
    model=model, tools=nba_tools,
    name="fact_checker",
    description="Verify NBA claims by looking up the actual data.",
    system_prompt=(
        "You are a fact checker. When given a claim about NBA stats, "
        "use your tools to verify it. Return 'VERIFIED' or 'INCORRECT: <correction>'."
    ),
)
```

### Step 3: The Editor (orchestrator)

```python
editor = Agent(
    model=model,
    tools=[researcher, fact_checker],
    system_prompt=(
        "You are a sports editor. Use nba_researcher to gather data, "
        "draft a recap, then use fact_checker to verify your key claims. "
        "Correct any errors before publishing."
    ),
)

response = editor("Write a verified recap of today's best NBA game")
```

## Why This Matters

- **Quality control**: The fact checker catches hallucinations
- **Separation of concerns**: Each agent has a focused role
- **Composability**: Add more agents (translator, social media formatter, etc.)
- **Same `tools=[]` pattern**: Agents compose the same way tools compose

## Reference

- [Strands multi-agent docs](https://strandsagents.com/docs/user-guide/concepts/multi-agent/)
- The production NBA Discord Agent uses a single agent with MCP tools + heartbeat. Multi-agent is the pattern for when you need delegation and quality control.
