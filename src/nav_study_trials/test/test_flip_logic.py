from nav_study_trials.flip_logic import FlipDetector


def feed(d, series):
    return [d.add_plan(t, length) for t, length in series]


def test_steady_plans_never_flip():
    out = feed(FlipDetector(), [(t, 12.0 - 0.2 * t) for t in range(20)])
    assert not any(f or tr for f, tr in out)


def test_small_jump_is_not_a_flip():
    out = feed(FlipDetector(), [(0, 10.0), (1, 12.9)])
    assert out == [(False, False), (False, False)]


def test_trigger_on_third_flip_within_window():
    out = feed(FlipDetector(), [(0, 9.0), (5, 16.0), (10, 9.0), (15, 16.0)])
    assert [f for f, _ in out] == [False, True, True, True]
    assert [tr for _, tr in out] == [False, False, False, True]


def test_flips_outside_window_do_not_trigger():
    out = feed(FlipDetector(), [(0, 9.0), (20, 16.0), (40, 9.0), (60, 16.0)])
    assert not any(tr for _, tr in out)


def test_reset_forgets_history():
    d = FlipDetector()
    feed(d, [(0, 9.0), (5, 16.0), (10, 9.0)])
    d.reset()
    assert d.add_plan(11, 16.0) == (False, False)
