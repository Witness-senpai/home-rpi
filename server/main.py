import logging
import time
import datetime
import threading
import sys, os
import random
sys.path.append(os.path.join(os.path.dirname(__file__), '../recognizer'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../tools'))

from flask import Flask, render_template, Response, request
import cv2

from detector import CASCADE_PATH
from trainer import MODEL_PATH
from recognizer import one_frame_recognition
import tools

settings = tools.load_settings()

FONT = cv2.FONT_HERSHEY_SIMPLEX
IP = 'localhost'
PORT = 8080

logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(message)s')

app = Flask(__name__)

# Flag to stop iunfinity Recognition thread
sflag_recognition = False
# Frame to output after recognition
flip = -1
# If True -- recognition is enable
do_reconize = True
outFrame = 0
ready = True
widht = 1024
height = 720
cam = cv2.VideoCapture(0)
cam.set(3, int(settings['resolution'].split('x')[0])) # set Width
cam.set(4, int(settings['resolution'].split('x')[1])) # set Height

@app.route('/')
def index():
    return render_template('index.html', **settings)

@app.route('/video_feed')
def video_feed():
    logger.info('Call generate()')
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/process_settings', methods=['POST'])
def process_settings():
    global cam, sflag_recognition, settings
    triggers = request.form.getlist('triggers')
    logger.info(triggers)
    resolution = request.form.get('resolution')
    logger.info(resolution)
    orientation = request.form.get('orientation')
    logger.info(orientation)
    recognition_status = request.form.get('recognition_status')
    logger.info(recognition_status)

    if triggers:
        settings['triggers'] = []
        for el in triggers:
            settings['triggers'].append(el)
    if resolution:
        sflag_recognition = True # Stop flag for thread with recognition
        settings['resolution'] = resolution
        wh = resolution.split('x')
        cam.set(3, int(wh[0])) # set Width
        cam.set(4, int(wh[1])) # set Height
        logger.info(f'Change resolution to {wh[0]}x{wh[1]}')
        sflag_recognition = False 
        start_rec_thread() # Start thread with recognition
    if orientation:
        settings['orientation'] = orientation
        logger.info(f'Change orientation to {orientation}')
    if recognition_status:
        settings['recognition_status'] = recognition_status
        logger.info(f'Change recognoition status: {recognition_status}')
    
    tools.save_settings(settings)
    logging.info(f'All settings: {settings}')
    return render_template('index.html', **settings)

def generate():
    global outFrame, ready
    while True:
        while not ready:
            pass
            #time.sleep(0.0001)
        flag, encodedImage = cv2.imencode(".jpg", outFrame)

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')

def recognition():
    global outFrame, cam, ready, sflag_recognition, settings
    labels = ['Person X']
    minWinSize = (100, 100)
    scaleFactor = 1.5
    minNeighbors = 5
    while True:
        if sflag_recognition:
            break
        ready = False
        try:
            ret, frame = cam.read()
            frame = cv2.flip(frame, int(settings['orientation']))
            if settings['recognition_status'] == "True":
                outFrame = one_frame_recognition(
                    frame,
                    scaleFactor,
                    minNeighbors,
                    minWinSize,
                    labels,
                )
            else:
                outFrame = frame
        except Exception as ex:
            logger.warning(ex)
            continue
        ready = True
        time.sleep(0.0001)

def start_rec_thread():
    t_recognition = threading.Thread(target=recognition)
    t_recognition.setName('Recognition')
    t_recognition.daemon = True
    t_recognition.start()

def main():
    start_rec_thread()

    app.run(host=IP, port=PORT, debug=True,
        threaded=True, use_reloader=False)

if __name__ == '__main__':
    main()
    
