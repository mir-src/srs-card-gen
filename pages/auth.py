import streamlit as st
from db.users import verify_login, create_user

st.title("Memora")

# Create two tabs for a clean UI
tab1, tab2 = st.tabs(["Login", "Sign Up"])

# --- LOGIN TAB ---
with tab1:
    st.subheader("Login to your account")
    with st.form("login_form", clear_on_submit=True):
        login_username = st.text_input("Username")
        login_password = st.text_input("Password", type="password") 
        
        if st.form_submit_button("Login"):
            if login_username and login_password:
                user = verify_login(login_username, login_password)
                
                if user:
                    st.session_state.active_user_id = user.id
                    st.success("Login successful! Redirecting...")
                    st.switch_page("app.py")
                else:
                    st.error("Invalid username or password.")
            else:
                st.warning("Please fill out both fields.")

# --- SIGN UP TAB ---
with tab2:
    st.subheader("Create a new account")
    with st.form("signup_form", clear_on_submit=True):
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.form_submit_button("Sign Up"):
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    try:
                        # 1. Ask the backend to hash and save
                        create_user(new_username, new_password)
                        st.success("Account created! Please switch to the Login tab.")
                    except Exception as e:
                        # If the username column has a UNIQUE constraint, it will fail safely here
                        st.error("Username already exists or database error occurred.")
                else:
                    st.error("Passwords do not match.")
            else:
                st.warning("Please fill out all fields.")