from google import genai
from transformers import pipeline
import joblib
from flask import Flask, request, jsonify

# Load your trained model and tokenizer
model = joblib.load("cognitive_distortion_detection_model.pkl")
tokenizer = joblib.load("cognitive_distortion_detection_tfidf_vectorizer.pkl")

app = Flask(__name__)

# Initialize the Google GenAI client with your API key
client = genai.Client(api_key="AIzaSyBkZNR2X0xDuOV-3ymOsmU4Dzo7MlXvfC8")

# Initialize EmoRoBERTa for emotion detection using Hugging Face
emotion_pipeline = pipeline('sentiment-analysis', model='arpanghoshal/EmoRoBERTa')

def detect_cognitive_distortion(user_message):
    """
    This function will detect cognitive distortion in the user message.
    It should use the trained model to classify or predict distortions in the input message.
    """
    # Tokenize the user message
    tokens = tokenizer.transform([user_message])

    # Predict the cognitive distortion
    distortion_prediction = model.predict(tokens)

    # Assuming the model returns a list of distortion labels or categories
    return distortion_prediction[0]

def detect_emotion(user_message):
    """
    This function uses the EmoRoBERTa model to predict the emotion in the user message.
    It uses Hugging Face's sentiment analysis pipeline.
    """
    # Predict the emotion in the user message
    emotion_prediction = emotion_pipeline(user_message)[0]
    return emotion_prediction['label']

@app.route("/generate", methods=["POST"])
def generate():
    try:
        # Get the user message from the frontend
        data = request.json
        user_message = data.get("userMessage")
        
        if not user_message:
            return jsonify({"error": "User message is missing"}), 400
        
        
        # Detect cognitive distortion and emotion
        distortion = detect_cognitive_distortion(user_message)
        emotion = detect_emotion(user_message)

        print(f"Cognitive distortion detected: {distortion}")
        print(f"Emotion detected: {emotion}")

        # Count the number of words in the user message
        word_count = len(user_message.split())
        print(f"Word count: {word_count}")

        # Initialize the structured prompt
        structured_prompt = user_message

        # Add emotion to the structured prompt if more than 10 words
        if word_count > 10:
            structured_prompt += f"\nEmotion: {emotion} \nconsider detected emotion while crafting your response"

        # Add both distortion and emotion if more than 20 words
        if word_count > 20:
            structured_prompt += f"\nCognitive Distortion: {distortion} \nconsider detected distortion while crafting your response.  You can provide advice, support, or ask questions to engage the user."

        # Add instruction to the structured prompt on how to respond
        structured_prompt
        print(f"Structured prompt: {structured_prompt}")

        # Request the generated content from the model
        response = client.models.generate_content(
            model="tunedModels/prompt3-6ljcc26zvkvk",
            contents=structured_prompt
        )

        # Return the generated response, cognitive distortion, and emotion to the frontend
        return jsonify({
            "message": response.text,
            "cognitiveDistortion": distortion,
            "emotion": emotion
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Start the Flask server
    app.run(port=5001)
