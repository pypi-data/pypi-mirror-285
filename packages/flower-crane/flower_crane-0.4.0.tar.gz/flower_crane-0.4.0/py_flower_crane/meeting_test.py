from meeting import find_meeting
from util import get_data, truth

import flower_crane

MAX_DIST_KM = 2.0
MAX_DIST_DEGREE = MAX_DIST_KM / 111.0
MAX_ALT_DIST = 500


def test_find_meeting_py():
    meeting, _ = find_meeting(*get_data())
    assert meeting == truth, f"Found: {meeting}"


def test_find_meeting():
    meeting, _ = flower_crane.find_meeting(*get_data())
    assert meeting == truth, f"Found: {meeting}"
