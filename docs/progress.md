# Progress journal (Project 2)

The external drive can crash, so this file is the memory of the project. Update it after every meaningful step, then commit and push. Keep "Current state" and "Next steps" accurate; append to the session log, never rewrite history.

## Current state
- Date of last update: 2026-10-26
- Phase: none started. Plan written (`PLAN.md`), rules in `CLAUDE.md`, phases in `PHASES.md`.
- Environment: Ubuntu 24.04 on an external SATA drive; Gazebo and RViz already installed there (per the owner). Nothing else verified yet.
- Last commit: see `git log -1`.

## Checklist
- [ ] Phase 0: `docs/protocol.md` written, draft items in PLAN.md section 3 finalised with the owner, committed before any trial
- [ ] Phase 1: `scripts/check_env.sh` run, result in `docs/environment.md`, missing items installed, smoke test works
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

## Open questions
- Which three worlds and which start/goal pairs (Phase 0).
- Own robot description or a stock one for the baseline (decide in Phase 2; plan says own robot).

## Next steps
1. On the Ubuntu drive: clone the repo, set the git identity, `gh auth login` (PLAN.md section 7).
2. Run `bash scripts/check_env.sh`, note the result here.
3. Phase 0: write `docs/protocol.md` with the owner, then commit and push.

## Session log
- 2026-10-26 (Windows laptop): wrote `PLAN.md`, `CLAUDE.md`, `PHASES.md` update, `scripts/check_env.sh`, this journal and `docs/restore-prompt.md`. No code run yet.
