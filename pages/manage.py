import streamlit as st
from db.users import create_user, get_users
from db.decks import create_deck

with st.form("Create User"):
    username = st.text_input("Enter the username")
    if st.form_submit_button("Create User"):
        user = create_user(username)
        st.success("User Created!")

all_users = get_users() or []
chosen_user = st.selectbox(label="All Users", options=all_users, format_func=lambda u: u.name)

with st.form("Create Deck"):
    d_name = st.text_input("Enter deck name")
    l_steps = st.text_input("Enter learning steps")
    r_steps = st.text_input("Enter relearning steps")

    if st.form_submit_button("Create Deck"):
        if chosen_user:
            deck = create_deck(chosen_user.id, d_name, l_steps, r_steps)
            st.success("Successfully created a deck!")
        else:
            st.error("Please create a user first!")
            
