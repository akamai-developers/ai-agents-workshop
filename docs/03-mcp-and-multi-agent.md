# Section 3: MCP Tools + Multi-Agent

[← Custom Tools](02-custom-tools.md) · [Index](README.md) · [Next → Memory](04-conversation-memory.md)

> MCP scales tools via a protocol. Agents scale delegation via composition.

## What You'll Learn

- How MCP servers provide tools to agents
- How to combine custom, built-in, and MCP tools in one agent
- How to use an agent as a tool (multi-agent orchestration)

## The Key Idea

In Section 2 you wrote one tool. MCP (Model Context Protocol) lets an external server provide **many** tools via a standard protocol. The `nba-stats-mcp` server exposes a fleet of NBA data tools — scoreboard, box scores, standings, player stats, and more.

```python
from strands.tools.mcp import MCPClient
from mcp import StdioServerParameters, stdio_client

nba_mcp = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx", args=["nba-stats-mcp"])
))

with nba_mcp:
    nba_tools = nba_mcp.list_tools_sync()
```

You can combine ALL tool sources in one `tools=` list:

```python
agent = Agent(tools=[get_weather, current_time, *nba_tools])
#                    custom ↑     built-in ↑     MCP ↑
```

**Then the multi-agent step:** an Agent can be a tool too.

```python
researcher = Agent(
    model=model, tools=nba_tools,
    name="nba_researcher",
    description="Looks up live NBA scores, stats, and standings.",
)

writer = Agent(
    model=model,
    tools=[researcher, get_weather],   # researcher is just another tool
    system_prompt="You are a sports writer. Use nba_researcher for facts.",
)
```

The writer doesn't see the 20+ NBA tools — only the researcher. That keeps each agent's context window focused. Four tool sources, one mental model: function, built-in, MCP server, agent. They all work the same way.

## Run It

```
python 03_mcp_tools.py
```

## Expected Output

**Part A** — one agent, three tool sources:
```
  nba-stats-mcp exposed 21 tools

  ↳ [agent] tool call #1: get_scoreboard
  ↳ [agent] tool call #2: get_weather

Tonight's NBA slate: Pistons 59 @ Cavaliers 46 at the half… and
it's a cool 63°F in San Francisco.
```

**Part B** — writer delegates to researcher:
```
  ↳ [sports_writer] tool call #1: nba_researcher
  ↳ [nba_researcher] tool call #1: get_scoreboard
  ↳ [nba_researcher] tool call #2: get_team_log

The Pistons are up big at the half over the Cavaliers, 59-46…
```

Notice the nested `↳` — the writer called the researcher, and the researcher called MCP tools. Two layers of agent loop, one tool list each.

## Try This

- Ask the writer about weather + NBA — watch it pick the right tool source
- Change the researcher's system prompt to focus on player stats
- Change the writer's prompt to "write like a poet"
- Add a third agent — a `fact_checker` — that the writer calls before publishing

## What Just Happened

You connected to an MCP server that provided a fleet of NBA tools, combined them with a custom tool and a built-in in one agent, then built a multi-agent system where a writer delegates to a researcher. All tool sources — functions, built-ins, MCP servers, and agents — are entries in the same `tools=[...]` list.

Next: [Conversation Memory](04-conversation-memory.md)
