# Project phases and status

Standard shape: see the workspace `docs/phases.md`. Status: **planned, no phase started.** Phases follow `docs/master-plan.md` section 4; they may change as work proceeds.

| Phase | Content | Status |
|---|---|---|
| 0. Scope and protocol | Research question (how do Nav2 planner/controller settings and recovery behaviours change success, collisions, time and path length); trial counts and metrics fixed before any trial | planned |
| 1. Setup | Supported ROS 2 distribution with matching Gazebo and Nav2 (verify the version table first); WSL2 or dual boot; containerised one-command simulation | planned |
| 2. Pipeline and validation | Differential-drive robot with LiDAR and odometry in simulation; automated trial runner logging CSV; seeds and start/goal pairs fixed | planned |
| 3. Baseline | SLAM Toolbox mapping, AMCL localisation, default Nav2 across three or more worlds of increasing difficulty | planned |
| 4. Intervention | Controller and planner comparison, recovery behaviour on/off, 20 or more trials per condition | planned |
| 5. Diagnosis and iteration | Explain failures from logs and short rosbag excerpts | planned |
| 6. Extension | Custom mission/waypoint node and custom recovery behaviour, effect isolated by the on/off ablation; simulated thermal camera in Gazebo for later use by Project 3 | planned |
| 7. Report and release | Report, TF and architecture diagrams, trial logs and plots, demo video; fresh clone plus one command reproduces the headline table | planned |
