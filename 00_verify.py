# ============================================================
# SECTION 0: Verify Your Environment
# ============================================================
#
# Run this first: python workshop/00_verify.py
# ============================================================

import _path  # noqa: F401

import os
import shutil

checks = []

# Check 1: Strands SDK
try:
    import strands
    print("  ✅ Strands Agents SDK")
    checks.append(True)
except ImportError:
    print("  ❌ Strands Agents SDK — run: pip install strands-agents")
    checks.append(False)

# Check 2: MCP SDK
try:
    import mcp
    print("  ✅ MCP SDK")
    checks.append(True)
except ImportError:
    print("  ❌ MCP SDK — run: pip install mcp")
    checks.append(False)

# Check 3: nba-stats-mcp
if shutil.which("nba-stats-mcp"):
    print("  ✅ nba-stats-mcp")
    checks.append(True)
else:
    print("  ❌ nba-stats-mcp — run: pip install nba-stats-mcp")
    checks.append(False)

# Check 4: LLM backend
if os.environ.get("VLLM_HOST"):
    print(f"  ✅ vLLM at {os.environ['VLLM_HOST']}")
    checks.append(True)
else:
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        print("  ✅ Ollama at localhost:11434")
        checks.append(True)
    except Exception:
        print("  ❌ No LLM backend — set VLLM_HOST or start Ollama")
        checks.append(False)

print()
if all(checks):
    print("  ✅ You're ready!")
else:
    print("  ⚠️  Fix the issues above and re-run.")
