import time

import flower_crane
from py_flower_crane.meeting import find_meeting
from py_flower_crane.util import get_data

N = 100


def bench_flower_crane():
    data = get_data()
    start = time.time()
    for _ in range(N):
        _ = flower_crane.find_meeting(*data)
    end = time.time()
    print(f"Rust: {N} iterations in {end-start:.4f} seconds")


def bench_py_flower_crane():
    data = get_data()
    start = time.time()
    for _ in range(N):
        _ = find_meeting(*data)
    end = time.time()
    print(f"Python: {N} iterations in {end-start:.4f} seconds")


if __name__ == "__main__":
    bench_py_flower_crane()
    bench_flower_crane()
