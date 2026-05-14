# Section 4: Conversation Memory

> Memory turns a single-shot tool into a conversation partner.

## What You'll Learn

- Why agents are stateless by default
- How `SlidingWindowConversationManager` adds memory
- The difference one constructor argument makes

## The Key Idea

By default, each agent call is independent. The agent doesn't remember what you asked before. "How did their center play?" means nothing if the agent forgot you were asking about the Nuggets.

`SlidingWindowConversationManager` keeps the last N messages in context. The agent can now reference prior questions and answers:

```python
from strands.agent.conversation_manager import SlidingWindowConversationManager

agent = Agent(
    model=model,
    tools=tools,
    conversation_manager=SlidingWindowConversationManager(window_size=10),
)
```

One constructor argument. The agent now remembers the last 10 messages.

The tradeoff: more memory = more tokens per request = slower and more expensive. `window_size=10` is a practical default. The production NBA Discord Agent uses `window_size=16` with per-user conversation isolation across 100 concurrent conversations.

## Run It

```
python workshop/04_add_memory.py
```

## Expected Output

**WITHOUT memory:**
```
Turn 1: What's the score of the Nuggets game?
→ (agent answers with scores)

Turn 2: How did their center play?
→ "I'm not sure which team you're referring to..."
```

**WITH memory:**
```
Turn 1: What's the score of the Nuggets game?
→ (agent answers with scores)

Turn 2: How did their center play?
→ "Nikola Jokic had 28 points, 14 rebounds, and 12 assists..."
```

Same questions. The only difference is `conversation_manager=SlidingWindowConversationManager(window_size=10)`.

## Try This

- Change `window_size` from 10 to 2 — what happens with longer conversations?
- Ask 4-5 follow-up questions and see how context carries forward
- Remove the `conversation_manager` entirely and compare

## What Just Happened

Without memory, each call is stateless — "their" has no referent. With `SlidingWindowConversationManager`, the agent keeps the last N messages as context. It knows "their center" means Jokic because it remembers you asked about the Nuggets. One argument transforms a tool runner into a conversation partner.

Next: [Autonomous Reasoning](05-autonomous-reasoning.md)
