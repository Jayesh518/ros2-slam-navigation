# Project phases and status

Standard shape: see the workspace `docs/phases.md`. Status: **Phases 0 to 3 done (all 2026-10-26); next: Phase 4 (intervention), awaiting the owner's go-ahead and a decision on world C (see `docs/baseline.md`).** Detailed plan written 2026-10-26: see `PLAN.md` (stack: ROS 2 Jazzy, Gazebo Harmonic, Nav2, Ubuntu 24.04 native on an external SATA drive). Phases follow `docs/master-plan.md` section 4; they may change as work proceeds.

| Phase | Content | Status |
|---|---|---|
| 0. Scope and protocol | Research question (how do Nav2 planner/controller settings and recovery behaviours change success, collisions, time and path length); trial counts and metrics fixed before any trial. Frozen in `docs/protocol.md` v1; decision rule changed to pair-level paired bootstrap; layouts A1, B1, C1 | done |
| 1. Setup | ROS 2 Jazzy with Gazebo Harmonic and Nav2 on Ubuntu 24.04 running natively from an external drive (version table checked against REP-2000 on 2026-10-26; re-verify packages before installing); versions and licences recorded; smoke test; containerised one-command simulation comes in Phase 7. Done: `docs/environment.md`, `scripts/smoke_test.sh` | done |
| 2. Pipeline and validation | Differential-drive robot with LiDAR and odometry in simulation; automated trial runner logging CSV; seeds and start/goal pairs fixed . Done: own Burger-based robot (`src/nav_study_robot`), STEP CAD for Fusion 360 (`cad/`), worlds A1/B1/C1, SLAM Toolbox maps, Nav2 configurations (`configs/nav2/`), 30 start/goal pairs, trial runner with metric unit tests, CI green; gate: repeats of one trial vary by about 2 percent (not bit-identical), real-time factor fixed at 1 | done |
| 3. Baseline | SLAM Toolbox mapping, AMCL localisation, default Nav2 across three or more worlds of increasing difficulty . Done: 60 trials (20 pairs x 3 worlds, `results/trials/baseline_*.csv`), `docs/baseline.md`; 56 of 60 succeeded (A 20/20, B 16/20, C 20/20) | done |
| 4. Intervention | Controller and planner comparison, recovery behaviour on/off, 20 or more trials per condition | planned |
| 5. Diagnosis and iteration | Explain failures from logs and short rosbag excerpts | planned |
| 6. Extension | Custom mission/waypoint node and custom recovery behaviour, effect isolated by the on/off ablation; simulated thermal camera in Gazebo for later use by Project 3 | planned |
| 7. Report and release | Report, TF and architecture diagrams, trial logs and plots, demo video; fresh clone plus one command reproduces the headline table | planned |

Plan changes so far (also in `docs/progress.md`): decision rule at pair level (Phase 0); robot modelled on the TurtleBot 3 Burger (Phase 2); baseline controller is the shipped MPPI, DWB becomes a variant (Phase 2); success tolerance 0.5 m, real-time factor 1, reset verification (Phase 2). All logged in `docs/protocol.md` (change log (e) to (j)).
