# Section 4: Memory (Two Layers)

[← MCP + Multi-Agent](03-mcp-and-multi-agent.md) · [Index](README.md) · [Next → Heartbeat](05-autonomous-reasoning.md)

> "Memory" means two different things. Don't conflate them.

## What You'll Learn

- The difference between conversation context and persistent memory
- `SlidingWindowConversationManager` — for "their best player?" follow-ups
- Persistent memory as a **tool** over a real store (SQLite here, anything tomorrow)
- Why "memory" isn't a Strands feature — it's a tool pattern

## The Key Idea

Two things share the name "memory":

| Layer | Lifetime | Mechanism |
|---|---|---|
| **A. Conversation context** | One Python process | `ConversationManager` (sliding window) |
| **B. Persistent memory** | Forever | A `@tool` that reads/writes a store |

They solve different problems. Layer A lets the agent resolve "their" → "Nuggets" three turns into a chat. Layer B lets you walk away, come back tomorrow, and have the agent still remember you're a Stanford alum and a Warriors fan.

### Layer A — `SlidingWindowConversationManager`

Keeps the last N messages so follow-ups have context:

```python
from strands.agent.conversation_manager import SlidingWindowConversationManager

agent = Agent(
    model=model,
    conversation_manager=SlidingWindowConversationManager(window_size=10),
)
```

One argument. The agent remembers the last 10 messages; older messages get dropped. Trade-off: bigger window = more tokens per request.

### Layer B — Memory as a tool

`src/tools/memory.py` defines three plain `@tool` functions backed by SQLite:

```python
@tool
def remember_fact(user_id: str, fact: str) -> str:
    """Persist a single fact about a user. Use this whenever the user
    tells you something durable — a preference, a name, a constraint."""
    # …INSERT INTO facts…

@tool
def recall_facts(user_id: str) -> str:
    """Return everything we know about a user. Call this at the start
    of a conversation so you can personalize your reply."""
    # …SELECT FROM facts…
```

That's it. The agent reads the docstrings and decides when to call. The DB lives at `memory.db` in the workshop directory and **survives across process restarts** — re-run the script and the agent recalls what you taught it last time.

The point isn't SQLite. The point is: any store with a sensible API can be memory. Swap SQLite for Redis, mem0, Pinecone, or an S3 bucket — the agent doesn't care, only the docstring changes.

## Run It

```
python 04_add_memory.py
```

## Expected Output

**Layer A.1 — without conversation memory:**
```
  Turn 1: My favorite team is the Denver Nuggets.
  → Solid pick.

  Turn 2: Who is their best player?
  → I'd need more context — which team are you asking about?
```

**Layer A.2 — with sliding window:**
```
  Turn 1: My favorite team is the Denver Nuggets.
  → Solid pick.

  Turn 2: Who is their best player?
  → Nikola Jokić — three-time MVP, anchors the offense from the elbow.
```

**Layer B — persistent across runs:**
```
  ↳ [agent] tool call #1: remember_fact
      {"user_id": "me", "fact": "User is a Stanford alum"}
  ↳ [agent] tool call #2: remember_fact
      {"user_id": "me", "fact": "User is a die-hard Warriors fan"}
  ↳ [agent] tool call #3: remember_fact
      {"user_id": "me", "fact": "User prefers short bullet-point summaries"}

Got it — saved three facts about you.

  ↳ [agent] tool call #4: recall_facts
      {"user_id": "me"}

Tonight's NBA action:
  • Warriors beat Lakers 108-102 — Curry 32 pts
  • Nuggets/Wolves close at the half
  • Two more games tipping off later tonight
```

Now **kill the script and re-run it**. Before you teach it anything new, ask "what do you know about me?" — the agent calls `recall_facts`, pulls the rows out of `memory.db`, and answers, because Layer B lives on disk, not in process memory.

## Try This

- Run the script twice. On run #2, ask "what do you know about me?" before teaching anything new.
- Change `window_size` from 10 to 2 — watch Layer A break on longer chains.
- Import `forget_facts` from `src/tools/memory.py`. Tell the agent "forget everything about me" — watch it pick the right tool.
- Replace SQLite with Redis or mem0. The docstrings stay the same. The agent doesn't care.

## What Just Happened

Layer A: one constructor argument keeps the recent conversation in scope. Layer B: three `@tool` functions over SQLite give you memory that outlives the Python process. The takeaway is that "agent memory" is mostly the second one — a `@tool` pointed at a real store. Pick the store you like.

Next: [Autonomous Reasoning](05-autonomous-reasoning.md)
