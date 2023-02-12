from dataclasses import dataclass
import logging

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
        self.logger = logging.getLogger(__name__)
        self.model = model
        self.capture = None

    def start_capture(self):
        self.capture = cv2.VideoCapture(self.model.camera_id)
        if not self.capture.isOpened():
            raise RuntimeError("Cannot open camera")
        self.model.capture_active = True
        self.logger.debug("Capture started")

    def stop_capture(self):
        self.capture.release()
        self.model.capture_active = False
        self.logger("Capture stopped")


class CrosshairController:

    def __init__(self, model: DataModel):
        self.logger = logging.getLogger(__name__)
        self.model = model

    def draw_crosshair(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # N.B. frame.shape returns a tuple: (height, width, color)
        #      - frame is an ndarray
        cv2.line(  # Vertical line
            frame,
            (int(frame.shape[1] * self.model.xhair_centre[0]), 0),
            (int(frame.shape[1] * self.model.xhair_centre[0]), frame.shape[0]),
            color=self.model.xhair_colour,
            thickness=self.model.xhair_thickness
        )
        cv2.line(  # Horizontal line
            frame,
            (0, int(frame.shape[0] * self.model.xhair_centre[1])),
            (frame.shape[1], int(frame.shape[0] * self.model.xhair_centre[1])),
            color=self.model.xhair_colour,
            thickness=self.model.xhair_thickness
        )
        return frame
