from langdetect import detect, DetectorFactory

# Make langdetect deterministic
DetectorFactory.seed = 0

# Language code → display name
LANGUAGE_NAMES = {
    "en": "English", "sq": "Albanian", "de": "German", "fr": "French",
    "es": "Spanish", "it": "Italian", "pt": "Portuguese", "nl": "Dutch",
    "pl": "Polish", "ru": "Russian", "tr": "Turkish", "ar": "Arabic",
    "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "hi": "Hindi",
    "bg": "Bulgarian", "cs": "Czech", "da": "Danish", "el": "Greek",
    "et": "Estonian", "fi": "Finnish", "hu": "Hungarian", "id": "Indonesian",
    "lv": "Latvian", "lt": "Lithuanian", "nb": "Norwegian", "ro": "Romanian",
    "sk": "Slovak", "sl": "Slovenian", "sv": "Swedish", "th": "Thai",
    "uk": "Ukrainian", "vi": "Vietnamese",
}


def detect_language(text: str) -> str:
    """Detect language of text. Returns ISO 639-1 code (e.g. 'en', 'sq')."""
    try:
        sample = text[:2000]
        lang = detect(sample)
        return lang
    except Exception:
        return "en"


def get_language_name(code: str) -> str:
    """Get display name for a language code."""
    return LANGUAGE_NAMES.get(code, code)


def filter_voices(voices: list, lang_code: str) -> list:
    """Filter voices matching the detected language code."""
    matched = []
    for v in voices:
        locale = v.get("Locale", "")
        base_lang = locale.split("-")[0] if "-" in locale else locale
        if base_lang == lang_code:
            matched.append({
                "short_name": v["ShortName"],
                "friendly_name": v.get("FriendlyName", v["ShortName"]),
                "gender": v.get("Gender", "Unknown"),
                "locale": locale,
                "personalities": v.get("VoiceTag", {}).get("VoicePersonalities", []),
            })

    matched.sort(key=lambda x: (x["gender"], x["friendly_name"]))
    return matched
