"""Waypoint-mission bookkeeping for the waypoint_mission node (ROS-free so it can be unit-tested).

A mission is an ordered list of legs. Each leg gets at most `max_attempts` attempts; a leg that still fails is skipped (recorded as 'skipped') and the
mission continues with the next one. The mission ends when every leg is 'reached' or 'skipped'.
"""


class Mission:
    def __init__(self, waypoints, max_attempts=2):
        if not waypoints:
            raise ValueError("a mission needs at least one waypoint")
        self.waypoints, self.max_attempts = list(waypoints), max_attempts
        self.index, self.attempts, self.log = 0, 0, []

    @property
    def done(self):
        return self.index >= len(self.waypoints)

    def current(self):
        """The waypoint to drive to now (None when the mission is over); counts one attempt."""
        if self.done:
            return None
        self.attempts += 1
        return self.waypoints[self.index]

    def report(self, reached, duration_s):
        """Record the outcome of the attempt just made; returns 'reached', 'retry' or 'skipped'."""
        leg = self.index
        if reached:
            outcome = "reached"
        elif self.attempts < self.max_attempts:
            outcome = "retry"
        else:
            outcome = "skipped"
        self.log.append({"leg": leg, "attempt": self.attempts, "outcome": outcome, "duration_s": round(duration_s, 2)})
        if outcome != "retry":
            self.index += 1
            self.attempts = 0
        return outcome

    def summary(self):
        final = {}
        for e in self.log:
            final[e["leg"]] = e["outcome"]
        return {"legs": len(self.waypoints), "reached": sum(v == "reached" for v in final.values()),
                "skipped": sum(v == "skipped" for v in final.values())}
