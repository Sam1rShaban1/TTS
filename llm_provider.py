import os
import litellm

PROVIDER_KEY_MAP = {
    "OPENAI_API_KEY": "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY": "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY": "GEMINI_API_KEY",
    "GROQ_API_KEY": "GROQ_API_KEY",
    "MISTRAL_API_KEY": "MISTRAL_API_KEY",
    "OPENROUTER_API_KEY": "OPENROUTER_API_KEY",
    "NVIDIA_API_KEY": "NVIDIA_API_KEY",
    "COHERE_API_KEY": "COHERE_API_KEY",
    "DEEPSEEK_API_KEY": "DEEPSEEK_API_KEY",
    "TOGETHERAI_API_KEY": "TOGETHERAI_API_KEY",
    "XAI_API_KEY": "XAI_API_KEY",
}


def set_provider_key(provider_id: str, api_key: str):
    """Set the API key for the selected provider in environment."""
    if provider_id == "OLLAMA":
        os.environ["OLLAMA_API_BASE"] = os.environ.get(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        )
        return
    os.environ[provider_id] = api_key


def _get_api_key(provider_id: str) -> str | None:
    """Get the API key for a provider from env."""
    return os.environ.get(PROVIDER_KEY_MAP.get(provider_id, provider_id), "").strip() or None


async def clean_text(raw_text: str, model: str) -> str:
    """Send extracted text to LLM for fat-trimming / formatting cleanup."""
    from config import get_model_info
    info = get_model_info(model)
    api_key = _get_api_key(info["provider"]) if info else None
    kwargs = {}
    if api_key:
        kwargs["api_key"] = api_key
    response = litellm.completion(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a text cleaner. Clean this extracted document text by:\n"
                    "- Removing page numbers, headers, footers, footnotes\n"
                    "- Fixing broken words and split lines\n"
                    "- Removing duplicate lines or repeated headers\n"
                    "- Removing extraction artifacts (random characters, garbled text)\n\n"
                    "Do NOT:\n"
                    "- Change any actual content, sentences, or meaning\n"
                    "- Summarize or rephrase anything\n"
                    "- Add or remove any sentences\n\n"
                    "Return ONLY the cleaned text, nothing else."
                ),
            },
            {"role": "user", "content": raw_text},
        ],
        temperature=0.1,
        **kwargs,
    )
    return response["choices"][0]["message"]["content"]


async def ocr_extract(image_b64: str, model: str) -> str:
    """Use a vision-capable LLM to extract text from a scanned document image."""
    from config import get_model_info
    info = get_model_info(model)
    api_key = _get_api_key(info["provider"]) if info else None
    kwargs = {}
    if api_key:
        kwargs["api_key"] = api_key
    response = litellm.completion(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract ALL text from this document image exactly as written. "
                    "Preserve the original structure, paragraphs, and formatting. "
                    "Return ONLY the extracted text, nothing else."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}",
                        },
                    }
                ],
            },
        ],
        temperature=0.0,
        **kwargs,
    )
    return response["choices"][0]["message"]["content"]
