import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import sounddevice as sd
import scipy.io.wavfile as wavfile
import tempfile
import librosa
import noisereduce as nr
import torch
import tensorflow as tf
import joblib
import numpy as np
import pandas as pd
import altair as alt
import sounddevice as sd
import scipy.io.wavfile as wavfile
import tempfile
import librosa
import noisereduce as nr
import torch
import tensorflow as tf
import joblib
import os
import matplotlib.pyplot as plt
from collections import Counter
from transformers import Wav2Vec2Processor, Wav2Vec2Model
import time

from transformers import Wav2Vec2Processor, Wav2Vec2Model

def audio_emotion_detection_page():

    # --- Initialize session state variables ---
    if "emotion_history" not in st.session_state:
        st.session_state.emotion_history = []

    if "timestamp_history" not in st.session_state:
        st.session_state.timestamp_history = []

    if "emotion_counts" not in st.session_state:
        st.session_state.emotion_counts = {}

    # Load scalers and encoders
    scaler = joblib.load("SER_models/scaler.pkl")
    emotion_encoder = joblib.load("SER_models/label_encoder.pkl")

    # Load HuggingFace Wav2Vec2 model and processor
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    wav2vec_model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")

    # Load main model
    st.title("🎤 Real-time Audio Emotion Detection")
    st.subheader("🔄 Loading model...")
    model_path = os.path.join("SER_models", "emotion_model.keras")
    model = tf.keras.models.load_model(model_path)
    st.success("✅ Model loaded!")

    st.markdown(" ")  # Blank line using markdown
    st.markdown(" ")  # Blank line using markdown


    def record_audio(duration, fs=16000):

        # # Use a placeholder so the alert can be cleared later
        # status_placeholder = st.empty()
        # status_placeholder.info("Recording...")

        # Start recording
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()

        # # Clear the "Recording..." message and replace it with success
        # status_placeholder.success("Recording complete")


        return audio.flatten(), fs

    def save_temp_wav(audio, fs):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            wavfile.write(tmpfile.name, fs, (audio * 32767).astype(np.int16))
            return tmpfile.name

    def plot_waveform(audio, fs):
        time = np.linspace(0, len(audio) / fs, num=len(audio))
        fig, ax = plt.subplots()
        ax.plot(time, audio, color='blue')
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.set_title("Audio Waveform")
        st.pyplot(fig)

    def preprocess_and_extract(audio_path):
        audio, sr = librosa.load(audio_path, sr=16000)
        reduced_noise = nr.reduce_noise(y=audio, sr=sr)
        inputs = processor(reduced_noise, sampling_rate=sr, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = wav2vec_model(**inputs)
        features = outputs.last_hidden_state.squeeze().mean(dim=0).numpy()
        features_scaled = scaler.transform([features])
        frames_per_timestep = 8
        features_per_frame = features_scaled.shape[1] // frames_per_timestep
        features_reshaped = features_scaled.reshape((1, frames_per_timestep, features_per_frame))
        return features_reshaped

    def predict_emotion_and_intensity(audio_path):
        input_features = preprocess_and_extract(audio_path)
        predictions = model.predict(input_features)
        emotion_probs = predictions[0]
        intensity_pred = predictions[1]
        predicted_emotion_idx = np.argmax(emotion_probs, axis=1)[0]
        predicted_emotion = emotion_encoder.inverse_transform([predicted_emotion_idx])[0]
        intensity_percentage = intensity_pred[0][0] * 100
        return predicted_emotion, intensity_percentage, emotion_probs[0]

    def get_most_frequent_recent_emotion(history, window_size=5):
        """
        Returns the most frequent emotion in the last `window_size` entries of the emotion history.
        """
        if not history:
            return None  # No emotions recorded yet

        recent_emotions = history[-window_size:]  # Get last 10 or fewer
        emotion_counts = Counter(recent_emotions)
        most_common_emotion, count = emotion_counts.most_common(1)[0]
        return most_common_emotion


    # UI
    st.subheader("🎙️ Record Audio")
    duration = st.slider("Recording Duration (seconds)", 1, 10, 3)
    silence_threshold = st.slider("Silence Threshold (RMS)", 0.001, 0.05, 0.01)

    # Session state to store emotion history
    if "emotion_history" not in st.session_state:
        st.session_state.emotion_history = []

    if "emotion_counts" not in st.session_state:
        st.session_state.emotion_counts = {label: 0 for label in emotion_encoder.classes_}


    # Toggle to start/stop continuous 3-second recording loop
    recording_toggle = st.checkbox("🔄 Enable Continuous Real-Time Recording")

    # Placeholders to update UI dynamically
    status_placeholder = st.empty()
    current_result_placeholder = st.empty()
    # waveform_placeholder = st.empty()
    # emotion_placeholder = st.empty()
    # bar_chart_placeholder = st.empty()
    trend_chart_placeholder = st.empty()
    freq_chart_placeholder = st.empty()
    most_common_placeholder = st.empty()

    if recording_toggle:
        # Create placeholders that are reset on each iteration
        # current_result_placeholder = st.empty()  # For waveform and bar chart block

        while True:
            status_placeholder.info("🎙️ Recording...")

            st.markdown(" ")  # Blank lines
            st.markdown(" ")

            # Record and process audio
            audio, fs = record_audio(duration)
            audio_path = save_temp_wav(audio, fs)

            rms_energy = np.sqrt(np.mean(audio**2))
            if rms_energy < silence_threshold:
                status_placeholder.warning("⚠️ No voice detected.")
            else:
                status_placeholder.success("✅ Recording complete and processed.")

                predicted_emotion, intensity_percentage, emotion_probs = predict_emotion_and_intensity(audio_path)

                import datetime
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                st.session_state.timestamp_history.append(current_time)
                st.session_state.emotion_history.append(predicted_emotion)
                st.session_state.emotion_counts[predicted_emotion] = st.session_state.emotion_counts.get(predicted_emotion, 0) + 1

                st.markdown(" ")
                st.markdown(" ")
                st.markdown(" ")
                st.markdown(" ")
                

                # --- Display current result block ---
                with current_result_placeholder.container():
                    col1, col2 = st.columns([2, 2])

                    with col1:
                        time_vals = np.linspace(0, len(audio) / fs, num=len(audio))
                        fig, ax = plt.subplots()
                        ax.plot(time_vals, audio, color='blue')
                        ax.set_xlabel("Time (s)")
                        ax.set_ylabel("Amplitude")
                        ax.set_title("Audio Waveform")
                        st.pyplot(fig)

                    with col2:
                        st.markdown(f"### 🧠 Predicted Emotion: **{predicted_emotion}**")
                        st.markdown(f"### 🔥 Emotion Intensity: **{intensity_percentage:.2f}%**")

                        emotion_labels = emotion_encoder.classes_
                        prob_df = pd.DataFrame({
                            'Emotion': emotion_labels,
                            'Probability': emotion_probs
                        })
                        bar_chart = alt.Chart(prob_df).mark_bar().encode(
                            x='Emotion',
                            y='Probability',
                            color='Emotion'
                        ).properties(height=400)
                        st.altair_chart(bar_chart, use_container_width=True)
                        st.markdown(" ")
                        st.markdown(" ")
                        st.markdown(" ")
                        st.markdown(" ")

                        
                # --- Trend chart below current prediction ---
                
                emotion_time_df = pd.DataFrame({
                    'Time': st.session_state.timestamp_history,
                    'Emotion': st.session_state.emotion_history
                })
                emotion_time_df['EmotionLabel'] = pd.Categorical(
                    emotion_time_df['Emotion'],
                    categories=emotion_labels,
                    ordered=True
                )
                trend_chart = alt.Chart(emotion_time_df).mark_line(point=True).encode(
                    x=alt.X('Time', title='Time'),
                    y=alt.Y('EmotionLabel', title='Emotion'),
                    tooltip=['Time', 'Emotion']
                ).properties(height=300)
                emotion_rules = alt.Chart(pd.DataFrame({'y': emotion_labels})).mark_rule(
                    strokeDash=[3, 3], color='gray'
                ).encode(y=alt.Y('y', type='ordinal'))
                final_trend = trend_chart + emotion_rules
                trend_chart_placeholder.altair_chart(final_trend, use_container_width=True)

                st.markdown(" ")
                st.markdown(" ")
                st.markdown(" ")
                st.markdown(" ")
                st.markdown(" ")
                st.markdown(" ")
                st.markdown(" ")

                emotion_freq_df = pd.DataFrame({
                    'Emotion': list(st.session_state.emotion_counts.keys()),
                    'Count': list(st.session_state.emotion_counts.values())
                }).sort_values(by='Count', ascending=False)
                freq_bar_chart = alt.Chart(emotion_freq_df).mark_bar().encode(
                    x='Emotion',
                    y='Count',
                    color='Emotion',
                    tooltip=['Emotion', 'Count']
                ).properties(height=300)
                freq_chart_placeholder.altair_chart(freq_bar_chart, use_container_width=True)

                st.markdown(" ")
                st.markdown(" ")

                most_common = get_most_frequent_recent_emotion(st.session_state.emotion_history, window_size=5)
                if most_common:
                    most_common_placeholder.markdown(f"### 🔁 Most Frequent Emotion (last 5): **{most_common}**")

            time.sleep(3)