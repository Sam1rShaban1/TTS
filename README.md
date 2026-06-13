# Doc-to-Speech

Upload documents (PDF, DOCX, PPTX, TXT), extract text, and generate speech audio using Microsoft's edge_tts.

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Sam1rShaban1/TTS.git
cd TTS

# 2. Copy env and add your API keys
cp .env.example .env
# Edit .env and fill in at least one LLM provider API key

# 3. Run with Docker Compose
docker compose up -d

# 4. Open http://localhost:8000
```

## Features

- **Document upload**: PDF, DOCX, PPTX, TXT
- **Text extraction**: PyMuPDF, python-docx, python-pptx (fast, free, no API needed)
- **LLM cleaning**: Fat-trim extracted text via any LLM provider (removes page numbers, headers, footers, broken lines)
- **Scanned PDF support**: Vision-capable LLMs can OCR scanned documents
- **Language detection**: Auto-detects document language and shows matching voices
- **322+ voices**: All edge_tts voices across 74 languages
- **Audio controls**: Speed, pitch, volume sliders
- **Multi-provider LLM**: OpenAI, Anthropic, Gemini, Groq, Mistral, OpenRouter, NVIDIA, Cohere, DeepSeek, Together, xAI, Ollama

## Supported LLM Providers

| Provider | Env Variable | Free Tier |
|----------|-------------|-----------|
| OpenAI | `OPENAI_API_KEY` | No |
| Anthropic | `ANTHROPIC_API_KEY` | No |
| Google Gemini | `GEMINI_API_KEY` | 15 RPM |
| Groq | `GROQ_API_KEY` | 30 RPM |
| Mistral | `MISTRAL_API_KEY` | Yes |
| OpenRouter | `OPENROUTER_API_KEY` | Varies |
| NVIDIA NIM | `NVIDIA_API_KEY` | Yes |
| Cohere | `COHERE_API_KEY` | Yes |
| DeepSeek | `DEEPSEEK_API_KEY` | Yes |
| Together AI | `TOGETHERAI_API_KEY` | Yes |
| xAI | `XAI_API_KEY` | Yes |
| Ollama | `OLLAMA_ENABLED=true` | Free (local) |

Providers with empty API keys are hidden from the UI.

## Development (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

## Project Structure

```
TTS/
├── main.py              # FastAPI app
├── config.py            # Provider registry + env loading
├── extractors.py        # PDF/DOCX/PPTX/TXT extraction
├── llm_provider.py      # litellm wrapper (any provider)
├── tts_engine.py        # edge_tts wrapper
├── language.py          # Language detection + voice filtering
├── templates/index.html # Frontend (Tailwind CSS)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```
