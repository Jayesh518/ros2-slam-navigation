#!/usr/bin/env python3
"""Build the Nav2 parameter files of the study from the shipped Jazzy defaults.

Input : configs/nav2/shipped_default.yaml (copy of /opt/ros/jazzy/share/nav2_bringup/params/nav2_params.yaml, Nav2 1.3.13)
Output: configs/nav2/{baseline,smac2d,thetastar,dwb,rpp}.yaml  (full files, so each configuration is one file in git)
        configs/nav2/CHANGES.md (the exact differences to the shipped file, generated)

Baseline = shipped defaults (NavFn planner, MPPI controller) plus ONLY the robot-specific edits in ROBOT. Each variant = baseline plus ONE
change (its overlay). Run: /usr/bin/python3 scripts/make_nav2_configs.py
"""
import copy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/nav2"
shipped = yaml.safe_load((CFG / "shipped_default.yaml").read_text())
robot = yaml.safe_load((ROOT / "src/nav_study_robot/config/robot_params.yaml").read_text())
vmax = robot["limits"]["max_linear_velocity"]
RADIUS = 0.15  # circumscribed radius of the collision box about the axle centre, 0.150 m (robot_params.yaml: plate 0.138 x 0.140 at x -0.064)


def setp(cfg, path, value):
    d = cfg
    keys = path.split(".")
    for k in keys[:-1]:
        d = d[k]
    d[keys[-1]] = value


# Robot-specific edits only: footprint radius and the robot's speed limits (the shipped file assumes a faster, larger robot).
ROBOT = {
    "local_costmap.local_costmap.ros__parameters.robot_radius": RADIUS,
    "global_costmap.global_costmap.ros__parameters.robot_radius": RADIUS,
    "controller_server.ros__parameters.FollowPath.vx_max": vmax,
    "controller_server.ros__parameters.FollowPath.vx_min": -vmax,
    "velocity_smoother.ros__parameters.max_velocity": [vmax, 0.0, 2.0],
    "velocity_smoother.ros__parameters.min_velocity": [-vmax, 0.0, -2.0],
}
baseline = copy.deepcopy(shipped)
for k, v in ROBOT.items():
    setp(baseline, k, v)

# One change each. Controller blocks replace FollowPath whole (plugin parameters differ); speed limits again follow the robot.
DWB = {
    "plugin": "dwb_core::DWBLocalPlanner", "debug_trajectory_details": True,
    "min_vel_x": 0.0, "min_vel_y": 0.0, "max_vel_x": vmax, "max_vel_y": 0.0, "max_vel_theta": 1.0,
    "min_speed_xy": 0.0, "max_speed_xy": vmax, "min_speed_theta": 0.0,
    "acc_lim_x": 2.5, "acc_lim_y": 0.0, "acc_lim_theta": 3.2, "decel_lim_x": -2.5, "decel_lim_y": 0.0, "decel_lim_theta": -3.2,
    "vx_samples": 20, "vy_samples": 5, "vtheta_samples": 20, "sim_time": 1.7,
    "linear_granularity": 0.05, "angular_granularity": 0.025, "transform_tolerance": 0.2,
    "xy_goal_tolerance": 0.25, "trans_stopped_velocity": 0.25, "short_circuit_trajectory_evaluation": True, "stateful": True,
    "critics": ["RotateToGoal", "Oscillation", "BaseObstacle", "GoalAlign", "PathAlign", "PathDist", "GoalDist"],
    "BaseObstacle.scale": 0.02, "PathAlign.scale": 32.0, "PathAlign.forward_point_distance": 0.1,
    "GoalAlign.scale": 24.0, "GoalAlign.forward_point_distance": 0.1, "PathDist.scale": 32.0, "GoalDist.scale": 24.0,
    "RotateToGoal.scale": 32.0, "RotateToGoal.slowing_factor": 5.0, "RotateToGoal.lookahead_time": -1.0,
}
RPP = {
    "plugin": "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController",
    "desired_linear_vel": vmax, "lookahead_dist": 0.6, "min_lookahead_dist": 0.3, "max_lookahead_dist": 0.9, "lookahead_time": 1.5,
    "rotate_to_heading_angular_vel": 1.8, "transform_tolerance": 0.1, "use_velocity_scaled_lookahead_dist": False,
    "min_approach_linear_velocity": 0.05, "approach_velocity_scaling_dist": 0.6,
    "use_collision_detection": True, "max_allowed_time_to_collision_up_to_carrot": 1.0,
    "use_regulated_linear_velocity_scaling": True, "use_cost_regulated_linear_velocity_scaling": False,
    "regulated_linear_scaling_min_radius": 0.9, "regulated_linear_scaling_min_speed": 0.1,
    "use_rotate_to_heading": True, "allow_reversing": False, "rotate_to_heading_min_angle": 0.785, "max_angular_accel": 3.2,
    "max_robot_pose_search_dist": 10.0,
}
VARIANTS = {
    "smac2d": {"planner_server.ros__parameters.GridBased.plugin": "nav2_smac_planner::SmacPlanner2D"},
    "thetastar": {"planner_server.ros__parameters.GridBased.plugin": "nav2_theta_star_planner::ThetaStarPlanner"},
    "dwb": {"controller_server.ros__parameters.FollowPath": DWB},
    "rpp": {"controller_server.ros__parameters.FollowPath": RPP},
}
for name, overlay in VARIANTS.items():
    cfg = copy.deepcopy(baseline)
    for k, v in overlay.items():
        setp(cfg, k, v)
    (CFG / f"{name}.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
(CFG / "baseline.yaml").write_text(yaml.safe_dump(baseline, sort_keys=False))
# `recovery` (Phase 6, protocol change (n)): Nav2 parameters identical to the baseline; the difference is the plan_flip_guard node launched next to Nav2
(CFG / "recovery.yaml").write_text(yaml.safe_dump(baseline, sort_keys=False))

# Phase 5 diagnostic configurations (not part of the study grid, never analysed with the Phase 4 tables): baseline plus ONE change used to test a
# hypothesis about the failures (docs/diagnosis.md).
DIAGNOSTIC = {
    "diag_known": {"planner_server.ros__parameters.GridBased.allow_unknown": False},  # planner may not route through unknown map cells
}
for name, overlay in DIAGNOSTIC.items():
    cfg = copy.deepcopy(baseline)
    for k, v in overlay.items():
        setp(cfg, k, v)
    (CFG / f"{name}.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))

# Mapping run only (not a study configuration): Nav2 drives the robot while SLAM Toolbox builds the map. The SLAM map grows, and Nav2's
# static-layer global costmap does not grow with it (goals rejected as "outside bounds"), so use a rolling-window global costmap
# without the static layer. The saved map is an input to the trials, produced once per world.
mapping = copy.deepcopy(baseline)
gc = mapping["global_costmap"]["global_costmap"]["ros__parameters"]
gc.update({"global_frame": "odom", "rolling_window": True, "width": 20, "height": 20,
           "plugins": ["obstacle_layer", "inflation_layer"]})
gc.pop("static_layer", None)
(CFG / "mapping.yaml").write_text(yaml.safe_dump(mapping, sort_keys=False))


def flat(d, prefix=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flat(v, f"{prefix}.{k}" if prefix else str(k)))
    else:
        out[prefix] = d
    return out


def diff(a, b):
    fa, fb = flat(a), flat(b)
    rows = []
    for k in sorted(set(fa) | set(fb)):
        if fa.get(k, "<absent>") != fb.get(k, "<absent>"):
            rows.append(f"| `{k}` | `{fa.get(k, '<absent>')}` | `{fb.get(k, '<absent>')}` |")
    return rows


lines = ["# Nav2 configuration differences (generated by scripts/make_nav2_configs.py; do not edit)\n",
         "Shipped default = `/opt/ros/jazzy/share/nav2_bringup/params/nav2_params.yaml` (Nav2 1.3.13): NavFn planner, **MPPI** controller.\n",
         "\n## baseline vs shipped default (robot-specific edits only)\n", "| parameter | shipped | baseline |", "|---|---|---|"]
lines += diff(shipped, baseline)
for name in [*VARIANTS, *DIAGNOSTIC]:
    cfg = yaml.safe_load((CFG / f"{name}.yaml").read_text())
    lines += [f"\n## {name} vs baseline\n", "| parameter | baseline | " + name + " |", "|---|---|---|"] + diff(baseline, cfg)
(CFG / "CHANGES.md").write_text("\n".join(lines) + "\n")
print("wrote", ", ".join(f"{n}.yaml" for n in ["baseline", "recovery", *VARIANTS]), "and CHANGES.md")
