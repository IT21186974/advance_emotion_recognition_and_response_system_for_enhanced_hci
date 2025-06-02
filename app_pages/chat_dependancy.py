import streamlit as st
from database import get_messages
from streamlit.runtime.scriptrunner import RerunException, RerunData
import os
import pandas as pd
import pandas as pd
import altair as alt
import joblib
from database import (
    get_messages,
    get_total_user_prompts,
    get_daily_user_prompts,
    get_late_night_conversations,
    max_consecutive_days,
    has_late_night_negative,
    total_negative_emotion_count,
)

def safe_rerun():
    try:
        raise RerunException(RerunData(widget_states=None))
    except Exception:
        os._exit(0)


def emotional_dependency_analysis_page():
    st.title("Emotional Dependency Analysis")

    username = st.session_state.username
    messages = get_messages(username)  # List of message objects

    st.markdown(f"### User: {username}")

    # Total prompts
    total_prompts = get_total_user_prompts(username)

    # Daily prompts data
    daily_data = get_daily_user_prompts(username)

    # Late night prompts
    late_night_count = get_late_night_conversations(username)

    # Max consecutive days
    daily_prompts = get_daily_user_prompts(username)
    prompt_dates = [entry['date'] for entry in daily_prompts] if daily_prompts else []
    max_streak = max_consecutive_days(prompt_dates) if prompt_dates else 0

    # Prepare user messages with emotions
    user_messages_with_emotions = []
    for msg in messages:
        if msg.sender == "user":
            user_messages_with_emotions.append({
                "timestamp": msg.timestamp,
                "emotion": msg.emotion if hasattr(msg, "emotion") else None
            })

    # Calculate total negative emotion count
    neg_emotion_count = total_negative_emotion_count(user_messages_with_emotions)

    # Calculate late night negative emotion count
    late_night_neg_count = sum(
        1 for m in user_messages_with_emotions
        if m['emotion'] in ['anger', 'sadness', 'fear', 'disapproval', 'disgust', 'disappointment', 'remorse']
        and m['timestamp'].hour >= 22
    )

    # CSS styling for square cards
    st.markdown(
        """
        <style>
        .card {
            background-color: #8CD2F0;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 5px;
            text-align: center;
            box-shadow: 2px 2px 8px rgb(0 0 0 / 0.1);
            height: 130px;  /* fixed height for square shape */
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .card-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #4B5563;
            line-height: 1;
        }
        .card-label {
            font-size: 1rem;
            font-weight: 500;
            color: black;
            margin-top: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    cols = st.columns(5)

    with cols[0]:
        st.markdown(f'<div class="card"><div class="card-value">{total_prompts}</div><div class="card-label">Total User Messages</div></div>', unsafe_allow_html=True)

    with cols[1]:
        st.markdown(f'<div class="card"><div class="card-value">{late_night_count}</div><div class="card-label">Late Night Prompts (after 10 PM)</div></div>', unsafe_allow_html=True)

    with cols[2]:
        st.markdown(f'<div class="card"><div class="card-value">{max_streak}</div><div class="card-label">Max Consecutive Days</div></div>', unsafe_allow_html=True)

    with cols[3]:
        st.markdown(f'<div class="card"><div class="card-value">{neg_emotion_count}</div><div class="card-label">Total Negative Emotion Count</div></div>', unsafe_allow_html=True)

    with cols[4]:
        st.markdown(f'<div class="card"><div class="card-value">{late_night_neg_count}</div><div class="card-label">Late Night Negative Emotion Count</div></div>', unsafe_allow_html=True)

    # Continue with the rest of your page below...

    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")

    if daily_data:
        df_daily = pd.DataFrame(daily_data)
        df_daily['date'] = pd.to_datetime(df_daily['date'])

        st.markdown("#### Daily User Prompts Over Time")
        chart = alt.Chart(df_daily).mark_line(point=True).encode(
            x='date:T',
            y='prompt_count:Q',
            tooltip=['date:T', 'prompt_count:Q']
        ).properties(
            width=700,
            height=300
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No daily prompt data available.")

    has_late_neg = has_late_night_negative(user_messages_with_emotions)
    color = "white"
    font_size = "24px"
    text = "Yes" if has_late_neg else "No"
    st.markdown(f'<p style="font-size: {font_size}; color: {color}; font-weight: bold;">Late Night Negative Emotion Detected: {text}</p>', unsafe_allow_html=True)




    # --- PREDICTION: Is user dependent on chat? ---

    # Features for model - make sure these match your model's expected features
    features = pd.DataFrame([{
        "total_turns": total_prompts,
        "late_night_conversations": late_night_count,
        "max_consecutive_days": max_streak,
        "has_late_night_negative": int(has_late_neg),
        "total_negative_emotion_count": neg_emotion_count
        #"late_night_neg_emotions": late_night_neg_count,
        
    }])

    # Load scaler and model - adjust paths as needed
    try:
        scaler = joblib.load("dependancy_models/scaler.pkl")
        kmeans_model = joblib.load("dependancy_models/kmeans_model.pkl")
    except Exception as e:
        st.error(f"Error loading model or scaler: {e}")
        return

    # Scale features
    features_scaled = scaler.transform(features)

    # Predict cluster
    cluster = kmeans_model.predict(features_scaled)[0]

    # Map cluster to dependency interpretation (adjust labels according to your clusters)
    cluster_labels = {
        0: "Not Dependent on Chat",
        1: "Emotionally Dependent on Chat",
        
        # add more if your model has more clusters
    }
    dependency_label = cluster_labels.get(cluster, "Unknown")

    st.markdown(f'<h3 style="color:red;">Chat Dependency Prediction: <strong>{dependency_label}</strong></h3>', unsafe_allow_html=True)
