import cv2
import numpy as np


def dashed_lines(frame, points_list: list[np.array], colour, thickness,
                 n_dash=80):
    # n_dash needs to be odd to ensure we get a dash on each end of the line
    if n_dash % 2:
        n_dash = n_dash + 1

    dash_points = []
    for pair in points_list:
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

    cv2.polylines(
        frame, dash_points, isClosed=False,
        color=colour,
        thickness=thickness,
    )
