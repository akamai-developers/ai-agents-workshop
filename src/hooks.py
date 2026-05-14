"""
Display hooks — colored terminal output showing agent tool calls and reasoning.

Students see exactly what the agent is doing: which tools it calls,
what parameters it passes, and what results come back.
"""

from __future__ import annotations

import json

try:
    from rich.console import Console
    from rich.text import Text
    _console = Console()
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False


def _print_colored(text: str, color: str = "white") -> None:
    """Print with color using rich, falling back to plain text."""
    if _HAS_RICH:
        _console.print(f"[{color}]{text}[/{color}]")
    else:
        print(text)


def _truncate(text: str, max_len: int = 200) -> str:
    """Truncate text to max_len characters."""
    text = str(text)
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


class ToolDisplayHook:
    """Strands callback hook that prints tool calls and results to the terminal.

    Usage:
        hook = ToolDisplayHook()
        agent = Agent(model=model, tools=tools, callback_handler=hook)
    """

    def __init__(self):
        self._last_tool_name = None

    def __call__(self, **kwargs):
        """Handle Strands agent callback events."""
        # Tool use — the agent decided to call a tool
        if "current_tool_use" in kwargs and "message" not in kwargs:
            tool_use = kwargs["current_tool_use"]
            if isinstance(tool_use, dict) and "name" in tool_use:
                name = tool_use["name"]
                self._last_tool_name = name
                tool_input = tool_use.get("input", {})
                if isinstance(tool_input, dict):
                    params = ", ".join(f'{k}="{v}"' for k, v in tool_input.items())
                else:
                    params = str(tool_input)
                _print_colored(f"\n🔧 Tool Call: {name}({params})", "cyan")

        # Tool result — delivered inside "message" content blocks as toolResult
        if "message" in kwargs:
            msg = kwargs["message"]
            if isinstance(msg, dict):
                for block in msg.get("content", []):
                    if isinstance(block, dict) and "toolResult" in block:
                        tr = block["toolResult"]
                        content_parts = tr.get("content", [])
                        text_parts = []
                        for part in (content_parts if isinstance(content_parts, list) else []):
                            if isinstance(part, dict) and "text" in part:
                                text_parts.append(part["text"])
                        content = "\n".join(text_parts) if text_parts else str(tr)
                        _print_colored(f"📊 Result: {_truncate(content)}", "green")
