import streamlit as st
import time
from utils.user_store import validate_user

def login_page():
    st.markdown("## 🤖 Sunbeam GenAI Assistant")
    st.caption("Your personal AI learning companion")

    # ---- center layout ----
    left, center, right = st.columns([1,2,1])
    with center:

        with st.container():
            st.markdown("### 🔐 Login")

            if "redirect_at" not in st.session_state:
                st.session_state.redirect_at = None

            with st.form("login_form"):
                username = st.text_input("Username")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                login = st.form_submit_button("Login")

            if login:
                if validate_user(username, email, password):
                    st.toast("Login successful!", icon="🎉")
                    st.session_state.username = username
                    st.session_state.redirect_at = time.time() + 2
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")

            if st.session_state.redirect_at:
                st.success("Heyy you successfully logged in ...")
                time.sleep(2)
                st.session_state.logged_in = True
                st.session_state.page = "dashboard"
                st.session_state.redirect_at = None
                st.rerun()

            st.divider()

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📝 Register"):
                    st.session_state.page = "register"
                    st.rerun()
            with col2:
                st.info("New user? Register here.")
