import streamlit as st 
from utils.user_store import add_user, user_exists

def register_page():
    st.title("📝 Register")

    with st.form("register_form"):
        username =  st.text_input("Choose Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Register")

    if submit:
        if not username or not email or not password:
            st.warning("⚠️ All fields are required")

        elif password != confirm:
            st.error("❌ Passwords do not match")

        elif user_exists(username, email):
            st.error("❌ Username or Email already exists")
        
        else:
            add_user(username, email, password)
            st.success("✅ Registration successful")
            st.session_state.page = "login"
            st.rerun()

    if st.button("⬅️ Back"):
        st.session_state.page = "login"
        st.rerun()    
