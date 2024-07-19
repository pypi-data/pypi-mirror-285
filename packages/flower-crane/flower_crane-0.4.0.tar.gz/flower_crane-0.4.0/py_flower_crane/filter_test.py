import numpy as np
from numpy.testing import assert_array_equal
import flower_crane


def test_filter():
    bad_data = np.array([1, 2, 3, 1000, 5, 1000], dtype=int)
    
    allowed_offset = 500
    filtered, count = flower_crane.filter(bad_data, allowed_offset)

    clean_data = np.array([1, 2, 3, 3, 5, 5], dtype=int)
    assert_array_equal(filtered, clean_data)
    assert count == 2

