# Dependencies
import os
import numpy as np
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg19 import (
    VGG19, 
    preprocess_input, 
    decode_predictions
)

def doPredict():
    model = load_model('model_saved.h5')
    #model = VGG19(include_top=True, weights='imagenet')
    image_size = (256, 256)
    #image_size = (224, 224)
    image_path = "static\\img\\saved_img_125.jpg"
    img = image.load_img(image_path, target_size=image_size)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    predictions = model.predict(x)
    y_classes = predictions.argmax(axis=-1)
    
    return y_classes[0]



