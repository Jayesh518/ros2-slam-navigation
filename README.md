# ROS 2 Mobile Robot: SLAM, Localization and Navigation

**Status: Phase 4 of 7 (planner and controller comparison) complete; diagnosis of failures is next**

A simulated differential-drive robot that maps an unknown environment, localizes itself, and navigates to goals while avoiding obstacles, built on mature ROS 2 packages (SLAM Toolbox, AMCL, Nav2).

Part 2 of 3: follows [robust-computer-vision](https://github.com/jayesh518/robust-computer-vision) and feeds [autonomous-rescue-rover](https://github.com/jayesh518/autonomous-rescue-rover).

## Planned scope
- ROS 2 + Gazebo + RViz simulation, no hardware.
- Map building with SLAM Toolbox, localization with AMCL.
- Nav2 goal navigation and obstacle avoidance.
- At least one custom ROS 2 node (e.g. waypoint sequencing or recovery behaviour).
- Repeatable trials across maps and start/goal pairs.

## Metrics (reported only once measured)
Navigation success rate, collisions, time to goal, path length, recovery events, with number of trials and conditions stated.

## Structure
```
src/        ROS 2 packages and launch files
maps/       saved maps
docs/       report.md and diagrams/ (TF and architecture)
```

## Progress figures
One final screenshot per phase, with captions, in [docs/figures](docs/figures/README.md).

![Phase 1: stock Nav2 smoke test in RViz 2 (map, costmaps, laser scan, AMCL particles; not our own robot yet)](docs/figures/phase1-smoke-test-rviz.png)

![Phase 2: our own Burger-based robot in the office world (Gazebo Sim)](docs/figures/phase2-robot-in-world-b.png)

![The three study worlds (plans generated from the SDF files)](docs/figures/world-plans.png)

## Results so far
Baseline (shipped Nav2 defaults: NavFn planner, MPPI controller) against four variants that each change one component (Smac2D or Theta\* planner; DWB or Regulated Pure Pursuit controller): 400 simulated trials in four worlds, 20 start/goal pairs each, no collisions. Details, limits and the decision rule: [docs/results.md](docs/results.md); baseline alone: [docs/baseline.md](docs/baseline.md).

- Success was at or near 100% in the open room, the pillar grid and the dense-clutter world for every configuration; all differences are in the office world (baseline 16/20, Smac2D 11/20, Theta\* 19/20, DWB 11/20, RPP 11/20). By the pre-registered rule no variant changed success clearly, except Regulated Pure Pursuit in the original three worlds (-10 points, exactly at the threshold).
- Smac2D and Theta\* found routes about 7% shorter and 6 to 7 s faster than the baseline; Regulated Pure Pursuit was about 4 s slower.
- DWB and Regulated Pure Pursuit failures in the office coincide with large localisation error (cause not yet diagnosed).
- Not yet done: the custom recovery behaviour (Phase 6) and the diagnosis of the failures (Phase 5). Results are from simulation only.

![Success by configuration and world](docs/figures/phase4-success-by-config.png)

![Paired differences to the baseline](docs/figures/phase4-paired-differences.png)

## Notes
My contribution is configuration, integration, custom behaviours, experiments and interpretation, not a reimplementation of SLAM or Nav2.
