# What's Next

[← Heartbeat](05-autonomous-reasoning.md) · [Index](README.md)

> From workshop to production — where to go from here.

## What You Built

In one hour, you learned the core patterns behind production AI agents:

| Pattern | Workshop Script | What It Does |
|---------|----------------|--------------|
| **First agent** | `01_first_agent.py` | LLM + system prompt; no tools = no real-time anything |
| **Custom + built-in tools** | `02_custom_tools.py` | `@tool` decorator, docstring as API contract |
| **MCP + multi-agent** | `03_mcp_tools.py` | One MCP server = many tools. Agents themselves are tools. |
| **Memory (two layers)** | `04_add_memory.py` | Conversation context AND persistent SQLite memory |
| **Heartbeat (5 phases)** | `05_heartbeat.py` | Python controller + LLM-as-router + idempotency log |

These aren't toy patterns. The production NBA Discord Agent runs this same shape 24/7.

## The Production NBA Discord Agent

Based on a real agent: [labeveryday/nba-discord-agent](https://github.com/labeveryday/nba-discord-agent)

Workshop → production map:

| Workshop section | Production equivalent |
|---|---|
| §2 custom `@tool` | `src/tools/*.py` Discord-posting tools |
| §3 MCP + multi-agent | Single agent with MCP tools (production found multi-agent overhead wasn't worth it for this domain) |
| §4 Layer A (`SlidingWindowConversationManager`) | Per-user conversation isolation across 100+ concurrent users with `window_size=16` |
| §4 Layer B (SQLite memory tools) | Same SQLite store; production adds `game_threads`, `game_state` tables next to `heartbeat_log` |
| §5 5-phase heartbeat | Same 5 phases; production wraps them in asyncio + a semaphore so interactive users get priority |

## Take-Home Challenges

| Challenge | What You'll Build |
|-----------|-------------------|
| [Deploy to Discord](../extend/01-deploy-to-discord.md) | Wire your agent to a real Discord bot |
| [Add Persistence](../extend/02-add-persistence.md) | Extend §4's memory tools with production-grade idempotency |
| [Multi-Agent Deep Dive](../extend/03-multi-agent.md) | Researcher → writer → fact-checker pipeline |
| [Your Own Domain](../extend/04-your-own-domain.md) | Drop NBA, plug in any domain you care about |
| [Self-Extending Agent](../extend/05-self-extending-agent.md) | An agent that writes its own tools at runtime |

## Resources

- **Strands Agents SDK** — [github.com/strands-agents/sdk-python](https://github.com/strands-agents/sdk-python)
- **Strands Documentation** — [strandsagents.com](https://strandsagents.com)
- **MCP (Model Context Protocol)** — [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **nba-stats-mcp** — [github.com/labeveryday/nba-stats-mcp](https://github.com/labeveryday/nba-stats-mcp)
- **Workshop infrastructure (Akamai Cloud + k8s + vLLM)** — [github.com/labeveryday/building-ai-agents-on-akamai-cloud](https://github.com/labeveryday/building-ai-agents-on-akamai-cloud)
- **Self-extending agents** — [github.com/labeveryday/strands-agents-meta-tooling](https://github.com/labeveryday/strands-agents-meta-tooling)

## Questions?

- **Du'An Lightfoot** — [duanl@labeveryday.com](mailto:duanl@labeveryday.com)
- GitHub — [labeveryday](https://github.com/labeveryday)
