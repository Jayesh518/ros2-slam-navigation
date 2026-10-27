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
**A fourth world D (dense random clutter) was added on 2026-10-26 after the baseline had been run in A to C; see change log (l).**

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
- Start/goal pairs: **20 per world (amended 2026-10-26, change log (k); was 10)**, chosen once, checked as reachable, with straight-line distance of at least 4 m, written to `configs/pairs.yaml` and committed before any trial. They are not changed after results are seen.
- Repeats: **1 trial per pair per configuration (amended, change log (k); was 2)**, so 20 trials per world per configuration, as before. Each trial has a recorded seed.
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

Total: 6 configurations x 3 worlds x 20 trials = 360 trials (**480 with world D, change log (l)**). If measured wall-clock cost in Phase 2 makes this too slow, the grid is cut before any trial is run (fewer repeats, not a different analysis), and the cut is logged.

## 6. Metrics (per trial, one CSV row)
- **Success** (tolerance amended 2026-10-26, see change log (g)): the robot's ground-truth position is within 0.5 m (was 0.25 m) of the goal before 120 s of simulated time have passed, and Nav2 did not abort the goal. Anything else is a failure, with a failure reason recorded (timeout, aborted, other).
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
Unit of analysis: the start/goal pair. For each pair and configuration, success is 1 or 0 (one trial per pair; amended, change log (k)). Differences to baseline are paired by pair.

- **Primary comparisons (5):** each non-baseline configuration against the baseline, pooled over all 60 pairs (3 worlds x 20; amended, change log (k)).
  - Success: paired mean difference in success fraction, with a 95 percent bootstrap interval over pairs (10,000 resamples, fixed seed). A difference counts as **real** if its size is at least 10 percentage points and the interval excludes zero.
  - Time to goal and path length: paired difference on pairs where both configurations succeeded, 95 percent bootstrap interval. Real if the interval excludes zero and the size is above 5 percent of the baseline value.
  - Anything else is reported as **no clear effect**.
- **Per-world results (secondary, covers H1, H2, H3):** the same quantities within each world (20 pairs), reported with intervals and labelled **suggestive**, never "real", because they rest on 20 pairs per world.
- **Descriptive:** per configuration and world, success rate with a Wilson 95 percent interval and the number of trials.
- No correction for multiple comparisons; the report states that 5 primary comparisons were made and that intervals are unadjusted.
- Unsupported hypotheses are reported as unsupported. Negative and mixed results are reported as they are.

Why pairs as the unit: trials on the same pair are almost the same trial (change log (j)), so the pair, not the trial, is the independent sample.

## 9. Known limits (stated now, repeated in the report)
Simulation hides real sensor noise, wheel slip, lighting and latency. Gazebo physics, AMCL particles and the Nav2 behaviour tree are not fully deterministic; the spread of repeated identical trials is measured in Phase 2. Three worlds and 10 pairs per world is a small sample of environments. Results hold for these worlds, this robot and these default parameters only.

## Change log
- 2026-10-26: v1 frozen by the owner. Layouts A1, B1, C1. Decision rule is the pair-level paired bootstrap in section 8 (replaces the trial-level draft in PLAN.md section 3). No trial has been run.
- 2026-10-26: v1 frozen by the owner (Layouts A1, B1, C1; decision rule is the pair-level paired bootstrap in section 8, replaces the trial-level draft in PLAN.md section 3). No trial has been run.
- 2026-10-26 (before any trial): fixed conditions that section 3 left open. (a) Robot: own differential-drive description (`src/nav_study_robot`, parameters in `config/robot_params.yaml`) modelled on the TurtleBot 3 Burger: wheel radius 0.033 m, separation 0.160 m, 360-sample LiDAR at 5 Hz, range 0.12 to 3.5 m, speed limits 0.22 m/s and 2.84 rad/s. (b) LiDAR noise: Gaussian, mean 0, standard deviation 0.01 m (the value in the Burger simulation file). (c) Collisions are counted from Gazebo contact sensors on the base, LiDAR and both wheels; a contact counts only if the other body is not the ground plane. (d) The Gazebo real-time factor is a fixed condition, chosen after a check with the study robot (see `docs/environment.md`, Timing); the value is recorded here as a further entry before the baseline.
- 2026-10-26 (before any trial) (e): **baseline controller corrected.** Section 5 and PLAN.md assumed the shipped Nav2 default controller was DWB. The shipped file for Nav2 1.3.13 (`/opt/ros/jazzy/share/nav2_bringup/params/nav2_params.yaml`) uses **MPPI** (`nav2_mppi_controller::MPPIController`) with the NavFn planner. The baseline is defined as "default planner and controller as shipped for Jazzy" (PLAN.md section 3), so the baseline is NavFn + MPPI. The configuration `mppi` is therefore the baseline itself, and the controller comparison becomes `dwb` (DWB) and `rpp` (Regulated Pure Pursuit) against it. Still 6 configurations (baseline, smac2d, thetastar, dwb, rpp, recovery), 360 trials. Hypotheses and the decision rule are unchanged. Robot-specific edits to the shipped file are only the footprint radius (0.22 to 0.15 m) and the robot's speed limits (0.22 m/s); every configuration file and its exact differences are in `configs/nav2/` (generated, `CHANGES.md`). DWB and RPP use the standard Nav2 default parameter sets with speed limits set to the robot's. No trial had been run.
- 2026-10-26 (before any trial) (f): **maps.** Each world was mapped once with SLAM Toolbox 2.8.5 (default parameters) while Nav2 drove a fixed waypoint tour (`scripts/map_world.sh`; `configs/nav2/mapping.yaml` is the baseline with a rolling-window global costmap, used only for mapping, because the static-layer costmap does not grow with a map under construction). Real-time factor 2 during mapping. The saved maps (`maps/world_*.pgm/yaml`) are fixed inputs. Known limits: map rotation of about 1 to 2 degrees relative to the world and unobserved patches (3.5 m LiDAR range). Start/goal pairs are chosen in observed free space. Trials use the maps through AMCL; ground truth is in the world frame, so the runner converts goals between world and map frames with a fixed per-world alignment fitted offline (documented when written).
- 2026-10-26 (before any trial) (g): **success tolerance and metric definitions made precise.** (1) Ground-truth arrival tolerance changed from 0.25 m to **0.5 m**. Reason: found in the first pipeline trial (`results/validation/first_pipeline_trial.csv`): Nav2 stops as soon as it believes it is within its own 0.25 m goal tolerance, and AMCL's position error is about 0.15 m, so a 0.25 m ground-truth check fails trials at random (final error 0.265 m for a trial Nav2 reported as succeeded) and would mostly measure AMCL noise, not navigation. 0.5 m is twice Nav2's tolerance and equals the localisation-failure threshold; Nav2 must still report SUCCEEDED, and `final_error_m` is recorded for every trial. The value was chosen by this argument, not from outcomes; one validation trial had been seen. (2) A **recovery event** is an activation (IDLE to any other status) of the behaviour-tree nodes `ClearLocalCostmap-Subtree`, `Spin`, `Wait` or `BackUp` of the default NavigateToPose tree. (3) A **collision** is one contact episode (contact messages between the same robot part and the same non-ground body, at most 0.5 s apart count as one) from the contact sensors on the base, LiDAR and both wheels. (4) **Seeds:** `gz sim --seed` is set per session (one session = one configuration in one world, all its trials in a randomised order); AMCL and Nav2 are not seedable, so identical repeated trials are expected to differ and the spread is measured in Phase 2. (5) Trials run in persistent sessions (one per configuration and world); between trials the robot is teleported to the start pose, the AMCL pose is set to the true start pose, and the costmaps are cleared.
- 2026-10-26 (before any trial) (h): **real-time factor fixed at 1** (Gazebo default, no speed-up), after a check with the study robot and the baseline configuration (`results/validation/rtf_robot_f*.csv`, `scripts/rtf_check_robot.sh`; same 6 pairs of world A at factors 1, 2 and 4). Factors 2 and 4 made trials slower (about 10 percent at factor 2) and changed one route, because the planner and controller are CPU-bound; factor 10 on the stock robot changed outcomes (3 of 6 goals reached against 6 of 6). Cost: about 40 s wall per trial, so the 360-trial grid is roughly 5 to 6 hours plus about 1 minute start-up per session (36 sessions). Sample sizes in this check are small (6 trials per factor).
- 2026-10-26 (before any trial) (i): **reset verification and validity.** The runner verifies, against ground truth, that AMCL accepted the true start pose (error below 0.5 m), retries up to 5 times, and otherwise records the trial with `valid=0`, `failure_reason=invalid_reset` and does not send a goal; invalid trials are excluded from success rates and their number is reported. Reason: in validation one trial started with AMCL 6 m off (the initial pose was ignored right after the teleport), which would have been counted as a navigation failure. The reset check uses ground truth only to validate the reset, never to help navigation.
- 2026-10-26 (before any trial) (j): **repeatability measured.** Same pair (baseline, world A, a01) 10 times in one session: all succeeded, time 35.07 +- 0.57 s, path 6.512 +- 0.049 m. In 3 fresh sessions with the same seed: times 34.49 to 35.04 s, paths 6.48 to 6.64 m. Trials are not bit-identical (AMCL and Nav2 are not seedable) but the spread is small, about 2 percent in time. Consequence for the design: a second repeat of the same pair adds little information beyond the first; the pair is the effective unit (section 8 already analyses by pair). Whether to replace the second repeat by more pairs is raised with the owner at the Phase 2 gate; nothing is changed here.
- 2026-10-26 (before any trial) (k): **20 pairs per world, 1 trial per pair (was 10 pairs x 2 repeats).** Reason: repeats of one pair varied by only about 2 percent in time and all succeeded (change log (j)), so the second repeat is nearly redundant, while more pairs cover more start/goal situations and give the paired comparison 60 independent units instead of 30. Total trials unchanged: 6 configurations x 3 worlds x 20 = 360. The first 10 pairs per world are the ones already in `configs/pairs.yaml`; 10 more per world (ids x11 to x20) were added with `scripts/make_pairs.py` (seed 20261026 + 1 + 10, same selection rules) and no existing pair was changed. Validation trials (`results/validation/`) used only pairs a01 to a06. Section 8 numbers updated accordingly (60 pooled pairs; per-world 20 pairs). The decision rule, thresholds and hypotheses are unchanged. Proposed by Claude, approved by the owner. No study trial had been run.
- 2026-10-26 (m, entry numbered (l)): **fourth world D added after seeing the baseline in A to C.** The baseline reached 20 of 20 in world A and in world C1 (`docs/baseline.md`), so H2 (the custom recovery raises success in the cluttered world) cannot be shown in C1: there is no room to improve. With the owner's approval (option b), world D was added: 12 x 12 m room, 24 randomly placed boxes and cylinders (fixed seed 20261027, at least 0.8 m between obstacles, a clear disc at the spawn point; `scripts/make_worlds.py`), mapped once with SLAM Toolbox (`maps/world_d.*`, 41 of 43 tour waypoints reached), alignment fitted (`configs/map_alignment.yaml`), 20 pairs drawn (`scripts/make_pairs.py`, seed 20261027 + 100, same rules; the 60 pairs of A to C are unchanged). **Status of D:** it is a post-hoc addition made because of what the baseline showed. All results for A to C are reported as originally designed; D is reported separately and labelled as added after the baseline. The decision rule is applied to D unchanged, and the pooled primary comparison is reported both over A to C only (60 pairs, the original design) and over A to D (80 pairs). H2 is tested in C1 as pre-registered (expected untestable because of the ceiling) and additionally in D; the D test is labelled post-hoc. Total grid: 6 configurations x 4 worlds x 20 = 480 trials. No trial in D had been run when this entry was written.

- 2026-10-27 (before any `recovery` trial) (n): **the `recovery` configuration is defined (Phase 6, step 1); H2 is re-targeted.** 400 trials of Phase 4 and 44 trials of Phase 5 had been seen; no `recovery` trial had been run. (1) **What it is.** An external ROS 2 node `plan_flip_guard` (package `nav_study_trials`), launched next to Nav2 only in this configuration (`guard:=true`); the Nav2 parameter file `configs/nav2/recovery.yaml` is identical to `baseline.yaml` (NavFn + MPPI), so the only difference is the node. It is not a behaviour-tree plugin; it acts through a published, runtime-settable planner parameter. (2) **Detection.** It reads `/plan`. A *flip* is a change of more than 3.0 m in the length of the global plan between two consecutive plans (the Phase 5 definition). A *trigger* is 3 flips within 30 s of simulated time while a NavigateToPose goal is active. (3) **Action.** On a trigger it sets `planner_server` parameter `GridBased.allow_unknown` to `false`, at most once per goal. When no goal has been active for 2 s it sets the parameter back to `true`, so every trial starts as the baseline does. Nothing else is changed (no costmap clearing, no waypoints). (4) **Thresholds.** 3 m, 3 flips and 30 s were fixed from the Phase 5 baseline traces of world B (flipping trials show 3 to 21 flips, roughly one every 3 to 10 s; the shortest flipping episode, b11, had 3 flips in 14 s; non-flipping trials show none). They were chosen on the same pairs the guard is then tested on, so the world-B result is **not independent of the design** and probably optimistic; they will not be changed after the first trial. (5) **Trials.** 4 worlds x 20 pairs x 1 trial = 80 trials, the same pairs and session seeds as the other configurations (`scripts/run_config.sh recovery`); the runner adds a column `guard_triggers` (number of triggers during the trial) for this configuration only. (6) **Hypothesis H2 (re-targeted).** Original H2 ("raises success in world C at a cost in time") is untestable in C1 and D (baseline 20/20, ceiling). It is replaced by **H2b**: in world B the guard raises success compared with the baseline (prediction: at least 18 of 20 pairs, against the baseline's 16), at a cost in time on the pairs it triggers on; in worlds A, C and D it should trigger rarely or never and change nothing (prediction: success stays 20/20 and a median time difference below 5 percent). H2b is a post-hoc target chosen after seeing the baseline and the diagnosis, and is reported as such. (7) **Decision rule, unchanged.** The primary comparison (recovery against baseline, success fraction over all pairs, rule of section 8) is applied as written, over A to C (60 pairs) and over A to D (80 pairs). Because the baseline fails only in world B, the largest possible pooled gain is 4 of 60 (6.7 points) or 4 of 80 (5 points), below the 10-point threshold: **the pooled rule cannot report a "real" success effect for this configuration, whatever happens**, and the report says so. The world-B comparison (20 pairs) is the one that tests H2b; it is suggestive, as for every per-world result. Time and path are compared on pairs both solved, with the rule of section 8. (8) **Reported either way.** If the guard never triggers, or triggers and does not help, that is the result. Trigger counts per world and per outcome are reported.
