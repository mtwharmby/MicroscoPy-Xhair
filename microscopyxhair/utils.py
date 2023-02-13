import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def convert_to_dashed_line_points(points_list: list[np.array], n_dash=80):
    # n_dash needs to be odd to ensure we get a dash on each end of the line
    if n_dash % 2:
        n_dash = n_dash + 1

    dash_points = []
    for pair in points_list:
        logger.debug(f"Converting line ({pair[0]} -> {pair[1]}) to dashed "
                     "line")
        line = pair[1] - pair[0]
        line_length = np.linalg.norm(line)
        unit_line = line / line_length
        dash = line_length / n_dash
        new_line = unit_line * dash

        point = pair[0]
        for n in range(0, n_dash):
            next_point = point + new_line
            if n & 1:
                # Add only every second line segment to get dashes
                dash_points.append(np.array([point, next_point], np.int32))
            point = next_point

    return dash_points


def dashed_polylines(frame, points_list: list[np.array], colour, thickness,
                     n_dash=80, use_cached=False, cached=None):
    if not use_cached:
        dash_points = convert_to_dashed_line_points(points_list, n_dash)
    else:
        dash_points = cached

    cv2.polylines(
        frame, dash_points, isClosed=False,
        color=colour,
        thickness=thickness,
    )

    return dash_points
