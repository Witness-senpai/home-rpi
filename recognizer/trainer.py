import os

import cv2
import numpy as np
from PIL import Image

from detector import CASCADE_PATH, face_demo


# Path for face image database
MODEL_PATH = 'database/models/model.yml'
TEMP_IMG_PATH = 'database/_temp'
SAMPLES_FOR_TRAINING = 30

def main():
    face_demo()

    save_imgs_from_cam()

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(CASCADE_PATH)

    print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    faces, ids = get_imgs_and_labels(TEMP_IMG_PATH, detector)
    recognizer.train(faces, np.array(ids))

    # Save the model
    recognizer.write(MODEL_PATH)

    # Print the numer of faces trained and end program
    print(f"\n [INFO] {len(np.unique(ids))} faces trained. Exiting Program")

# function to get the images and label data
def get_imgs_and_labels(path, detector):
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if f != '.gitkeeper']     
    face_samples=[]
    ids = []

    for image_path in image_paths:
        img_PIL = Image.open(image_path).convert('L') # convert it to grayscale
        img_numpy = np.array(img_PIL,'uint8')

        _id = int(os.path.split(image_path)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)

        for (x, y, w, h) in faces:
            face_samples.append(img_numpy[y: y+h, x: x+w])
            ids.append(_id)

    return face_samples, ids

def save_imgs_from_cam(samples=SAMPLES_FOR_TRAINING):
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) # set video width
    cam.set(4, 480) # set video height

    face_detector = cv2.CascadeClassifier(CASCADE_PATH)

    users_count = int(input('\nEnter count of users: '))

    for face_id in range(users_count):
        print("\n [INFO] Initializing face capture. Look the camera and wait ...")
        # Initialize individual sampling face count
        count = 0

        while(True):
            ret, img = cam.read()
            img = cv2.flip(img, -1) # flip video image vertically
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)

            for (x,y,w,h) in faces:
                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
                count += 1

                # Save the captured image into the datasets folder
                file_name = f'{TEMP_IMG_PATH}/user.{face_id}.{count}.jpg'
                cv2.imwrite(file_name, gray[y:y+h,x:x+w])
                cv2.imshow('image', img)
                print(f'Complete {file_name}')

            k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
            if k == 27:
                break
            elif count >= samples:
                break

    # Do a bit of cleanup
    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
