import streamlit as st
from db.cards import create_card
from db.core import DatabaseWriteError, initialize_database
from core.ai_service import generate_knowledge_back, generate_language_card

@st.cache_resource
def startup_logic():
    initialize_database()
    return True

startup_logic()

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
    language = st.selectbox("Language", ["Spanish", "French", "German"])
    st.write("Using Local Mode. Options Limited!")

    if st.button("Generate Language Flashcard!"):
        if target_word and language:
            with st.spinner(f"Translating and explaining using Llama 3.2..."):
                card_data = generate_language_card(target_word=target_word, language=language)

                if "error" in card_data:
                    st.error(card_data["error"])
                else:
                    st.success("Generated!")

                    st.markdown(f"### Front")
                    st.info(f"**Word:** {target_word}")
                    st.info(f"**Example:** {card_data['example_sentence_foreign']}")

                    st.markdown(f"### Back")
                    st.info(f"Target Word Definition: {card_data['definition']}")
                    st.info(f"Example sentence translation: {card_data['example_sentence_english']}")
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

