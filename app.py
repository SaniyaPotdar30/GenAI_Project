import streamlit as st
from utils.user_store import init_session
from loginpage import login_page
from registerpage import register_page
from dashboard import dashboard

st.set_page_config(page_title="Sunbeam GenAI", page_icon="🤖")

init_session()

if st.session_state.logged_in:
    dashboard()
else:
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "register":
        register_page()
    else:
        st.session_state.page = "login"
        st.rerun()
