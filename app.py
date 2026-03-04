import streamlit as st
from db.core import initialize_database
from db.decks import get_decks
from db.cards import get_due_cards

# 1. Initialize DB
initialize_database()

# 2. THE BOUNCER: If not logged in, kick them to auth.py
if "active_user_id" not in st.session_state:
    st.switch_page("pages/auth.py")

st.title("My Dashboard")

# Logout Button
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.switch_page("pages/auth.py")

# 3. Fetch decks directly using the session state ID
user_decks = get_decks(st.session_state.active_user_id) or []

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
            st.session_state.active_deck_id = deck.id
            st.switch_page("pages/study.py")
else:
    st.info("You don't have any decks yet! Go to the Manage page to create one.")