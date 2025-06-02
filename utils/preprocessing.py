import cv2
import numpy as np
from tensorflow.keras.applications.resnet_v2 import ResNet152V2, preprocess_input
from tensorflow.keras.models import Model

# Load the ResNet model once
base_model = ResNet152V2(weights="imagenet", include_top=False, pooling="avg")
resnet     = Model(inputs=base_model.input, outputs=base_model.output)

def preprocess_frame(face_img_rgb): 
    resized   = cv2.resize(face_img_rgb, (224, 224))
    img_array = resized.astype(np.float32)
    img_array = preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    deep_features = resnet.predict(img_array)  # Shape: (1, 2048)
    return deep_features
