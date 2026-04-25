from groq import Groq
import ollama
from dotenv import load_dotenv
import os
import re
import json
import requests
from deep_translator import GoogleTranslator
from core.audio_service import generate_audio

load_dotenv(override=True)

AI_MODE = os.getenv("AI_MODE")

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)



def generate_knowledge_back(front_prompt: str, ai_mode: str = "REMOTE", local_model: str = 'phi:latest') -> dict:
    system_prompt = f"""
    You are a professional flashcard creator.
    Return ONLY a JSON object with the following keys:
    {{
        "front": "The question/concept provided",
        "back": "The accurate, concise answer (max 3 sentences)"
    }}
    """
    if ai_mode == "LOCAL":
        response = ollama.chat(
            model=local_model,
            format='json',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': front_prompt}
            ]
        )
        content = response.get('message', {}).get('content')
        return json.loads(content) if content else {"error": "Local AI failed"}
    else:
        client = get_groq_client()
        if not client:
            return {"error": "groq api key not found"}

        groq_response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": front_prompt}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        content = groq_response.choices[0].message.content
        return json.loads(content or "{}")

def generate_language_card(
    target_word: str,
    target_translation_language: str,
    language: str,
    ai_mode: str = "REMOTE",
    local_model: str = "phi:latest",
) -> dict:
    # --- Prompt Local & Groq ---
    system_prompt_local = f"""
    You are a professional {language} teacher.
    Provide a simple, natural example sentence in {language} for the word '{target_word}'.
    
    Return ONLY a JSON object with these keys:
    {{
       "target_word": "{target_word}",
       "definition": null,
       "example_sentence_foreign": "The sentence in {language} containing '{target_word}'",
       "example_sentence_english": "The translation of the 'example_sentence_foreign' in english",
    }}
    """

    system_prompt_groq = f"""
    You are a professional {language} translator and teacher.
    Provide the exact definition and a simple, natural example sentence in {language} for the word '{target_word}'.
    
    Return ONLY a JSON object with these exact keys:
    {{
       "target_word": "{target_word}",
       "definition": "The accurate {target_translation_language} translation of '{target_word}' (max 3 words)",
       "example_sentence_foreign": "The sentence in {language} containing '{target_word}'",
       "example_sentence_language": "Translation of {target_word} in {target_translation_language}",
       "word_hiragana": "If Japanese, provide hiragana for '{target_word}'. Otherwise null.",
       "sentence_hiragana": "If Japanese, provide hiragana for 'example_sentence_foreign'. Otherwise null.",
    }}
    """
    # --- Prompt Local & Groq ---

    if ai_mode == "LOCAL":
        try:
            response = ollama.chat(model='phi:latest', format='json', messages=[
                {'role': 'system', 'content': system_prompt_local},
                {'role': 'user', 'content': target_word}
            ])
            card_data = json.loads(response['message']['content'])
      
            translated = GoogleTranslator(source='auto', target='en').translate(target_word)
            card_data['definition'] = " ".join(translated.split()[:3]) if translated else "No definition"
            
            return card_data
        except Exception as e:
            return {"error": f"Ollama failed: {str(e)}"}
    else:
            client = get_groq_client()
            if not client:
                return {"error": "groq api key not found"}

            groq_response = client.chat.completions.create(
            messages=[
                {'role': 'system', 'content': system_prompt_groq},
                {'role': 'user', 'content': target_word}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
    content = groq_response.choices[0].message.content
    return json.loads(content) if content else {"error": "Groq failed"}

def extract_json_array(raw_text: str):
    pattern = r"\[.*\]"

    match = re.search(pattern, raw_text, flags=re.DOTALL)

    if match:
        json_str = match.group(0)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return []
        
    return []

def process_ai_response(ai_data) -> list:
    raw_list = [ai_data] if isinstance(ai_data, dict) else ai_data
    clean_cards = []

    for item in raw_list:
        if item.get('example_sentence_foreign'): 
            word = item.get('target_word') or "" 
            ex_foreign = item.get('example_sentence_foreign', '')
            definition = item.get('definition', '')
            ex_trans = item.get('example_sentence_english') or item.get('example_sentence_language', '')
            
            front = f"{word}\n{ex_foreign}".strip() if word else ex_foreign.strip()
            
            back_parts = [f"Definition: {definition}", f"Translation: {ex_trans}"]
            
            word_hira = item.get('word_hiragana')
            sent_hira = item.get('sentence_hiragana')
            if word_hira and str(word_hira).lower() != 'null':
                back_parts.append(f"Reading: {word_hira}")
            if sent_hira and str(sent_hira).lower() != 'null':
                back_parts.append(f"Sentence Reading: {sent_hira}")
            
            back = "\n".join(back_parts).strip()

        else:
            front = (item.get('question') or item.get('front') or "").strip()
            back = (item.get('answer') or item.get('back') or "").strip()

        if front and back:
            clean_cards.append({
                "front": front,
                "back": back,
                "card_type": "basic"
            })

    return clean_cards



def check_services() -> dict:
    status = {"groq": False, "ollama": False}

    if os.getenv("GROQ_API_KEY"):
        status["groq"] = True
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=1)
        if response.status_code == 200:
            status["ollama"] = True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        status["ollama"] = False

    return status

