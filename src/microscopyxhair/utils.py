import logging

import device
import numpy as np

logger = logging.getLogger(__name__)


def convert_line_to_dashed_line(points_list: list[np.array], n_dash=80):
    # n_dash needs to be odd to ensure we get a dash on each end of the line
    if not n_dash & 1:
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
            if not n & 1:
                # Add only every other line segment, starting with first,
                # to get dashes
                dash_points.append(np.array([point, next_point], np.int32))
            point = next_point

    return dash_points


def get_device_names() -> tuple[str, ...]:
    # getDeviceList() also returns the resolutions the camera can show.
    dev_names = [d[0] for d in device.getDeviceList()]
    return tuple(dev_names)
