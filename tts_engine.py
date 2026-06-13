import io
import edge_tts

# edge_tts parameter formats:
#   rate:   "+0%", "-30%", "+50%"    (regex: ^[+-]\d+%$)
#   pitch:  "+0Hz", "-20Hz", "+30Hz" (regex: ^[+-]\d+Hz$)
#   volume: "+0%", "-50%", "+100%"   (regex: ^[+-]\d+%$)


async def list_all_voices():
    """Return all available edge_tts voices."""
    return await edge_tts.list_voices()


async def synthesize(text: str, voice: str, rate: str, pitch: str, volume: str) -> bytes:
    """Generate MP3 audio from text. Returns audio bytes."""
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume=volume,
    )

    audio_buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])

    audio_buffer.seek(0)
    return audio_buffer.read()


async def preview_voice(voice: str, rate: str, pitch: str, volume: str) -> bytes:
    """Generate a short preview sample."""
    text = "This is a preview of the selected voice. The quick brown fox jumps over the lazy dog."
    return await synthesize(text, voice, rate, pitch, volume)
