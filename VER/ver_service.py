import threading
import time
import cv2
import numpy as np
import joblib
import tensorflow as tf
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.preprocessing import preprocess_frame  # your preprocessing code

app = FastAPI()

# Map your model indices to emotion labels:
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

# Load models
emotion_model = joblib.load("VER_models/best_mlp_pca_pipeline.pkl")
va_models = {
    label: tf.keras.models.load_model(f"VER_models/va_models/emotion{idx}_intensity_model.h5", compile=False)
    for idx, label in EMOTION_LABELS.items()
}

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Variables to hold latest detected emotion and intensities
latest_visual_emotion = "Neutral"
latest_valence = 0.0
latest_arousal = 0.0

# Service running flag
visual_service_running = False

def visual_emotion_loop():
    global latest_visual_emotion, latest_valence, latest_arousal, visual_service_running

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not camera.isOpened():
        print("Camera not accessible")
        visual_service_running = False
        return

    visual_service_running = True

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Failed to capture frame")
            latest_visual_emotion = "Camera error"
            latest_valence = 0.0
            latest_arousal = 0.0
            time.sleep(1)
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_img_rgb = frame_rgb[y:y+h, x:x+w]

            # Preprocess face image and extract features
            features = preprocess_frame(face_img_rgb)

            # Predict emotion label index
            emotion_label_idx = emotion_model.predict(features)[0]
            emotion_label = EMOTION_LABELS.get(emotion_label_idx, "Unknown")

            # Predict valence and arousal
            va_model = va_models.get(emotion_label)
            if va_model:
                input_image = cv2.resize(face_img_rgb, (224, 224))
                input_image = input_image.astype(np.float32) / 255.0
                input_image = np.expand_dims(input_image, axis=0)

                va_prediction = va_model.predict(input_image)
                valence = float(va_prediction[0][0])
                arousal = float(va_prediction[1][0])
            else:
                valence, arousal = 0.0, 0.0

            latest_visual_emotion = emotion_label
            latest_valence = valence
            latest_arousal = arousal

        else:
            latest_visual_emotion = "No face detected"
            latest_valence = 0.0
            latest_arousal = 0.0

        time.sleep(0.1)  # Adjust for processing speed

    camera.release()

class VisualEmotionResponse(BaseModel):
    emotion: str
    valence: float
    arousal: float

@app.on_event("startup")
def start_camera_thread():
    thread = threading.Thread(target=visual_emotion_loop, daemon=True)
    thread.start()

@app.get("/latest-visual-emotion", response_model=VisualEmotionResponse)
def get_latest_visual_emotion():
    if not visual_service_running:
        raise HTTPException(status_code=503, detail="Visual emotion service is not running or camera unavailable")
    return {
        "emotion": latest_visual_emotion,
        "valence": latest_valence,
        "arousal": latest_arousal
    }
