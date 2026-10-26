#!/usr/bin/env python3
"""Print the map-frame pose (x y yaw) of the robot's spawn pose (world origin, yaw 0) for a world, using configs/map_alignment.yaml.
Usage: python3 scripts/spawn_pose_map.py world_a
"""
import math
import sys
from pathlib import Path

import yaml

al = yaml.safe_load((Path(__file__).resolve().parents[1] / "configs/map_alignment.yaml").read_text())[sys.argv[1]]
c, s = math.cos(al["yaw"]), math.sin(al["yaw"])
x, y = -al["x"], -al["y"]  # world origin relative to the map origin
print(c * x + s * y, -s * x + c * y, -al["yaw"])
