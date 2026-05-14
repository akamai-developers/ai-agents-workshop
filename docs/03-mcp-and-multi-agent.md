# Section 3: MCP Tools + Multi-Agent

> MCP scales tools via a protocol. Agents scale delegation via composition.

## What You'll Learn

- How MCP servers provide tools to agents
- How to combine custom, built-in, and MCP tools in one agent
- How to use an agent as a tool (multi-agent orchestration)

## The Key Idea

In Section 2 you wrote one tool. MCP (Model Context Protocol) lets an external server provide **many** tools via a standard protocol. The `nba-stats-mcp` server provides 21 NBA data tools — scoreboard, box scores, standings, player stats, and more.

```python
from strands.tools.mcp import MCPClient
from mcp import StdioServerParameters, stdio_client

mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx", args=["nba-stats-mcp"])
))

with mcp_client:
    mcp_tools = mcp_client.list_tools_sync()  # 21 tools discovered
```

You can combine ALL tool sources in one `tools=` list:

```python
agent = Agent(tools=[get_weather, current_time] + mcp_tools)
#              custom ↑     built-in ↑        MCP ↑
```

**Then the multi-agent step:** an Agent can be a tool too.

```python
researcher = Agent(
    model=model, tools=mcp_tools,
    name="nba_researcher",
    description="Research NBA stats and scores.",
)

orchestrator = Agent(tools=[researcher, get_weather, current_time])
#                    agent ↑    custom ↑    built-in ↑
```

Four tool sources in one list: function, built-in, MCP server, agent. They all work the same way.

## Run It

```
python workshop/03_mcp_tools.py
```

## Expected Output

**Part A** — Combined tools:
```
MCP server provided 21 tools
Total tools available: 23

🔧 Tool Call: get_scoreboard({})
🔧 Tool Call: get_weather({"city": "San Francisco"})
📊 Result: san francisco: 🌤️  +63°F
```

**Part B** — Multi-agent:
```
🔧 Tool Call: nba_researcher({"input": "today's NBA action"})
📊 Result: Today's NBA Games: Pistons 59 @ Cavaliers 46 — Half...

Today's NBA action featured the Pistons leading the Cavaliers
59-46 at halftime...
```

The orchestrator delegated to the researcher agent, which called MCP tools internally. The orchestrator then wrote the recap.

## Try This

- Ask the orchestrator about weather + NBA — watch it pick the right tool source
- Change the researcher's system prompt to focus on player stats
- Change the orchestrator's prompt to "write like a poet"

## What Just Happened

You connected to an MCP server that provided 21 tools, combined them with a custom tool and a built-in, and created a multi-agent system where an orchestrator delegates to a researcher. All tool sources — functions, built-ins, MCP servers, and agents — are entries in the same `tools=[]` list.

Next: [Conversation Memory](04-conversation-memory.md)
