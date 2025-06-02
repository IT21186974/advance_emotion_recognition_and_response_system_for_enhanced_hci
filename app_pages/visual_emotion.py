import streamlit as st
import cv2
import numpy as np
import joblib
import tensorflow as tf
import time
from collections import deque, Counter
from utils.preprocessing import preprocess_frame
from streamlit.runtime.scriptrunner import RerunException, RerunData
import os

EMOTION_LABELS = {
    0: "Neutral",
    1: "Happy",
    2: "Sad",
    3: "Surprise",
    4: "Fear",
    5: "Disgust",
    6: "Anger",
    7: "Contempt"
}

def visual_emotion_recognition_page():
    # Secondary emotion labels mapping
    secondary_emotion_labels = {
        0: "Excited",    1: "Relaxed", 2 : "Lonely",  3 : "Grateful",
        4: "Frustrated", 5: "Tense",   6 : "Content", 7 : "Curious",
        8: "Hopeless",   9: "Ashamed", 10: "Proud",   11: "Bored"
    }

    st.markdown("""
    <style>
        .title {
            font-size    : 2.8rem;
            font-weight  : 800;
            color        : #4B0082;
            margin-bottom: 0;
        }
        .subtitle {
            font-size    : 1.3rem;
            color        : #6A5ACD;
            margin-top   : 0;
            margin-bottom: 20px;
        }
        .metric-label {
            font-weight: 600;
            color      : #483D8B;
        }
        .metric-value {
            font-size  : 1.8rem;
            color      : #6A5ACD;
            font-weight: 700;
        }
        .emotion-badge {
            background-color: #E6E6FA;
            color           : #4B0082;
            padding         : 5px 15px;
            border-radius   : 20px;
            font-weight     : 700;
            font-size       : 1.1rem;
            display         : inline-block;
            margin-top      : 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="title">🎥 Real-Time Visual Emotion & Intensity Recognition</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Watch your emotions come alive — powered by AI & CV</p>', unsafe_allow_html=True)

    run = st.checkbox('Start Camera')

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    EMOTION_LABELS = {
        0: "Neutral", 1: "Happy",   2: "Sad",   3: "Surprise",
        4: "Fear",    5: "Disgust", 6: "Anger", 7: "Contempt"
    }

    pca             = joblib.load("VER_models/pca_model.pkl")
    emotion_model   = tf.keras.models.load_model("VER_models/best_mlp_model_focal.h5", compile=False)
    secondary_model = joblib.load("VER_models/secondary_emotion_model.pkl")

    @st.cache_resource
    def load_va_model(emotion_label): 
        idx = None
        for k,v in EMOTION_LABELS.items(): 
            if  v == emotion_label: 
                idx = k
                break
        if idx is None: 
            return None
        model_path = f"VER_models/va_models/emotion{idx}_intensity_model.h5"
        return tf.keras.models.load_model(model_path, compile=False)

    history_log              = []
    latest_secondary_emotion = "Unknown"

    if run: 
        camera = cv2.VideoCapture(0)

        col1, col2                         = st.columns([3, 1])
        frame_placeholder             = col1.empty()
        valence_metric                = col2.metric(label="Valence (Pleasure)", value="0.00", delta=None)
        arousal_metric                = col2.metric(label="Arousal (Excitement)", value="0.00", delta=None)
        secondary_emotion_display     = col2.empty()
        freq_dominant_emotion_display = col2.empty()

        dominant_emotions_buffer       = deque()
        window_duration                = 5.0  # seconds
        window_start_time              = time.time()
        most_frequent_dominant_emotion = "Unknown"

        while run: 
            ret, frame = camera.read()
            if not ret: 
                st.warning("⚠️ Failed to access the webcam.")
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray      = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces     = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            dominant_emotion = "Unknown"
            valence, arousal         = 0.0, 0.0

            if len(faces) > 0: 
                (x, y, w, h) = faces[0]
                face_img_rgb = frame_rgb[y:y + h, x:x + w]

                features     = preprocess_frame(face_img_rgb)
                features_pca = pca.transform(features)

                emotion_probs     = emotion_model.predict(features_pca)
                emotion_label_idx = np.argmax(emotion_probs)
                dominant_emotion  = EMOTION_LABELS.get(emotion_label_idx, "Unknown")

                dominant_emotions_buffer.append(dominant_emotion)

                va_model = load_va_model(dominant_emotion)
                if va_model is not None: 
                    input_image   = cv2.resize(face_img_rgb, (224, 224)).astype(np.float32) / 255.0
                    input_image   = np.expand_dims(input_image, axis=0)
                    va_prediction = va_model.predict(input_image)
                    valence       = float(va_prediction[0][0])
                    arousal       = float(va_prediction[1][0])
                else: 
                    valence, arousal = 0.0, 0.0

                va_input                 = np.array([[valence, arousal]])
                predicted_cluster        = secondary_model.predict(va_input)[0]
                latest_secondary_emotion = secondary_emotion_labels.get(int(predicted_cluster), "Unknown")

                history_log.append({
                    "timestamp": time.time(),
                    "dominant" : dominant_emotion,
                    "valence"  : valence,
                    "arousal"  : arousal,
                    "secondary": latest_secondary_emotion
                })

                # Draw rectangle and info on frame
                cv2.rectangle(frame, (x, y), (x + w, y + h), (70, 130, 180), 3)
                cv2.putText(frame, f'Emotion: {dominant_emotion}', (x, y - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.85, (70, 130, 180), 2)
                cv2.putText(frame, f'Valence: {valence:.2f}', (x, y + h + 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 215, 0), 2)
                cv2.putText(frame, f'Arousal: {arousal:.2f}', (x, y + h + 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 215, 0), 2)
                cv2.putText(frame, f'Secondary: {latest_secondary_emotion}', (x, y + h + 75),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (138, 43, 226), 2)
            else: 
                cv2.putText(frame, 'No face detected', (20, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            frame_placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Update metrics live
            valence_metric.metric("Valence (Pleasure)", f"{valence:.2f}")
            arousal_metric.metric("Arousal (Excitement)", f"{arousal:.2f}")
            secondary_emotion_display.markdown(
                f'<div class="emotion-badge">🌟 Secondary Emotion: {latest_secondary_emotion}</div>',
                unsafe_allow_html = True
            )

            # Every 5 seconds, update most frequent dominant emotion
            current_time= time.time()
            if current_time - window_start_time >= window_duration:
                if dominant_emotions_buffer: 
                    counter                        = Counter(dominant_emotions_buffer)
                    most_frequent_dominant_emotion = counter.most_common(1)[0][0]
                    dominant_emotions_buffer.clear()  # reset for next window
                else: 
                    most_frequent_dominant_emotion = "Unknown"
                window_start_time              = current_time

            freq_dominant_emotion_display.markdown(
                f'<div class="emotion-badge">🔥 Most Frequent Dominant Emotion (last 5s): <b>{most_frequent_dominant_emotion}</b></div>',
                unsafe_allow_html = True
            )

            time.sleep(0.03)

        camera.release()
    else:
        st.write("▶️ Please start the camera by checking the box above.")

