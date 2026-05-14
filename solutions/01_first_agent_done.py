# SOLUTION: Section 1 — Your First Agent
# Run this if you're stuck: python workshop/solutions/01_first_agent_done.py

import _path  # noqa: F401

from strands import Agent
from src.config import get_model

agent = Agent(
    model=get_model(),
    system_prompt="You are a helpful NBA analyst.",
)

print("=" * 60)
print("  Question 1: Training data")
print("=" * 60)
print()
response = agent("Who won the 2024 NBA Championship?")
print(f"\n{response}\n")

print("=" * 60)
print("  Question 2: Real-time data (no tools)")
print("=" * 60)
print()
response = agent("What are today's live NBA scores?")
print(f"\n{response}\n")
