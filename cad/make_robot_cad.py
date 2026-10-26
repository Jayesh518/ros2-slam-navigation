#!/usr/bin/env python3
"""Generate the robot CAD (STEP assembly) from src/nav_study_robot/config/robot_params.yaml.

Output: cad/nav_study_robot_v1.step, an assembly of named solids in millimetres, ready to open in Fusion 360
(File > Open > Open from my computer). Origin: on the ground under the axle centre, x forward, y left, z up.
Run with the project venv:  .venv/bin/python cad/make_robot_cad.py
"""
import sys
from pathlib import Path

import cadquery as cq
import yaml

ROOT = Path(__file__).resolve().parents[1]
P = yaml.safe_load((ROOT / "src/nav_study_robot/config/robot_params.yaml").read_text())
OUT = ROOT / "cad" / "nav_study_robot_v1.step"
MM = 1000.0  # parameters are in metres, CAD is in millimetres


def mm(v):
    return v * MM


def box(center, size, z0=None):
    """Box from centre x,y and size; z from z0 (bottom) in metres."""
    return (cq.Workplane("XY")
            .box(mm(size[0]), mm(size[1]), mm(size[2]), centered=(True, True, False))
            .translate((mm(center[0]), mm(center[1]), mm(z0))))


def cyl(radius, height, center_xy, z0, axis="z"):
    w = cq.Workplane("XY").circle(mm(radius)).extrude(mm(height))
    if axis == "y":  # axis along y, centred on height
        w = (cq.Workplane("XZ").circle(mm(radius)).extrude(mm(height) / 2, both=True))
        return w.translate((mm(center_xy[0]), mm(center_xy[1]), mm(z0)))
    return w.translate((mm(center_xy[0]), mm(center_xy[1]), mm(z0)))


b, w, lid, c = P["body"], P["wheel"], P["lidar"], P["caster"]
thick = b["plate_thickness"]
standoffs = [(x, s * y) for (x, y) in b["standoff_xy"] for s in (1, -1)]


def plate(z0):
    rect = (cq.Workplane("XY")
            .box(mm(b["plate_length"]), mm(b["plate_width"]), mm(thick), centered=(True, True, False))
            .translate((mm(b["plate_center_x"]), 0, mm(z0))))
    disc = cq.Workplane("XY").circle(mm(b["clip_radius"])).extrude(mm(thick)).translate((0, 0, mm(z0)))
    p = rect.intersect(disc)
    pts = [(mm(x), mm(y)) for x, y in standoffs]
    holes = (cq.Workplane("XY").workplane(offset=mm(z0)).pushPoints(pts)
             .circle(1.6).extrude(mm(thick)))  # 3.2 mm clearance holes
    return p.cut(holes)


parts = []  # (name, solid, rgba)
z_bot, z_mid, z_top = b["plate_z0"]
parts += [("bottom_plate", plate(z_bot), (0.20, 0.20, 0.22)),
          ("middle_plate", plate(z_mid), (0.20, 0.20, 0.22)),
          ("top_plate", plate(z_top), (0.20, 0.20, 0.22))]

# standoffs: bottom to middle and middle to top
for i, (x, y) in enumerate(standoffs):
    lo = cyl(b["standoff_diameter"] / 2, z_mid - (z_bot + thick), (x, y), z_bot + thick)
    hi = cyl(b["standoff_diameter"] / 2, z_top - (z_mid + thick), (x, y), z_mid + thick)
    parts += [(f"standoff_low_{i + 1}", lo, (0.75, 0.75, 0.78)), (f"standoff_high_{i + 1}", hi, (0.75, 0.75, 0.78))]

# drive: wheels, motors
half_sep = w["separation"] / 2
for name, s in (("left", 1), ("right", -1)):
    wheel = cyl(w["radius"], w["width"], (0, s * half_sep), w["radius"], axis="y")
    hub = cyl(0.010, w["width"], (0, s * half_sep), w["radius"], axis="y")
    parts += [(f"wheel_{name}", wheel.union(hub), (0.10, 0.10, 0.10))]
    msize = b["motor"]["size"]
    ycenter = s * (half_sep - w["width"] / 2 - msize[1] / 2)
    parts += [(f"motor_{name}", box((b["motor"]["x"], ycenter), msize, b["motor"]["z0"]), (0.55, 0.55, 0.60))]

# ball caster: sphere plus a post up to the bottom plate
cx = c["x"]
ball = cq.Workplane("XY").sphere(mm(c["radius"])).translate((mm(cx), 0, mm(c["radius"])))
post = cyl(0.004, z_bot - c["radius"], (cx, 0), c["radius"])  # starts at the ball centre so the two fuse
parts += [("ball_caster", ball.union(post), (0.80, 0.80, 0.80))]

# electronics on the bottom and middle plates
parts += [("battery", box(b["battery"]["center"], b["battery"]["size"], z_bot + thick), (0.15, 0.30, 0.65)),
          ("controller_board", box(b["controller"]["center"], b["controller"]["size"], z_bot + thick), (0.10, 0.45, 0.20)),
          ("sbc_board", box(b["sbc"]["center"], b["sbc"]["size"], z_mid + thick), (0.10, 0.45, 0.20))]

# LiDAR on the top plate
lidar = cyl(lid["radius"], lid["height"], (lid["x"], 0), lid["z0"])
parts += [("lidar", lidar, (0.05, 0.05, 0.05))]

asm = cq.Assembly(name=P["robot_name"])
for name, solid, rgba in parts:
    asm.add(solid, name=name, color=cq.Color(*rgba))
asm.save(str(OUT), "STEP")

# self-check: re-import and compare with the design numbers
shape = cq.importers.importStep(str(OUT))
bb = shape.val().BoundingBox()
size = (bb.xlen, bb.ylen, bb.zlen)
expect_w = mm(w["separation"] + w["width"])
expect_h = mm(lid["z0"] + lid["height"])
n_solids = len(shape.solids().vals())
print(f"wrote {OUT.relative_to(ROOT)}: {len(parts)} parts, {n_solids} solids")
print(f"bounding box mm: x {bb.xmin:.1f}..{bb.xmax:.1f}, y {bb.ymin:.1f}..{bb.ymax:.1f}, z {bb.zmin:.1f}..{bb.zmax:.1f}")
print(f"overall width {size[1]:.1f} mm (design {expect_w:.1f}), height {size[2]:.1f} mm (design {expect_h:.1f})")
ok = abs(size[1] - expect_w) < 0.5 and abs(size[2] - expect_h) < 0.5 and abs(bb.zmin) < 0.5 and n_solids == len(parts)
print("self-check:", "OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
