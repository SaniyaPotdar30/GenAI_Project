import pandas as pd
import os
import streamlit as st

DATA_DIR = "data"
USERS_FILE = "users.csv"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["username", "email", "password"]).to_csv(USERS_FILE, index=False)

def load_users():
    return pd.read_csv(USERS_FILE)

def user_exists(username, email):
    users = load_users()
    return not users[
        (users["username"] == username) |
        (users["email"] == email)
    ].empty

def add_user(username, email, password):
    users = load_users()
    users.loc[len(users)] = [username, email, password]
    users.to_csv(USERS_FILE, index=False)

def validate_user(username, email, password):
    users = load_users()
    return not users[
        (users["username"] == username) &
        (users["email"] == email) &
        (users["password"] == password)
    ].empty


def init_session():
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""


