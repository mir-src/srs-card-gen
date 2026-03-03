import streamlit as st
from db.users import get_users
from db.decks import get_decks
from db.cards import get_due_cards, update_card
from core.engine import router

st.title("Study Session")

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

all_users = get_users() or []
if all_users:
    chosen_user = st.selectbox(
    label="Select User",
    options=all_users,
    format_func=lambda u: u.name
    )
    if chosen_user:
        all_decks = get_decks(user_id=chosen_user.id) or [] 
        chosen_deck = st.selectbox(
            label="Select a deck",
            options=all_decks,
            format_func=lambda u: u.name
        )
        if chosen_deck:
            due_cards = get_due_cards(chosen_deck.id)
            if not due_cards:
                st.success("You finished your reviews for the day")
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
                        updated_card = router(current_card, chosen_deck, 1)
                        new_card = update_card(updated_card)
                        st.session_state.show_answer = False
                        st.rerun()
                    
                    if col2.button("Hard"):
                        updated_card = router(current_card, chosen_deck, 2)
                        new_card = update_card(updated_card)
                        st.session_state.show_answer = False
                        st.rerun()

                    if col3.button("Good"):
                        updated_card = router(current_card, chosen_deck, 3)
                        new_card = update_card(updated_card)
                        st.session_state.show_answer = False
                        st.rerun()

                    if col4.button("Easy"):
                        updated_card = router(current_card, chosen_deck, 4)
                        new_card = update_card(updated_card)
                        st.session_state.show_answer = False
                        st.rerun() 

                    