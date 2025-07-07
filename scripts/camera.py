import os
import cv2

class Camera(object):
    def __init__(self):
        path = os.path.join(os.path.expanduser('~'), 'PycharmProjects', 'guess-the-song-game', 'data', 'videos', 'Dubioza Kolektiv - Balkan Boys (Official Video).mp4')
        self.capture = cv2.VideoCapture(path)

        if not self.capture.isOpened():
            raise ValueError("Error opening video file")


    def get_frame(self):
        ret, frame = self.capture.read()
        (flag, encoded_image) = cv2.imencode(".jpg", frame)
        # print(type(frame))
        # print(frame)
        return bytearray(encoded_image) if ret else b''
