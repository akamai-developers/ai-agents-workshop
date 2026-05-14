# What's Next

> From workshop to production — where to go from here.

## What You Built

In one hour, you learned the core patterns behind production AI agents:

| Pattern | Workshop Script | What It Does |
|---------|----------------|--------------|
| **Custom Tools** | `02_custom_tools.py` | Write a `@tool` function, agent decides when to call it |
| **MCP + Multi-Agent** | `03_mcp_tools.py` | MCP servers provide tools; agents can be tools too |
| **Conversation Memory** | `04_add_memory.py` | Agent maintains context across turns |
| **Autonomous Reasoning** | `05_heartbeat.py` | Agent checks data and decides what to post on its own |

These aren't toy patterns. The production NBA Discord Agent uses these same patterns to serve a live Discord community 24/7.

## The Production NBA Discord Agent

The workshop is based on a real agent: [nba-discord-agent](https://github.com/labeveryday/nba-discord-agent)

See [reference/README.md](../reference/README.md) for a concept map showing exactly where each workshop pattern appears in the production code.

## Take-Home Challenges

| Challenge | What You'll Build |
|-----------|-------------------|
| [Deploy to Discord](../extend/01-deploy-to-discord.md) | Wire your agent to a Discord bot |
| [Add Persistence](../extend/02-add-persistence.md) | Track posted games with SQLite |
| [Multi-Agent Deep Dive](../extend/03-multi-agent.md) | Advanced orchestration patterns |
| [Your Own Domain](../extend/04-your-own-domain.md) | Replace NBA with your own domain |
| [Self-Extending Agent](../extend/05-self-extending-agent.md) | Agent that writes its own tools at runtime |

## Resources

- **Strands Agents SDK**: [github.com/strands-agents/sdk-python](https://github.com/strands-agents/sdk-python)
- **Strands Documentation**: [strandsagents.com](https://strandsagents.com)
- **MCP (Model Context Protocol)**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **nba-stats-mcp**: [github.com/labeveryday/nba-stats-mcp](https://github.com/labeveryday/nba-stats-mcp)
- **Self-Extending Agents**: [github.com/labeveryday/strands-agents-meta-tooling](https://github.com/labeveryday/strands-agents-meta-tooling)

## Questions?

- **Du'An Lightfoot** — [duanl@labeveryday.com](mailto:duanl@labeveryday.com)
- GitHub: [labeveryday](https://github.com/labeveryday)
