import gdown
import os

def download_model():
    model_url = 'https://drive.google.com/file/d/1-0yymlHp9R6tngV4-JqY-mhx1fifMQq_/view?usp=sharing'  
    output_path = 'model/emotion_model.keras'
    if not os.path.exists(output_path):
        gdown.download(model_url, output_path, quiet=False)
    return output_path
