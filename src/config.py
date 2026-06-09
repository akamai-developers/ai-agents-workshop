"""Model configuration — vLLM (workshop) or Ollama (local).

Picks the backend based on env vars:

- If VLLM_HOST is set         → OpenAI-compatible client pointing at vLLM
- If OLLAMA_HOST is reachable → Ollama
- Otherwise                   → friendly error

Defaults are tuned for Qwen3-8B served by vLLM in the workshop cluster.
"""

import os


def get_model():
    vllm_host = os.environ.get("VLLM_HOST")
    if vllm_host:
        from strands.models.openai import OpenAIModel
        class VLLMModel(OpenAIModel):
            # vLLM 0.20+ rejects an empty `tools: []`; drop it only when the agent has no tools.
            def format_request(self, *args, **kwargs):
                request = super().format_request(*args, **kwargs)
                if not request.get("tools"):
                    request.pop("tools", None)
                    request.pop("tool_choice", None)
                return request
            # Filter gpt-oss's reasoning (analysis) channel out of the stream: keeps the
            # chain-of-thought off the screen AND out of message history (so the
            # "reasoningContent is not supported in multi-turn" warning never fires).
            # Answer text and tool-call events stream through untouched.
            async def stream(self, *args, **kwargs):
                pending_start = None
                skip = False
                async for event in super().stream(*args, **kwargs):
                    if isinstance(event, dict) and "contentBlockStart" in event:
                        pending_start, skip = event, False
                        continue
                    if isinstance(event, dict) and "contentBlockDelta" in event:
                        if "reasoningContent" in event["contentBlockDelta"].get("delta", {}):
                            skip = True
                            continue
                        if pending_start is not None:
                            yield pending_start
                            pending_start = None
                        yield event
                        continue
                    if isinstance(event, dict) and "contentBlockStop" in event:
                        if skip:
                            skip, pending_start = False, None
                            continue
                        if pending_start is not None:
                            yield pending_start
                            pending_start = None
                        yield event
                        continue
                    yield event

        model_id = os.environ.get("MODEL_NAME", "Qwen/Qwen3-8B-FP8")
        params = {"temperature": 0.3}

        # `enable_thinking` is a Qwen3-only chat-template kwarg; gpt-oss (harmony) rejects it.
        if "qwen3" in model_id.lower():
            params["extra_body"] = {"chat_template_kwargs": {"enable_thinking": False}}

        return VLLMModel(
            client_args={
                "base_url": vllm_host,
                "api_key": os.environ.get("VLLM_API_KEY", "not-needed"),
            },
            model_id=model_id,
            params=params,
        )
        
    from strands.models.ollama import OllamaModel
    return OllamaModel(
        host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
        model_id=os.environ.get("MODEL_NAME", "qwen3:8b"),
    )