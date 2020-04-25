import logging
import time
import threading

from flask import Flask, render_template, Response
import cv2


IP = 'localhost'
PORT = 8080

logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(message)s')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen(cv2.VideoCapture(-1)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def gen(camera):
    """Video streaming generator function."""
    while True:
        ret, frame = camera.read()
        flag, encodedImage = cv2.imencode(".jpg", cv2.flip(frame, -1))
        cv2.imwrite('kok.jpg', cv2.flip(frame, -1))
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')

if __name__ == '__main__':
    app.run(host=IP, port=PORT, debug=True)