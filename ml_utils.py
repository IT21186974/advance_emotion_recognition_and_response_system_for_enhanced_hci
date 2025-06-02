import joblib

# Globals for lazy loading
cd_model = None
cd_tokenizer = None
emotion_pipeline = None
client = None

# Mapping dictionaries for emotion label normalization
text_to_common = {
    "sadness": "sadness",
    "grief": "sadness",
    "disappointment": "sadness",
    "remorse": "sadness",
    "nervousness": "sadness",
    "disgust": "disgust",
    "disapproval": "anger",
    "anger": "anger",
    "annoyance": "anger",
    "embarrassment": "confusion",
    "fear": "fear",
    "confusion": "confusion",
    "neutral": "neutral",
    "realization": "surprise",
    "surprise": "surprise",
    "desire": "desire",
    "curiosity": "caring",
    "caring": "caring",
    "approval": "joy",
    "admiration": "joy",
    "excitement": "joy",
    "amusement": "joy",
    "relief": "joy",
    "pride": "joy",
    "optimism": "joy",
    "gratitude": "joy",
    "love": "joy",
    "joy": "joy",
}

video_to_common = {
    "neutral": "neutral",
    "happy": "joy",
    "sad": "sadness",
    "surprise": "surprise",
    "fear": "fear",
    "disgust": "disgust",
    "anger": "anger",
    "contempt": "anger",
    "boredom": "boredom",
}

audio_to_common = {
    "neutral": "neutral",
    "happy": "joy",
    "sad": "sadness",
    "surprise": "surprise",
    "fear": "fear",
    "disgust": "disgust",
    "anger": "anger",
    "boredom": "boredom",
}

def map_to_common_emotion(text_emotion, audio_emotion, visual_emotion):
    te = text_to_common.get(text_emotion.lower(), "neutral")
    ae = audio_to_common.get(audio_emotion.lower(), "neutral")
    ve = video_to_common.get(visual_emotion.lower(), "neutral")
    return te, ae, ve


def load_models():
    global cd_model, cd_tokenizer, emotion_pipeline, client
    if cd_model is None or cd_tokenizer is None or emotion_pipeline is None or client is None:
        import joblib
        from transformers import pipeline, AutoTokenizer, TFAutoModelForSequenceClassification

        # Load sklearn cognitive distortion model and tokenizer
        cd_model = joblib.load("cognitive_distortion_detection_model.pkl")
        cd_tokenizer = joblib.load("cognitive_distortion_detection_tfidf_vectorizer.pkl")

        # Load HF emotion detection model and tokenizer
        emotion_model_name = "arpanghoshal/EmoRoBERTa"
        hf_tokenizer = AutoTokenizer.from_pretrained(emotion_model_name)
        hf_model = TFAutoModelForSequenceClassification.from_pretrained(emotion_model_name)
        emotion_pipeline = pipeline("sentiment-analysis", model=hf_model, tokenizer=hf_tokenizer, framework="tf")

        from google import genai
        client = genai.Client(api_key="AIzaSyBkZNR2X0xDuOV-3ymOsmU4Dzo7MlXvfC8")

def detect_cognitive_distortion(text: str) -> str:
    load_models()
    tokens = cd_tokenizer.transform([text])
    prediction = cd_model.predict(tokens)
    return prediction[0]

def detect_emotion(text: str) -> str:
    load_models()
    pred = emotion_pipeline(text)[0]
    return pred['label']

from collections import Counter

def unify_emotions_weighted(text_emotion, audio_emotion, audio_intensity, visual_emotion, valence, arousal):
    weights = {
        "text": 0.4,
        "audio": 0.3 if audio_intensity < 40 else 0.5,
        "visual": 0.3 if abs(arousal) < 0.3 else 0.5
    }

    weighted_votes = Counter()
    weighted_votes[text_emotion.lower()] += weights["text"]
    weighted_votes[audio_emotion.lower()] += weights["audio"]
    weighted_votes[visual_emotion.lower()] += weights["visual"]

    return weighted_votes.most_common(1)[0][0]


def generate_response(user_message: str, distortion: str, emotion: str) -> str:
    load_models()
    word_count = len(user_message.split())
    prompt = user_message
    if word_count > 0:
        prompt += f"\nUnified Emotion: {emotion} \nConsider this combined emotion from text, audio, and visual input while crafting your response."
    if word_count > 20:
        prompt += (
            f"\nCognitive Distortion: {distortion} "
            "consider detected distortion while crafting your response. "
            "You can provide advice, support, or ask questions to engage the user."
        )
    response = client.models.generate_content(
        model="tunedModels/prompt3-6ljcc26zvkvk",
        contents=prompt
    )
    return response.text
