from dataclasses import dataclass
import logging

import cv2
import numpy as np
from wx import Colour       # TODO Remove this dependency


@dataclass
class DataModel:
    xhair_colour: Colour
    xhair_thickness: int
    xhair_centre: tuple[int, int]
    xhair_hgrads: bool
    xhair_hgrad_n: int
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
        # This will be a tuple (w, h) reformatted from numpy array shape
        self.frame_shape = None
        self.recentre = True
        self.grad_line_points = None

    def draw_crosshair(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.frame_shape = (frame.shape[1], frame.shape[0])
        # N.B. frame.shape returns a tuple: (height, width, color)
        #      - frame is an ndarray
        cv2.line(  # Vertical line
            frame,
            (int(self.frame_shape[0] * self.model.xhair_centre[0]), 0),
            (
                int(self.frame_shape[0] * self.model.xhair_centre[0]),
                self.frame_shape[1]
            ),
            color=self.model.xhair_colour,
            thickness=self.model.xhair_thickness
        )
        cv2.line(  # Horizontal line
            frame,
            (0, int(self.frame_shape[1] * self.model.xhair_centre[1])),
            (
                self.frame_shape[0],
                int(self.frame_shape[1] * self.model.xhair_centre[1])
            ),
            color=self.model.xhair_colour,
            thickness=self.model.xhair_thickness
        )

        if self.model.xhair_hgrads:
            self.draw_grad_lines(frame)

        # All one-time actions, post recentre, complete. Switch off flag
        self.recentre = False

        return frame

    def draw_grad_lines(self, frame):
        if self.recentre:
            self.calculate_grad_line_positions()

        cv2.polylines(
            frame, self.grad_line_points, isClosed=False,
            color=self.model.xhair_colour,
            thickness=self.model.xhair_thickness
        )

    def recentre_crosshair(self, position, frame_size):
        self.logger.debug(f"New crosshair coord: {position}")

        new_xhair_centre = tuple(
            position[i] / frame_size[i]
            for i in range(2)
        )
        self.logger.debug("Converted to new crosshair center: "
                          f"{new_xhair_centre}")
        self.model.xhair_centre = new_xhair_centre
        self.recentre = True

    def calculate_grad_line_positions(self):
        # n refers to number of lines above or below the crosshair
        # We need 2n + 2 divisions to draw these
        frac_grad_sep = 1 / (2 * (self.model.xhair_hgrad_n + 1))

        self.grad_line_points = []
        for n in range(self.model.xhair_hgrad_n):
            # Nr. fractional separations to add/sub. from crosshair centre
            n_frac_seps = (n + 1) * frac_grad_sep
            for fac in [-1, 1]:
                # Calculate fractional position of line then its absolute by
                # multiplying by frame size
                frac_line_pos = (self.model.xhair_centre[1]
                                 + (fac * n_frac_seps))
                line_pos = self.frame_shape[1] * frac_line_pos

                # This array is two points: line begin & end
                pts = np.array(
                    [
                        [0, line_pos],
                        [self.frame_shape[0], line_pos]
                    ], dtype=np.int32
                )
                self.grad_line_points.append(pts)

        self.logger.debug("New graduated line positions:"
                          f"\n{self.grad_line_points}")
