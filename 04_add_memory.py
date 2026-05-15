# ============================================================
# SECTION 4 — Memory (Two Layers)
# ============================================================
# There are two things people call "memory". Don't confuse them.
#
#   A. Conversation context — does the agent remember what
#      you said three turns ago in the SAME conversation?
#      Solved by a ConversationManager.
#
#   B. Persistent memory — does it remember you when you start
#      a brand new conversation tomorrow?
#      Solved by a TOOL that reads/writes a store.
#
# Run:  python 04_add_memory.py
# ============================================================

import _path  # noqa: F401

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands_tools import current_time

from src.config import get_model
from src.hooks import LoggingHook
from src.tools.memory import remember_fact, recall_facts


model = get_model()


# ============================================================
# LAYER A — Conversation context
# ============================================================
# Without a conversation manager, each call is stateless. A
# follow-up like "And who's their best player?" is meaningless
# because the agent has no record of which team you meant.

print("=" * 60)
print("  Layer A.1 — NO conversation memory (stateless)")
print("=" * 60)

stateless = Agent(
    model=model,
    tools=[current_time],
    system_prompt="You are an NBA analyst. Be brief.",
    hooks=[LoggingHook(verbose=False)],
)

print("\n  Turn 1:")
print(stateless("My favorite team is the Denver Nuggets."))

print("\n  Turn 2 (same agent):")
print(stateless("Who is their best player?"))
# Likely the model has no idea who "their" refers to.

# By default Strands ships SlidingWindowConversationManager,
# so plain Agent() actually DOES keep history. We override it
# above with `agent.messages.clear()`-equivalent behaviour by
# making a NEW agent each call would be more honest — but the
# point is the same: turn off context and the agent forgets.
stateless.messages.clear()

print("\n" + "=" * 60)
print("  Layer A.2 — WITH SlidingWindowConversationManager")
print("=" * 60)

# window_size = N most recent messages to keep. Older messages
# get dropped. Good default; cheap; preserves recency.
conv_agent = Agent(
    model=model,
    tools=[current_time],
    system_prompt="You are an NBA analyst. Be brief.",
    conversation_manager=SlidingWindowConversationManager(window_size=10),
    hooks=[LoggingHook(verbose=False)],
)

print("\n  Turn 1:")
print(conv_agent("My favorite team is the Denver Nuggets."))

print("\n  Turn 2:")
print(conv_agent("Who is their best player?"))
# Now the agent knows "their" = Nuggets.


# ============================================================
# LAYER B — Persistent memory across runs
# ============================================================
# A ConversationManager only lives as long as the Python
# process. Kill the script, lose the context. For real memory
# we need to write to a STORE.
#
# Open src/tools/memory.py — those are just @tool functions
# (like Section 2's weather tool) backed by SQLite. The agent
# decides when to call them based on their docstrings.

USER_ID = "me"

print("\n" + "=" * 60)
print(f"  Layer B — persistent memory (user_id = {USER_ID})")
print("=" * 60)

mem_agent = Agent(
    model=model,
    tools=[remember_fact, recall_facts],
    system_prompt=(
        f"You are a personal assistant for user_id='{USER_ID}'.\n"
        "At the start of every conversation, call recall_facts to load "
        "what you already know about the user.\n"
        "When the user shares a durable preference, name, team, role, "
        "or constraint — call remember_fact to persist it.\n"
        "Keep replies short."
    ),
    hooks=[LoggingHook(verbose=True)],
)

print("\n  Turn 1 — teach the agent something:")
print(mem_agent(
    "Hi! I'm a Stanford alum, I'm a die-hard Warriors fan, and I prefer "
    "short bullet-point summaries."
))

print("\n  Turn 2 — ask for a recap, see if it personalizes:")
print(mem_agent("Give me a quick rundown of tonight's NBA action."))

# ⬇ Now re-run this whole script: python 04_add_memory.py
# Layer A starts fresh every time. Layer B remembers you because
# remember_fact wrote to memory.db, which is still on disk.


# ============================================================
# TRY THIS
#   1. Run this script twice. On the second run, before any
#      teaching, ask: "What do you know about me?" — the agent
#      should call recall_facts and surface the Stanford / Warriors
#      / bullet-points preferences from run #1.
#
#   2. Add a `forget_facts` import (it already exists in
#      src/tools/memory.py). Tell the agent "forget everything
#      about me" and watch it pick the right tool.
#
#   3. Swap SQLite for Redis, mem0, or S3 — the docstrings stay
#      the same, the agent doesn't care. "Memory" is just a tool.
#
# Next:  python 05_heartbeat.py
# ============================================================
