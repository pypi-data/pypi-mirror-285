import numpy as np

import flower_crane


def test_arg_max_positive_diff():
    bearing = np.array([0.0, 90.0, 180.0, 270.0, 0.0, 270.0, 0.0])
    raw_time = np.array([0, 1, 2, 3, 4, 5, 6])
    ratio = 1
    result = flower_crane.bearing_change_rate(bearing, raw_time, ratio)
    assert result == [0.0, 90.0, 90.0, 90.0, 90.0, -90.0, 90.0]
