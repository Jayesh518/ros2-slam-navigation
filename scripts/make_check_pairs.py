#!/usr/bin/env python3
"""Draw the 20 fresh world-B start/goal pairs of the independent check (protocol change (o)) into configs/pairs_check.yaml.

Same rules and code as scripts/make_pairs.py (it is run up to the point where its pairs_for() is defined); the 20 pairs of configs/pairs.yaml are passed
as 'keep' so no new pair repeats one of them (start within 1 m and goal within 1 m), and only the 20 added pairs are written, ids k01 to k20.
Refuses to overwrite an existing file. Usage: /usr/bin/python3 scripts/make_check_pairs.py
"""
import math
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "configs/pairs_check.yaml"
SEED = 20261028
if OUT.exists():
    raise SystemExit(f"{OUT} exists; pairs are never redrawn")
ns = {"__file__": str(ROOT / "scripts/make_pairs.py")}
exec(compile((ROOT / "scripts/make_pairs.py").read_text().split("existing = {}")[0], "make_pairs_head", "exec"), ns)
orig = yaml.safe_load((ROOT / "configs/pairs.yaml").read_text())["worlds"]["world_b"]
ns["N"] = len(orig) + 20
new = ns["pairs_for"]("world_b", np.random.default_rng(SEED), orig)[len(orig):]
for i, p in enumerate(new, 1):
    p["id"] = f"k{i:02d}"
assert len(new) == 20
OUT.write_text("# Fresh world-B pairs for the independent check (protocol change (o)), drawn once by scripts/make_check_pairs.py. Not changed after any trial.\n"
               + yaml.safe_dump({"seed": SEED, "min_straight_m": ns["MIN_DIST"], "frame": "world (Gazebo)", "worlds": {"world_b": new}}, sort_keys=False))
print(len(new), "pairs; straight distances", [p["straight_m"] for p in new])
