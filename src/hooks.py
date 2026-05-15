"""LoggingHook — print each tool invocation so students can SEE the agent loop.

Usage:
    from src.hooks import LoggingHook
    agent = Agent(..., hooks=[LoggingHook()])
"""

import json
from strands.hooks import HookProvider, HookRegistry, BeforeToolCallEvent


class LoggingHook(HookProvider):
    """Print tool calls in a compact, readable format."""

    def __init__(self, verbose: bool = True):
        self.calls = 0
        self.verbose = verbose

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeToolCallEvent, self._on_before_tool)

    def _on_before_tool(self, event: BeforeToolCallEvent) -> None:
        self.calls += 1
        name = event.tool_use["name"]
        agent_name = event.agent.name or "agent"
        print(f"\n  ↳ [{agent_name}] tool call #{self.calls}: {name}")

        if self.verbose:
            inputs = event.tool_use.get("input") or {}
            if inputs:
                for line in json.dumps(inputs, indent=2).splitlines():
                    print(f"      {line}")
