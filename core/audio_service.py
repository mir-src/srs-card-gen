import os
import uuid
from gtts import gTTS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

LANG_CODES = {
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Romanian": "ro",
    "Italian": "it"
}

def generate_audio(text: str, language: str) -> str | None:
    if not text:
        return None
    
    lang_code = LANG_CODES.get(language, "en")

    filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
    file_path = os.path.join(MEDIA_DIR, filename)

    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save(file_path)
        return file_path
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None


