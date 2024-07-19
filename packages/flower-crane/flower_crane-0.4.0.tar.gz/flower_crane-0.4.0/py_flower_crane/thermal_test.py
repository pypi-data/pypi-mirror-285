import numpy as np

import flower_crane


def test_compute_thermals():
    scoring_windows = [[0, 10]]
    circling = np.array(
        [False, False, False, True, True, True, False, False, False, False]
    )
    raw_time = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    bearing_change_rate = np.array(
        [0.0, 90.0, 180.0, 270.0, 0.0, 270.0, 0.0, 0.0, 0.0, 0.0]
    )
    abs_bearing_change_rate = np.array(
        [0.0, 90.0, 180.0, 270.0, 0.0, 270.0, 0.0, 0.0, 0.0, 0.0]
    )
    min_time_for_thermal = 1
    min_time_for_glide = 1
    min_bearing_change_thermal = 90.0
    min_abs_bearing_change_thermal = 90.0
    result = flower_crane.compute_thermals(
        scoring_windows,
        circling,
        raw_time,
        bearing_change_rate,
        abs_bearing_change_rate,
        min_time_for_thermal,
        min_time_for_glide,
        min_bearing_change_thermal,
        min_abs_bearing_change_thermal,
    )
    assert result == ([[0, 3], [6, 10]], [[3, 6]])
