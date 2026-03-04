import streamlit as st
from db.users import get_users
from db.decks import get_deck
from db.cards import get_due_cards, update_card
from core.engine import router, get_intervals

st.title("Study Session")

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

if "active_deck_id" not in st.session_state:
    st.warning("Please select a deck from the Dashboard first.")
    if st.button("Go to Dashboard"):
        st.switch_page("app.py")
else:
    chosen_deck = get_deck(st.session_state.active_deck_id)
    if chosen_deck:
        due_cards = get_due_cards(chosen_deck.id)

        if not due_cards:
            st.success("You finished your reviews for the day")
            if st.button("Go to Dashboard"):
                st.switch_page("app.py")
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

                interval = get_intervals(current_card, chosen_deck)

                col1, col2, col3, col4 = st.columns(4)
                if col1.button(f"Again ({interval[0]})"):
                    updated_card = router(current_card, chosen_deck, 1)
                    new_card = update_card(updated_card)
                    st.session_state.show_answer = False
                    st.rerun()
                
                if col2.button(f"Hard ({interval[1]})"):
                    updated_card = router(current_card, chosen_deck, 2)
                    new_card = update_card(updated_card)
                    st.session_state.show_answer = False
                    st.rerun()

                if col3.button(f"Good ({interval[2]})"):
                    updated_card = router(current_card, chosen_deck, 3)
                    new_card = update_card(updated_card)
                    st.session_state.show_answer = False
                    st.rerun()
                
                if col4.button(f"Easy ({interval[3]})"):
                    updated_card = router(current_card, chosen_deck, 4)
                    new_card = update_card(updated_card)
                    st.session_state.show_answer = False
                    st.rerun()

    