# ============================================================
# SECTION 0 — Verify Your Environment
# ============================================================
# Run this first:   python 00_verify.py
# ============================================================

import _path  # noqa: F401

import os
import shutil
import urllib.request

checks = []


def ok(label):
    print(f"  ✅ {label}")
    checks.append(True)


def bad(label):
    print(f"  ❌ {label}")
    checks.append(False)


# 1. Strands SDK
try:
    import strands  # noqa: F401
    ok("strands-agents SDK installed")
except ImportError:
    bad("strands-agents — run: pip install -r requirements.txt")

# 2. MCP SDK
try:
    import mcp  # noqa: F401
    ok("mcp SDK installed")
except ImportError:
    bad("mcp — run: pip install -r requirements.txt")

# 3. nba-stats-mcp on PATH
if shutil.which("nba-stats-mcp"):
    ok("nba-stats-mcp on PATH")
else:
    bad("nba-stats-mcp — run: pip install nba-stats-mcp  (or `uvx nba-stats-mcp` works too)")

# 4. LLM backend
vllm_host = os.environ.get("VLLM_HOST")
if vllm_host:
    try:
        urllib.request.urlopen(f"{vllm_host.rstrip('/')}/models", timeout=3).read(1)
        ok(f"vLLM reachable at {vllm_host}")
    except Exception as e:
        bad(f"VLLM_HOST set but unreachable: {e}")
else:
    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2).read(1)
        ok("Ollama reachable at localhost:11434")
    except Exception:
        bad("No LLM backend — start Ollama OR set VLLM_HOST=https://your-vllm/v1")

# 5. One real call through Strands, so we know the whole stack works
print()
if all(checks):
    print("  Trying one round-trip through Strands…")
    try:
        from strands import Agent
        from src.config import get_model

        agent = Agent(model=get_model(), system_prompt="Reply with exactly the word: pong")
        reply = str(agent("ping")).strip().lower()
        if "pong" in reply:
            ok("end-to-end call succeeded")
        else:
            bad(f"agent replied but didn't say pong: {reply!r}")
    except Exception as e:
        bad(f"end-to-end call failed: {e}")

print()
if all(checks):
    print("  ✅ You're ready. Next:  python 01_first_agent.py")
else:
    print("  ⚠️  Fix the ❌ items above and re-run.")
