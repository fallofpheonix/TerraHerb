import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import os

def predict_tf(image_path):
    """
    Prediction script using the TensorFlow .h5 model.
    """
    model_path = "models/saved/plant_disease_model.h5"
    
    if not os.path.exists(model_path):
        print(f"⚠️ Model not found at {model_path}")
        return

    model = tf.keras.models.load_model(model_path)

    img = image.load_img(image_path, target_size=(224,224))
    img_array = image.img_to_array(img)/255
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)
    class_idx = np.argmax(prediction)
    
    print(f"🌿 Prediction: Class {class_idx} (Confidence: {np.max(prediction):.2f})")
    return prediction

if __name__ == "__main__":
    # Test with a dummy image if exists
    pass
