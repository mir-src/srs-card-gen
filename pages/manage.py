import streamlit as st
import bcrypt
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import core.ai_service as ai_service
from core.audio_service import generate_audio
import time
from db.users import get_user, update_user, delete_user, verify_login, update_password
from db.decks import create_deck, get_decks, update_deck, delete_deck
from db.cards import create_card, get_cards, delete_card, update_card
from core.ai_service import generate_knowledge_back, generate_language_card, process_ai_response, check_services

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

tab_profile, tab_decks, tab_cards, tab_statistics = st.tabs(["👤 Profile", "📚 Decks", "🗂️ Cards", "📊 Statistics"])

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
                st.write("### 🤖 Generate with AI")

                ai_status = check_services()
                available_sources = []

                if ai_status.get("ollama"):
                    available_sources.append("Ollama AI")
                if ai_status.get("groq"):
                    available_sources.append("Groq AI")

                if not available_sources:
                    st.warning("No AI services detected.")
                else:
                    ai_source = st.radio("AI Source", available_sources, horizontal=True)
                    if "Groq AI" not in ai_source:
                        ai_card_type = st.radio("Card Type", ["Knowledge Card"], horizontal=True)
                    else:    
                        ai_card_type = st.radio("Card Type", ["Knowledge Card", "Language Card"], horizontal=True)

                    with st.form("ai_card_form"):
                        if ai_card_type == "Knowledge Card":
                            ai_prompt = st.text_area("Enter concept/question")
                            target_word = None
                        else:
                            col1, col2 = st.columns(2)
                            target_word = col1.text_input("Target word")
                            target_language_example = col2.text_input("Translation Language", value="English")
                            language = st.text_input("Language", value="Spanish")
                            ai_prompt = None

                        submit_ai = st.form_submit_button("⚡ Generate")

                        if submit_ai:
                            selected_mode = "LOCAL" if ai_source == "Ollama AI" else "REMOTE"

                            if ai_card_type == "Knowledge Card" and not ai_prompt:
                                st.error("Prompt required.")
                            elif ai_card_type == "Language Card" and not target_word:
                                st.error("Target word required.")
                            else:
                                with st.spinner("Generating..."):
                                    try:
                                        if ai_card_type == "Knowledge Card":
                                            ai_raw = generate_knowledge_back(ai_prompt, ai_mode=selected_mode)
                                            cards = process_ai_response(ai_raw)
                                            
                                            if cards:
                                                for card in cards:
                                                    create_card(
                                                        chosen_deck.id,
                                                        card["front"],
                                                        card["back"],
                                                        audio_front='',
                                                        audio_back='',
                                                        card_type="basic"
                                                    )
                                                st.success(f"{len(cards)} card(s) created!")
                                                time.sleep(1)
                                                st.rerun()
                                            else:
                                                st.error("AI returned nothing.")
                                        
                                        else:  # Language Card
                                            ai_raw = generate_language_card(
                                                target_word=target_word,
                                                target_translation_language=target_language_example,
                                                language=language,
                                                ai_mode=selected_mode
                                            )
                                            target_word_audio = generate_audio(target_word, language=language)
                                            target_sentence_audio = generate_audio(ai_raw['example_sentence_foreign'], language=language)
                                            
                                            cards = process_ai_response(ai_raw)
                                            
                                            if cards:
                                                for card in cards:
                                                    create_card(
                                                        chosen_deck.id,
                                                        card["front"],
                                                        card["back"],
                                                        audio_front=target_word_audio,
                                                        audio_back=target_sentence_audio,
                                                        card_type="basic"
                                                    )
                                                st.success(f"{len(cards)} card(s) created!")
                                                time.sleep(1)
                                                st.rerun()
                                            else:
                                                st.error("AI returned nothing.")

                                    except Exception as e:
                                        st.error(f"Error: {e}")

                c_type = st.selectbox("Card Type", ["basic", "type", "cloze", "language"])
                with st.form("create_card_form", clear_on_submit=True):
                    if c_type == 'language':
                        language = st.text_input("Enter language of target word") 
                        word = st.text_input("Enter target word") 
                        sentence = st.text_area("Enter example sentence") 
                        word_meaning = st.text_input("Enter word meaning")
                        sentence_meaning = st.text_area("Enter example sentence meaning") or ""
                        word_hiragana = st.text_input("Hiragana of Japanese word (Optional)") or ""
                        sentence_hiragana = st.text_area("Sentence hiragana (Optional)") or ""

                        if st.form_submit_button("Add Language Card"):
                            card_dict = {
                            "target_word": word,
                            "definition": word_meaning,
                            "example_sentence_foreign": sentence,
                            "example_sentence_language": sentence_meaning,
                            "word_hiragana": word_hiragana,
                            "sentence_hiragana": sentence_hiragana
                            }

                            if card_dict:
                                cards = process_ai_response(card_dict) 

                            if word and sentence and language:
                                word_audio = generate_audio(text = word, language = language)
                                sentence_audio = generate_audio(text = sentence, language = language)

                            if cards and word_audio and sentence_audio:
                                for card in cards: 
                                    create_card(deck_id = chosen_deck.id, front = card["front"], back = card["back"],card_type = 'basic', audio_front = word_audio, audio_back = sentence_audio) 
                                    st.success(f"{len(cards)} Cards added!")
                                    time.sleep(1)
                                    st.rerun()
                            else:    
                                st.error("Adding card failed, a field was empty.")
                    else:
                        front = st.text_area("Front / Cloze Text")
                        back = st.text_area("Back / Extra Notes")
                        if st.form_submit_button("Add Normal Card"):
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

# ==========================================
# TAB 4: STATISTICS
# ==========================================
with tab_statistics:
    if user_decks:
        chosen_deck = st.selectbox("Select Deck for Statistics", options=user_decks, format_func=lambda d: d.name, key="stats_deck_sel")
        
        if chosen_deck:
            all_cards = get_cards(chosen_deck.id) or []
            
            if all_cards:
                # Extract due dates from cards
                due_dates = []
                for card in all_cards:
                    if card.due_date:
                        try:
                            due_date = datetime.fromisoformat(card.due_date) if isinstance(card.due_date, str) else card.due_date
                            due_dates.append(due_date)
                        except:
                            pass
                
                if due_dates:
                    # Create bins for the next 30 days
                    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    date_range = pd.date_range(start=today, periods=30, freq='D')
                    
                    # Count cards due on each day
                    due_counts = []
                    for date in date_range:
                        count = sum(1 for d in due_dates if d.replace(hour=0, minute=0, second=0, microsecond=0) == date)
                        due_counts.append(count)
                    
                    # Create the graph
                    fig, ax = plt.subplots(figsize=(12, 5), facecolor='#0e1117')
                    ax.set_facecolor('#1e1e2e')
                    bars = ax.bar(date_range, due_counts, color='#6366f1', alpha=0.8, edgecolor='#4f46e5', width=0.8)
                    
                    ax.set_xlabel('Date', fontsize=12, color='#cbd5e1')
                    ax.set_ylabel('Cards Due', fontsize=12, color='#cbd5e1')
                    ax.set_title(f'Flashcard Due Dates - {chosen_deck.name}', fontsize=14, fontweight='bold', color='#cbd5e1')
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
                    ax.tick_params(colors='#cbd5e1')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    
                    st.pyplot(fig)
                    
                    # Statistics summary
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Cards", len(all_cards))
                    
                    with col2:
                        due_today = sum(1 for d in due_dates if d.replace(hour=0, minute=0, second=0, microsecond=0) == today)
                        st.metric("Due Today", due_today)
                    
                    with col3:
                        tomorrow = today + timedelta(days=1)
                        due_tomorrow = sum(1 for d in due_dates if d.replace(hour=0, minute=0, second=0, microsecond=0) == tomorrow)
                        st.metric("Due Tomorrow", due_tomorrow)
                    
                    with col4:
                        due_this_week = sum(1 for d in due_dates if today <= d <= today + timedelta(days=7))
                        st.metric("Due This Week", due_this_week)
                    
                    # Card state breakdown
                    st.markdown("---")
                    st.subheader("Card States")
                    
                    state_counts = {}
                    for card in all_cards:
                        state = card.state or "unknown"
                        state_counts[state] = state_counts.get(state, 0) + 1
                    
                    col1, col2, col3, col4 = st.columns(4)
                    states = ['new', 'learning', 'review', 'relearning']
                    cols = [col1, col2, col3, col4]
                    
                    for state, col in zip(states, cols):
                        with col:
                            count = state_counts.get(state, 0)
                            st.metric(state.capitalize(), count)
                else:
                    st.info("No cards with due dates yet.")
            else:
                st.info("No cards in this deck.")
    else:
        st.info("Create a deck first.")

