# pylint: disable=C0200
import numpy as np


def find_meeting(
    line1: np.ndarray,
    line2: np.ndarray,
    alt1: np.ndarray,
    alt2: np.ndarray,
    time1: np.ndarray,
    time2: np.ndarray,
    max_dist_degree_squared: float,
    max_alt_dist: int,
) -> tuple[list[int], float]:
    assert len(time2) == len(alt2)
    assert len(time2) == len(line2)
    assert len(line1) == len(alt1) == len(time1)

    # very simple theta calculation, but we don't need more for short distances
    theta: float = np.cos(np.radians(line1[0][1]))
    meeting = []
    started: bool = False
    i: int = 0
    min_distance: float = 10000.0
    for j in range(len(time2)):
        # we always expect source time to be ahead
        while time1[i] < time2[j] and i < len(time1) - 1:
            i += 1
        if i == len(time1) - 1:
            break
        dist = ((line1[i, 0] - line2[j, 0]) * theta) ** 2 + (
            line1[i, 1] - line2[j, 1]
        ) ** 2
        if (
            np.abs(alt1[i] - alt2[j]) < max_alt_dist
            and dist < max_dist_degree_squared
            and time2[min(len(time2) - 1, j + 1)] - time2[j]
            < 20  # check if time jump to next chunk
        ):
            if dist < min_distance:
                min_distance = dist
            if not started:
                start_time = time1[i]
                started = True
            else:
                continue
        elif not started:
            continue
        else:
            started = False
            end_time = time1[i]
            if start_time != end_time:
                if len(meeting) >= 1 and start_time == meeting[-1]:
                    meeting[-1] = end_time
                else:
                    meeting.append(start_time)
                    meeting.append(end_time)

    if started:
        end_time = time1[i]
        meeting.append(start_time)
        meeting.append(end_time)

    return meeting, min_distance
