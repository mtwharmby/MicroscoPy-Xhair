from dataclasses import dataclass
import logging

import cv2
import numpy as np
from wx import Colour       # TODO Remove this dependency

from .utils import convert_line_to_dashed_line


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
    available_cameras: tuple[str, ...]


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
        self.logger.debug("Capture stopped")


class CrosshairController:

    def __init__(self, model: DataModel):
        self.logger = logging.getLogger(__name__)
        self.model = model
        # This will be a tuple (w, h) reformatted from numpy array shape
        self.frame_shape = None
        self.recentre = True
        self.xhair_line_points = None
        self.grad_line_points = None
        self.grad_dash_line_points = None

    def draw_crosshair(self, frame):
        """
        Draw crosshair on frame
        """
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.frame_shape = (frame.shape[1], frame.shape[0])
        # N.B. frame.shape returns a tuple: (height, width, color)
        #      - frame is an ndarray

        if self.recentre:
            # Calculates points for crosshair lines. Only called when required
            # - i.e. when crosshair recentered
            self.xhair_line_points = [
                np.array(
                    [  # Vertical line
                        [self.frame_shape[0] * self.model.xhair_centre[0], 0],
                        [self.frame_shape[0] * self.model.xhair_centre[0],
                         self.frame_shape[1]]
                    ], np.int32),
                np.array(
                    [  # Horizontal line
                        [0, self.frame_shape[1] * self.model.xhair_centre[1]],
                        [self.frame_shape[0],
                         self.frame_shape[1] * self.model.xhair_centre[1]]
                    ], np.int32)
            ]

        cv2.polylines(
            frame, self.xhair_line_points, isClosed=False,
            color=self.model.xhair_colour,
            thickness=self.model.xhair_thickness
        )

        if self.model.xhair_hgrads:
            self.draw_grad_lines(frame)

        # All one-time actions, post recentre, complete. Switch off flag
        self.recentre = False

        return frame

    def draw_grad_lines(self, frame):
        """
        Draws graduated lines on frame placed relative to crosshair.
        """
        grad_dashed = True  # TODO Consider putting this in the model
        if self.recentre:
            self.calculate_grad_line_points()

            if grad_dashed:
                self.grad_dash_line_points = convert_line_to_dashed_line(
                    points_list=self.grad_line_points, n_dash=80
                )

        if grad_dashed:
            grad_line_points = self.grad_dash_line_points
        else:
            grad_line_points = self.grad_line_points

        cv2.polylines(
            frame, grad_line_points, isClosed=False,
            color=self.model.xhair_colour,
            thickness=self.model.xhair_thickness,
        )

    def recentre_crosshair(self, position, frame_size):
        """
        Calculates new fractional position for crosshair & updates model.
        """
        self.logger.debug(f"New crosshair coord: {position}")

        new_xhair_centre = tuple(
            position[i] / frame_size[i]
            for i in range(2)
        )
        self.logger.debug("Converted to new crosshair center: "
                          f"{new_xhair_centre}")
        self.model.xhair_centre = new_xhair_centre
        self.recentre = True

    def calculate_grad_line_points(self):
        """
        Calculate start and end positions of graduated lines.
        """
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
