import numpy as np
from numpy.testing import assert_array_equal
import flower_crane


def test_filter():
    bad_data = np.array([1.0, 2.0, 3.0, 1000.0, 5.0, 1000.0])

    allowed_offset = 500.0
    filtered, count = flower_crane.filter(bad_data, allowed_offset)

    clean_data = np.array([1.0, 2.0, 3.0, 3.0, 5.0, 5.0])
    assert_array_equal(filtered, clean_data)
    assert count == 2
