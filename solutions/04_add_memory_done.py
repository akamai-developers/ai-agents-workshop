# SOLUTION — Section 4: two layers of "memory".
#
# A. Conversation context — recent messages, lives in-process.
# B. Persistent memory — a tool that reads/writes a real store.

import _path  # noqa: F401

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager

from src.config import get_model
from src.hooks import LoggingHook
from src.tools.memory import remember_fact, recall_facts


model = get_model()


# ── Layer A: in-conversation context ──────────────────────────
# SlidingWindowConversationManager keeps the last N messages so
# a follow-up like "their best player?" can resolve "their" back
# to the team you mentioned earlier. Cheap, no external store.
conv_agent = Agent(
    model=model,
    system_prompt="You are an NBA analyst. Be brief.",
    conversation_manager=SlidingWindowConversationManager(window_size=10),
    hooks=[LoggingHook()],
)
print(conv_agent("My favorite team is the Denver Nuggets."))
print(conv_agent("Who is their best player?"))   # 'their' = Nuggets ✓


# ── Layer B: persistent memory across runs ────────────────────
# remember_fact / recall_facts are just @tool functions backed by
# SQLite (see src/tools/memory.py). Re-run this script and the
# agent will recall what it learned last time — proof that memory
# is just a tool over a store you control.
USER_ID = "me"

mem_agent = Agent(
    model=model,
    tools=[remember_fact, recall_facts],
    system_prompt=(
        f"You are a personal assistant for user_id='{USER_ID}'. "
        "Call recall_facts at the start of every chat. "
        "Call remember_fact when the user shares a durable preference."
    ),
    hooks=[LoggingHook()],
)
print(mem_agent("I'm a Stanford alum, Warriors fan, prefer bullet points."))
print(mem_agent("Give me a quick rundown of tonight's NBA action."))
