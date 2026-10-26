#!/usr/bin/env python3
"""Fit the rigid transform world <- map for each world by matching occupied map cells to the true SDF geometry.

Why: SLAM Toolbox's map frame starts at the robot's start pose and drifts slightly (about 1 to 2 degrees), but trials are judged against Gazebo
ground truth in the world frame. This script finds (x, y, yaw) such that  p_world = R(yaw) p_map + (x, y)  minimises the mean distance from
occupied map cells to the nearest true obstacle edge. Result: configs/map_alignment.yaml (committed, fixed for all trials).
Usage: /usr/bin/python3 scripts/align_map.py
"""
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import yaml
from PIL import Image
from scipy import ndimage, optimize

ROOT = Path(__file__).resolve().parents[1]
WORLDS = ROOT / "src/nav_study_bringup/worlds"
RES = 0.025  # raster resolution of the true geometry (m)


def true_obstacles(world):
    """Rasterise the SDF boxes and cylinders (footprints) on a grid; return (mask, x0, y0)."""
    shapes = []
    for col in ET.parse(WORLDS / f"{world}.sdf").getroot().iter("collision"):
        if col.findtext("pose") is None:
            continue
        px, py = [float(v) for v in col.findtext("pose").split()[:2]]
        g = col.find("geometry")
        if g.find("box") is not None:
            sx, sy, _ = [float(v) for v in g.find("box/size").text.split()]
            shapes.append(("box", px, py, sx, sy))
        else:
            shapes.append(("cyl", px, py, float(g.findtext("cylinder/radius")), 0))
    xs = [s[1] for s in shapes]; ys = [s[2] for s in shapes]
    x0, x1, y0, y1 = min(xs) - 12, max(xs) + 12, min(ys) - 12, max(ys) + 12
    nx, ny = int((x1 - x0) / RES), int((y1 - y0) / RES)
    gx = x0 + (np.arange(nx) + 0.5) * RES
    gy = y0 + (np.arange(ny) + 0.5) * RES
    X, Y = np.meshgrid(gx, gy)
    mask = np.zeros_like(X, dtype=bool)
    for kind, px, py, a, b in shapes:
        mask |= (np.abs(X - px) <= a / 2) & (np.abs(Y - py) <= b / 2) if kind == "box" else (X - px) ** 2 + (Y - py) ** 2 <= a ** 2
    return mask, x0, y0


def map_occupied(world):
    meta = yaml.safe_load((ROOT / "maps" / f"{world}.yaml").read_text())
    im = np.array(Image.open(ROOT / "maps" / meta["image"]).convert("L"))
    h = im.shape[0]
    rows, cols = np.nonzero(im < 50)  # occupied (trinary map: 0)
    ox, oy, _ = meta["origin"]
    res = meta["resolution"]
    return np.stack([ox + (cols + 0.5) * res, oy + (h - rows - 0.5) * res], axis=1)


def fit(world):
    mask, x0, y0 = true_obstacles(world)
    dist = ndimage.distance_transform_edt(~mask) * RES  # distance to the nearest true obstacle cell
    pts = map_occupied(world)

    def cost(p):
        x, y, yaw = p
        c, s = math.cos(yaw), math.sin(yaw)
        wx = c * pts[:, 0] - s * pts[:, 1] + x
        wy = s * pts[:, 0] + c * pts[:, 1] + y
        ix = np.clip(((wx - x0) / RES).astype(int), 0, dist.shape[1] - 1)
        iy = np.clip(((wy - y0) / RES).astype(int), 0, dist.shape[0] - 1)
        return float(np.mean(np.minimum(dist[iy, ix], 0.5)))  # robust: cap far outliers at 0.5 m

    best = None
    for yaw in np.radians(np.arange(-4, 4.01, 0.5)):
        for x in np.arange(-0.4, 0.41, 0.1):
            for y in np.arange(-0.4, 0.41, 0.1):
                c = cost((x, y, yaw))
                if best is None or c < best[0]:
                    best = (c, (x, y, yaw))
    res = optimize.minimize(cost, best[1], method="Nelder-Mead", options={"xatol": 1e-3, "fatol": 1e-5})
    return res.x, float(res.fun), cost((0.0, 0.0, 0.0)), len(pts)


out = {}
for w in ("world_a", "world_b", "world_c"):
    (x, y, yaw), c, c0, n = fit(w)
    out[w] = {"x": round(float(x), 4), "y": round(float(y), 4), "yaw": round(float(yaw), 5),
              "mean_dist_after_m": round(float(c), 4), "mean_dist_identity_m": round(float(c0), 4), "occupied_cells": int(n)}
    print(f"{w}: x {x:+.3f} m, y {y:+.3f} m, yaw {math.degrees(yaw):+.2f} deg; mean edge distance {c0:.3f} m (identity) -> {c:.3f} m (fitted), {n} cells")
(ROOT / "configs/map_alignment.yaml").write_text(
    "# p_world = R(yaw) * p_map + (x, y); fitted by scripts/align_map.py from maps/*.pgm and the SDF worlds. Fixed for all trials.\n"
    + yaml.safe_dump(out, sort_keys=False))
