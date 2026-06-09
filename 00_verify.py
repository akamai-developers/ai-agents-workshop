# ============================================================
# SECTION 0 — Verify Your Environment
# ============================================================
# Run this first:   python 00_verify.py
# ============================================================

import _path  # noqa: F401

import os
import json
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
    api_key = os.environ.get("VLLM_API_KEY", "not-needed")
    model = os.environ.get("MODEL_NAME", "Qwen/Qwen3-8B-FP8")
    body = json.dumps({"model": model,
                       "messages": [{"role": "user", "content": "ping"}],
                       "max_tokens": 1}).encode()
    req = urllib.request.Request(f"{vllm_host.rstrip('/')}/chat/completions", data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
    try:
        urllib.request.urlopen(req, timeout=10).read(1)
        ok(f"vLLM reachable at {vllm_host} (model: {model})")
    except Exception as e:
        bad(f"VLLM_HOST set but unreachable: {e}")

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
