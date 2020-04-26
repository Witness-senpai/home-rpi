import os 
import logging

import cv2
import numpy as np

from detector import CASCADE_PATH
from trainer import MODEL_PATH


logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(message)s')

logger.info('Start face recognition...')

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(MODEL_PATH)
faceCascade = cv2.CascadeClassifier(CASCADE_PATH)

font = cv2.FONT_HERSHEY_SIMPLEX

# names related to ids: example ==> Marcelo: id=1,  etc
names = ['u0', 'u1', 'u2', 'u3'] 

# Initialize and start realtime video capture
cam = cv2.VideoCapture(0)
cam.set(3, 2560) # set video widht
cam.set(4, 1440) # set video height

# Define min window size to be recognized as a face
minW = 100
minH = 100
while True:
    ret, img = cam.read()
    img = cv2.flip(img, -1) # Flip vertically

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale( 
        gray,
        scaleFactor = 1.5,
        minNeighbors = 5,
        minSize = (int(minW), int(minH)),
    )

    for(x, y, w, h) in faces:
        cv2.rectangle(img, (x,y), (x+w, y+h), (0, 255, 0), 2)

        _id, confidence = recognizer.predict(gray[y: y+h, x: x+w])

        # Check if confidence is less them 100 ==> "0" is perfect match 
        if (confidence < 100):
            _id = names[_id]
            confidence = f'{100 - confidence:.1f}%'
        else:
            _id = "unknown"
            confidence = f'{100 - confidence:.1f}%'
        
        cv2.putText(img, str(_id), (x+5, y-5), font, 1, (255, 255, 255), 2)
        cv2.putText(img, str(confidence), (x+5, y+h-5), font, 1, (255, 255, 0), 1)  
    
    cv2.imshow('Face recognition', img) 

    k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break

logger.info('Stop face recognition')
cam.release()
cv2.destroyAllWindows()