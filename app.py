import streamlit as st
import os
from dotenv import load_dotenv
from db.cards import create_card, delete_card, update_card, get_card, get_cards
from db.users import create_user, delete_user, update_user, get_user, get_users
from db.decks import create_deck, delete_deck, update_deck, get_deck, get_decks
from db.media import create_media
from db.core import DatabaseWriteError, initialize_database
from core.ai_service import generate_knowledge_back, generate_language_card
from core.audio_service import generate_audio

load_dotenv(override=True)
AI_MODE = os.getenv("AI_MODE")

initialize_database()

def get_active_deck_id() -> int:
    users = get_users()
    if not users:
        user_id = create_user("Default User")
        if user_id is None:
            raise RuntimeError("Database failed to create a default user.")
    else:
        user_id = users[0].id
    
    decks = get_decks(user_id)
    if not decks:
        deck_id = create_deck(user_id=user_id, name="Language Learning Deck")
        if deck_id is None:
            raise RuntimeError("Database failed to create a default deck.")
    else:
        deck_id = decks[0].id
    return deck_id

st.title("AI Flashcard Generator")

mode = st.radio("Choose Generator Mode:", ["General Knowledge", "Language Learning", "Manual Mode"])

if mode == "General Knowledge":
    st.subheader("Generate A Knowledge Card")
    front_text = st.text_input(
        "Front of card (e.g., 'What is mitochondria?')"
    )
    if st.button("Generate & Save"):
        if front_text:
            with st.spinner("The local model is thinking..."):
                back_text = generate_knowledge_back(front_text)
                st.success("Generated!")
                st.info(f"**Back:** {back_text}")
        else:
            st.warning("Please enter a prompt first.")

elif mode == "Language Learning":
    st.subheader("Generate a Language Card")

    target_word = st.text_input("Enter Foreign Word...")
    
    if AI_MODE == "LOCAL":
        language = st.selectbox("Language", ["Spanish", "French", "German"])
        st.warning("⚙️ Using Local Mode (Llama 3.2 3B). Languages Limited.")
        spinner_text = "Local model is thinking..."
    else:
        language = st.selectbox("Language", ["Spanish", "French", "German", "Japanese", "Romanian", "Italian"])
        st.success("☁️ Using Cloud Mode (Groq 70B). Full access granted!")
        spinner_text = "Groq 70B is translating..."

    if st.button("Generate Language Flashcard!"):
        if target_word and language:
            with st.spinner(spinner_text):
                card_data = generate_language_card(target_word=target_word, language=language)
                

                st.markdown("### Audio Pronunciation")
                with st.spinner("Generating audio..."):
                    audio_path_word = generate_audio(target_word, language)
                    audio_path_sentence = generate_audio(card_data['example_sentence_foreign'], language)
                    if audio_path_sentence and audio_path_word:
                        st.audio(audio_path_word, format="audio/mp3")
                        st.audio(audio_path_sentence, format="audio/mp3")

                        front_text = target_word
                        back_text = f"Definition: {card_data['definition']}\n\nExample: {card_data['example_sentence_foreign']}\nTranslation: {card_data['example_sentence_english']}"
                        try:
                            active_deck_id = get_active_deck_id()

                            card_id = create_card(deck_id=active_deck_id, front=front_text, back=back_text)

                            if card_id:
                                create_media(card_id=card_id, media_type='audio', path=audio_path_word)
                                create_media(card_id=card_id, media_type='audio', path=audio_path_sentence)
                                st.success(f"💾 Flashcard and audio saved successfully! (Card #{card_id} in Deck #{active_deck_id})")
                            else:
                                st.warning("Flashcard wasn't saved successfully.")
                        except Exception as e:
                            st.error(f"Failed to save to database: {e}")
        else:
            st.warning("Please enter a prompt first.")

elif mode == "Manual Mode":
    with st.form("manual_card_form", clear_on_submit=True):
        st.subheader("Manual Entry")
        front = st.text_input("Front of card")
        back = st.text_area("Back of card")

        submitted = st.form_submit_button("Save Flashcard")
        if submitted:
            if front and back:
                card_id = create_card(deck_id=1, front=front, back=back)
                st.success(f"Card #{card_id} saved!")
            else:
                st.error("Both sides are required.")

