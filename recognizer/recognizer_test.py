import threading
import logging

import cv2

from detector import CASCADE_PATH
from trainer import MODEL_PATH


FONT = cv2.FONT_HERSHEY_SIMPLEX

logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(message)s')

class VideoStream(threading.Thread):
    def __init__(self, cam):
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read(MODEL_PATH)
        self.faceCascade = cv2.CascadeClassifier(CASCADE_PATH)
        self.labels = ['Person X']
        self.cam = cam
        # Minimal window size to be recognized as a face
        self.minWinSize = (50, 50)
        self.flip = -1
        self.scaleFactor = 1.5
        self.minNeighbors = 4
        # Out frame to display
        self.img = 0
        threading.Thread.__init__(self)


    def run(self):
        self.recognition()


    def get_frame(self):
        return self.img

    def set_frame(self, k):
        self.img = k

    def recognition(self):
        while True:
            ret, self.img = self.cam.read()
            self.img = cv2.flip(self.img, self.flip)
            cv2.imwrite('kok.jpg', self.get_frame())
            gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

            faces = self.faceCascade.detectMultiScale( 
                gray,
                scaleFactor = self.scaleFactor,
                minNeighbors = self.minNeighbors,
                minSize = self.minWinSize,
            )

            for(x, y, w, h) in faces:
                cv2.rectangle(self.img, (x,y), (x+w, y+h), (0, 0, 255), 2)

                _id, confidence = self.recognizer.predict(gray[y: y+h, x: x+w])

                # Check if confidence is less them 100 ==> "0" is perfect match 
                if (confidence < 100):
                    _id = self.labels[_id]
                    confidence = f'{confidence:.1f}%'
                else:
                    _id = "unknown"
                    confidence = f'{confidence:.1f}%'
                
                cv2.putText(self.img, str(_id), (x+5, y-5), FONT, 1, (255, 255, 255), 2)
                cv2.putText(self.img, str(confidence), (x+5, y+h-5), FONT, 1, (255, 255, 0), 1)
                cv2.imwrite('kok2.jpg', self.img)
