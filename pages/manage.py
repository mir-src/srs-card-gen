import streamlit as st
import bcrypt
from db.users import get_user, update_user, delete_user, verify_login, update_password
from db.decks import create_deck, get_decks, update_deck, delete_deck
from db.cards import create_card, get_cards, delete_card, update_card

# THE BOUNCER
if "active_user_id" not in st.session_state:
    st.switch_page("pages/auth.py")

user_id = st.session_state.active_user_id
current_user = get_user(user_id)

if current_user is None:
    st.session_state.clear()
    st.switch_page("pages/auth.py")

st.title("Data Inspector")
st.markdown("---")

tab_profile, tab_decks, tab_cards = st.tabs(["👤 Profile", "📚 Decks", "🗂️ Cards"])

# ==========================================
# TAB 1: USER PROFILE
# ==========================================
with tab_profile:
    st.subheader("Profile Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.form("change_name_form"):
            new_name = st.text_input("Change Username", value=current_user.name)
            if st.form_submit_button("Update Name"):
                update_user(user_id, new_name)
                st.success("Username updated!")
                st.rerun()

    with col2:
        with st.form("change_password_form", clear_on_submit=True):
            old_pass = st.text_input("Current Password", type="password")
            new_pass = st.text_input("New Password", type="password")
            if st.form_submit_button("Update Password"):
                if verify_login(current_user.name, old_pass):
                    if new_pass:
                        # 🔐 HASH THE NEW PASSWORD BEFORE SAVING
                        salt = bcrypt.gensalt()
                        hashed_new = bcrypt.hashpw(new_pass.encode('utf-8'), salt).decode('utf-8')
                        update_password(user_id, hashed_new)
                        st.success("Password updated securely!")
                    else:
                        st.warning("New password cannot be empty.")
                else:
                    st.error("Incorrect current password.")

    st.markdown("---")
    st.subheader("Danger Zone")
    
    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False

    if not st.session_state.confirm_delete:
        if st.button("Delete Account", type="primary"):
            st.session_state.confirm_delete = True
            st.rerun()
    else:
        st.warning("Are you sure you want to delete your account? This cannot be undone.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, Delete Everything", type="primary"):
                delete_user(user_id)
                st.session_state.clear()
                st.switch_page("pages/auth.py")
        with c2:
            if st.button("No, Cancel"):
                st.session_state.confirm_delete = False
                st.rerun()

# ==========================================
# TAB 2: DECKS
# ==========================================
with tab_decks:
    user_decks = get_decks(user_id) or []
    
    with st.expander("➕ Create New Deck"):
        with st.form("create_deck_form", clear_on_submit=True):
            d_name = st.text_input("Deck Name")
            col1, col2 = st.columns(2)
            l_steps = col1.text_input("Learning Steps", value="1m 10m")
            r_steps = col2.text_input("Relearning Steps", value="10m")
            n_lim = col1.number_input("New Cards / Day", value=20, min_value=0)
            r_lim = col2.number_input("Reviews / Day", value=200, min_value=0)
            l_tresh = col1.number_input("Leech Treshold", value=8, min_value=1)
            
            if st.form_submit_button("Create Deck"):
                if d_name:
                    create_deck(user_id, d_name, l_steps, r_steps, n_lim, r_lim, l_tresh)
                    st.success(f"Deck '{d_name}' created!")
                    st.rerun()

    st.subheader("Edit Decks")
    if user_decks:
        edit_deck = st.selectbox("Select a deck to modify", options=user_decks, format_func=lambda d: d.name)
        if edit_deck:
            with st.form(f"edit_deck_{edit_deck.id}"):
                u_name = st.text_input("Name", value=edit_deck.name)
                c1, c2 = st.columns(2)
                u_l_steps = c1.text_input("Learning Steps", value=edit_deck.learning_steps)
                u_r_steps = c2.text_input("Relearning Steps", value=edit_deck.relearning_steps)
                u_n_lim = c1.number_input("New / Day", value=edit_deck.new_per_day)
                u_r_lim = c2.number_input("Reviews / Day", value=edit_deck.reviews_per_day)
                l_tresh = c1.number_input("Leech Threshold", value=8, min_value=1)
                
                if st.form_submit_button("Save Changes"):
                    update_deck(edit_deck.id, u_name, u_l_steps, u_r_steps, u_n_lim, u_r_lim, l_tresh)
                    st.success("Deck updated!")
                    st.rerun()
            
            # The delete button must be outside the form!
            if st.button("Delete Deck", type="primary", key=f"del_deck_{edit_deck.id}"):
                delete_deck(edit_deck.id)
                st.success("Deck deleted!")
                st.rerun()
    else:
        st.info("No decks found.")

# ==========================================
# TAB 3: CARDS
# ==========================================
with tab_cards:
    if user_decks:
        chosen_deck = st.selectbox("Select Deck to Manage Cards", options=user_decks, format_func=lambda d: d.name, key="card_deck_sel")
        
        if chosen_deck:
            with st.expander("➕ Add New Card"):
                with st.form("create_card_form", clear_on_submit=True):
                    c_type = st.selectbox("Card Type", ["basic", "type", "cloze"])
                    front = st.text_area("Front / Cloze Text")
                    back = st.text_area("Back / Extra Notes")
                    
                    if st.form_submit_button("Add Card"):
                        if front:
                            create_card(chosen_deck.id, front, back, audio_front='', audio_back='', card_type=c_type) 
                            st.success("Card added!")
                            st.rerun()
                        else:
                            st.error("Front cannot be empty.")

            st.subheader("🔍 Card Browser (Bulk Edit & Filter)")
            st.caption("Hover over a column header to filter. Select a row and press 'Delete' to remove it.")
            
            all_cards = get_cards(chosen_deck.id) or []
            
            if all_cards:
                # 1. Convert custom objects into a list of dictionaries for the Data Editor
                card_data = []
                for c in all_cards:
                    card_data.append({
                        "id": c.id,
                        "front": c.front,
                        "back": c.back,
                        "state": c.state,
                        "type": c.card_type,
                        "suspended": bool(c.is_suspended)
                    })
                
                # 2. Render the interactive table
                edited_cards = st.data_editor(
                    card_data,
                    column_config={
                        "id": st.column_config.NumberColumn("ID", disabled=True, width="small"),
                        "front": st.column_config.TextColumn("Front"),
                        "back": st.column_config.TextColumn("Back"),
                        "state": st.column_config.TextColumn("State", disabled=True),
                        "type": st.column_config.TextColumn("Type", disabled=True),
                        "suspended": st.column_config.CheckboxColumn("Suspended?")
                    },
                    hide_index=True,
                    use_container_width=True,
                    num_rows="dynamic", # This enables the row deletion feature!
                    key=f"editor_{chosen_deck.id}"
                )
                
                # 3. The Sync Button
                if st.button("💾 Save Database Changes", type="primary"):
                    # Extract the IDs that survived the editor (weren't deleted)
                    remaining_ids = [row["id"] for row in edited_cards if row.get("id") is not None]
                    
                    # Handle Deletions: If an original ID is missing from the editor, delete it
                    for orig_c in all_cards:
                        if orig_c.id not in remaining_ids:
                            delete_card(orig_c.id)
                    
                    # Handle Edits: Update the remaining cards
                    for row in edited_cards:
                        if row.get("id") is not None:
                            # Find the original card object
                            orig_c = next((c for c in all_cards if c.id == row["id"]), None)
                            if orig_c:
                                # Update attributes
                                orig_c.front = row["front"]
                                orig_c.back = row["back"]
                                orig_c.is_suspended = row["suspended"] # Safe because python bool translates to SQL
                                
                                # Send to backend
                                update_card(orig_c)
                                
                    st.success("Database fully synced with editor!")
                    st.rerun()
            else:
                st.info("No cards in this deck yet.")
    else:
        st.info("Create a deck first.")