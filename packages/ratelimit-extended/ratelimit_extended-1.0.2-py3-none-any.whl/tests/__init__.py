import unittest


class Clock(object):
    def __init__(self) -> None:
        self.reset()

    def __call__(self) -> float:
        return self.now

    def reset(self) -> None:
        self.now = 0

    def increment(self, num: int = 1) -> None:
        self.now += num


clock = Clock()

__all__ = ["unittest", "clock"]
