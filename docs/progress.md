# Progress journal (Project 2)

The external drive can crash, so this file is the memory of the project. Update it after every meaningful step, then commit and push. Keep "Current state" and "Next steps" accurate; append to the session log, never rewrite history.

## Current state
- Date of last update: 2026-10-26
- Phase: 1 done (gate passed 2026-10-26). Phase 2 next, awaiting owner go-ahead.
- Environment: Ubuntu 24.04 external drive. `scripts/check_env.sh` reports all required items present (Nav2 1.3.13, SLAM Toolbox 2.8.5, Gazebo 8.15.0, pandas) after installing the 4 missing ones on 2026-10-26.
- Last commit: see `git log -1`.

## Checklist
- [x] Phase 0: `docs/protocol.md` written, draft items in PLAN.md section 3 finalised with the owner, committed before any trial
- [x] Phase 1: `scripts/check_env.sh` run, result in `docs/environment.md`, missing items installed, smoke test works
- [ ] Phase 2: robot, worlds, trial runner, tests, CI
- [ ] Phase 3: baseline
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

## Ideas parked (suggested, not adopted)
- None yet.

## Open questions
- Which three worlds and which start/goal pairs (Phase 0).
- Own robot description or a stock one for the baseline (decide in Phase 2; plan says own robot).

## Next steps
1. Phase 2 (needs owner go-ahead): decide own robot vs stock (plan says own), build worlds A1/B1/C1, `scripts/env.sh` clean-env helper, trial runner, tests, CI. Measure wall-clock cost of a trial and real-time factor first.

## Session log
- 2026-10-26 (Windows laptop): wrote `PLAN.md`, `CLAUDE.md`, `PHASES.md` update, `scripts/check_env.sh`, this journal and `docs/restore-prompt.md`. No code run yet.
- 2026-10-26 (Ubuntu): environment check found 4 missing items; owner installed navigation2, nav2-bringup, slam-toolbox, python3-pandas via apt; re-check says all required present. Drafted `docs/protocol.md` v0 (decision rule changed from trial-level to pair-level paired bootstrap, see below). Not committed yet.
- 2026-10-26: owner accepted the pair-level decision rule (Plan change: PLAN.md draft rule replaced in protocol v0), B = office world, asked for 1-2 candidate layouts per world with an option to change one. Layout options added to protocol draft; awaiting choice before freeze.
- 2026-10-26: owner chose layouts A1, B1, C1 ("what u like"). Protocol v1 frozen; PHASES.md and PLAN.md updated. Phase 0 complete.
- 2026-10-26 (Ubuntu): Phase 1 work. `docs/environment.md` written (versions, licences, machine). `colcon build` on empty `src/` works. Smoke test: first run crashed RViz and Gazebo GUI (snap VS Code env leaks snap libs); fixed with clean-env launcher `scripts/smoke_test.sh`; Nav2 goal SUCCEEDED, /scan 5 Hz. Also noted: `~/.bashrc` sources `articuno_ws` (unrelated project) which sets Gazebo paths; not edited.
- 2026-10-26 (Ubuntu): second smoke run; Claude took desktop screenshots: RViz showed map, scan, AMCL particles, Nav2 active; goal SUCCEEDED twice. Phase 1 gate passed. Note: stock tb3 world is a hexagon with 9 pillars, a useful reference for world C1.
- 2026-10-26 (Ubuntu): added `docs/figures/` (Phase 1 figure, captions index), README figure section, and a CLAUDE.md rule: one final cropped screenshot per phase, temporary ones deleted after use. Temporary screenshots from the smoke test were deleted.
