import cv2

class Camera(object):
    def __init__(self, obs_cam_index: int):
        self.capture = cv2.VideoCapture(obs_cam_index)

        if not self.capture.isOpened():
            raise ValueError("Error opening video file")


    def get_frame(self):
        ret, frame = self.capture.read()
        (flag, encoded_image) = cv2.imencode(".jpg", frame)
        return bytearray(encoded_image) if ret else b''
