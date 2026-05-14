# ============================================================
# SECTION 4: Add Memory — Conversation Context
# ============================================================
#
# Without memory, each call is stateless. "Their center" means
# nothing if the agent forgot you asked about the Nuggets.
#
# Run this: python workshop/04_add_memory.py
# ============================================================

import _path  # noqa: F401

from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.tools.mcp import MCPClient
from strands.agent.conversation_manager import SlidingWindowConversationManager
from src.config import get_model
from src.hooks import LoggingHook

mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx", args=["nba-stats-mcp"])
))

model = get_model()

with mcp_client:
    tools = mcp_client.list_tools_sync()

    # ── WITHOUT memory ─────────────────────────────────────
    print("=" * 60)
    print("  WITHOUT Memory (stateless)")
    print("=" * 60)

    agent = Agent(
        model=model,
        tools=tools,
        system_prompt="You are an NBA analyst. Use your tools to answer questions.",
        hooks=[LoggingHook(verbose=True)],
    )

    print("\n  Turn 1: What's the score of the Nuggets game?\n")
    response = agent("What's the score of the Nuggets game?")
    print(f"\n{response}\n")

    print("\n  Turn 2: How did their center play?\n")
    response = agent("How did their center play?")
    print(f"\n{response}\n")
    # ❌ The agent doesn't know who "their" refers to

    # ── WITH memory ────────────────────────────────────────
    print("=" * 60)
    print("  WITH Memory (SlidingWindowConversationManager)")
    print("=" * 60)

    agent_with_memory = Agent(
        model=model,
        tools=tools,
        system_prompt="You are an NBA analyst. Use your tools to answer questions.",
        hooks=[LoggingHook(verbose=True)]
        conversation_manager=SlidingWindowConversationManager(window_size=10),
    )

    print("\n  Turn 1: What's the score of the Nuggets game?\n")
    response = agent_with_memory("What's the score of the Nuggets game?")
    print(f"\n{response}\n")

    print("\n  Turn 2: How did their center play?\n")
    response = agent_with_memory("How did their center play?")
    print(f"\n{response}\n")
    # ✅ The agent remembers "their" = Nuggets, "center" = Jokic

# ============================================================
# TRY THIS:
# - Change window_size from 10 to 2 — what happens with longer
#   conversations?
# - Ask 3-4 follow-up questions with agent_with_memory
# - The production NBA Discord Agent uses window_size=16 with
#   per-user conversation isolation across 100 conversations.
#
# When you're ready: python workshop/05_heartbeat.py
# ============================================================
