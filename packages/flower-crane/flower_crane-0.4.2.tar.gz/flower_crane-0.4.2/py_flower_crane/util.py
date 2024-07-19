import json

import numpy as np

MAX_DIST_KM = 2.0
MAX_DIST_DEGREE = MAX_DIST_KM / 111.0
MAX_ALT_DIST = 500


def get_data():
    with open("data/line1.json", encoding="utf-8") as f:
        line1 = json.load(f)
    with open("data/line2.json", encoding="utf-8") as f:
        line2 = json.load(f)
    with open("data/alt1.json", encoding="utf-8") as f:
        alt1 = json.load(f)
    with open("data/alt2.json", encoding="utf-8") as f:
        alt2 = json.load(f)
    with open("data/time1.json", encoding="utf-8") as f:
        time1 = json.load(f)
    with open("data/time2.json", encoding="utf-8") as f:
        time2 = json.load(f)
    return (
        np.array(line1),
        np.array(line2),
        np.array(alt1),
        np.array(alt2),
        np.array(time1),
        np.array(time2),
        MAX_DIST_DEGREE**2,
        MAX_ALT_DIST,
    )


truth = [
    1660125112,
    1660137176,
    1660137184,
    1660139832,
    1660139868,
    1660143536,
    1660143788,
    1660147200,
]
