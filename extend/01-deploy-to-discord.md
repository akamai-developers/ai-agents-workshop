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
from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from src.config import get_model, get_tools
from src.hooks import ToolDisplayHook

load_dotenv()

model = get_model()
tools = get_tools()

# Create an agent with memory
agent = Agent(
    model=model,
    tools=tools,
    system_prompt="You are an NBA assistant in a Discord server.",
    conversation_manager=SlidingWindowConversationManager(window_size=10),
    callback_handler=None,
)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        content = message.content.replace(f"<@{client.user.id}>", "").strip()
        response = agent(content)
        # Discord has a 2000 char limit
        text = str(response)
        for i in range(0, len(text), 2000):
            await message.reply(text[i:i+2000])

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

## Reference

The production bot at `nba-discord-agent/src/agent.py` adds:
- Per-user conversation scoping
- Rate limiting
- Heartbeat integration
- Error handling for context window overflow
