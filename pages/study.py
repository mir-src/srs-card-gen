import streamlit as st
from db.cards import get_due_cards, update_card
from core.engine import router
from db.decks import get_deck

st.title("Study Session")

deck = get_deck(1)
if not deck:
    st.error("Deck not found!")
    st.stop()

due_cards = get_due_cards(1)

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

if not due_cards:
    st.success("You finished your reviews!")
else:
    current_card = due_cards[0]

    st.write("Front of the card")
    st.info(current_card.front)
    st.markdown("---")

    if st.session_state.show_answer == False:
        if st.button("Show Answer"):
            st.session_state.show_answer = True
            st.rerun()
    else:
        st.write("Back of the card")
        st.info(current_card.back)
        st.markdown("---")

        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Again"):
            updated_card = router(current_card, deck, 1) 
            new_card = update_card(updated_card)
            st.session_state.show_answer = False
            st.rerun()

        if col2.button("Hard"):
            updated_card = router(current_card, deck, 2) 
            new_card = update_card(updated_card)
            st.session_state.show_answer = False
            st.rerun()

        if col3.button("Good"):
            updated_card = router(current_card, deck, 3) 
            new_card = update_card(updated_card)
            st.session_state.show_answer = False
            st.rerun()

        if col4.button("Easy"):
            updated_card = router(current_card, deck, 4) 
            new_card = update_card(updated_card)
            st.session_state.show_answer = False
            st.rerun()
    