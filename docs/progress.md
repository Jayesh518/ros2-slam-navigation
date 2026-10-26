# Progress journal (Project 2)

The external drive can crash, so this file is the memory of the project. Update it after every meaningful step, then commit and push. Keep "Current state" and "Next steps" accurate; append to the session log, never rewrite history.

## Current state
- Date of last update: 2026-10-26
- Phase: 3 in progress (owner approved 20 pairs and go-ahead 2026-10-26). Baseline runs: `scripts/run_config.sh baseline` (world A done 20/20; B and C running). Analysis: `scripts/analyse.py`. Done so far: `scripts/env.sh`, timing and real-time-factor check (stock robot), own Burger-based robot (`src/nav_study_robot`, URDF/SDF/bridge, tested in `test_arena`), STEP CAD file for Fusion 360 (`cad/`). Worlds A1/B1/C1 generated and checked; Nav2 configs generated (`configs/nav2/`); SLAM Toolbox maps for all three worlds saved (`maps/`). Left: map-to-world alignment, start/goal pairs, trial runner, metric tests, CI, factor check with own robot.
- Environment: Ubuntu 24.04 external drive. `scripts/check_env.sh` reports all required items present (Nav2 1.3.13, SLAM Toolbox 2.8.5, Gazebo 8.15.0, pandas) after installing the 4 missing ones on 2026-10-26.
- Last commit: see `git log -1`.

## Checklist
- [x] Phase 0: `docs/protocol.md` written, draft items in PLAN.md section 3 finalised with the owner, committed before any trial
- [x] Phase 1: `scripts/check_env.sh` run, result in `docs/environment.md`, missing items installed, smoke test works
- [x] Phase 2: robot, worlds, trial runner, tests, CI
- [~] Phase 3: baseline (running)
- [ ] Phase 4: intervention
- [ ] Phase 5: diagnosis
- [ ] Phase 6: extension
- [ ] Phase 7: report and release

## What this project is, in one paragraph
A Nav2 configuration study in simulation: a differential-drive robot in Gazebo builds maps (SLAM Toolbox), localises (AMCL) and navigates (Nav2); we add our own robot and worlds, a trial runner and custom ROS 2 nodes, then measure how planner, controller and recovery choices change success, collisions, time and path length. It is Project 2 of 3 in a personal research-grade portfolio and prepares Project 3 (a physical rover). Full scenario: PLAN.md section 0.

## Decisions made (do not re-ask)
- ROS 2 Jazzy + Gazebo Harmonic + Nav2 + SLAM Toolbox on Ubuntu 24.04 (verified against REP-2000 on 2026-10-26).
- Gazebo and RViz are already installed on the drive; check, do not reinstall.
- Experiment style: one change at a time from a default-Nav2 baseline; draft grid and hypotheses in PLAN.md section 3 (still DRAFT until Phase 0).

## Plan changes (dated; why; who decided)
- 2026-10-26: decision rule changed from trial-level Wilson intervals to pair-level paired bootstrap (draft rule could never be met at n=20 per cell). Decided by owner ("do as u like"), proposed by Claude.

- 2026-10-26: robot decision (was an open question): own differential-drive robot description, modelled on the TurtleBot 3 Burger as reference (owner: "use turtlebot 3 burger for reference"). Interpreted as: dimensions, sensor and drive parameters from the Burger so Nav2 defaults stay valid; stock Burger remains the cross-check.

- 2026-10-26: BASELINE CONTROLLER CORRECTED (protocol change (e)): the shipped Jazzy default is MPPI, not DWB as PLAN.md assumed; baseline = NavFn + MPPI, DWB becomes a variant. Found by reading the shipped nav2_params.yaml; applied before any trial; owner to be told (no objection raised so far).

- 2026-10-26: PROPOSED, awaiting owner: replace 2 repeats x 10 pairs by 1 repeat x 20 pairs per world (same 360 trials). Reason: repeats of the same pair vary by only about 2 percent in time (protocol change log (j)), so the second repeat is nearly redundant, while more pairs widen what the results generalise to and tighten the pair-level interval. Cost: pairs file must be extended (10 more per world, same script and seed rule) before any trial.

## Ideas parked (suggested, not adopted)
- None yet.

## Open questions
- Which three worlds and which start/goal pairs (Phase 0).
- (resolved 2026-10-26: own robot modelled on TurtleBot 3 Burger.)

## Next steps
1. Owner decides: keep 2 repeats x 10 pairs, or 1 repeat x 20 pairs per world (see Plan changes, PROPOSED). If 20 pairs: extend `configs/pairs.yaml` first.
2. Phase 3: baseline runs (`scripts/run_session.sh baseline world_x 1 1 2`) for the three worlds, then analysis script with Wilson intervals and a baseline figure.
3. (done in Phase 2:) Nav2 baseline config for our robot (`configs/`), then the trial runner (explicit zero cmd_vel at the end), metric unit tests, CI.
3. Repeat the real-time-factor check with our robot and baseline, then log the chosen factor in the protocol change log.
4. Owner: open `cad/nav_study_robot_v1.step` in Fusion 360 and report anything odd.

## Session log
- 2026-10-26 (Windows laptop): wrote `PLAN.md`, `CLAUDE.md`, `PHASES.md` update, `scripts/check_env.sh`, this journal and `docs/restore-prompt.md`. No code run yet.
- 2026-10-26 (Ubuntu): environment check found 4 missing items; owner installed navigation2, nav2-bringup, slam-toolbox, python3-pandas via apt; re-check says all required present. Drafted `docs/protocol.md` v0 (decision rule changed from trial-level to pair-level paired bootstrap, see below). Not committed yet.
- 2026-10-26: owner accepted the pair-level decision rule (Plan change: PLAN.md draft rule replaced in protocol v0), B = office world, asked for 1-2 candidate layouts per world with an option to change one. Layout options added to protocol draft; awaiting choice before freeze.
- 2026-10-26: owner chose layouts A1, B1, C1 ("what u like"). Protocol v1 frozen; PHASES.md and PLAN.md updated. Phase 0 complete.
- 2026-10-26 (Ubuntu): Phase 1 work. `docs/environment.md` written (versions, licences, machine). `colcon build` on empty `src/` works. Smoke test: first run crashed RViz and Gazebo GUI (snap VS Code env leaks snap libs); fixed with clean-env launcher `scripts/smoke_test.sh`; Nav2 goal SUCCEEDED, /scan 5 Hz. Also noted: `~/.bashrc` sources `articuno_ws` (unrelated project) which sets Gazebo paths; not edited.
- 2026-10-26 (Ubuntu): second smoke run; Claude took desktop screenshots: RViz showed map, scan, AMCL particles, Nav2 active; goal SUCCEEDED twice. Phase 1 gate passed. Note: stock tb3 world is a hexagon with 9 pillars, a useful reference for world C1.
- 2026-10-26 (Ubuntu): added `docs/figures/` (Phase 1 figure, captions index), README figure section, and a CLAUDE.md rule: one final cropped screenshot per phase, temporary ones deleted after use. Temporary screenshots from the smoke test were deleted.
- 2026-10-26 (Ubuntu): Phase 2 started. `scripts/env.sh` written; found the repo's first colcon build had baked `articuno_ws` into `install/` prefix chain, rebuilt in the clean env. Timing: headless stock sim runs at real-time factor 1 by default (59 s for one goal); raising to 10 via `gz service set_physics` gave 56 sim-s in 5.7 s wall. Owner chose TurtleBot 3 Burger as reference for the robot.
- 2026-10-26 (Ubuntu): real-time factor on stock robot: 1, 2, 4 reach 6/6 goals; 10 only 3/6 (earlier 2/6) so 10 is out. Built `nav_study_robot` (params YAML as single source, URDF, SDF, bridge) and `nav_study_bringup` (sim launch, test arena). Fixed contact topics (scoped names) in the bridge. Created `cad/make_robot_cad.py` and `cad/nav_study_robot_v1.step` (20 solids, 178 x 192 mm, self-check OK). Protocol change log: robot, noise 0.01 m, contact rule, factor to be set. Installed cadquery 2.8.0 into the repo `.venv`.
- 2026-10-26 (Ubuntu): `scripts/make_worlds.py` writes `world_a/b/c.sdf` (valid, scans sane: A 66 hits min 1.69 m; B 313 hits min 0.68 m; C 65 hits 1.49 to 1.77 m from origin). `scripts/plot_worlds.py` -> `docs/figures/world-plans.png`. `scripts/stop_sim.sh` stops sim processes (do not use `pkill -f` with text that appears in your own command line; it kills the calling shell). PLAN.md layout line updated (worlds live in the bringup package).
- 2026-10-26 (Ubuntu): `configs/nav2/` generated by `scripts/make_nav2_configs.py` (baseline, smac2d, thetastar, dwb, rpp, mapping, CHANGES.md). Mapping took several fixes: stale `parameter_bridge` processes (15-char process-name truncation) published a second /clock; goals must be stamped time 0; static-layer global costmap does not grow with SLAM, so mapping uses a rolling-window costmap. Maps: A 18/18 waypoints, B 37/40 (3 room-interior goals failed), C 32/32. Figure `docs/figures/maps-slam.png`. Protocol change-log entries (e) controller, (f) maps.
- 2026-10-26 (Ubuntu): Phase 2 build-out. Added `scripts/align_map.py` (-> `configs/map_alignment.yaml`: A 2.4 deg, B 0.22 m shift, C identity), `scripts/make_pairs.py` (-> `configs/pairs.yaml`, 10 per world, seed 20261026), `src/nav_study_trials` (metrics.py + runner.py, 8 unit tests), `tests/test_study_files.py` (8 tests), `.github/workflows/ci.yml`, `scripts/run_session.sh`, `rtf_check_robot.sh`, `determinism_check.sh`. First end-to-end trials work. Protocol change log (g) success tolerance 0.5 m, (h) real-time factor 1, (i) reset verification, (j) repeatability. Validation CSVs in `results/validation/` (not study data). Left: CI result, Phase 2 screenshot, gate report.
- 2026-10-26 (Ubuntu): Phase 2 gate. CI fixed twice (git missing in the ros:jazzy image; nav_study_robot installed an untracked empty launch/ dir) and is green. Final figure `docs/figures/phase2-robot-in-world-b.png`; README updated. Temporary screenshots deleted.
- 2026-10-26 (Ubuntu): Owner chose 20 pairs per world (protocol change (k)); pairs extended (first 10 unchanged). Added `analysis.py` (pre-registered decision rule + 5 unit tests), `scripts/analyse.py`, `scripts/run_config.sh`. Baseline world A: 20/20 succeeded. World B running (first timeouts seen).
