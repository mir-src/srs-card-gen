import streamlit as st
from db.users import create_user, get_users
from db.decks import create_deck, get_decks
from db.cards import create_card

with st.form("Create User", clear_on_submit=True):
    username = st.text_input("Enter the username")
    if st.form_submit_button("Create User"):
        user = create_user(username)
        st.success("User Created!")

all_users = get_users() or []
chosen_user = st.selectbox(label="All Users", options=all_users, format_func=lambda u: u.name)

with st.form("Create Deck", clear_on_submit=True):
    d_name = st.text_input("Enter deck name")
    l_steps = st.text_input("Enter learning steps")
    r_steps = st.text_input("Enter relearning steps")

    if st.form_submit_button("Create Deck"):
        if chosen_user:
            deck = create_deck(chosen_user.id, d_name, l_steps, r_steps)
            st.success("Successfully created a deck!")
        else:
            st.error("Please create a user first!")
            
st.markdown("---")
st.subheader("Create a Flashcard")

if chosen_user:
    user_decks = get_decks(chosen_user.id)
    if user_decks:
        chosen_deck = st.selectbox(
            label="Choose a deck",
            options=user_decks,
            format_func=lambda u: u.name
        )
    else: 
        st.info("You need to make a deck first.")
    with st.form("create_card", clear_on_submit=True):
        if user_decks:
            front = st.text_area("Front")
            back = st.text_area("Back")
            if st.form_submit_button("Create Card"):
                if chosen_deck and front and back:
                    card = create_card(chosen_deck.id, front, back, card_type='basic', state='new') 
                    st.success("You successfully created a flashcard")
else:
    st.info("Create a user and a deck to start adding flashcards.")