# Section 0: Setup

[← Index](README.md) · [Next → Your First Agent](01-your-first-agent.md)

> Confirm your environment is ready to build agents.

## Run It

```
python 00_verify.py
```

## Expected Output

```
  ✅ strands-agents SDK installed
  ✅ mcp SDK installed
  ✅ nba-stats-mcp on PATH
  ✅ vLLM reachable at https://your-vllm.example.com/v1

  Trying one round-trip through Strands…
  ✅ end-to-end call succeeded

  ✅ You're ready. Next:  python 01_first_agent.py
```

Five green check marks? You're ready. The last one is the important one — it does a real `agent("ping")` call through Strands so you catch any configuration issues before Section 1.

## Project Layout

```
ai-agents-workshop/
├── 00_verify.py            # ← you start here
├── 01_first_agent.py
├── 02_custom_tools.py
├── 03_mcp_tools.py
├── 04_add_memory.py
├── 05_heartbeat.py
├── solutions/              # annotated reference if you fall behind
├── src/
│   ├── config.py           # model selection (vLLM / Ollama)
│   ├── hooks.py            # LoggingHook — prints tool calls
│   └── tools/
│       └── memory.py       # §4 SQLite memory tools
├── docs/                   # this guide (one .md per section)
└── extend/                 # take-home challenges
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `strands-agents not installed` | `pip install -r requirements.txt` |
| `vLLM unreachable` | Check `VLLM_HOST` env var. Ask an instructor — the vLLM pod may need a restart. |
| `Ollama not running` | `ollama serve` in another terminal, then `ollama pull qwen3:8b` |
| `nba-stats-mcp not found` | `pip install nba-stats-mcp`, or rely on `uvx nba-stats-mcp` (used by §3-5) |
| `end-to-end call failed` | The first four checks passed but the round-trip didn't. Usually a model_id mismatch — set `MODEL_NAME` to whatever your vLLM endpoint actually serves. |

Next: [Your First Agent](01-your-first-agent.md)
