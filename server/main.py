import logging
import time
import datetime
import threading
import sys, os
import random
sys.path.append(os.path.join(os.path.dirname(__file__), '../recognizer'))

from flask import Flask, render_template, Response
import cv2

from recognizer_test import VideoStream
from detector import CASCADE_PATH
from trainer import MODEL_PATH
from recognizer import one_frame_recognition


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
cam.set(3, 1024) # set Width
cam.set(4, 720) # set Height

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    logger.info('Call generate()')
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def generate():
    global outFrame, ready
    while True:
        while not ready:
            pass
        flag, encodedImage = cv2.imencode(".jpg", outFrame)

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')


def recognition():
    global outFrame, cam, ready
    labels = ['Person X']
    minWinSize = (100, 100)
    flip = -1
    scaleFactor = 1.5
    minNeighbors = 5
    while True:
        ready = False
        try:
            ret, frame = cam.read()
            frame = cv2.flip(frame, flip)
        except Exception as ex:
            continue
        outFrame = one_frame_recognition(
            frame,
            scaleFactor,
            minNeighbors,
            minWinSize,
            labels,
        )
        ready = True
        time.sleep(0.001)

def kok():
    global cam
    while True:
        s = input('kok?')
        if s == '1':
            cam.release()
        elif s == '2':
            cam = cv2.VideoCapture(0)
            cam.set(3, 1024) # set Width
            cam.set(4, 720) # set Height


if __name__ == '__main__':
    t = threading.Thread(target=recognition)
    t.setName('Recognition')
    #t.daemon = True
    t.start()

    t2 = threading.Thread(target=kok)
    #t2.daemon = True
    t2.start()

    app.run(host=IP, port=PORT, debug=True,
        threaded=True, use_reloader=False)
