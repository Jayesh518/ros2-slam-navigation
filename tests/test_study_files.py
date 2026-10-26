"""Consistency tests for the committed study files (run with: python3 -m pytest tests src/nav_study_trials/test)."""
import math
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORLDS = ("world_a", "world_b", "world_c")
CONFIGS = ("baseline", "smac2d", "thetastar", "dwb", "rpp")


def load(rel):
    return yaml.safe_load((ROOT / rel).read_text())


def flat(d, prefix=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flat(v, f"{prefix}.{k}" if prefix else str(k)))
    else:
        out[prefix] = d
    return out


def test_pairs_file_matches_protocol():
    pairs = load("configs/pairs.yaml")
    assert pairs["min_straight_m"] == 4.0
    for w in WORLDS:
        ps = pairs["worlds"][w]
        assert len(ps) == 10, f"{w}: protocol fixes 10 pairs per world"
        assert len({p["id"] for p in ps}) == 10
        for p in ps:
            d = math.dist((p["start"]["x"], p["start"]["y"]), (p["goal"]["x"], p["goal"]["y"]))
            assert d >= 4.0 - 0.02, p["id"]  # rounding to 0.01 m


def test_alignment_exists_and_is_small():
    al = load("configs/map_alignment.yaml")
    for w in WORLDS:
        assert abs(al[w]["x"]) < 0.5 and abs(al[w]["y"]) < 0.5 and abs(al[w]["yaw"]) < math.radians(5)
        assert al[w]["mean_dist_after_m"] <= al[w]["mean_dist_identity_m"] + 1e-6


def test_maps_exist_for_every_world():
    for w in WORLDS:
        assert (ROOT / "maps" / f"{w}.yaml").exists() and (ROOT / "maps" / f"{w}.pgm").exists()


def test_baseline_is_shipped_default_plus_robot_edits_only():
    shipped, base = flat(load("configs/nav2/shipped_default.yaml")), flat(load("configs/nav2/baseline.yaml"))
    changed = {k for k in set(shipped) | set(base) if shipped.get(k) != base.get(k)}
    allowed_prefixes = ("local_costmap.local_costmap.ros__parameters.robot_radius", "global_costmap.global_costmap.ros__parameters.robot_radius",
                        "controller_server.ros__parameters.FollowPath.vx_", "velocity_smoother.ros__parameters.m")
    assert changed and all(k.startswith(allowed_prefixes) for k in changed), changed
    assert shipped["controller_server.ros__parameters.FollowPath.plugin"] == "nav2_mppi_controller::MPPIController"  # protocol change (e)
    assert shipped["planner_server.ros__parameters.GridBased.plugin"] == "nav2_navfn_planner::NavfnPlanner"


def test_each_variant_changes_exactly_one_component():
    base = flat(load("configs/nav2/baseline.yaml"))
    for name, area in (("smac2d", "planner_server"), ("thetastar", "planner_server"), ("dwb", "controller_server"), ("rpp", "controller_server")):
        v = flat(load(f"configs/nav2/{name}.yaml"))
        changed = {k for k in set(base) | set(v) if base.get(k) != v.get(k)}
        assert changed and all(k.startswith(area) for k in changed), (name, changed)


def test_robot_limits_respected_by_every_config():
    vmax = load("src/nav_study_robot/config/robot_params.yaml")["limits"]["max_linear_velocity"]
    for c in CONFIGS:
        cfg = load(f"configs/nav2/{c}.yaml")
        assert cfg["velocity_smoother"]["ros__parameters"]["max_velocity"][0] <= vmax + 1e-9
        fp = cfg["controller_server"]["ros__parameters"]["FollowPath"]
        speed = fp.get("vx_max", fp.get("max_vel_x", fp.get("desired_linear_vel")))
        assert speed <= vmax + 1e-9, c


def test_world_files_share_the_same_header():
    heads = []
    for w in WORLDS:
        text = (ROOT / f"src/nav_study_bringup/worlds/{w}.sdf").read_text()
        heads.append(text[text.index("<world"):text.index('<model name="walls">')])
    assert heads[0] == heads[1] == heads[2]


def test_cad_and_simulation_share_robot_parameters():
    p = load("src/nav_study_robot/config/robot_params.yaml")
    assert abs(p["wheel"]["separation"] + p["wheel"]["width"] - 0.178) < 1e-9  # Burger overall width
    assert abs(p["lidar"]["z0"] + p["lidar"]["height"] - 0.192) < 1e-9          # Burger overall height
    assert (ROOT / "cad/nav_study_robot_v1.step").stat().st_size > 10_000
