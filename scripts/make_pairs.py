#!/usr/bin/env python3
"""Choose the start/goal pairs (protocol section 4 and change log (k)): 20 per world, fixed seeds, written to configs/pairs.yaml.

The first 10 per world were drawn with SEED; the second 10 (ids x11..x20) were added before any trial with SEED + 1. Existing pairs are never redrawn:
if configs/pairs.yaml exists, its pairs are kept and only missing ones are added.

Rules: start and goal are in observed free space of the saved map (clearance 0.30 m from occupied or unknown map cells) and 0.45 m from true
obstacles; straight-line distance at least 4 m; reachable for the robot (8-connected search on the true geometry inflated by 0.20 m).
Poses are in the WORLD frame; the runner converts goals to the map frame with configs/map_alignment.yaml.
Usage: /usr/bin/python3 scripts/make_pairs.py
"""
import math
from collections import deque
from pathlib import Path

import numpy as np
import yaml
from PIL import Image
from scipy import ndimage


ROOT = Path(__file__).resolve().parents[1]
SEED, N, MIN_DIST = 20261026, 20, 4.0
align = yaml.safe_load((ROOT / "configs/map_alignment.yaml").read_text())

# reuse the SDF rasteriser from align_map.py without running its main part
src = (ROOT / "scripts/align_map.py").read_text().split("def fit(world):")[0]
ns = {"__file__": str(ROOT / "scripts/align_map.py")}
exec(compile(src, "align_map_head", "exec"), ns)
true_obstacles, RES = ns["true_obstacles"], ns["RES"]


def pairs_for(world, rng, keep):
    mask, x0, y0 = true_obstacles(world)
    d_true = ndimage.distance_transform_edt(~mask) * RES
    meta = yaml.safe_load((ROOT / "maps" / f"{world}.yaml").read_text())
    im = np.array(Image.open(ROOT / "maps" / meta["image"]).convert("L"))
    mres, (ox, oy, _) = meta["resolution"], meta["origin"]
    d_map = ndimage.distance_transform_edt(im >= 250) * mres  # distance to the nearest non-free map cell
    rows, cols = np.nonzero(d_map >= 0.30)
    h = im.shape[0]
    mx, my = ox + (cols + 0.5) * mres, oy + (h - rows - 0.5) * mres
    a = align[world]
    c, s = math.cos(a["yaw"]), math.sin(a["yaw"])
    wx, wy = c * mx - s * my + a["x"], s * mx + c * my + a["y"]
    ix, iy = ((wx - x0) / RES).astype(int), ((wy - y0) / RES).astype(int)
    ok = d_true[iy, ix] >= 0.45
    cand = np.stack([wx[ok], wy[ok]], axis=1)

    free = d_true >= 0.20  # robot radius 0.15 plus margin
    lab, _ = ndimage.label(free, structure=np.ones((3, 3)))

    def reachable(p, q):
        pi = (int((p[1] - y0) / RES), int((p[0] - x0) / RES))
        qi = (int((q[1] - y0) / RES), int((q[0] - x0) / RES))
        return lab[pi] != 0 and lab[pi] == lab[qi]

    out = list(keep)
    tries = 0
    while len(out) < N and tries < 100000:
        tries += 1
        p, q = cand[rng.integers(len(cand))], cand[rng.integers(len(cand))]
        if math.dist(p, q) < MIN_DIST or not reachable(p, q):
            continue
        if any(math.dist(p, (e["start"]["x"], e["start"]["y"])) < 1.0 and math.dist(q, (e["goal"]["x"], e["goal"]["y"])) < 1.0 for e in out):
            continue
        out.append({"id": f"{world[-1]}{len(out) + 1:02d}",
                    "start": {"x": round(float(p[0]), 2), "y": round(float(p[1]), 2), "yaw": round(float(rng.uniform(-math.pi, math.pi)), 2)},
                    "goal": {"x": round(float(q[0]), 2), "y": round(float(q[1]), 2)},
                    "straight_m": round(math.dist(p, q), 2)})
    return out


existing = {}
if (ROOT / "configs/pairs.yaml").exists():
    existing = yaml.safe_load((ROOT / "configs/pairs.yaml").read_text())["worlds"]
result = {"seed": SEED, "seed_second_batch": SEED + 1, "min_straight_m": MIN_DIST, "frame": "world (Gazebo)", "worlds": {}}
for w in ("world_a", "world_b", "world_c", "world_d"):
    keep = existing.get(w, [])
    rng = np.random.default_rng(SEED if (not keep and w != "world_d") else (SEED + 100 if not keep else SEED + 1 + len(keep)))
    result["worlds"][w] = pairs_for(w, rng, keep)
    print(w, len(result["worlds"][w]), "pairs, straight distances", [p["straight_m"] for p in result["worlds"][w]])
(ROOT / "configs/pairs.yaml").write_text("# Start/goal pairs, chosen once by scripts/make_pairs.py (seed below). Not changed after any trial.\n" + yaml.safe_dump(result, sort_keys=False))
