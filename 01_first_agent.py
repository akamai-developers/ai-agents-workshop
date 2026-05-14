# ============================================================
# SECTION 1: Your First Agent
# ============================================================
#
# An agent is just an LLM with a system prompt.
# Without tools, it can only answer from training data.
#
# Run this: python workshop/01_first_agent.py
# ============================================================

import _path  # noqa: F401

from strands import Agent
from src.config import get_model

agent = Agent(
    model=get_model(),
    system_prompt="You are a helpful NBA analyst.",
)

# Question 1: Something the LLM knows from training data
print("=" * 60)
print("  Question 1: Training data (the LLM knows this)")
print("=" * 60)
print()
response = agent("Who won the 2024 NBA Championship?")
print(f"\n{response}\n")

# Question 2: Something that requires real-time data — the agent can't help
print("=" * 60)
print("  Question 2: Real-time data (the LLM does NOT know this)")
print("=" * 60)
print()
response = agent("What are today's live NBA scores?")
print(f"\n{response}\n")

# ============================================================
# TRY THIS:
# - Change the system_prompt to "You are a sarcastic sports
#   commentator" and re-run. Same question, different personality.
# - Ask about tonight's games — the agent will guess or refuse.
#   It has no way to look up real data. It needs tools.
#
# When you're ready: python workshop/02_custom_tools.py
# ============================================================
