from dataclasses import dataclass

import cv2
from wx import Colour       # TODO Remove this dependency


@dataclass
class DataModel:
    xhair_colour: Colour
    xhair_thickness: int
    xhair_centre: tuple[int, int]
    camera_id: int
    framerate: int
    capture_active: bool
    available_cameras: tuple


class CaptureController:

    def __init__(self, model: DataModel):
        self.model = model
        self.capture = None

    def start_capture(self):
        self.capture = cv2.VideoCapture(self.model.camera_id)
        if not self.capture.isOpened():
            raise RuntimeError("Cannot open camera")
        self.model.capture_active = True

    def stop_capture(self):
        self.capture.release()
        self.model.capture_active = False
