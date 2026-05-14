# SOLUTION: Section 4 — Add Memory
# Run this if you're stuck: python workshop/solutions/04_add_memory_done.py

import _path  # noqa: F401

from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.tools.mcp import MCPClient
from strands.agent.conversation_manager import SlidingWindowConversationManager
from src.config import get_model
from src.hooks import ToolDisplayHook

mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx", args=["nba-stats-mcp"])
))

model = get_model()

with mcp_client:
    tools = mcp_client.list_tools_sync()

    print("=" * 60)
    print("  WITHOUT Memory")
    print("=" * 60)

    agent = Agent(
        model=model, tools=tools,
        system_prompt="You are an NBA analyst. Use your tools to answer questions.",
        callback_handler=ToolDisplayHook(),
    )

    agent("What's the score of the Nuggets game?")
    agent("How did their center play?")

    print("\n" + "=" * 60)
    print("  WITH Memory")
    print("=" * 60)

    agent_with_memory = Agent(
        model=model, tools=tools,
        system_prompt="You are an NBA analyst. Use your tools to answer questions.",
        callback_handler=ToolDisplayHook(),
        conversation_manager=SlidingWindowConversationManager(window_size=10),
    )

    agent_with_memory("What's the score of the Nuggets game?")
    agent_with_memory("How did their center play?")
