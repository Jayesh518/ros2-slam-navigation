# Project phases and status

Standard shape: see the workspace `docs/phases.md`. Status: **Phases 0 and 1 done (protocol frozen 2026-10-26; environment and smoke test passed 2026-10-26); next: Phase 2, awaiting go-ahead.** Detailed plan written 2026-10-26: see `PLAN.md` (stack: ROS 2 Jazzy, Gazebo Harmonic, Nav2, Ubuntu 24.04 native on an external SATA drive). Phases follow `docs/master-plan.md` section 4; they may change as work proceeds.

| Phase | Content | Status |
|---|---|---|
| 0. Scope and protocol | Research question (how do Nav2 planner/controller settings and recovery behaviours change success, collisions, time and path length); trial counts and metrics fixed before any trial. Frozen in `docs/protocol.md` v1; decision rule changed to pair-level paired bootstrap; layouts A1, B1, C1 | done |
| 1. Setup | ROS 2 Jazzy with Gazebo Harmonic and Nav2 on Ubuntu 24.04 running natively from an external drive (version table checked against REP-2000 on 2026-10-26; re-verify packages before installing); versions and licences recorded; smoke test; containerised one-command simulation comes in Phase 7. Done: `docs/environment.md`, `scripts/smoke_test.sh` | done |
| 2. Pipeline and validation | Differential-drive robot with LiDAR and odometry in simulation; automated trial runner logging CSV; seeds and start/goal pairs fixed | planned |
| 3. Baseline | SLAM Toolbox mapping, AMCL localisation, default Nav2 across three or more worlds of increasing difficulty | planned |
| 4. Intervention | Controller and planner comparison, recovery behaviour on/off, 20 or more trials per condition | planned |
| 5. Diagnosis and iteration | Explain failures from logs and short rosbag excerpts | planned |
| 6. Extension | Custom mission/waypoint node and custom recovery behaviour, effect isolated by the on/off ablation; simulated thermal camera in Gazebo for later use by Project 3 | planned |
| 7. Report and release | Report, TF and architecture diagrams, trial logs and plots, demo video; fresh clone plus one command reproduces the headline table | planned |
