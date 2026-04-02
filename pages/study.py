import streamlit as st
import re
from db.decks import get_deck
from db.cards import get_due_cards, update_card, log_review
from core.engine import router, get_intervals
import time
from db.models import Card, Deck
from core.parsers import render_cloze_back, render_cloze_front, check_type_answer

if "active_user_id" not in st.session_state:
    st.switch_page("pages/auth.py")

if "active_deck_id" not in st.session_state:
    st.warning("Please select a deck from the Dashboard first.")
    if st.button("Go to Dashboard"):
        st.switch_page("app.py")
    st.stop()

def submit_guess():
    st.session_state.saved_guess = st.session_state.user_guess
    st.session_state.show_answer = True

def render_language_front(front_text: str):
                parts = front_text.split("\n")
                if len(parts) >= 2:
                    word = parts[0]
                    sentence = parts[1]

                    st.markdown(f"""
                    <div style='text-align:center; font-size:28px; font-weight:bold; margin-bottom:10px;'>
                        {word}
                    </div>
                    <div style='text-align:center; font-size:20px; opacity:0.8;'>
                        {sentence}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info(front_text)

def render_language_back(back_text: str):
    lines = [line.strip() for line in back_text.split("\n") if line.strip()]

    def clean(line, prefix):
        return line.replace(prefix, "").strip() if line.startswith(prefix) else line

    definition = clean(lines[0], "Definition:") if len(lines) > 0 else ""
    translation = clean(lines[1], "Translation:") if len(lines) > 1 else ""
    reading = clean(lines[2], "Reading:") if len(lines) > 2 else ""
    sentence_reading = clean(lines[3], "Sentence Reading:") if len(lines) > 3 else ""

    html = f"""<div style="text-align:center;padding:20px;background-color:#1e1e2e;border-radius:12px;margin-bottom:20px;">
<div style="font-size:26px;font-weight:bold;margin-bottom:10px;color:white;">{definition}</div>
<div style="font-size:18px;margin-bottom:15px;color:#cbd5e1;">{translation}</div>
<hr style="border:1px solid #444;margin:15px 0;">
<div style="font-size:18px;color:#a1a1aa;">{reading}</div>
<div style="font-size:18px;color:#71717a;margin-top:5px;">{sentence_reading}</div>
</div>"""
    
    return html

def strip_html(text: str) -> str:
    return re.sub(r"<.*?>", "", text)

st.title("Study Session")

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

chosen_deck = get_deck(st.session_state.active_deck_id)

if chosen_deck:
    due_cards = get_due_cards(chosen_deck, chosen_deck.user_id)
    
    if not due_cards:
        st.success("You finished your reviews for the day!")
        if st.button("Back to Dashboard"):
            st.switch_page("app.py")
    else:
        current_card = due_cards[0]

        # === FRONT RENDERING ===
        if current_card.card_type == 'cloze':
            safe_front = render_cloze_front(current_card.front)
            st.markdown(f"<div style='text-align: center; font-size: 1.5rem; padding: 20px; background-color: #1e1e2e; border-radius: 12px; margin-bottom: 20px;'>{safe_front}</div>", unsafe_allow_html=True)

        if current_card.card_type == 'type' and not st.session_state.show_answer:
            st.text_input("Type your answer here (Press Enter to flip):", key="user_guess", on_change=submit_guess)
        
        if current_card.card_type == 'basic':
            render_language_front(current_card.front)

        st.markdown("---")
        start_time = time.perf_counter()

        if st.session_state.show_answer == False:
            if st.button("Show Answer"):
                if "user_guess" in st.session_state:
                    st.session_state.saved_guess = st.session_state.user_guess
                st.session_state.show_answer = True
                st.rerun()
        else:
            # === BACK RENDERING ===
            if current_card.card_type == 'cloze':
                safe_back = render_cloze_back(current_card.front)
                st.markdown(f"<div style='text-align: center; font-size: 1.5rem; padding: 20px; background-color: #1e1e2e; border-radius: 12px; margin-bottom: 20px;'>{safe_back}</div>", unsafe_allow_html=True)
                if current_card.back:
                    st.info(current_card.back)

            elif current_card.card_type == 'type':
                user_guess = st.session_state.get("saved_guess", "")
                diff_html = check_type_answer(current_card.back, user_guess)
                st.markdown(f"<div style='text-align: center; font-size: 1.5rem; padding: 20px; background-color: #1e1e2e; border-radius: 12px; margin-bottom: 20px; letter-spacing: 2px;'>{diff_html}</div>", unsafe_allow_html=True)

            else:
                with st.container():
                    html = render_language_back(current_card.back)
                    st.markdown(html, unsafe_allow_html=True)
            
            # === FEEDBACK BUTTONS ===
            st.markdown("---")

            interval = get_intervals(current_card, chosen_deck)
            original_state = current_card.state

            col1, col2, col3, col4 = st.columns(4)
            
            if col1.button(f"Again ({interval[0]})", key=f"again_btn_{current_card.id}"):
                updated_card = router(current_card, chosen_deck, 1)
                log_review(card_id=current_card.id, deck_id=chosen_deck.id, user_id=chosen_deck.user_id, response_time=time.perf_counter() - start_time, rating=1, state_at_review=original_state)
                update_card(updated_card)
                st.session_state.show_answer = False
                if "saved_guess" in st.session_state: del st.session_state["saved_guess"]
                st.rerun()
            
            if col2.button(f"Hard ({interval[1]})",key=f"hard_btn_{current_card.id}"):
                updated_card = router(current_card, chosen_deck, 2)
                log_review(card_id=current_card.id, deck_id=chosen_deck.id, user_id=chosen_deck.user_id, response_time=time.perf_counter() - start_time, rating=2, state_at_review=original_state)
                update_card(updated_card)
                st.session_state.show_answer = False
                if "saved_guess" in st.session_state: del st.session_state["saved_guess"]
                st.rerun()

            if col3.button(f"Good ({interval[2]})", key=f"good_btn_{current_card.id}"):
                updated_card = router(current_card, chosen_deck, 3)
                log_review(card_id=current_card.id, deck_id=chosen_deck.id, user_id=chosen_deck.user_id, response_time=time.perf_counter() - start_time, rating=3, state_at_review=original_state)
                update_card(updated_card)
                st.session_state.show_answer = False
                if "saved_guess" in st.session_state: del st.session_state["saved_guess"]
                st.rerun()

            if col4.button(f"Easy ({interval[3]})", key=f"easy_btn_{current_card.id}"):
                updated_card = router(current_card, chosen_deck, 4)
                log_review(card_id=current_card.id, deck_id=chosen_deck.id, user_id=chosen_deck.user_id, response_time=time.perf_counter() - start_time, rating=4, state_at_review=original_state)
                update_card(updated_card)
                st.session_state.show_answer = False
                if "saved_guess" in st.session_state: del st.session_state["saved_guess"]
                st.rerun()