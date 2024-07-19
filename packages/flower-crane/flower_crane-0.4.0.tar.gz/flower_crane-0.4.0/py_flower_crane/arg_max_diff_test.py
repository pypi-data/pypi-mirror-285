import numpy as np

import flower_crane


def test_arg_max_positive_diff():
    a = np.array([1, 2, 3, 2, 1], dtype=int)
    res = flower_crane.arg_max_positive_diff(a)
    assert res == (0, 2)

    a = np.array([3, 4, 8, 9, 2, 11, 0, 4, 4, 4, 10, 2, 3, 4, 5], dtype=int)
    res = flower_crane.arg_max_positive_diff(a)
    assert res == (6, 10)

    a = np.array([], dtype=int)
    res = flower_crane.arg_max_positive_diff(a)
    assert res is None

    a = np.array([1], dtype=int)
    res = flower_crane.arg_max_positive_diff(a)
    assert res is None

    a = np.array([8, 3, 2, 1, 0], dtype=int)
    res = flower_crane.arg_max_positive_diff(a)
    assert res is None
