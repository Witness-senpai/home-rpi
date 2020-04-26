import logging
import time
import datetime
import threading
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../recognizer'))

from imutils.video import VideoStream
from flask import Flask, render_template, Response
import cv2

from recognizer_test import VideoStream
from detector import CASCADE_PATH
from trainer import MODEL_PATH


FONT = cv2.FONT_HERSHEY_SIMPLEX
IP = 'localhost'
PORT = 8080

logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(message)s')

app = Flask(__name__)

outFrame = 0
ready = True
cam = cv2.VideoCapture(0)
cam.set(3, 1600) # set Width
cam.set(4, 1200) # set Height

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    logger.info('Call generate()')
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def gen():
    global outFrame
    while True:
        flag, encodedImage = cv2.imencode(".jpg", outFrame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')

def generate():
    global outFrame, ready
    while True:
        while not ready:
            pass
        #    logger.info('not ready')
        flag, encodedImage = cv2.imencode(".jpg", outFrame)

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')


def recognition():
    global outFrame, cam, ready
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_PATH)
    faceCascade = cv2.CascadeClassifier(CASCADE_PATH)
    labels = ['Person X']
    minWinSize = (100, 100)
    flip = -1
    scaleFactor = 1.2
    minNeighbors = 2
    f = 0
    img = 0
    while True:
        ready = False
        ret, img = cam.read()
        img = cv2.flip(img, flip)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = scaleFactor,
            minNeighbors = minNeighbors,
            minSize = minWinSize,
        )

        for(x, y, w, h) in faces:
            cv2.rectangle(img, (x,y), (x+w, y+h), (0, 0, 255), 2)
            _id, confidence = recognizer.predict(gray[y: y+h, x: x+w])
            # Check if confidence is less them 100 ==> "0" is perfect match 
            if (confidence < 100):
                _id = labels[_id]
                confidence = f"{100 - confidence:.1f}%"
            else:
                _id = "unknown"
                confidence = f'{100 - confidence:.1f}%'
            
            cv2.putText(img, str(_id), (x+5, y-5), FONT, 2, (255, 255, 255), 2)
            cv2.putText(img, str(confidence), (x+5, y+h-5), FONT, 2, (255, 255, 0), 1)

        f += 1
        timestamp = datetime.datetime.now()
        cv2.putText(
            img,
            timestamp.strftime("%A %d %B %Y %I:%M:%S%p"),
            (10, img.shape[0] - 10),
            FONT,
            1,
            (0, 255, 255),
            1
        )
        #logger.info(cam.get(cv2.CAP_PROP_FPS))
        #cv2.imwrite(f'{timestamp.seconds}.jpg', img)
        outFrame = img
        ready = True
        time.sleep(0.01)


if __name__ == '__main__':
    #vs = VideoStream(cam)
    #vs.start()
    t = threading.Thread(target=recognition)
    t.setName('Recognition')
    t.daemon = True
    t.start()

    app.run(host=IP, port=PORT, debug=True,
        threaded=True, use_reloader=False)
