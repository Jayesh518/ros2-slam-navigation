import numpy as np
import pytest

from nav_study_trials import analysis as a


def test_bootstrap_is_reproducible_and_brackets_the_mean():
    d = [1, 0, 0, 1, 1, 0, 1, 1, 0, 1]
    r1, r2 = a.paired_bootstrap(d), a.paired_bootstrap(d)
    assert r1 == r2
    mean, lo, hi = r1
    assert mean == pytest.approx(0.6) and lo < mean < hi


def test_bootstrap_constant_differences_have_zero_width():
    mean, lo, hi = a.paired_bootstrap([0.2] * 20)
    assert mean == lo == hi == pytest.approx(0.2)


def test_empty_input_gives_nan():
    assert all(np.isnan(v) for v in a.paired_bootstrap([]))


def test_success_rule_needs_both_size_and_interval():
    big_clear = [1] * 20 + [0] * 10          # +0.67, interval far from 0
    assert a.decide_success(big_clear)["verdict"] == "real increase"
    small_clear = [1] * 3 + [0] * 57         # +0.05: interval may exclude 0 but below 10 points
    assert a.decide_success(small_clear)["verdict"] == "no clear effect"
    big_noisy = [1, -1, 1, -1, 1, -1, 1, 0, 0, 0]  # mean +0.1 but interval includes 0
    assert a.decide_success(big_noisy)["mean_diff"] == pytest.approx(0.1)
    assert a.decide_success(big_noisy)["verdict"] == "no clear effect"
    assert a.decide_success([-1] * 15 + [0] * 5)["verdict"] == "real decrease"


def test_continuous_rule_uses_five_percent_of_baseline():
    base = [40.0] * 20
    assert a.decide_continuous([3.0] * 20, base)["verdict"] == "real increase"      # 7.5 percent
    assert a.decide_continuous([1.0] * 20, base)["verdict"] == "no clear effect"    # 2.5 percent
    assert a.decide_continuous([-3.0] * 20, base)["verdict"] == "real decrease"
    noisy = [5.0, -5.0] * 10
    assert a.decide_continuous(noisy, base)["verdict"] == "no clear effect"          # interval includes 0
