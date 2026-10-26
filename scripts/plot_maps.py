#!/usr/bin/env python3
"""Combine the saved SLAM Toolbox maps into one figure -> docs/figures/maps-slam.png (white free, grey unknown, black occupied)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
fig, axes = plt.subplots(1, 4, figsize=(19, 5.2))
for ax, (name, title) in zip(axes, (("world_a", "A1"), ("world_b", "B1"), ("world_c", "C1"), ("world_d", "D"))):
    meta = yaml.safe_load((ROOT / "maps" / f"{name}.yaml").read_text())
    im = Image.open(ROOT / "maps" / meta["image"]).convert("L")
    res, (ox, oy, _) = meta["resolution"], meta["origin"]
    ax.imshow(im, cmap="gray", origin="upper", extent=(ox, ox + im.width * res, oy, oy + im.height * res), vmin=0, vmax=255)
    ax.set_title(f"{title} (SLAM Toolbox map, {im.width}x{im.height} cells at {res} m)")
    ax.set_xlabel("map x (m)"); ax.set_ylabel("map y (m)")
fig.suptitle("Maps built once per world with SLAM Toolbox while Nav2 drove a fixed tour (baseline robot, LiDAR range 3.5 m)")
fig.tight_layout()
out = ROOT / "docs/figures/maps-slam.png"
fig.savefig(out, dpi=100)
print("wrote", out)
