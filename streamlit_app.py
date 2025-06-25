import streamlit as st

from supabase import create_client, Client
from dotenv import load_dotenv
import os


import pickle
from pathlib import Path
import streamlit_authenticator as stauth

import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

# ---- USER AUTHENTICATION ----------

#credits: https://github.com/turtlecode/How-to-Add-Authentication-to-Your-Python-App-Supabase-Streamlit-Tutorial/blob/main/app.py

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def sign_up(email, password):
    try:
        user = supabase.auth.sign_up({"email": email, "password": password})
        return user
    except Exception as e:
        st.error(f"Registration failed: {e}")

def sign_in(email, password):
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return user
    except Exception as e:
        st.error(f"Login failed: {e}")

def sign_out():
    try:
        supabase.auth.sign_out()
        st.session_state.user_email = None
        # Force a full browser reload
        st.markdown("""
            <meta http-equiv="refresh" content="0">
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Logout failed: {e}")

def main_app(user_email):
    st.success(f"Welcome, {user_email}! 👋")

    # ---- Pages Setup ----
    main_page = st.Page(
        page="views/main.py",
        title="Home Page",
        icon="🏠",
        default=True
    )

    fidebot_page = st.Page(
        page="views/FideBot.py",
        title="FideBot",
        icon="🤖",
    )

    note_page = st.Page(
        page="views/notes.py",
        title="As tuas Notas",
        icon="📋",
    )

    suggestions_page = st.Page(
        page="views/suggestions.py",
        title="Sugestões",
        icon="📩",
    )

    # --- Sidebar content (only for logged in users) ---
    with st.sidebar:
        st.logo("assets/logo.png", size="large")
        st.text("Made by Group P for Business Cases with Data Science course from NOVA IMS")
        st.markdown("### Acesso alternativo ao FideBot (Playground do Langflow)")
        st.markdown("[Abrir FideBot Playground 🚀](https://astra.datastax.com/langflow/2d0754d9-5a56-4019-a8ff-4d3a185fc195/playground/4bfc1d6b-10d1-4434-b59c-c7428d33e41a)")

        # Push logout button to bottom using custom CSS
        st.markdown(
            """
            <style>
                div[data-testid="stSidebar"] > div:first-child {
                    display: flex;
                    flex-direction: column;
                    height: 100%;
                }
                div[data-testid="stSidebar"] button {
                    margin-top: auto;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        if st.button("Logout"):
            sign_out()

    # --- Navigation ---
    pg = st.navigation(
        {
            "Home": [main_page],
            "Para ti": [fidebot_page, note_page, suggestions_page],
        }
    )

    pg.run()

def auth_screen():
    # Set background image
    bg_img = get_base64_image("assets/aseguradoras-fidelidade 1.png")
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{bg_img}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Login form
    st.title("🔐 FideBot App")
    option = st.selectbox("Choose an action:", ["Login", "Sign Up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Sign Up" and st.button("Register"):
        user = sign_up(email, password)
        if user and user.user:
            st.success("Registration successful. Please log in.")

    if option == "Login" and st.button("Login"):
        user = sign_in(email, password)
        if user and user.user:
            st.session_state.user_email = user.user.email
            st.success(f"Welcome back, {email}!")
            st.rerun()


if "user_email" not in st.session_state:
    st.session_state.user_email = None

if st.session_state.user_email:
    main_app(st.session_state.user_email)
else:
    auth_screen()
