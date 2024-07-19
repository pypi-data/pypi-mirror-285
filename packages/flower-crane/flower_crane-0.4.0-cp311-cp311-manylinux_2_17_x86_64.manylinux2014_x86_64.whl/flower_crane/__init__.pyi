import numpy as np


def viterbi_decode(init_probs: tuple[float, float], transition_probs: tuple[tuple[float, float], tuple[float, float]], emissions: np.ndarray) -> np.ndarray:
    ...


def compute_thermals(
        scoring_windows: list[list[int]],
        circling: np.ndarray,
        raw_times: np.ndarray,
        bearing_change_rate: np.ndarray,
        abs_bearing_change_rate: np.ndarray,
        min_time_for_thermal: int,
        min_time_for_glide: int,
        min_bearing_change_thermal: float,
        min_abs_bearing_change_thermal: float,
) -> tuple[list[list[int]], list[list[int]]]:
    ...


def apply_time_limit(
        array: np.ndarray,
        raw_times: np.ndarray,
        min_time: int,
        base_state: bool,
) -> list[bool]:
    ...


def arg_max_positive_diff(
    array: np.ndarray,
) -> tuple[int, int] | None:
    ...


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
    ...
    
    
def filter(data: np.ndarray, allowed_offset: int) -> tuple[list[float], int]:
    ...