# Building AI Agents with Strands

A hands-on workshop that takes you from "an LLM with a system prompt" to "an autonomous agent that decides when to act on its own."

Five sections, ~90 minutes end to end:

| # | Section | What you learn |
|---|---|---|
| 0 | Verify your environment | Confirm the SDK, MCP, and an LLM backend are reachable |
| 1 | Your first agent | An agent is just an LLM with a system prompt — without tools, it only knows training data |
| 2 | Built-in + custom tools | Use shipped Strands tools and add your own with the `@tool` decorator |
| 3 | MCP tools + multi-agent | One MCP server exposes many tools. An agent itself can be a tool. |
| 4 | Memory | Conversation context: making the agent remember what you talked about |
| 5 | The heartbeat | Autonomous reasoning — the agent acts on its own using criteria you define |

The running example: an agent that watches the NBA scoreboard and decides what's worth posting about.

---

## Run it locally

Two LLM backend options. Pick one.

### Option A — Ollama (laptop, free, no GPU needed for small models)

```bash
# 1. Install Ollama: https://ollama.com/download
ollama pull qwen3:8b
ollama serve   # leave running in another terminal

# 2. Clone and install
git clone https://github.com/akamai-developers/ai-agents-workshop.git
cd ai-agents-workshop
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Verify
python 00_verify.py
```

### Option B — vLLM (cloud, faster, more capable)

Point at any OpenAI-compatible inference endpoint (vLLM, Together, OpenRouter, your own deploy):

```bash
export VLLM_HOST="https://your-vllm.example.com/v1"
export MODEL_NAME="Qwen/Qwen3-8B-FP8"   # or whatever model your endpoint serves

git clone https://github.com/akamai-developers/ai-agents-workshop.git
cd ai-agents-workshop
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python 00_verify.py
```

The `00_verify.py` script auto-detects which backend you've configured.

---

## Work through the sections

```bash
python 01_first_agent.py
python 02_custom_tools.py
python 03_mcp_tools.py
python 04_add_memory.py
python 05_heartbeat.py
```

Each file is self-contained and prints what's happening with colored tool-call traces (via `rich`). Stuck? Compare against `solutions/` for the worked answer.

---

## Requirements

- Python 3.11+
- An LLM backend (Ollama OR an OpenAI-compatible endpoint)
- `pip install -r requirements.txt`:
  - `strands-agents[ollama,openai]` — the agent SDK
  - `strands-agents-tools` — built-in tools
  - `mcp` — Model Context Protocol SDK
  - `nba-stats-mcp` — example MCP server (NBA stats)
  - `rich` — colored tool-call output

---

## Workshop logistics

If you attended this live (Stanford, etc.), the workshop ran on a managed Kubernetes cluster on Akamai Cloud. Each attendee got a dedicated code-server workspace with everything pre-installed. The infra that powered it lives at <https://github.com/labeveryday/building-ai-agents-on-akamai-cloud> and is reusable for running your own workshop.

---

## License

Apache 2.0. Use it, fork it, run your own workshop.
