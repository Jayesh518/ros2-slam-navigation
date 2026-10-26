import math

import pytest

from nav_study_trials import metrics as m


def test_path_length_straight_and_corner():
    assert m.path_length([(0, 0), (3, 4)]) == pytest.approx(5.0)
    assert m.path_length([(0, 0), (1, 0), (1, 1)]) == pytest.approx(2.0)
    assert m.path_length([]) == 0 and m.path_length([(1, 1)]) == 0


def test_classify_outcome_cases():
    assert m.classify_outcome("SUCCEEDED", False, 0.10) == (True, "")
    assert m.SUCCESS_TOLERANCE_M == 0.5
    assert m.classify_outcome("SUCCEEDED", False, 0.5) == (True, "")  # exactly at the tolerance counts
    assert m.classify_outcome("SUCCEEDED", False, 0.51) == (False, "goal_not_reached_by_ground_truth")
    assert m.classify_outcome("SUCCEEDED", False, 0.30, tolerance_m=0.25) == (False, "goal_not_reached_by_ground_truth")
    assert m.classify_outcome("ABORTED", False, 0.10) == (False, "nav2_aborted")
    assert m.classify_outcome("SUCCEEDED", True, 0.0) == (False, "timeout")  # timeout wins


def test_collisions_ignore_ground_and_group_episodes():
    ev = [(1.0, "wheel", "ground_plane::link::collision"), (2.0, "base", "walls::link::e"), (2.2, "base", "walls::link::e"),
          (2.4, "base", "walls::link::e"), (5.0, "base", "walls::link::e"), (5.1, "wheel", "walls::link::e")]
    assert m.count_collisions(ev) == 3  # one long episode, a second later episode, a different robot part
    assert m.count_collisions([]) == 0
    assert m.count_collisions([(0.0, "wheel", "ground_plane::link::collision")]) == 0


def test_collisions_order_independent():
    ev = [(5.0, "base", "w"), (2.0, "base", "w"), (2.2, "base", "w")]
    assert m.count_collisions(ev) == 2


def test_recoveries_count_only_activations_of_recovery_nodes():
    ch = [("Spin", "IDLE", "RUNNING"), ("Spin", "RUNNING", "SUCCESS"), ("Spin", "SUCCESS", "IDLE"),
          ("Wait", "IDLE", "RUNNING"), ("FollowPath", "IDLE", "RUNNING"), ("BackUp", "IDLE", "RUNNING"),
          ("ClearLocalCostmap-Subtree", "IDLE", "SUCCESS"), ("ClearLocalCostmap-Context", "IDLE", "SUCCESS")]
    assert m.count_recoveries(ch) == 4


def test_localisation_stats_and_failure_window():
    assert m.localisation_stats([0.1, 0.3, 0.2]) == (0.3, pytest.approx(0.2))
    assert all(math.isnan(v) for v in m.localisation_stats([]))
    errs = [(0.0, 0.9), (50.0, 0.1), (95.0, 0.2), (115.0, 0.6)]
    assert m.localisation_failure(errs, t_end=120.0) is True       # 0.6 m inside the last 10 s? 115 is within 110..120
    assert m.localisation_failure(errs, t_end=100.0) is False      # the early 0.9 m is outside the window
    assert m.localisation_failure([], t_end=10.0) is False


def test_frame_conversion_round_trip():
    al = {"x": 0.22, "y": -0.09, "yaw": 0.0422}
    for p in [(1.0, 2.0, 0.3), (-3.5, 0.0, -1.0)]:
        back = m.map_to_world(*m.world_to_map(*p, al), al)
        assert back == pytest.approx(p)
    assert m.map_to_world(0, 0, 0, {"x": 1.0, "y": 2.0, "yaw": 0.0}) == (1.0, 2.0, 0.0)


def test_wilson_interval_known_values():
    lo, hi = m.wilson_interval(10, 20)
    assert (lo, hi) == (pytest.approx(0.299, abs=0.002), pytest.approx(0.701, abs=0.002))
    lo, hi = m.wilson_interval(20, 20)
    assert hi == pytest.approx(1.0) and lo == pytest.approx(0.839, abs=0.002)
    assert all(math.isnan(v) for v in m.wilson_interval(0, 0))
