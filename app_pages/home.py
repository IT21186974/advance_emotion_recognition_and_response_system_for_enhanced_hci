import streamlit as st

def home_page():
    # Center the logo image using Streamlit columns
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.image("assets/velorai-high-resolution-logo-removebg-preview.png", width=160)

    username = st.session_state.get("username", "User")
    st.markdown(f"<h2 style='text-align:center; color:#c4e0e5; font-family:Segoe UI;'>Hello, {username}!</h2>", unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>Welcome to VELORAI</h1>", unsafe_allow_html=True)

    # Description text styling and content
    st.markdown(
        """
        <style>
        .description {
            max-width: 600px;
            margin: 0 auto 40px auto;
            font-size: 18px;
            color: #eee;
            text-align: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.5;
        }
        </style>
        <div class="description">
            VELORAI is your personal AI-powered companion for emotional wellbeing. 
            Explore our tools to detect and analyze emotions in real-time through chat, audio, and video.
        </div>
        <div class="description">
            Start your journey to better mental health with VELORAI today.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        .button-container {
            max-width: 400px;
            margin: 50px auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .btn {
            background: linear-gradient(135deg, #4ca1af, #c4e0e5);
            color: #003349;
            font-weight: 600;
            font-size: 20px;
            padding: 15px 0;
            border-radius: 12px;
            text-align: center;
            cursor: pointer;
            user-select: none;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            border: none;
            width: 100%;
        }
        .btn:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    buttons = [
        "Chat with Therapist",
        "Real-time Audio Emotion Detection",
        "Visual Emotion Recognition",
        "Textual Emotion Recognition",
        "Cognitive Distortion Detection",
        "Emotional Dependancy Analysis",
    ]

    # Container for buttons
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    for idx, label in enumerate(buttons):
        if st.button(label, key=f"home-btn-{idx}", help=f"Go to {label}"):
            st.session_state.selected_page = label
            # Because this is a subpage, rerun handled in main.py
        # Note: Button CSS styling can't be applied directly but CSS is injected globally
    st.markdown('</div>', unsafe_allow_html=True)

    # Extra CSS to style all buttons inside button-container
    st.markdown(
        """
        <style>
        /* Style only buttons inside our container */
        .button-container > button {
            all: unset;
            display: block;
            width: 100%;
            background: linear-gradient(135deg, #4ca1af, #c4e0e5);
            color: #003349;
            font-weight: 600;
            font-size: 20px;
            padding: 15px 0;
            border-radius: 12px;
            text-align: center;
            cursor: pointer;
            user-select: none;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            border: none;
            margin-bottom: 20px;
            align-self: center;
            width: 100%;
        }
        .button-container > button:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
