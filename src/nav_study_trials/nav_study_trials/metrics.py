"""Metric definitions of the study (docs/protocol.md section 6) as plain functions, so they can be unit-tested without ROS.

Everything here works on lists of numbers; the runner collects the data and calls these functions.
"""
import math

SUCCESS_TOLERANCE_M = 0.5  # ground-truth arrival tolerance; Nav2 itself stops within 0.25 m of its own estimate (protocol change log (g))
TIMEOUT_S = 120.0
LOC_ERROR_THRESHOLD_M = 0.5
LOC_WINDOW_S = 10.0
# Activations of these behaviour-tree nodes count as recovery events (default NavigateToPose tree, RecoveryActions subtree).
RECOVERY_NODES = ("ClearLocalCostmap-Subtree", "Spin", "Wait", "BackUp")


def path_length(points):
    """Length in metres of the polyline through (x, y) points."""
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def goal_error(final_xy, goal_xy):
    return math.dist(final_xy, goal_xy)


def classify_outcome(nav2_status, timed_out, final_error_m, tolerance_m=SUCCESS_TOLERANCE_M):
    """Return (success, failure_reason). Success needs the ground-truth position within tolerance AND Nav2 reporting SUCCEEDED, before the timeout."""
    if timed_out:
        return False, "timeout"
    if nav2_status != "SUCCEEDED":
        return False, f"nav2_{str(nav2_status).lower()}"
    if final_error_m > tolerance_m:
        return False, "goal_not_reached_by_ground_truth"
    return True, ""


def count_collisions(events, gap_s=0.5, ground_marker="ground_plane"):
    """Count collision episodes. events: iterable of (time_s, robot_collision, other_collision), one per contact message entry.

    Contacts with the ground are ignored. Entries between the same pair separated by at most gap_s belong to one episode.
    """
    last = {}
    count = 0
    for t, mine, other in sorted(events, key=lambda e: e[0]):
        if ground_marker in other:
            continue
        key = (mine, other)
        if key not in last or t - last[key] > gap_s:
            count += 1
        last[key] = t
    return count


def count_recoveries(status_changes, nodes=RECOVERY_NODES):
    """Count recovery activations. status_changes: iterable of (node_name, previous_status, current_status)."""
    return sum(1 for name, prev, cur in status_changes if name in nodes and prev == "IDLE" and cur != "IDLE")


def localisation_stats(errors):
    """(max, mean) of a list of localisation errors in metres; (nan, nan) for an empty list."""
    if not errors:
        return math.nan, math.nan
    return max(errors), sum(errors) / len(errors)


def localisation_failure(timed_errors, t_end, window_s=LOC_WINDOW_S, threshold_m=LOC_ERROR_THRESHOLD_M):
    """True if the AMCL-to-truth error exceeded the threshold at any time in the last window_s seconds. timed_errors: list of (time_s, error_m)."""
    return any(e > threshold_m for t, e in timed_errors if t_end - window_s <= t <= t_end)


def map_to_world(x, y, yaw, alignment):
    """Apply configs/map_alignment.yaml (p_world = R(yaw) p_map + t) to a map-frame pose; returns (x, y, yaw) in the world frame."""
    c, s = math.cos(alignment["yaw"]), math.sin(alignment["yaw"])
    return c * x - s * y + alignment["x"], s * x + c * y + alignment["y"], yaw + alignment["yaw"]


def world_to_map(x, y, yaw, alignment):
    """Inverse of map_to_world."""
    c, s = math.cos(alignment["yaw"]), math.sin(alignment["yaw"])
    dx, dy = x - alignment["x"], y - alignment["y"]
    return c * dx + s * dy, -s * dx + c * dy, yaw - alignment["yaw"]


def wilson_interval(successes, n, z=1.96):
    """Wilson score interval for a proportion; (lo, hi)."""
    if n == 0:
        return math.nan, math.nan
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return centre - half, centre + half
