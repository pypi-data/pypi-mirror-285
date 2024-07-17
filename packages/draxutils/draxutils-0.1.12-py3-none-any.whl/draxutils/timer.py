# simple_timer.py

import time
from contextlib import ContextDecorator

class Timer(ContextDecorator):
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.laps = []

    def start(self):
        self.start_time = time.time()
        self.laps = []
        return self

    def end(self):
        self.end_time = time.time()
        return self.elapsed

    def lap(self, lap_name=None):
        current_time = time.time()
        if self.start_time is None:
            self.start()
        lap_time = current_time - (self.laps[-1][1] if self.laps else self.start_time)
        self.laps.append((lap_name, current_time, lap_time))
        return lap_time

    def __enter__(self):
        return self.start()

    def __exit__(self, *exc):
        self.end()
        return False

    def __str__(self):
        if self.end_time is None:
            return f"Timer running for {self.elapsed:.6f} seconds"
        return f"Total time: {self.elapsed:.6f} seconds"

    @property
    def elapsed(self):
        if self.start_time is None:
            return 0
        end = self.end_time if self.end_time is not None else time.time()
        return end - self.start_time

timer = Timer()  # Create a global timer instance for easy import

# Usage as context manager
def time_this():
    with timer:
        yield

# Usage as decorator
def timed(func):
    @Timer()
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper