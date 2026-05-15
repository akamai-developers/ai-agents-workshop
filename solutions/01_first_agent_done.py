# SOLUTION — Section 1: an agent is LLM + system_prompt.
# Without tools it can only answer from training data.

import _path  # noqa: F401

from strands import Agent
from src.config import get_model

agent = Agent(
    model=get_model(),
    system_prompt="You are a knowledgeable NBA analyst. Be concise.",
)

# This works — the LLM knows historical NBA results from training.
print(agent("Who won the 2024 NBA Championship?"))

# This fails — no tools means no path to real-time data. The model
# will either refuse, guess, or hallucinate. That's the whole lesson:
# an LLM by itself is a closed system; tools open it up to the world.
print(agent("What's the score of the Warriors game right now?"))
