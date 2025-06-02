import cv2
import numpy as np
from tensorflow.keras.applications.resnet_v2 import ResNet152V2, preprocess_input
from tensorflow.keras.models import Model

# Load the ResNet model once
base_model = ResNet152V2(weights="imagenet", include_top=False, pooling="avg")
resnet     = Model(inputs=base_model.input, outputs=base_model.output)

def preprocess_frame(frame): 
    resized = cv2.resize(frame, (224, 224))
    array   = np.expand_dims(resized.astype("float32"), axis=0)
    features = resnet.predict(preprocess_input(array))
    return features  # shape (1, 2048)
