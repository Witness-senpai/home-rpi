import logging
import time
import threading
import sys, os
import random
import argparse
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '../recognizer'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../tools'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from flask import Flask, render_template, Response, request, redirect
import cv2

from trainer import one_frame_detect_face, train_model
from recognizer import one_frame_recognition, CASCADE_PATH, MODEL_PATH
from tbot.start import bot_start
from tbot.tbot import send_message
import tools

settings = tools.load_settings()

FONT = cv2.FONT_HERSHEY_SIMPLEX
IP = 'localhost'
PORT = 5000
logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(message)s')

app = Flask(__name__)

# Flag to stop iunfinity Recognition thread
sflag_recognition = False
outFrame = 0
ready = True
cam = cv2.VideoCapture(0)
cam.set(3, int(settings['resolution'].split('x')[0])) # set Width
cam.set(4, int(settings['resolution'].split('x')[1])) # set Height

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', **settings)

@app.route('/train', methods=['GET', 'POST'])
def train():
    train_name = request.form.get('train_name')
    go_train = False
    train_frame_count = request.form.get('train_frame_count')
    logger.info(request.form)
    if train_name and train_frame_count:
        start_photoset_thread(int(train_frame_count), train_name)
        go_train = True

    return render_template(
        'train.html',
        photo_is_ready=False,
        train_name='Test',
        go_train=go_train
    )

@app.route('/video_feed')
def video_feed():
    logger.info('Call generate()')
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/process_settings', methods=['GET', 'POST'])
def process_settings():
    global cam, sflag_recognition, settings
    target_user = request.form.get('target_user')
    triggers = request.form.getlist('triggers')
    resolution = request.form.get('resolution')
    orientation = request.form.get('orientation')
    recognition_status = request.form.get('recognition_status')
    screenshot = request.form.get('screenshot')
    telegram_token = request.form.get('telegram_token')
    to_default_settings = request.form.get('to_default_settings')
    video_duration = request.form.get('video_duration')
    logger.info(request.form)

    settings = tools.load_settings()
    if video_duration:
        settings['video_duration'] = video_duration
    if screenshot:
        ret, frame = cam.read()
        frame = cv2.flip(frame, int(settings['orientation']))
        make_screenshot(frame)
    if telegram_token:
        settings['telegram_token'] = telegram_token
        try:
            start_tbot_thread()
        except Exception as ex:
            logger.error(ex)
    if triggers:
        settings['triggers'] = []
        for el in triggers:
            settings['triggers'].append(el)
    if target_user:
        settings['target_user'] = target_user
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

    if to_default_settings:
        tools.to_default()
        settings = tools.load_settings()
    else:
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
    detected_names = []
    minWinSize = (100, 100)
    scaleFactor = 1.5
    minNeighbors = 5
    #n_frame = 0
    temp_trigger = True # Temporary var for testing
    while True:
        #n_frame += 1
        if sflag_recognition:
            break
        ready = False
        try:
            ret, frame = cam.read()
            frame = cv2.flip(frame, int(settings['orientation']))
            if settings['recognition_status'] == "True":
                outFrame, detected_names = one_frame_recognition(
                    frame,
                    scaleFactor,
                    minNeighbors,
                    minWinSize,
                    settings['rec_users'],
                )
            else:
                outFrame = frame
        except Exception as ex:
            logger.warning(ex)
            continue

        if settings['target_user'] in detected_names and temp_trigger:
            if '1' in settings['triggers']: # screenshot
                make_screenshot(frame)
            if '2' in settings['triggers']: # video
                start_videowritter_thread()
            if '3' in settings['triggers']: # telegram alert
                target_user = settings['target_user']
                send_alert(f'{target_user} person is detected!', cv2.imencode('.jpg', frame)[1].tostring())
            temp_trigger = False
        ready = True
        time.sleep(0.0001)
    logger.info('Stop recognition...')

def process_photoset_and_train(train_frame_count, username):
    """
    Functioun like a recognition(), but with saving dataset
    of faces and training.
    """
    logger.info('Start photoset')
    global outFrame, cam, sflag_recognition, settings, ready
    sflag_recognition = True # Stop recognition thread
    minWinSize = (100, 100)
    scaleFactor = 1.5
    minNeighbors = 5
    n_frame = 0
    while True:
        ready = False
        try:
            ret, frame = cam.read()
            frame = cv2.flip(frame, int(settings['orientation']))
            frame, isdetect = one_frame_detect_face(
                frame,
                scaleFactor,
                minNeighbors,
                minWinSize,
                username,
                n_frame,
                train_frame_count,
            )
            outFrame = frame
            if isdetect:
                n_frame += 1
        except Exception as ex:
            logger.warning(ex)
            continue
        ready = True
        time.sleep(0.0001)
        if n_frame > train_frame_count:
            break
    # Train model after getting photos
    train_model(user_id=len(settings['rec_users']))
    if username in settings['rec_users']:
        del settings['rec_users'][username]
    settings['rec_users'].append(username)
    tools.save_settings(settings)
    sflag_recognition = False
    start_rec_thread()

def start_rec_thread():
    t_recognition = threading.Thread(target=recognition)
    t_recognition.setName('Recognition')
    t_recognition.daemon = True
    t_recognition.start()

def start_tbot_thread():
    t_tbot = threading.Thread(target=bot_start)
    t_tbot.setName('Telegram bot')
    t_tbot.daemon = True
    t_tbot.start()

def start_photoset_thread(train_frame_count, username):
    t_photoset = threading.Thread(
        target=process_photoset_and_train,
        args=(train_frame_count, username,))
    t_photoset.setName('Photoset')
    t_photoset.daemon = True
    t_photoset.start()

def start_videowritter_thread():
    t_videowritter = threading.Thread(target=video_writter)
    t_videowritter.setName('Video writter')
    t_videowritter.daemon = True
    t_videowritter.start()

def video_writter():
    global outFrame, settings
    wh = settings['resolution'].split('x')
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    w = int(wh[0])
    h = int(wh[1])
    out = cv2.VideoWriter(f'database/cam_content/video/{now}.avi',
        cv2.VideoWriter_fourcc('M','J','P','G'),
        20.0, (w, h))

    logger.info(f'Make video recorder {now}')    
    start = time.time()
    while (int(time.time()) - start) < int(settings['video_duration']):
        out.write(outFrame)
    logger.info(f'Stop video recorder')    

def make_screenshot(frame):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f'Make screenshoot {now}')
    cv2.imwrite(f'database/cam_content/photo/{now}.jpg', frame)

def send_alert(text, bynary_photo):
    """
    In another thread send message after detection of unknown person
    """
    t_tbot_message = threading.Thread(
        target=send_message,
        args=(text, bynary_photo,)
    )
    t_tbot_message.setName('Telegram bot: send message')
    t_tbot_message.daemon = True
    t_tbot_message.start()

def main(host, port):
    start_rec_thread()

    if settings['telegram_token']:
        start_tbot_thread()

    app.run(host=host, port=port, debug=True,
        threaded=True, use_reloader=False)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-i",
        "--ip",
        type=str,
        default=IP,
        help="Host IP for running server")
    argparser.add_argument(
        "-p",
        "--port",
        type=str,
        default=PORT,
        help=f"Port for running server")
    args = argparser.parse_args()
    main(args.ip, args.port)
    
