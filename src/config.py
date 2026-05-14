"""Model configuration — vLLM (workshop) or Ollama (local)."""

import os


def get_model():
    """Return the LLM model based on environment.

    - Workshop cluster: VLLM_HOST is set → OpenAIModel
    - Local development: Ollama at localhost → OllamaModel
    """
    vllm_host = os.environ.get("VLLM_HOST")
    if vllm_host:
        from strands.models.openai import OpenAIModel
        return OpenAIModel(
            client_args={"base_url": vllm_host, "api_key": "not-needed"},
            model_id=os.environ.get("MODEL_NAME", "Qwen/Qwen3-8B-FP8"),
        )

    from strands.models.ollama import OllamaModel
    return OllamaModel(
        host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
        model_id=os.environ.get("MODEL_NAME", "qwen3:8b"),
    )
