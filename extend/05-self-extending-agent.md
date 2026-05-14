# Challenge 5: Self-Extending Agent (Meta-Tooling)

What if an agent could **write its own tools** at runtime?

The Strands SDK supports `load_tools_from_directory=True` — the agent can create Python files with `@tool` functions, and they're immediately available without restarting.

## The Script

Save this as `self_extending.py` and run it:

```python
import os
from strands import Agent
from strands.models.ollama import OllamaModel
from strands_tools import editor, shell

# Allow file writes without prompts
os.environ["BYPASS_TOOL_CONSENT"] = "true"

model = OllamaModel(
    host="http://localhost:11434",
    model_id="qwen3:8b",
)

agent = Agent(
    model=model,
    tools=[editor, shell],
    system_prompt="""
You are a self-extending agent. You can create new Python tools at runtime.

To create a tool:
1. Use the editor to write a .py file in the tools/ directory
2. The file must use the @tool decorator from strands
3. The tool will be automatically loaded and available

Tool template:
    from strands import tool

    @tool
    def tool_name(param: str) -> str:
        '''Description of what the tool does.'''
        return result

After creating a tool, test it by calling it directly.
""",
    load_tools_from_directory=True,  # Hot-reload new tools
)

print(f"Starting tools: {agent.tool_names}\n")

# Ask the agent to create a tool and USE it
response = agent(
    "Create a tool called 'calculate_tip' that takes a bill amount "
    "and tip percentage, then returns the tip and total. "
    "Save it to tools/tip_calculator.py. "
    "Then use it to calculate a 20% tip on a $85 dinner bill."
)
print(f"\n{response}")
print(f"\nTools after: {agent.tool_names}")
```

## What Happens

1. The agent starts with only `editor` and `shell`
2. It uses `editor` to write `tools/tip_calculator.py` with a `@tool` function
3. `load_tools_from_directory=True` detects the new file and loads it
4. The agent calls `calculate_tip` — a tool it just created
5. `agent.tool_names` now includes `calculate_tip`

## Why This Matters

In the workshop, you saw four types of tools:
- `@tool` functions (Section 2)
- Built-in `strands_tools` (Section 2)
- MCP server tools (Section 3)
- Agents as tools (Section 3)

A self-extending agent adds a fifth: **tools the agent writes itself.** It can invent capabilities on demand. Need a CSV parser? The agent writes one. Need a data visualization tool? It creates it. The tool set grows as the agent encounters new problems.

## Full Example

See the complete implementation: [labeveryday/strands-agents-meta-tooling](https://github.com/labeveryday/strands-agents-meta-tooling)

That repo includes:
- Color-coded logging hooks
- Claude model with thinking mode
- Multiple tool creation in one session
- Automatic test generation with pytest
