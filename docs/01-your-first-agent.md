# Section 1: Your First Agent

> An agent is a program that uses an LLM as its reasoning engine.

## What You'll Learn

- How to create an agent with the Strands SDK
- What an agent can do with only an LLM (no tools)
- The gap between "knows things" and "can do things"

## The Key Idea

An agent starts with a model and a system prompt. The model is the brain. The system prompt is the personality.

```python
from strands import Agent
from src.config import get_model

agent = Agent(
    model=get_model(),
    system_prompt="You are a helpful NBA assistant.",
)
```

This agent can answer questions from its training data — historical facts, rules of the game, player biographies. But it can't tell you today's scores. It doesn't have access to the internet or any data source. It only knows what it learned during training.

This limitation is the setup for everything that follows. The gap between "knows things" and "can do things" is what tools close.

One thing worth noting: `get_model()` returns a model regardless of whether you're running against vLLM (in this workshop cluster) or Ollama (locally on your laptop). The Strands Agent API is identical either way. You write agent code once and swap backends.

## Run It

```
python workshop/01_first_agent.py
```

## Expected Output

```
============================================================
  Question 1: Training data (the LLM knows this)
============================================================

The Boston Celtics won the 2024 NBA Championship, defeating the
Dallas Mavericks 4-1 in the Finals...

============================================================
  Question 2: Real-time data (the LLM does NOT know this)
============================================================

I don't have access to live data, so I can't tell you today's
exact scores. I'd recommend checking NBA.com or the ESPN app...
```

The first answer is confident and correct. The second reveals the limitation — the agent admits it doesn't have real-time data (or worse, it hallucinates outdated scores).

## Try This

- Ask about a player's career stats (training data — the agent handles this)
- Ask about tonight's games (real-time — watch it struggle)
- Change the `system_prompt` to "You are a sarcastic basketball commentator" and re-run

## What Just Happened

You created an agent with nothing but an LLM. It answered from training data but failed on real-time questions. This is the starting point for every agent — and the reason tools exist.

Next: [Custom Tools + Built-ins](02-custom-tools.md)
