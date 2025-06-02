import streamlit as st
import os
from app_pages.home import home_page
from app_pages.chat import chat_page
from app_pages.audio_emotion import audio_emotion_detection_page
from app_pages.visual_emotion import visual_emotion_recognition_page
from database import init_db
from auth import register_user, authenticate_user
from streamlit.runtime.scriptrunner import RerunException, RerunData

st.set_page_config(
    page_title="VELORAI",
    page_icon="assets/velorai-high-resolution-logo-removebg-preview.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def safe_rerun():
    try:
        raise RerunException(RerunData(widget_states=None))
    except Exception:
        os._exit(0)

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Home"

def login():
    st.title("Login")

    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        login_btn = st.form_submit_button("Login")
        register_btn = st.form_submit_button("Register")

    if login_btn:
        try:
            if not username or not password:
                st.warning("Please enter both username and password.")
            elif authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.just_logged_in = True
                safe_rerun()
            else:
                st.error("Invalid username or password")
        except Exception as e:
            st.error(f"Error during login: {e}")

    if register_btn:
        try:
            if not username or not password:
                st.warning("Please enter both username and password for registration.")
            elif register_user(username, password):
                st.success("User registered! Please login.")
            else:
                st.error("User already exists.")
        except Exception as e:
            st.error(f"Error during registration: {e}")

def main():
    if not st.session_state.get("logged_in", False):
        login()
        return

    st.sidebar.image("assets/velorai-high-resolution-logo-removebg-preview.png", width=220)

    button_style = """
        <style>
        .sidebar-button {
            width: 100%;
            background-color: blue;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6em 0;
            margin-bottom: 0.5em;
            font-size: 1.1em;
            font-weight: 500;
            transition: background 0.2s;
        }
        .sidebar-button:hover {
            background-color: #356AC3;
            color: #fff;
        }
        </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)

    if st.sidebar.button("Home", key="home_btn", help="Go to Home", use_container_width=True):
        st.session_state.selected_page = "Home"
        safe_rerun()
    if st.sidebar.button("Chat Now", key="chat_btn", help="Chat with Therapist", use_container_width=True):
        st.session_state.selected_page = "Chat with Therapist"
        safe_rerun()
    if st.sidebar.button("Audio Emotion Detection", key="audio_btn", help="Detect emotions from audio", use_container_width=True):
        st.session_state.selected_page = "Real-time Audio Emotion Detection"
        safe_rerun()
    if st.sidebar.button("Visual Emotion Recognition", key="visual_btn", help="Recognize emotions visually", use_container_width=True):
        st.session_state.selected_page = "Visual Emotion Recognition"
        safe_rerun()
    if st.sidebar.button("Emotinal Dependancy Analysis", key="emotional_dependancy_btn", help="Emotional Dependancy Analysis", use_container_width=True):
        st.session_state.selected_page = "Emotional Dependancy Analysis"
        safe_rerun()
    if st.sidebar.button("Logout", key="logout_btn", help="Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.chat_history = []
        safe_rerun()

    page = st.session_state.selected_page

    if page == "Home":
        home_page()
    elif page == "Chat with Therapist":
        chat_page()
    elif page == "Real-time Audio Emotion Detection":
        audio_emotion_detection_page()
    elif page == "Visual Emotion Recognition":
        visual_emotion_recognition_page()
    elif page == "Emotional Dependancy Analysis":
        from app_pages.chat_dependancy import emotional_dependency_analysis_page
        emotional_dependency_analysis_page()
    else:
        st.warning("Page not implemented yet.")

if __name__ == "__main__":
    main()
