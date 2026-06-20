import os
from dotenv import load_dotenv

load_dotenv()

PROVIDERS = {
    "OPENAI_API_KEY": {
        "name": "OpenAI",
        "models": [
            ("openai/gpt-4o", "GPT-4o"),
            ("openai/gpt-4o-mini", "GPT-4o Mini"),
            ("openai/gpt-4.1-mini", "GPT-4.1 Mini"),
        ],
    },
    "ANTHROPIC_API_KEY": {
        "name": "Anthropic",
        "models": [
            ("anthropic/claude-sonnet-4-20250514", "Claude Sonnet 4"),
            ("anthropic/claude-3-5-haiku-20241022", "Claude 3.5 Haiku"),
        ],
    },
    "GEMINI_API_KEY": {
        "name": "Google Gemini",
        "models": [
            ("gemini/gemini-2.5-flash", "Gemini 2.5 Flash"),
            ("gemini/gemini-2.0-flash", "Gemini 2.0 Flash"),
        ],
    },
    "GROQ_API_KEY": {
        "name": "Groq",
        "models": [
            ("groq/llama-3.3-70b-versatile", "Llama 3.3 70B"),
            ("groq/llama-3.1-8b-instant", "Llama 3.1 8B"),
        ],
    },
    "MISTRAL_API_KEY": {
        "name": "Mistral AI",
        "models": [
            ("mistral/mistral-large-latest", "Mistral Large"),
            ("mistral/mistral-small-latest", "Mistral Small"),
        ],
    },
    "OPENROUTER_API_KEY": {
        "name": "OpenRouter",
        "models": [
            ("openrouter/meta-llama/llama-3.3-70b-instruct", "Llama 3.3 70B"),
            ("openrouter/google/gemini-2.0-flash-001", "Gemini 2.0 Flash"),
        ],
    },
    "NVIDIA_API_KEY": {
        "name": "NVIDIA NIM",
        "models": [
            ("nvidia_nim/moonshotai/kimi-k2.6", "Kimi 2.6"),
        ],
    },
    "COHERE_API_KEY": {
        "name": "Cohere",
        "models": [
            ("cohere/command-r-plus", "Command R+"),
            ("cohere/command-r", "Command R"),
        ],
    },
    "DEEPSEEK_API_KEY": {
        "name": "DeepSeek",
        "models": [
            ("deepseek/deepseek-chat", "DeepSeek Chat"),
        ],
    },
    "TOGETHERAI_API_KEY": {
        "name": "Together AI",
        "models": [
            ("together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo", "Llama 3.3 70B"),
        ],
    },
    "XAI_API_KEY": {
        "name": "xAI (Grok)",
        "models": [
            ("xai/grok-3", "Grok 3"),
            ("xai/grok-3-mini", "Grok 3 Mini"),
        ],
    },
}


def get_available_providers():
    """Return only providers with non-empty API keys."""
    available = []
    for env_var, info in PROVIDERS.items():
        key = os.environ.get(env_var, "").strip()
        if key:
            available.append(
                {
                    "id": env_var,
                    "name": info["name"],
                    "models": [{"value": m[0], "label": m[1]} for m in info["models"]],
                }
            )

    if os.environ.get("OLLAMA_ENABLED", "false").lower() == "true":
        available.append(
            {
                "id": "OLLAMA",
                "name": "Ollama (Local)",
                "models": [
                    {"value": "ollama/llama3.1", "label": "Llama 3.1"},
                    {"value": "ollama/llama3.3", "label": "Llama 3.3"},
                    {"value": "ollama/mistral", "label": "Mistral"},
                ],
            }
        )

    return available


def set_provider_key(provider_id: str, api_key: str):
    """Set a provider's API key at runtime."""
    if provider_id == "OLLAMA":
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        os.environ["OLLAMA_API_BASE"] = base_url
        return
    os.environ[provider_id] = api_key


def get_provider_key(provider_id: str) -> str:
    """Get the stored API key for a provider (masked for display)."""
    return os.environ.get(provider_id, "")


def get_model_info(model_id: str):
    """Find which provider a model belongs to."""
    for env_var, info in PROVIDERS.items():
        for m in info["models"]:
            if m[0] == model_id:
                return {"provider": env_var, "name": info["name"], "model_name": m[1]}
    return None
