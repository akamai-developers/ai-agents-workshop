# Building AI Agents with Strands

A 60-minute hands-on workshop. You'll go from "an LLM with a system prompt" to "an autonomous agent that loops on a timer and decides what to do."

Running example: an agent that watches the NBA scoreboard and decides what's worth posting.

| § | What you build | Time |
|---|---|---|
| 0 | Verify your environment | 5 min |
| 1 | Your first agent — LLM + system prompt, no tools | 8 min |
| 2 | Custom + built-in tools (`@tool`) | 10 min |
| 3 | MCP tools + multi-agent (agent as a tool) | 15 min |
| 4 | Memory — conversation context AND persistent across runs | 12 min |
| 5 | The heartbeat — autonomous loop | 10 min |

---

## Setup

Two LLM backend options. Pick one.

### Option A — vLLM (the workshop default)

This workshop is delivered against a vLLM endpoint serving Qwen3-8B in a managed Kubernetes cluster on Akamai Cloud. Point at any OpenAI-compatible inference endpoint:

```bash
export VLLM_HOST="https://your-vllm.example.com/v1"
export MODEL_NAME="Qwen/Qwen3-8B-FP8"   # whatever your endpoint serves
# export VLLM_API_KEY="..."             # optional, defaults to "not-needed"
```

### Option B — Ollama (laptop, no GPU needed for small models)

```bash
# Install Ollama: https://ollama.com/download
ollama pull qwen3:8b
ollama serve        # leave running in another terminal
```

### Install and verify

```bash
git clone https://github.com/akamai-developers/ai-agents-workshop.git
cd ai-agents-workshop
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python 00_verify.py
```

`00_verify.py` auto-detects which backend you've configured and does one round-trip through Strands to prove the stack works.

---

## Work through the sections

Self-contained, in order:

```bash
python 01_first_agent.py
python 02_custom_tools.py
python 03_mcp_tools.py
python 04_add_memory.py
python 05_heartbeat.py
```

Each file is heavily commented and prints tool-call traces so you can SEE the agent loop. Stuck? Compare against `solutions/`. Want the longer-form prose version? Read [`docs/`](docs/README.md) — one chapter per section, plus a "What's Next" with take-home challenges in [`extend/`](extend/).

---

## What each section teaches

**§1 — First agent.** An `Agent` is just `LLM + system_prompt`. Without tools it can only answer from training data. Ask it tonight's NBA score and it'll guess or refuse.

**§2 — Tools.** The `@tool` decorator turns any function into something the agent can call. The docstring IS the tool description — the model reads it to decide when to call. Use built-in tools (`current_time`, `calculator`…) and your own side-by-side.

**§3 — MCP and multi-agent.** One MCP server (`nba-stats-mcp`) exposes many tools through a standard protocol — drop it in `tools=[...]` like any other. Then one step further: an `Agent` itself can be a tool. A "writer" agent calls a "researcher" agent without ever seeing the researcher's tools.

**§4 — Memory.** Two different things share the name.

- *Conversation context*: `SlidingWindowConversationManager` keeps the last N messages so "their best player?" still refers to the team you mentioned three turns ago.
- *Persistent memory*: a tool that reads and writes a store. We use SQLite in `src/tools/memory.py` (`remember_fact`, `recall_facts`). Swap for Redis, mem0, or S3 — the agent doesn't care, only the docstring does.

**§5 — Heartbeat.** Request/response → autonomous loop, the production pattern. Five phases: Python builds context (no LLM), a boolean gate decides if there's any work at all (no LLM), the LLM emits a JSON action plan, Python dispatches each action to its own focused executor, and a SQLite idempotency log makes the whole thing exactly-once on retry. The LLM is a router and a writer — Python is the controller.

---

## Requirements

- Python 3.11+
- An LLM backend (Ollama OR an OpenAI-compatible endpoint like vLLM)
- `pip install -r requirements.txt`:
  - `strands-agents[ollama,openai]` — agent SDK
  - `strands-agents-tools` — built-in tools (`current_time`, etc.)
  - `mcp` — Model Context Protocol SDK
  - `nba-stats-mcp` — example MCP server (NBA scoreboard, stats, standings)

---

## Workshop logistics

Delivered live at Stanford. Each attendee got a dedicated code-server workspace on a managed Kubernetes cluster on Akamai Cloud with everything pre-installed, and a shared vLLM endpoint behind `VLLM_HOST`. The infra that powered it is open source and reusable for your own workshop:

> <https://github.com/labeveryday/building-ai-agents-on-akamai-cloud>

---

## License

Apache 2.0. Use it, fork it, run your own workshop.
