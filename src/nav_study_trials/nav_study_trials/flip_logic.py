"""Plan-flip detection used by the plan_flip_guard node (kept free of ROS so it can be unit-tested). Definitions: docs/protocol.md change (n)."""
from collections import deque

FLIP_JUMP_M = 3.0     # a flip: the global plan length changes by more than this between two consecutive plans
TRIGGER_FLIPS = 3     # a trigger: this many flips ...
TRIGGER_WINDOW_S = 30.0  # ... within this much simulated time


class FlipDetector:
    def __init__(self, jump=FLIP_JUMP_M, flips=TRIGGER_FLIPS, window=TRIGGER_WINDOW_S):
        self.jump, self.flips, self.window = jump, flips, window
        self.reset()

    def reset(self):
        """Forget everything (called when no goal is active)."""
        self.last_length = None
        self.flip_times = deque()

    def add_plan(self, t, length):
        """Register a new global plan. Returns (is_flip, is_trigger); a trigger needs `flips` flips inside the window."""
        is_flip = self.last_length is not None and abs(length - self.last_length) > self.jump
        self.last_length = length
        if not is_flip:
            return False, False
        self.flip_times.append(t)
        while self.flip_times and t - self.flip_times[0] > self.window:
            self.flip_times.popleft()
        return True, len(self.flip_times) >= self.flips
