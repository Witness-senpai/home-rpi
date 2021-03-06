import os
import logging
import threading

import cv2
import numpy as np
from PIL import Image

from recognizer import CASCADE_PATH, MODEL_PATH, FONT

# Path for face image database
TEMP_IMG_PATH = 'database/_temp'

recognizer = cv2.face.LBPHFaceRecognizer_create()
faceCascade = cv2.CascadeClassifier(CASCADE_PATH)

logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(funcName)s() %(lineno)d: %(message)s')

def train_model(user_id):
    """
    Func for training of model
    param: user_id = index in rec_users list
        If len==0 then index 0 will be use for first user in list
    """
    detector = cv2.CascadeClassifier(CASCADE_PATH)

    logger.info('Start training faces...')
    faces, ids = get_imgs_and_labels(TEMP_IMG_PATH, detector, user_id)

    recognizer.train(faces, np.array(ids))

    logger.info(f'Training is done! Saving model to {MODEL_PATH}')
    recognizer.write(MODEL_PATH)

    logger.info(f'Trained faces: {len(np.unique(ids))}')

# Function to get the images and label data from temp folder
def get_imgs_and_labels(path, detector, user_id):
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if f != '.gitkeeper']     
    face_samples=[]
    ids = [user_id] * len(image_paths)
    for image_path in image_paths:
        img_PIL = Image.open(image_path).convert('L') # convert it to grayscale
        img_numpy = np.array(img_PIL,'uint8')

        faces = detector.detectMultiScale(img_numpy)

        for (x, y, w, h) in faces:
            face_samples.append(img_numpy[y: y+h, x: x+w])

    return face_samples, ids

def one_frame_detect_face(
        frame,
        scaleFactor,
        minNeighbors, 
        minWinSize,
        username,
        number_of_frame,
        frames
    ):  
        isdetect = False
        try:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        except Exception as ex:
            logger.warning(ex)
            exit()

        faces = faceCascade.detectMultiScale( 
            gray_frame,
            scaleFactor = scaleFactor,
            minNeighbors = minNeighbors,
            minSize = minWinSize,
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            
            file_name = f'{TEMP_IMG_PATH}/{username}.{number_of_frame}.jpg'
            # Saving img in other thread because it is slow operating
            t = threading.Thread(
                target=save_img,
                args=(file_name, gray_frame[y: y+h, x: x+w])
            )
            t.start()
            isdetect = True

        progress = f'{number_of_frame}/{frames}'
        cv2.putText(frame, progress, (10, frame.shape[0] - 10), FONT, 1, (0, 255, 0), 2)

        return frame, isdetect

def save_img(file_name, img):
    cv2.imwrite(file_name, img)
    logger.info(f'Save img: {file_name}')