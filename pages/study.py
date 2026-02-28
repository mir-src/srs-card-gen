import streamlit as st
from db.cards import get_cards

st.title("Study Session")

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

cards = get_cards(deck_id=1)

if not cards:
    st.info("No cards in this deck yet! Go to the generator to make some.")

elif st.session_state.current_index >= len(cards):
    st.success("You've finished studying all your cards!")
    if st.button("Restart Deck"):
        st.session_state.current_index = 0
        st.rerun()

else:
    current_card = cards[st.session_state.current_index]
    st.markdown("---")
    st.subheader("Front")
    st.title(current_card.front)

    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False

    if not st.session_state.show_answer:
        if st.button("Show Answer", use_container_width=True):
            st.session_state.show_answer = True
            st.rerun()
    
    else:
        st.markdown("---")
        st.subheader("Back")
        st.write(current_card.back)

        st.markdown("---")
        st.write("How well did you know this?")

        col1, col2, col3, col4 = st.columns(4)
        if col1.button("🔴 Again", use_container_width=True):
            st.session_state.show_answer = False
            st.session_state.current_index += 1
            st.rerun()
        if col2.button("🟠 Hard", use_container_width=True):
            st.session_state.show_answer = False
            st.session_state.current_index += 1
            st.rerun()
        if col3.button("🟢 Good", use_container_width=True):
            st.session_state.show_answer = False
            st.session_state.current_index += 1
            st.rerun()
        if col4.button("🔵 Easy", use_container_width=True):
            st.session_state.show_answer = False
            st.session_state.current_index += 1
            st.rerun()

