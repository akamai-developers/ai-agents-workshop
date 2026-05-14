"""
Logging Hook - Log tool invocations before execution.
"""

import json
from strands.hooks import HookProvider, HookRegistry
from strands.hooks import BeforeToolCallEvent


class LoggingHook(HookProvider):
    """
    Hook that logs tool invocations before they are executed.

    Usage:
        agent = Agent(hooks=[LoggingHook()])
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize the logging hook.

        Args:
            verbose: If True, print full input parameters. If False, just tool name.
        """
        self.calls = 0
        self.verbose = verbose

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeToolCallEvent, self.log_start)

    def log_start(self, event: BeforeToolCallEvent) -> None:
        self.calls += 1
        print("=" * 60)
        print(f"TOOL INVOCATION: {self.calls}")
        print("=" * 60)
        print(f"Agent: {event.agent.name}")
        print(f"Tool: {event.tool_use['name']}")

        if self.verbose:
            print("Input Parameters:")
            formatted_input = json.dumps(event.tool_use["input"], indent=2)
            for line in formatted_input.split("\n"):
                print(f"  {line}")

        print("=" * 60)