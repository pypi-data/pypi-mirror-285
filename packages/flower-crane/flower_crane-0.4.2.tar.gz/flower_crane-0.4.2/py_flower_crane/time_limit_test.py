import numpy as np

import flower_crane


def test_time_limit():
    array = np.array(
        [
            True,
            False,
            True,
            True,
            False,
            True,
            True,
            True,
            False,
            False,
            True,
            False,
            False,
            True,
            True,
        ]
    )
    raw_time = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 15, 16, 17, 18])
    min_time = 3
    base_state = False
    result = flower_crane.apply_time_limit(array, raw_time, min_time, base_state)
    assert result == [
        True,
        False,
        False,
        False,
        False,
        True,
        True,
        True,
        False,
        False,
        False,
        False,
        False,
        True,
        True,
    ]

    base_state = True
    result = flower_crane.apply_time_limit(array, raw_time, min_time, base_state)
    assert result == [
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        False,
        False,
        True,
        True,
        True,
        True,
        True,
    ]
