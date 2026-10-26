# Protocol (Project 2)

**Status: FROZEN v1, 2026-10-26.** No trial is run before that. After that, every change is a dated entry in "Change log" at the end, never an edit in place.

Frozen: yes (2026-10-26)

## 1. Question
Across three simulated worlds of rising difficulty, how do Nav2 global-planner choice, local-controller choice and a custom recovery behaviour change navigation success, collisions, time to goal and path length, compared with a default-Nav2 baseline?

## 2. Ownership boundary
SLAM Toolbox, AMCL and Nav2 are used as published. The owner's work is the robot and world descriptions, configuration, the custom recovery node, the trial runner, the experiment and the analysis. Nothing here claims real-world performance or any safety property: this is a simulation study.

## 3. Fixed conditions (identical for every configuration)
- Stack: ROS 2 Jazzy, Gazebo Harmonic, Nav2 1.3.13, SLAM Toolbox 2.8.5 (versions re-recorded in `docs/environment.md`).
- Robot: one differential-drive robot, one LiDAR, wheel odometry. The same URDF/SDF in every trial.
- Sensor noise: LiDAR Gaussian noise with one fixed setting, chosen in Phase 2 and recorded here as a change-log entry before any trial. Without noise, repeated trials would be nearly identical.
- Maps: each world is mapped once with SLAM Toolbox, the map is saved and committed, and the same map is used by AMCL in every trial of that world. Maps are not rebuilt per trial or per configuration.
- Localisation: AMCL with default parameters. The initial pose is set to the true start pose at the start of each trial, so localisation is stressed by driving, not by initialisation.
- Simulation: headless `gz sim -s`, `use_sim_time:=true`, all timeouts in simulated time.
- Everything not named in section 5 stays at the Nav2 Jazzy default. The full parameter file of each configuration is committed under `configs/`.

## 4. Worlds and trials
- Worlds: (A) open room with a few obstacles; (B) office-like layout with corridors and doorways; (C) cluttered or symmetric world that stresses localisation.
- Layouts (draft, `#` wall or obstacle, `S`/`G` example start and goal; exact dimensions fixed in Phase 2, recommended option marked *):
  - A1* open room 10 x 10 m, 4 box obstacles scattered, no walls inside.
    ```
    ##########
    #S   #   #
    #  #     #
    #     #  #
    #  #    G#
    ##########
    ```
  - A2 same room with one long wall segment in the middle (a detour, still open).
  - B1* office 16 x 10 m: central corridor 1.5 m wide, 4 rooms with 1 m doorways.
    ```
    ################
    #S # |   | #   #
    #  /   /   / G #
    #  ############ #
    ```
    (simplified: corridor along the middle, rooms off both sides)
  - B2 office with two parallel corridors joined by a door, so two routes to some goals.
  - C1* cluttered 12 x 12 m: a 4 x 4 grid of identical pillars (symmetric, feature-poor, stresses AMCL).
  - C2 cluttered room of randomly placed boxes (fixed seed), dense but not symmetric.
  **Chosen (2026-10-26): A1, B1, C1.** Changes after this are logged as changes.
- Start/goal pairs: 10 per world, chosen once, checked as reachable, with straight-line distance of at least 4 m, written to `configs/pairs.yaml` and committed before any trial. They are not changed after results are seen.
- Repeats: 2 trials per pair per configuration, so 20 trials per world per configuration. Each trial has a recorded seed.
- Order: trials run in a randomised order (fixed shuffle seed) so drift in the machine is not confounded with a configuration.

## 5. Configurations (one change at a time from the baseline)
**Amended 2026-10-26, see change log (e): the shipped Jazzy default controller is MPPI, so the baseline controller is MPPI and the row `mppi` below is replaced by `dwb`.**

| Name | Planner | Controller | Recovery |
|---|---|---|---|
| baseline | NavFn | DWB | default behaviours |
| smac2d | SmacPlanner2D | DWB | default |
| thetastar | ThetaStar | DWB | default |
| rpp | NavFn | Regulated Pure Pursuit | default |
| mppi | NavFn | MPPI | default |
| recovery | NavFn | DWB | default plus custom recovery node |

Total: 6 configurations x 3 worlds x 20 trials = 360 trials. If measured wall-clock cost in Phase 2 makes this too slow, the grid is cut before any trial is run (fewer repeats, not a different analysis), and the cut is logged.

## 6. Metrics (per trial, one CSV row)
- **Success:** the robot's ground-truth position is within 0.25 m of the goal before 120 s of simulated time have passed, and Nav2 did not abort the goal. Anything else is a failure, with a failure reason recorded (timeout, aborted, other).
- **Collisions:** number of contact events from a Gazebo contact sensor on the base, counted per trial. A trial with a collision can still be a success; both are reported.
- **Time to goal (s, simulated) and path length (m):** from timestamps and the ground-truth pose path. Reported on successful trials only, and always with the number of successful trials.
- **Recovery events:** number of behaviour-tree recovery activations per trial.
- **Localisation error:** distance between the AMCL pose and the Gazebo ground-truth pose, sampled during the trial; report the maximum and the mean per trial.
- **Failure attribution (for H3):** a failed trial counts as a localisation failure if the AMCL-to-truth error exceeded 0.5 m at any time in the 10 s before the end of the trial; otherwise a planning/control failure.

## 7. Hypotheses (fixed before any trial)
- **H1:** planner choice changes success little in world A but more in world C.
- **H2:** the custom recovery behaviour raises success in world C at a cost in time to goal.
- **H3:** localisation error is highest in the most symmetric or feature-poor world, and failures there come mostly from localisation, not planning.

H1 and H2 are statements about specific worlds. With 20 trials per cell they are tested at low power (see section 8), and the report says so.

## 8. Analysis and decision rule
Unit of analysis: the start/goal pair. For each pair and configuration, success is the fraction of its 2 trials that succeeded (0, 0.5 or 1). Differences to baseline are paired by pair.

- **Primary comparisons (5):** each non-baseline configuration against the baseline, pooled over all 30 pairs (3 worlds x 10).
  - Success: paired mean difference in success fraction, with a 95 percent bootstrap interval over pairs (10,000 resamples, fixed seed). A difference counts as **real** if its size is at least 10 percentage points and the interval excludes zero.
  - Time to goal and path length: paired difference on pairs where both configurations succeeded, 95 percent bootstrap interval. Real if the interval excludes zero and the size is above 5 percent of the baseline value.
  - Anything else is reported as **no clear effect**.
- **Per-world results (secondary, covers H1, H2, H3):** the same quantities within each world (10 pairs), reported with intervals and labelled **suggestive**, never "real", because they rest on 10 pairs.
- **Descriptive:** per configuration and world, success rate with a Wilson 95 percent interval and the number of trials.
- No correction for multiple comparisons; the report states that 5 primary comparisons were made and that intervals are unadjusted.
- Unsupported hypotheses are reported as unsupported. Negative and mixed results are reported as they are.

Why pairs and not trials as the unit: the two repeats of one pair are not independent, so treating 20 trials as 20 independent samples would give intervals that are too narrow.

## 9. Known limits (stated now, repeated in the report)
Simulation hides real sensor noise, wheel slip, lighting and latency. Gazebo physics, AMCL particles and the Nav2 behaviour tree are not fully deterministic; the spread of repeated identical trials is measured in Phase 2. Three worlds and 10 pairs per world is a small sample of environments. Results hold for these worlds, this robot and these default parameters only.

## Change log
- 2026-10-26: v1 frozen by the owner. Layouts A1, B1, C1. Decision rule is the pair-level paired bootstrap in section 8 (replaces the trial-level draft in PLAN.md section 3). No trial has been run.
- 2026-10-26: v1 frozen by the owner (Layouts A1, B1, C1; decision rule is the pair-level paired bootstrap in section 8, replaces the trial-level draft in PLAN.md section 3). No trial has been run.
- 2026-10-26 (before any trial): fixed conditions that section 3 left open. (a) Robot: own differential-drive description (`src/nav_study_robot`, parameters in `config/robot_params.yaml`) modelled on the TurtleBot 3 Burger: wheel radius 0.033 m, separation 0.160 m, 360-sample LiDAR at 5 Hz, range 0.12 to 3.5 m, speed limits 0.22 m/s and 2.84 rad/s. (b) LiDAR noise: Gaussian, mean 0, standard deviation 0.01 m (the value in the Burger simulation file). (c) Collisions are counted from Gazebo contact sensors on the base, LiDAR and both wheels; a contact counts only if the other body is not the ground plane. (d) The Gazebo real-time factor is a fixed condition, chosen after a check with the study robot (see `docs/environment.md`, Timing); the value is recorded here as a further entry before the baseline.
- 2026-10-26 (before any trial) (e): **baseline controller corrected.** Section 5 and PLAN.md assumed the shipped Nav2 default controller was DWB. The shipped file for Nav2 1.3.13 (`/opt/ros/jazzy/share/nav2_bringup/params/nav2_params.yaml`) uses **MPPI** (`nav2_mppi_controller::MPPIController`) with the NavFn planner. The baseline is defined as "default planner and controller as shipped for Jazzy" (PLAN.md section 3), so the baseline is NavFn + MPPI. The configuration `mppi` is therefore the baseline itself, and the controller comparison becomes `dwb` (DWB) and `rpp` (Regulated Pure Pursuit) against it. Still 6 configurations (baseline, smac2d, thetastar, dwb, rpp, recovery), 360 trials. Hypotheses and the decision rule are unchanged. Robot-specific edits to the shipped file are only the footprint radius (0.22 to 0.15 m) and the robot's speed limits (0.22 m/s); every configuration file and its exact differences are in `configs/nav2/` (generated, `CHANGES.md`). DWB and RPP use the standard Nav2 default parameter sets with speed limits set to the robot's. No trial had been run.
- 2026-10-26 (before any trial) (f): **maps.** Each world was mapped once with SLAM Toolbox 2.8.5 (default parameters) while Nav2 drove a fixed waypoint tour (`scripts/map_world.sh`; `configs/nav2/mapping.yaml` is the baseline with a rolling-window global costmap, used only for mapping, because the static-layer costmap does not grow with a map under construction). Real-time factor 2 during mapping. The saved maps (`maps/world_*.pgm/yaml`) are fixed inputs. Known limits: map rotation of about 1 to 2 degrees relative to the world and unobserved patches (3.5 m LiDAR range). Start/goal pairs are chosen in observed free space. Trials use the maps through AMCL; ground truth is in the world frame, so the runner converts goals between world and map frames with a fixed per-world alignment fitted offline (documented when written).

