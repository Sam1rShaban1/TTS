import os
import uuid
import asyncio
import base64
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

import config
import extractors
import llm_provider
import tts_engine
from language import detect_language, get_language_name, filter_voices

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    yield
    # Cleanup on shutdown could go here


app = FastAPI(title="Doc-to-Speech", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/providers")
async def get_providers():
    return {"providers": config.get_available_providers()}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    allowed = {".pdf", ".docx", ".pptx", ".txt"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported file type. Allowed: {', '.join(allowed)}")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        text = extractors.extract_text(file_path)
        scanned = False

        if ext == ".pdf" and extractors.is_scanned_pdf(text):
            scanned = True
            text = ""  # Will need LLM OCR

        lang_code = detect_language(text if text else file.filename)
        lang_name = get_language_name(lang_code)

        return {
            "file_id": file_id,
            "filename": file.filename,
            "raw_text": text,
            "language_code": lang_code,
            "language_name": lang_name,
            "scanned": scanned,
        }
    finally:
        # Keep file for potential re-extraction, cleanup later
        pass


@app.post("/api/clean")
async def clean_text(request: Request):
    body = await request.json()
    raw_text = body.get("text", "")
    model = body.get("model", "openai/gpt-4o-mini")
    api_key = body.get("api_key", "")
    provider_id = body.get("provider_id", "")

    if not raw_text.strip():
        raise HTTPException(400, "No text to clean")

    if not provider_id:
        raise HTTPException(400, "No LLM provider selected")

    try:
        if api_key:
            llm_provider.set_provider_key(provider_id, api_key)

        cleaned = await llm_provider.clean_text(raw_text, model)
        return {"cleaned_text": cleaned}
    except Exception as e:
        raise HTTPException(500, f"LLM cleaning failed: {str(e)}")


@app.post("/api/ocr")
async def ocr_extract(request: Request):
    body = await request.json()
    image_b64 = body.get("image_b64", "")
    model = body.get("model", "openai/gpt-4o-mini")
    api_key = body.get("api_key", "")
    provider_id = body.get("provider_id", "")

    if not image_b64:
        raise HTTPException(400, "No image data")

    if not provider_id:
        raise HTTPException(400, "No LLM provider selected (vision-capable provider required for OCR)")

    try:
        if api_key:
            llm_provider.set_provider_key(provider_id, api_key)

        text = await llm_provider.ocr_extract(image_b64, model)
        return {"text": text}
    except Exception as e:
        raise HTTPException(500, f"OCR extraction failed: {str(e)}")


@app.get("/api/voices")
async def get_voices(lang: str = ""):
    all_voices = await tts_engine.list_all_voices()
    if lang:
        voices = filter_voices(all_voices, lang)
    else:
        voices = [
            {
                "short_name": v["ShortName"],
                "friendly_name": v.get("FriendlyName", v["ShortName"]),
                "gender": v.get("Gender", "Unknown"),
                "locale": v.get("Locale", ""),
                "personalities": v.get("VoiceTag", {}).get("VoicePersonalities", []),
            }
            for v in all_voices
        ]
    return {"voices": voices, "total": len(all_voices)}


@app.post("/api/preview")
async def preview_voice(request: Request):
    body = await request.json()
    voice = body.get("voice", "en-US-EmmaMultilingualNeural")
    rate = body.get("rate", "+0%")
    pitch = body.get("pitch", "+0Hz")
    volume = body.get("volume", "+0%")

    try:
        audio_bytes = await tts_engine.preview_voice(voice, rate, pitch, volume)
        return StreamingResponse(
            iter([audio_bytes]),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=preview.mp3"},
        )
    except Exception as e:
        raise HTTPException(500, f"Preview generation failed: {str(e)}")


@app.post("/api/synthesize")
async def synthesize(request: Request):
    body = await request.json()
    text = body.get("text", "")
    voice = body.get("voice", "en-US-EmmaMultilingualNeural")
    rate = body.get("rate", "+0%")
    pitch = body.get("pitch", "+0Hz")
    volume = body.get("volume", "+0%")

    if not text.strip():
        raise HTTPException(400, "No text to synthesize")

    try:
        audio_bytes = await tts_engine.synthesize(text, voice, rate, pitch, volume)

        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(audio_bytes)

        return {
            "filename": filename,
            "audio_url": f"/api/audio/{filename}",
        }
    except Exception as e:
        raise HTTPException(500, f"Synthesis failed: {str(e)}")


@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(404, "Audio file not found")
    return FileResponse(filepath, media_type="audio/mpeg", filename=filename)


@app.delete("/api/audio/{filename}")
async def delete_audio(filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
