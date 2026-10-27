#!/usr/bin/env python3
"""Summarise the Phase 5 traces (results/diagnosis/traces) one line per trial: how the trial ended and what the robot was doing.

Columns: plan flips = jumps of more than 3 m in the global plan length between consecutive plans (the planner switching between routes);
stalled = simulated seconds with commanded speed below 0.02 m/s; spin/backup/wait/clear = recovery nodes that started running;
amcl max = largest AMCL error against ground truth; end = distance of the last ground-truth pose to the goal; nearest = smallest LiDAR return.
Usage: /usr/bin/python3 scripts/diagnose_traces.py [glob prefix]   Writes results/diagnosis/trace_summary.csv
"""
import csv
import glob
import math
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAIRS = {p["id"]: p for p in yaml.safe_load((ROOT / "configs/pairs.yaml").read_text())["worlds"]["world_b"]}
rows = []
for tf in sorted(glob.glob(str(ROOT / f"results/diagnosis/traces/{sys.argv[1] if len(sys.argv) > 1 else ''}*_trace.csv"))):
    tid = Path(tf).name[:-len("_trace.csv")]
    config, pair = tid.split("-")[0], tid.split("-")[1]
    tr = list(csv.DictReader(open(tf)))
    ev = list(csv.DictReader(open(tf.replace("_trace", "_events"))))
    g = PAIRS[pair]["goal"]
    plans = [float(re.search(r"length_m=([\d.]+)", e["detail"]).group(1)) for e in ev if e["kind"] == "plan"]
    flips = sum(1 for a, b in zip(plans, plans[1:]) if abs(b - a) > 3.0)
    dt = 0.2
    stalled = sum(dt for r in tr if abs(float(r["cmd_v"])) < 0.02 and abs(float(r["cmd_w"])) < 0.05)
    started = {k: sum(1 for e in ev if e["kind"] == "bt" and k in e["detail"] and e["detail"].endswith("IDLE->RUNNING")) for k in ("Spin", "BackUp", "Wait", "ClearingActions")}
    err = [math.dist((float(r["x"]), float(r["y"])), (float(r["amcl_x"]), float(r["amcl_y"]))) for r in tr if r["amcl_x"] not in ("", "nan")]
    last = tr[-1]
    rows.append({"trial": tid, "t_end": last["t_s"], "end_to_goal_m": round(math.dist((float(last["x"]), float(last["y"])), (g["x"], g["y"])), 2),
                 "plan_flips": flips, "plan_min_m": min(plans) if plans else "", "plan_max_m": max(plans) if plans else "", "stalled_s": round(stalled, 1),
                 "spin": started["Spin"], "backup": started["BackUp"], "wait": started["Wait"], "clear": started["ClearingActions"],
                 "amcl_max_m": round(max(err), 2) if err else "", "nearest_m": min(float(r["scan_min_m"]) for r in tr if r["scan_min_m"] not in ("", "nan")),
                 "cm_active": sum(1 for r in tr if r["collision_monitor"] not in ("", "0:", "0:None"))})
out = ROOT / "results/diagnosis/trace_summary.csv"
if rows:
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(" | ".join(rows[0]))
    for r in rows:
        print(" | ".join(str(v) for v in r.values()))
