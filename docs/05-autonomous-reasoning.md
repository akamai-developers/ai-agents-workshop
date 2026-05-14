# Section 5: Autonomous Reasoning

> The heartbeat pattern makes agents act on their own.

## What You'll Learn

- How to make an agent proactive (not just reactive)
- Natural language as control flow
- The heartbeat pattern from the production NBA Discord Agent

## The Key Idea

Everything so far has been request/response: you ask a question, the agent answers. The heartbeat pattern flips this. The agent checks the NBA scoreboard using its tools and **decides on its own** whether to act.

Here's the pattern:

```
1. Agent checks scoreboard  → Uses MCP tools to get live data
2. Agent applies criteria   → Natural language rules YOU wrote
3. Agent decides            → POST something, or SKIP and explain why
```

The criteria is a string of natural language rules:

```python
HEARTBEAT_CRITERIA = """
- Post a recap for any game that just finished
- Post a highlight for any live game with a standout performance
- Skip games that aren't interesting yet
- Keep posts to 2-3 sentences with key stats
"""

agent = Agent(
    model=model,
    tools=mcp_tools,
    system_prompt=HEARTBEAT_CRITERIA,
)

agent("Heartbeat tick. Check the scoreboard and decide what to post.")
```

**You're programming agent behavior with natural language, not if/else.** Change the criteria string, and the agent behaves differently. No code changes.

In production, this runs on a 60-second timer. Every tick: check the scoreboard, reason about what's worth posting, act.

## Run It

```
python workshop/05_heartbeat.py
```

## Expected Output

```
============================================================
  Heartbeat tick
  Agent checking scoreboard and deciding what to post...
============================================================

🔧 Tool Call: get_scoreboard({})
📊 Result: NBA Games for 2026-05-05 (2 games)...

POST: The Cavaliers held off the Pistons 98-87 in a dominant
defensive performance. Donovan Mitchell led with 26 points.

SKIP: Thunder @ Lakers — hasn't started yet (8:30 PM ET).
```

The agent called `get_scoreboard` on its own, evaluated each game against the criteria, and decided what to post.

## Try This

Edit `HEARTBEAT_CRITERIA` in `workshop/05_heartbeat.py`:

1. Change the tone: "Write like a dry statistician" or "Write like a trash-talking fan"
2. Add a rule: "Only post about Western Conference games"
3. Add a rule: "If any player has 30+ points, make it the headline"
4. Run it in a loop (the production pattern):

```python
import time
while True:
    response = agent("Heartbeat tick. Check the scoreboard.")
    print(response)
    time.sleep(60)
```

## What Just Happened

You ran the heartbeat pattern: the agent used its MCP tools to check the NBA scoreboard, applied your natural language criteria, and decided what to POST and what to SKIP. The production NBA Discord Agent runs this same pattern every 60 seconds, 24/7.

Next: [What's Next](06-whats-next.md)
