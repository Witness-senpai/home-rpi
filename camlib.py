from picamera import PiCamera
from time import sleep

PICAM_PARAMS = dict(
    rotation=180,
    resolution=(1920, 1080),
    framerate=30,
)
PATH = "res"
DURATION = 10 # Продолжительность записи в секундах


class Camera():
    """
    Класс для удобного управления камерой
    через библиотеку picamera.
    
    piparams - словарь любых аргументов для класа PiCamera
    """
    def __init__(self, **piparams):
        # Учитываем, чтобы входные параметры замещали
        # дефолтные или только дополняли ихzz
        input_params = PICAM_PARAMS.copy()
        input_params.update(**piparams)
        self.camera = PiCamera()
        self.camera.rotation=180


    def capture_video(self,
                    path=PATH,
                    duration=DURATION,
                    ):
        """
        Метод для записи видео
        """
        self.camera.start_recording(path)
        sleep(DURATION)
        self.camera.stop_recording()


    def capture_photo(self, path=PATH):
        """
        Метод для сохранения снимка 
        """
        pass


def main():
    camera = Camera(**PICAM_PARAMS)

    #cam = PiCamera()
    #cam.rotation = 180 # Если камера перевёрнута
    #cam.resolution = (1920, 1080)
    #cam.framerate = 30
    
    camera.capture_video(path=PATH + 'vide0.h264')

if __name__ == "__main__":
    main()