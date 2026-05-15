# ============================================================
# SECTION 1 — Your First Agent
# ============================================================
# An agent is just an LLM with a system prompt.
# Without tools it can only answer from training data.
#
# Run:  python 01_first_agent.py
# ============================================================

import _path  # noqa: F401

from strands import Agent
from strands_tools import current_time
from src.config import get_model


# We give the agent ONE tool: current_time. That lets it know today's
# date (handy because the LLM's training data is from the past), but
# it still has no way to look up live game scores.
agent = Agent(
    model=get_model(),
    tools=[current_time],
    system_prompt="You are a knowledgeable NBA analyst. Be concise.",
)

# ── 1. Something the LLM knows from training data ────────────
print("=" * 60)
print("  Q1 — Training data (the LLM should know this)")
print("=" * 60)
print(agent("Who won the 2024 NBA Championship?"))

# ── 2. Something it CAN'T know — needs real-time data ────────
print("\n" + "=" * 60)
print("  Q2 — Real-time data (the LLM does NOT know this)")
print("=" * 60)
print(agent("What's the score of the Warriors game right now?"))

# The agent will either guess, refuse, or hallucinate. That's
# the whole point — without tools, an agent is just an LLM.
# In Section 2 we give it tools.

# ── Bonus: swap the personality on the fly ───────────────────
agent.system_prompt = "You are a sarcastic sports commentator. One sentence only."
print("\n" + "=" * 60)
print("  Same agent, new system_prompt")
print("=" * 60)
print(agent("Did the Cavs win last night?"))


# ============================================================
# TRY THIS
#   - Change the system_prompt to "You are a comedian who only
#     speaks in basketball metaphors." Re-run.
#   - Ask about a game that finished 5 minutes ago. Watch the
#     agent confidently make something up. That's why tools matter.
#
# Next:  python 02_custom_tools.py
# ============================================================
