import ollama
from dotenv import load_dotenv
import os
import json
from deep_translator import GoogleTranslator

load_dotenv()

AI_MODE = os.getenv("AI_MODE", "LOCAL")

def generate_knowledge_back(front_prompt: str, model: str = 'llama3.2') -> str:
    system_prompt_local = """
    You are a professional flashcard creator.
    The user will give you a concept or question.
    Write the back of the flashcard.
    Rules: Keep it under 3 sentences. Be highly accurate. DO NOT include conversational filler. Just the answer. Answer only in English regardless of the language the user asks the question in.
    """

    if AI_MODE == "LOCAL":
        response = ollama.chat(model=model, messages=[
            {'role': 'system', 'content': system_prompt_local},
            {'role': 'user', 'content': front_prompt}
        ])
        return response['message']['content'].strip()
    else:
        # Cloud/Groq version 
        return "Cloud API not yet implemented."

def generate_language_card(target_word: str, language: str, model: str = 'llama3.2') -> dict:
    system_prompt = f"""
    You are a professional {language} teacher.
    Provide a simple, natural example sentence in {language} for the word '{target_word}'.
    
    Return ONLY a JSON object with these keys:
    {{
       "definition": None,
       "example_sentence_foreign": "The sentence in {language} containing '{target_word}'",
       "example_sentence_english": "The translation of the sentence",
       "word_hiragana": "If Japanese, provide hiragana for '{target_word}'. Otherwise null.",
       "sentence_hiragana": "If Japanese, provide hiragana for the example sentence. Otherwise null."
    }}
    """

    if AI_MODE == "LOCAL":
        try:
            response = ollama.chat(model=model, format='json', messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': target_word}
            ])

            card_data = json.loads(response['message']['content'])

            translated_definition = GoogleTranslator(source='auto', target='en').translate(target_word)

            card_data['definition'] = " ".join(translated_definition.split()[:3])

            return card_data
        except json.JSONDecodeError:
            return {"error": "AI failed to generate valid JSON"}
    return {"error": "Cloud mode is not yet implemented"}   
    

