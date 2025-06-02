import datetime
import streamlit as st
from database import save_message, get_messages
from ml_utils import detect_cognitive_distortion, detect_emotion, generate_response
from streamlit.runtime.scriptrunner import RerunException, RerunData
import os
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
import requests
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from ml_utils import unify_emotions_weighted
from ml_utils import map_to_common_emotion, unify_emotions_weighted


def safe_rerun():
    try:
        raise RerunException(RerunData(widget_states=None))
    except Exception:
        os._exit(0)

def load_chat(username):
    try:
        msgs = get_messages(username)
        st.session_state.chat_history = [{"sender": m.sender, "text": m.text} for m in msgs]
    except Exception as e:
        st.error(f"Error loading chat messages: {e}")
        st.session_state.chat_history = []


def plot_emotion_timeline(emotions):
    if not emotions:
        st.info("No emotions to plot yet.")
        return

    df = pd.DataFrame(emotions)
    df = df.sort_values('timestamp')

    # Ordered from positive to negative emotions
    emotion_order = [
        'sadness', 'grief', 'disappointment', 'remorse', 'disgust', 'disapproval', 'anger', 'annoyance',
        'embarrassment', 'fear', 'nervousness', 'confusion', 'neutral', 'realization', 'surprise', 'desire',
        'curiosity', 'caring', 'approval', 'admiration', 'excitement', 'amusement', 'relief', 'pride',
        'optimism', 'gratitude', 'love', 'joy'
    ]

    # Normalize and map emotions to index
    df['emotion_norm'] = df['emotion'].str.strip().str.lower()
    df = df[df['emotion_norm'].isin(emotion_order)]
    if df.empty:
        st.info("No valid emotions to plot.")
        return

    df['emotion_code'] = df['emotion_norm'].apply(lambda e: emotion_order.index(e))

    df['timestamp_mpl'] = pd.to_datetime(df['timestamp'])
    df['timestamp_mpl'] = df['timestamp_mpl'].apply(mdates.date2num)

    fig, ax = plt.subplots(figsize=(12, 5))

    # Plot continuous line over time
    ax.plot(df['timestamp_mpl'], df['emotion_code'], marker='o', linestyle='-', color='tab:blue')

    ax.set_yticks(range(len(emotion_order)))
    ax.set_yticklabels([e.capitalize() for e in emotion_order])
    ax.set_xlabel("Time")
    ax.set_title("Text Emotion Change Over Chat Session")

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate()

    ax.grid(True, axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    st.pyplot(fig)

def plot_distortion_timeline(emotions):
    df = pd.DataFrame(emotions)
    df = df.sort_values('timestamp')

    # Ensure 'distortion' column exists; fill missing with None
    if 'distortion' not in df.columns:
        df['distortion'] = None

    df = df[df['distortion'].notnull()]
    
    if df.empty:
        st.info("No cognitive distortions detected yet.")
        return

    distortions = df['distortion'].unique().tolist()
    distortion_map = {d: i for i, d in enumerate(distortions)}

    df['distortion_code'] = df['distortion'].map(distortion_map)

    df['timestamp_mpl'] = pd.to_datetime(df['timestamp'])
    df['timestamp_mpl'] = df['timestamp_mpl'].apply(mdates.date2num)

    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(df['timestamp_mpl'], df['distortion_code'], marker='o', linestyle='-', color='tab:red')

    ax.set_yticks(range(len(distortions)))
    ax.set_yticklabels(distortions)
    ax.set_xlabel("Time")
    ax.set_title("Cognitive Distortion Detection Over Time")

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate()

    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    st.pyplot(fig)

def fetch_latest_audio_emotion():
    try:
        response = requests.get("http://localhost:8000/latest-audio-emotion", timeout=2)
        data = response.json()
        # Example API returns {"emotion": "happy", "intensity": 75.0}
        return data.get("emotion", "Audio Emotion Detection is not running"), data.get("intensity", 0.0)
    except Exception as e:
        st.error(f"Could not fetch latest audio emotion: {e}")
        return "neutral", 0.0


def fetch_latest_visual_emotion():
    try:
        response = requests.get("http://localhost:8001/latest-visual-emotion", timeout=2)
        data = response.json()
        return data.get("emotion", "Visual Emotion Detection is not running"), data.get("valence", 0.0), data.get("arousal", 0.0)
    except Exception as e:
        st.error(f"Could not fetch latest visual emotion: {e}")
        return "Neutral", 0.0, 0.0


def chat_page():
    if "detected_emotions" not in st.session_state:
        st.session_state.detected_emotions = []

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.session_state.chat_history == [] and st.session_state.get("username"):
        load_chat(st.session_state.username)

    if "fused_emotion" not in st.session_state:
        st.session_state.fused_emotion = "None"


    st.markdown("""
        <style>
        .stApp {
            background-image: url("https://media.istockphoto.com/id/2205967828/photo/abstract-blue-swirl-technology-background.jpg?s=612x612&w=0&k=20&c=uHDXiXevV5jPP2I-tza0ccl3s2oAqvSCGmKWE0hdpCU=");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        #chat-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid rgba(255, 255, 255, 0.6);
            padding: 15px;
            background-color: rgba(0, 0, 0, 0.7);
            border-radius: 10px;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
        }
        .chat-message {
            max-width: 70%;
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 20px;
            line-height: 1.3;
            word-wrap: break-word;
            clear: both;
            position: relative;
        }
        .bot {
            background: linear-gradient(135deg, #6ba8ff, #a3c1ff);
            color: black;
            align-self: flex-start;
            border-bottom-left-radius: 0;
            box-shadow: 0 0 5px #3b82f6;
        }
        .user {
            background: linear-gradient(135deg, #43cea2, #185a9d);
            color: black;
            align-self: flex-end;
            border-bottom-right-radius: 0;
            box-shadow: 0 0 5px #10b981;
        }
        </style>
    """, unsafe_allow_html=True)

    chat_html = '<div id="chat-container">'
    for msg in st.session_state.chat_history:
        cls = "bot" if msg["sender"] == "bot" else "user"
        chat_html += f'<div class="chat-message {cls}">{msg["text"]}</div>'
    chat_html += '</div>'

    st.markdown(chat_html, unsafe_allow_html=True)

    # Scroll to bottom with JS
    st.markdown("""
        <script>
        var chatDiv = document.getElementById('chat-container');
        if (chatDiv) {
            chatDiv.scrollTop = chatDiv.scrollHeight;
        }
        </script>
    """, unsafe_allow_html=True)

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Your message:")
        submit = st.form_submit_button("Send")

        if submit:
            if user_input.strip() == "":
                st.warning("Please enter a message.")
            else:
                try:
                    # Fetch latest audio emotion from your background API service
                    audio_emotion, audio_intensity = fetch_latest_audio_emotion()

                    st.session_state.latest_audio_emotion = audio_emotion
                    st.session_state.latest_audio_intensity = audio_intensity

                    # Fetch latest visual emotion from your visual emotion service API
                    visual_emotion, valence, arousal = fetch_latest_visual_emotion()

                    # Save in session state so it persists after rerun
                    st.session_state.latest_visual_emotion = visual_emotion
                    st.session_state.latest_valence = valence
                    st.session_state.latest_arousal = arousal
                    
                    distortion = None
                    if len(user_input.split()) > 20:
                        distortion = detect_cognitive_distortion(user_input)
                    else:
                        distortion = None  # or "Input too short to detect distortion"

                    distortion = detect_cognitive_distortion(user_input)
                    text_emotion = detect_emotion(user_input)

                    
                    st.session_state.distortion = distortion
                    st.session_state.text_emotion = text_emotion

                    st.session_state.detected_emotions.append({
                        "emotion": text_emotion,
                        "distortion": distortion if distortion and len(user_input.split()) > 20 else None,
                        "timestamp": datetime.datetime.now(),
                        "message": user_input
                    })

                    text_emotion_common, audio_emotion_common, visual_emotion_common = map_to_common_emotion(
                        text_emotion,
                        audio_emotion,
                        visual_emotion
                    )

                    # Then fuse using weighted voting
                    fused_emotion = unify_emotions_weighted(
                        text_emotion_common,
                        audio_emotion_common,
                        audio_intensity,
                        visual_emotion_common,
                        valence,
                        arousal
                    )
                    st.session_state.fused_emotion = fused_emotion

                    save_message(
                        st.session_state.username,
                        "user",
                        user_input,
                        emotion=fused_emotion,
                        distortion=distortion
                    )
                    st.session_state.chat_history.append({"sender": "user", "text": user_input})

                    response = generate_response(user_input, distortion, fused_emotion)

                    save_message(
                        st.session_state.username,
                        "bot",
                        response,
                        emotion=None,
                        distortion=None
                    )
                    st.session_state.chat_history.append({"sender": "bot", "text": response})
                    safe_rerun()

                except Exception as e:
                    st.error(f"Error during chat processing: {e}")

    st.markdown(" ")
    st.markdown(" ")              
    st.markdown(" ")
    st.markdown("### Multimodal Emotion & Cognitive Distortion Detection Summary")
    st.markdown(" ")
    st.markdown(" ")
    # Emotion summary bar chart
    if st.session_state.detected_emotions:
        card_row_html = '<div class="emotion-card-row">'

        card_row_html += f"""
        <div class="emotion-card">
            <span class="emotion-label">🎧 Audio Emotion</span>
            <span class="emotion-value">{st.session_state.latest_audio_emotion.title()} ({st.session_state.latest_audio_intensity:.2f}%)</span>
        </div>
        """

        card_row_html += f"""
        <div class="emotion-card">
            <span class="emotion-label">📷 Visual Emotion</span>
            <div class="emotion-value">{st.session_state.latest_visual_emotion.title()}</div>
            <div class="emotion-value">Valence: {st.session_state.latest_valence:.2f}</div>
            <div class="emotion-value">Arousal: {st.session_state.latest_arousal:.2f}</div>
        </div>
        """

        card_row_html += f"""
        <div class="emotion-card">
            <span class="emotion-label">💬 Text Emotion</span>
            <div class="emotion-value">{st.session_state.text_emotion.title()}</div>
        </div>
        """

        # Show cognitive distortion only if input is long enough
        if st.session_state.distortion and len(user_input.split()) > 20:
            distortion_display = st.session_state.distortion.title()
        elif len(user_input.split()) <= 20:
            distortion_display = "Input is too short to detect a distortion"
        else:
            distortion_display = "None"

        card_row_html += f"""
        <div class="emotion-card">
            <span class="emotion-label">🧠 Cognitive Distortion</span>
            <div class="emotion-value">{distortion_display}</div>
        </div>
        """
        card_row_html += f"""
        <div class="emotion-card">
            <span class="emotion-label">🔄 Fused Emotion</span>
            <div class="emotion-value">{st.session_state.fused_emotion.title()}</div>
        </div>
        """

        card_row_html += "</div>"

        full_html = f"""
        <style>
        .emotion-card-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 18px;
            margin-bottom: 10px;
            max-width: 100%;
            overflow-x: auto;
        }}
        .emotion-card {{
            flex: 1 1 300px;
            background: linear-gradient(135deg, #e0f7fa 60%, #f8fafc 100%);
            border-radius: 16px;
            box-shadow: 0 4px 18px rgba(24,90,157,0.13);
            padding: 22px 30px;
            margin-bottom: 22px;
            border: 2px solid #6ba8ff;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            gap: 14px;
            transition: transform 0.15s;
        }}
        .emotion-card:hover {{
            transform: translateY(-4px) scale(1.03);
            box-shadow: 0 8px 28px rgba(24,90,157,0.18);
            border-color: #43cea2;
        }}
        .emotion-label {{
            font-weight: 700;
            color: #185a9d;
            min-width: 170px;
            font-size: 1.18rem;
            letter-spacing: 0.03em;
            text-shadow: 0 1px 0 #fff;
        }}
        .emotion-value {{
            font-weight: 600;
            color: #222;
            font-size: 1.18rem;
            padding: 4px 0 2px 0;
            border-radius: 6px;
            background: #f0f7ff;
            box-shadow: 0 1px 2px rgba(67,206,162,0.07);
        }}
        </style>
        {card_row_html}
        """

        st.markdown(full_html, unsafe_allow_html=True)

        # Emotion summary bar chart
        emotion_list = [e["emotion"] for e in st.session_state.detected_emotions]
        emotion_counts = Counter(emotion_list)
        df = pd.DataFrame(emotion_counts.items(), columns=["Emotion", "Count"])
        st.markdown("### Emotion Summary so far:")
        st.bar_chart(df.set_index("Emotion"))

        # Toggle for timeline plot
        if st.checkbox("Show emotion timeline"):
            plot_emotion_timeline(st.session_state.detected_emotions)

        if st.button("Refresh Emotion Timeline"):
            safe_rerun()
        
        if st.checkbox("Show distortion timeline"):
            plot_distortion_timeline(st.session_state.detected_emotions)
        
        if st.button("Refresh Distortion Timeline"):
            safe_rerun()

    else:
        st.info("No emotions detected yet.")

