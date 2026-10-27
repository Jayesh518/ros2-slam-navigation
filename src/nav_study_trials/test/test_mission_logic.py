import pytest

from nav_study_trials.mission_logic import Mission


def test_all_legs_reached_first_try():
    m = Mission([1, 2, 3])
    while not m.done:
        m.current()
        assert m.report(True, 10.0) == "reached"
    assert m.summary() == {"legs": 3, "reached": 3, "skipped": 0}


def test_failed_leg_is_retried_once_then_skipped():
    m = Mission(["a", "b"], max_attempts=2)
    assert m.current() == "a" and m.report(False, 5) == "retry"
    assert m.current() == "a" and m.report(False, 5) == "skipped"
    assert m.current() == "b" and m.report(True, 5) == "reached"
    assert m.done and m.summary() == {"legs": 2, "reached": 1, "skipped": 1}


def test_retry_that_succeeds_counts_as_reached():
    m = Mission(["a"])
    m.current(); m.report(False, 1)
    m.current(); m.report(True, 1)
    assert m.summary() == {"legs": 1, "reached": 1, "skipped": 0}


def test_empty_mission_is_rejected():
    with pytest.raises(ValueError):
        Mission([])
