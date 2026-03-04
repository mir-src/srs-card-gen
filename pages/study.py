import streamlit as st
from db.decks import get_deck
from db.cards import get_due_cards, update_card, log_review
from core.engine import router, get_intervals
import time
from db.models import Card, Deck

# DOUBLE BOUNCER
if "active_user_id" not in st.session_state:
    st.switch_page("pages/auth.py")

if "active_deck_id" not in st.session_state:
    st.warning("Please select a deck from the Dashboard first.")
    if st.button("Go to Dashboard"):
        st.switch_page("app.py")
    st.stop() # Stops the rest of the page from rendering and crashing

st.title("Study Session")

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# Fetch the specific deck from the backpack
chosen_deck = get_deck(st.session_state.active_deck_id)

if chosen_deck:
    due_cards = get_due_cards(chosen_deck, chosen_deck.user_id)
    
    if not due_cards:
        st.success("You finished your reviews for the day!")
        if st.button("Back to Dashboard"):
            st.switch_page("app.py")
    else:
        current_card = due_cards[0]

        st.write("Front of the card")
        st.info(current_card.front)
        st.markdown("---")
        start_time = time.perf_counter()

        if st.session_state.show_answer == False:
            if st.button("Show Answer"):
                st.session_state.show_answer = True
                st.rerun()
        else:
            st.write("Back of the card")
            st.info(current_card.back)
            st.markdown("---")

            interval = get_intervals(current_card, chosen_deck)

            original_state = current_card.state

            col1, col2, col3, col4 = st.columns(4)
            col1, col2, col3, col4 = st.columns(4)
            if col1.button(f"Again ({interval[0]})"):
                updated_card = router(current_card, chosen_deck, 1)
                answer_time = time.perf_counter() - start_time
                log_review(card_id=current_card.id, deck_id=chosen_deck.id, user_id=chosen_deck.user_id, response_time=answer_time, rating=1, state_at_review=original_state)
                update_card(updated_card)
                st.session_state.show_answer = False
                st.rerun()
            
            if col2.button(f"Hard ({interval[1]})"):
                updated_card = router(current_card, chosen_deck, 2)
                answer_time = time.perf_counter() - start_time
                log_review(card_id=current_card.id, deck_id=chosen_deck.id, user_id=chosen_deck.user_id, response_time=answer_time, rating=2, state_at_review=original_state)
                update_card(updated_card)
                st.session_state.show_answer = False
                st.rerun()

            if col3.button(f"Good ({interval[2]})"):
                updated_card = router(current_card, chosen_deck, 3)
                answer_time = time.perf_counter() - start_time
                log_review(card_id=current_card.id, deck_id=chosen_deck.id, user_id=chosen_deck.user_id, response_time=answer_time, rating=3, state_at_review=original_state)
                update_card(updated_card)
                st.session_state.show_answer = False
                st.rerun()

            if col4.button(f"Easy ({interval[3]})"):
                updated_card = router(current_card, chosen_deck, 4)
                answer_time = time.perf_counter() - start_time
                log_review(card_id=current_card.id, deck_id=chosen_deck.id, user_id=chosen_deck.user_id, response_time=answer_time, rating=4, state_at_review=original_state)
                update_card(updated_card)
                st.session_state.show_answer = False
                st.rerun()