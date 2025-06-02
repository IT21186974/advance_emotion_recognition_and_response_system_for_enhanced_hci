import threading
import time
import numpy as np
import joblib
import librosa
import noisereduce as nr
import torch
import tensorflow as tf
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import Wav2Vec2Processor, Wav2Vec2Model
import sounddevice as sd
import scipy.io.wavfile as wavfile
import tempfile

app = FastAPI()

# Load models once (adjust paths as needed)
scaler = joblib.load("SER_models/scaler.pkl")
emotion_encoder = joblib.load("SER_models/label_encoder.pkl")
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
wav2vec_model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
model = tf.keras.models.load_model("SER_models/emotion_model.keras")

latest_emotion = ""
latest_intensity = 0.0

def record_audio(duration=3, fs=16000):
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    return audio.flatten(), fs

def save_temp_wav(audio, fs):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        wavfile.write(tmpfile.name, fs, (audio * 32767).astype(np.int16))
        return tmpfile.name

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
    return predicted_emotion, intensity_percentage

def continuous_audio_loop():
    global latest_emotion, latest_intensity
    while True:
        try:
            audio, fs = record_audio(duration=3)
            audio_path = save_temp_wav(audio, fs)
            rms_energy = np.sqrt(np.mean(audio**2))
            if rms_energy < 0.00:
                latest_emotion = "neutral"
                latest_intensity = 0.0
            else:
                pred_emotion, intensity = predict_emotion_and_intensity(audio_path)
                latest_emotion = pred_emotion
                latest_intensity = intensity
        except Exception as e:
            print(f"Error in audio loop: {e}")
        time.sleep(0.1)

@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=continuous_audio_loop, daemon=True)
    thread.start()


class EmotionResponse(BaseModel):
    emotion: str
    intensity: float

@app.get("/latest-audio-emotion", response_model=EmotionResponse)
def get_latest_emotion():
    return {"emotion": latest_emotion, "intensity": latest_intensity}
