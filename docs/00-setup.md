# Section 0: Setup

> Confirm your environment is ready to build agents.

## Run It

```
python workshop/00_verify.py
```

## Expected Output

```
============================================================
  AI Agents Workshop — Environment Check
============================================================

Strands Agents SDK
  ✓ strands-agents installed

LLM Backend
  ✓ vLLM reachable at http://vllm:8000/v1 (model: Qwen/Qwen3-8B)

MCP Tools (nba-stats-mcp)
  ✓ nba-stats-mcp found on PATH

Status
  ✓ Environment ready!

============================================================
  ✅ Ready! Run: python workshop/01_first_agent.py
============================================================
```

All three checkmarks green? You're ready.

## Project Layout

```
ai-agents-workshop/
├── workshop/              # Scripts you'll run (00-04)
│   └── solutions/         # Completed versions if you fall behind
├── src/                   # Agent code
│   ├── config.py          # Model selection, environment config
│   ├── hooks.py           # Display hooks for terminal output
│   ├── agent.py           # Agent factory
│   ├── heartbeat.py       # Autonomous reasoning pattern
│   └── tools/
│       ├── mcp.py         # MCP client for nba-stats-mcp
│       └── demo.py        # Mock tools for demo mode
├── docs/                  # This guide
├── reference/             # Maps workshop → production code
└── extend/                # Take-home challenges
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `strands-agents not installed` | Run `pip install -r requirements.txt` |
| `No LLM backend found` | Ask an instructor — the vLLM server may need a restart |
| `nba-stats-mcp not found` | Run `pip install nba-stats-mcp` |

Next: [Your First Agent](01-your-first-agent.md)
