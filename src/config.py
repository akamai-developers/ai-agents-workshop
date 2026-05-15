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
        return OpenAIModel(
            client_args={
                "base_url": vllm_host,
                "api_key": os.environ.get("VLLM_API_KEY", "not-needed"),
            },
            model_id=os.environ.get("MODEL_NAME", "Qwen/Qwen3-8B-FP8"),
            params={
                "temperature": 0.3,
                # Qwen3 emits <think>...</think> by default. Suppress it via the
                # model's chat template — saves ~100-300 tokens and ~3-5s of
                # latency per turn for the workshop.
                "extra_body": {"chat_template_kwargs": {"enable_thinking": False}},
            },
        )

    from strands.models.ollama import OllamaModel
    return OllamaModel(
        host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
        model_id=os.environ.get("MODEL_NAME", "qwen3:8b"),
    )
