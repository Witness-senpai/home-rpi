import numpy as np
import cv2

CASCADE_PATH = '/home/pi/Public/opencv/opencv-4.2.0/data/haarcascades/haarcascade_frontalface_default.xml' 

# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades
faceCascade = cv2.CascadeClassifier(CASCADE_PATH)

cap = cv2.VideoCapture(0)
cap.set(3, 640) # set Width
cap.set(4, 480) # set Height

while True:
    ret, img = cap.read()
    img = cv2.flip(img, -1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.5,
        minNeighbors=3,     
        minSize=(50, 50)
    )

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        roi_gray = gray[y: y+h, x: x+w]
        roi_color = img[y: y+h, x: x+w]
        
    cv2.imshow('Detect faces', img)

    k = cv2.waitKey(30) & 0xff
    if k == 27: # press 'ESC' to quit
        break

cap.release()
cv2.destroyAllWindows()