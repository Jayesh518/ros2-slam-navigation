"""Analysis functions implementing docs/protocol.md section 8 exactly (unit of analysis = start/goal pair, paired against the baseline).

Plain numpy, no ROS. All randomness is seeded so a table can be regenerated bit for bit.
"""
import numpy as np

N_BOOT = 10_000
BOOT_SEED = 20261026
SUCCESS_MIN_EFFECT = 0.10      # 10 percentage points
CONTINUOUS_MIN_REL = 0.05      # 5 percent of the baseline value


def paired_bootstrap(diffs, n_boot=N_BOOT, seed=BOOT_SEED):
    """Mean of the paired differences with a 95 percent percentile bootstrap interval over pairs. Returns (mean, lo, hi); NaNs if empty."""
    d = np.asarray(diffs, dtype=float)
    if d.size == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = d[rng.integers(0, d.size, size=(n_boot, d.size))].mean(axis=1)
    return float(d.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def decide_success(diffs):
    """Protocol rule for success rate: real if |mean difference| >= 10 percentage points and the 95 percent interval excludes zero."""
    mean, lo, hi = paired_bootstrap(diffs)
    excludes_zero = lo > 0 or hi < 0
    real = bool(abs(mean) >= SUCCESS_MIN_EFFECT and excludes_zero)
    return {"mean_diff": mean, "ci_lo": lo, "ci_hi": hi, "n_pairs": len(diffs), "verdict": ("real " + ("increase" if mean > 0 else "decrease")) if real else "no clear effect"}


def decide_continuous(diffs, baseline_values):
    """Protocol rule for time and path length (pairs where both trials succeeded): real if the interval excludes zero and |mean| > 5 percent of the baseline mean."""
    mean, lo, hi = paired_bootstrap(diffs)
    base = float(np.mean(baseline_values)) if len(baseline_values) else float("nan")
    excludes_zero = lo > 0 or hi < 0
    real = bool(excludes_zero and abs(mean) > CONTINUOUS_MIN_REL * base)
    return {"mean_diff": mean, "ci_lo": lo, "ci_hi": hi, "n_pairs": len(diffs), "baseline_mean": base,
            "verdict": ("real " + ("increase" if mean > 0 else "decrease")) if real else "no clear effect"}
