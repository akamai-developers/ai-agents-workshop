# Challenge 1: Deploy to Discord

> Wire your agent to a Discord bot so others can interact with it.

## What You'll Build

A Discord bot that answers NBA questions using the same agent you built in the workshop.

## Prerequisites

- A Discord account
- A server where you have admin permissions (or create a test server)

## Steps

### 1. Create a Discord Bot

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Click "New Application", name it "NBA Agent"
3. Go to the "Bot" tab, click "Reset Token", copy it
4. Enable "Message Content Intent" under Privileged Gateway Intents
5. Go to "OAuth2" → "URL Generator", select `bot` scope and `Send Messages` + `Read Message History` permissions
6. Copy the URL and open it to invite the bot to your server

### 2. Install discord.py

```bash
pip install discord.py python-dotenv
```

### 3. Create the Bot Script

Create `discord_bot.py`:

```python
import os
import discord
from dotenv import load_dotenv
from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.tools.mcp import MCPClient
from strands.agent.conversation_manager import SlidingWindowConversationManager

from src.config import get_model
from src.hooks import LoggingHook
from src.tools.memory import remember_fact, recall_facts

load_dotenv()

nba_mcp = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx", args=["nba-stats-mcp"])
))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# We open the MCP client once at startup and reuse the agent across messages.
# In production you'd also want per-user conversation managers — see the note
# at the bottom of this doc.
nba_mcp.__enter__()
nba_tools = nba_mcp.list_tools_sync()

agent = Agent(
    model=get_model(),
    tools=[*nba_tools, remember_fact, recall_facts],
    system_prompt="You are an NBA assistant in a Discord server. Be concise.",
    conversation_manager=SlidingWindowConversationManager(window_size=10),
    hooks=[LoggingHook(verbose=False)],
)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        content = message.content.replace(f"<@{client.user.id}>", "").strip()
        response = str(agent(content))
        # Discord caps messages at 2000 chars.
        for i in range(0, len(response), 2000):
            await message.reply(response[i:i + 2000])


client.run(os.getenv("DISCORD_TOKEN"))
```

### 4. Create .env

```
DISCORD_TOKEN=your-token-here
```

### 5. Run It

```bash
python discord_bot.py
```

Mention the bot in Discord or DM it with an NBA question.

## Production Notes

The script above is the smallest thing that works. To make it production-shaped:

- **Per-user conversation scoping** — one shared agent means everyone's messages mix into one window. Spin up an agent per `message.author.id`, or carry the conversation in §4's SQLite memory keyed by user id.
- **Rate limiting** — Discord allows ~5 messages/5s per channel. Add a per-channel queue.
- **Heartbeat integration** — run §5's heartbeat in a background task (`asyncio.create_task`) and post via `channel.send` from inside the heartbeat's custom `@tool`.
- **Context window overflow** — wrap `agent(content)` and catch `ContextWindowOverflowException`; `SlidingWindowConversationManager` already trims, but a single oversized message can still hit the wall.

See `nba-discord-agent/src/agent.py` in the production repo for all four wired up together.
