import logging

import numpy as np
import cv2

CASCADE_PATH = '/home/pi/Public/opencv/opencv-4.2.0/data/haarcascades/haarcascade_frontalface_default.xml' 

logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(message)s')

def face_demo():
    logger.info('Start demo camera view')
    faceCascade = cv2.CascadeClassifier(CASCADE_PATH)

    cap = cv2.VideoCapture(0)
    cap.set(3, 2560) # set Width
    cap.set(4, 1440) # set Height

    while True:
        ret, img = cap.read()
        img = cv2.flip(img, -1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,     
            minSize=(100, 100)
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi_gray = gray[y: y+h, x: x+w]
            roi_color = img[y: y+h, x: x+w]
            
        cv2.imshow('Demo face view', img)

        k = cv2.waitKey(50) & 0xff
        if k == 27: # press 'ESC' to quit
            break

    cap.release()
    cv2.destroyAllWindows()
    logger.info('Stop demo camera view')

if __name__ == '__main__':
    face_demo()