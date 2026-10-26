#!/usr/bin/env python3
"""Draw top-down plans of the study worlds from their SDF files -> docs/figures/world-plans.png (a generated drawing, not a screenshot)."""
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

ROOT = Path(__file__).resolve().parents[1]
WORLDS = ROOT / "src/nav_study_bringup/worlds"
TITLES = {"world_a": "A1: open room, 4 obstacles", "world_b": "B1: office, corridor and doorways", "world_c": "C1: symmetric pillar grid"}

fig, axes = plt.subplots(1, 3, figsize=(15, 5.4))
for ax, name in zip(axes, TITLES):
    for col in ET.parse(WORLDS / f"{name}.sdf").getroot().iter("collision"):
        geom = col.find("geometry")
        if col.findtext("pose") is None:  # ground plane
            continue
        pose = [float(v) for v in col.findtext("pose").split()]
        if geom.find("box") is not None:
            sx, sy, _ = [float(v) for v in geom.find("box/size").text.split()]
            ax.add_patch(Rectangle((pose[0] - sx / 2, pose[1] - sy / 2), sx, sy, color="#444"))
        elif geom.find("cylinder") is not None:
            ax.add_patch(Circle((pose[0], pose[1]), float(geom.findtext("cylinder/radius")), color="#444"))
    ax.set_aspect("equal"); ax.autoscale_view(); ax.set_title(TITLES[name]); ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
    ax.grid(alpha=0.3)
fig.suptitle("Study worlds (top-down plans generated from the SDF files; walls and obstacles dark)")
fig.tight_layout()
out = ROOT / "docs/figures/world-plans.png"
fig.savefig(out, dpi=110)
print("wrote", out)
