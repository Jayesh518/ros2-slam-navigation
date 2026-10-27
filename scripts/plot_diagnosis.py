#!/usr/bin/env python3
"""Phase 5 figure: the same start/goal pair (b14, world B) with the baseline and with allow_unknown false.

Left: saved SLAM map (grey = unknown, white = free, black = occupied) with the ground-truth tracks; right: length of the global plan over time
(a jump between about 8 and 16 m is the planner switching between the route through the unmapped wall and the route through the doorway).
Usage: PYTHONPATH=src/nav_study_trials /usr/bin/python3 scripts/plot_diagnosis.py   Writes docs/figures/phase5-plan-flipping.png
"""
import csv
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml
from PIL import Image

from nav_study_trials import metrics

ROOT = Path(__file__).resolve().parents[1]
al = yaml.safe_load((ROOT / "configs/map_alignment.yaml").read_text())["world_b"]
img = np.array(Image.open(ROOT / "maps/world_b.pgm"))
H, W = img.shape
ox, oy, res = -8.363, -5.810, 0.05
pair = "b14"
P = next(p for p in yaml.safe_load((ROOT / "configs/pairs.yaml").read_text())["worlds"]["world_b"] if p["id"] == pair)
runs = [("baseline-b14-r1", "baseline (allow_unknown true): timed out", "#d62728"), ("diag_known-b14-r1", "allow_unknown false: reached the goal", "#1f77b4")]
D = ROOT / "results/diagnosis/traces"

fig, (ax, bx) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.25, 1]})
ax.imshow(img, cmap="gray", extent=(ox, ox + W * res, oy, oy + H * res), vmin=0, vmax=254)
for tid, label, col in runs:
    tr = list(csv.DictReader(open(D / f"{tid}_trace.csv")))
    xy = np.array([metrics.world_to_map(float(r["x"]), float(r["y"]), 0.0, al)[:2] for r in tr])
    ax.plot(xy[:, 0], xy[:, 1], color=col, lw=1.6, label=label)
    ev = [e for e in csv.DictReader(open(D / f"{tid}_events.csv")) if e["kind"] == "plan"]
    bx.plot([float(e["t_s"]) for e in ev], [float(re.search(r"length_m=([\d.]+)", e["detail"]).group(1)) for e in ev], color=col, lw=1.4, label=label)
s, g = P["start"], P["goal"]
for (p, m, name) in ((s, "o", "start"), (g, "*", "goal")):
    mx, my, _ = metrics.world_to_map(p["x"], p["y"], 0.0, al)
    ax.plot(mx, my, m, color="k", ms=9, mfc="w")
    ax.annotate(name, (mx, my), textcoords="offset points", xytext=(6, 6), fontsize=9)
ax.axvline(0.2, color="#ff7f0e", lw=1, ls=":")
ax.annotate("divider wall at x = 0\n(missing from the saved map)", (0.3, 3.9), fontsize=8, color="#ff7f0e")
ax.set_xlim(-8.4, 8.4); ax.set_ylim(-5.9, 5.9); ax.set_aspect("equal")
ax.set_xlabel("x in map frame (m)"); ax.set_ylabel("y (m)"); ax.legend(loc="lower left", fontsize=8)
ax.set_title(f"World B, pair {pair}: ground-truth tracks on the saved map", fontsize=10)
bx.set_xlabel("time since goal sent (s)"); bx.set_ylabel("remaining length of the global plan (m)"); bx.grid(alpha=0.3); bx.legend(fontsize=8)
bx.set_title("Global plan length: flips between a short and a long route", fontsize=10)
fig.tight_layout()
fig.savefig(ROOT / "docs/figures/phase5-plan-flipping.png", dpi=110)
print("wrote docs/figures/phase5-plan-flipping.png")
