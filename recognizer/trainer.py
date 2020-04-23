import os

import cv2
import numpy as np
from PIL import Image

from detector import CASCADE_PATH 
from face_saver import TEMP_IMG_PATH

# Path for face image database
MODEL_PATH = 'database/models/model.yml'

recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier(CASCADE_PATH)

# function to get the images and label data
def get_imgs_and_labels(path):
    image_paths = [os.path.join(path, f) for f in os.listdir(path)]     
    face_samples=[]
    ids = []

    for image_path in image_paths:
        img_PIL = Image.open(image_path).convert('L') # convert it to grayscale
        img_numpy = np.array(img_PIL,'uint8')

        _id = int(os.path.split(image_path)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)

        for (x, y, w, h) in faces:
            face_samples.append(img_numpy[y: y+h, x: x+w])
            ids.append(_id)

    return face_samples, ids

print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
faces, ids = get_imgs_and_labels(TEMP_IMG_PATH)
recognizer.train(faces, np.array(ids))

# Save the model
recognizer.write(MODEL_PATH)

# Print the numer of faces trained and end program
print(f"\n [INFO] {len(np.unique(ids))} faces trained. Exiting Program")