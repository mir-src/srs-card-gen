import streamlit as st
from db.core import initialize_database
from db.users import get_users
from db.decks import get_decks
from db.cards import get_due_cards

initialize_database()


all_users = get_users() or []
chosen_user = st.selectbox(label="Select User", options=all_users, format_func=lambda u: u.name)

if chosen_user:
    user_decks = get_decks(chosen_user.id) or []

    if user_decks:
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.markdown("**Deck Name**")
        col2.markdown("**Cards Due**")
        col3.markdown("**Action**")
        st.markdown("---")

        for deck in user_decks:
            due_cards = get_due_cards(deck.id)
            due_count = len(due_cards) if due_cards else 0
            
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(deck.name)
            c2.write(str(due_count))
            
            if c3.button("Study", key=f"study_{deck.id}"):
                st.session_state.active_user_id = chosen_user.id
                st.session_state.active_deck_id = deck.id

                st.switch_page("pages/study.py")
            