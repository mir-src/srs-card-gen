import os
import uuid
from gtts import gTTS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

LANG_CODES = {
    "English": "en",
    "Mandarin Chinese": "zh-cn",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "Arabic": "ar",
    "Bengali": "bn",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Punjabi": "pa",
    "German": "de",
    "Javanese": "jv",
    "Wu Chinese": "zh-yue",
    "Marathi": "mr",
    "Telugu": "te",
    "Turkish": "tr",
    "Tamil": "ta",
    "Vietnamese": "vi",
    "Urdu": "ur",
    "Gujarati": "gu",
    "Polish": "pl",
    "Ukrainian": "uk",
    "Kannada": "kn",
    "Thai": "th",
    "Malay": "ms",
    "Burmese": "my",
    "Odia": "or",
    "Filipino": "fil",
    "Romanian": "ro",
    "Italian": "it",
    "Greek": "el",
    "Czech": "cs",
    "Swedish": "sv",
    "Hungarian": "hu",
    "Hebrew": "he",
    "Dutch": "nl",
    "Hausa": "ha",
    "Malagasy": "mg",
    "Somali": "so",
    "Norwegian": "no",
    "Swahili": "sw",
    "Amharic": "am",
    "Yoruba": "yo",
    "Igbo": "ig",
    "Sinhalese": "si",
    "Khmer": "km",
    "Turkmen": "tk",
    "Uyghur": "ug",
    "Zulu": "zu"
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


