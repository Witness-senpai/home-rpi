import logging
import time
import datetime
import threading
import sys, os
import random

from flask import Flask, render_template, Response
import cv2

from detector import CASCADE_PATH
from trainer import MODEL_PATH


FONT = cv2.FONT_HERSHEY_SIMPLEX

logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(message)s')

recognizer = cv2.face.LBPHFaceRecognizer_create()
faceCascade = cv2.CascadeClassifier(CASCADE_PATH)
try:
    recognizer.read(MODEL_PATH)
except Exception as ex:
    logger.warning(ex)

def one_frame_recognition(
        frame,
        scaleFactor,
        minNeighbors, 
        minWinSize,
        labels,
    ):  
        detected_names = []
        try:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        except Exception as ex:
            # Exception if other thread change some vars
            logger.warning(ex)
            exit()

        faces = faceCascade.detectMultiScale( 
            gray_frame,
            scaleFactor = scaleFactor,
            minNeighbors = minNeighbors,
            minSize = minWinSize,
        )

        for(x, y, w, h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 0, 255), 2)
            _id, confidence = recognizer.predict(gray_frame[y: y+h, x: x+w])
            # Check if confidence is less them 100 ==> "0" is perfect match 
            if (confidence < 100):
                if labels:
                    _id = labels[_id]
                confidence = f"{100 - confidence:.1f}%"
            else:
                _id = "unknown"
                confidence = f'{100 - confidence:.1f}%'
            detected_names.append(_id)
            cv2.putText(frame, str(_id), (x+5, y-5), FONT, 1, (255, 255, 255), 2)
            cv2.putText(frame, str(confidence), (x+5, y+h-5), FONT, 1, (255, 255, 0), 1)

        timestamp = datetime.datetime.now()
        cv2.putText(
            frame,
            timestamp.strftime("%A %d %B %Y %I:%M:%S%p"),
            (10, frame.shape[0] - 10),
            FONT,
            1,
            (0, 255, 255),
            1
        )

        return frame, detected_names