# ros2-slam-navigation (Project 2 of 3)

Personal robotics project by Jayesh Chaudhari (GitHub `Jayesh518`): a Nav2 configuration study in simulation. This repo is public. It is part of a personal AI/ML and robotics portfolio.

## On session start
Read `docs/progress.md` (the journal), then `PLAN.md` (start with section 0, the scenario: what we are building and why) and `PHASES.md`. If the drive crashed or the session was restarted, follow `docs/restore-prompt.md`. Give the owner a short briefing (where we stopped, what is done, the proposed next step) and wait for a go-ahead before doing work.

## Rules (always)
- Work in phases with exit gates (`PHASES.md`, plan in `PLAN.md`). At the end of a phase: update `PHASES.md`, commit and push, then stop and propose the next phase. Do not start the next phase without the owner's go-ahead.
- Fix success measures, trial counts, hypotheses and the decision rule in `docs/protocol.md` BEFORE running any trial. A later change is logged as a change. Report negative and mixed results as they are.
- Commits and PRs: the owner's identity only (`Jayesh chaudhari <127026542+Jayesh518@users.noreply.github.com>`). Never add `Co-Authored-By`, "Generated with Claude" or any other AI attribution line. Never force-push or skip hooks. "commit and push" is a standing authorisation: stage, commit, `git push origin main`.
- Fully personal project: no employer code, data, hardware, designs or documents, and no mention of employer products. Never copy confidential material.
- SLAM Toolbox, AMCL and Nav2 are used as published; do not describe them as the owner's algorithms. The owner's work is configuration, integration, custom nodes, the trial runner, experiments and analysis.
- Do not commit secrets, rosbags (`*.db3`, `*.mcap`), videos or build output.
- Screenshots: at the end of every phase take one final screenshot of the result (the app window only, cropped; no desktop or personal items), save it as `docs/figures/phaseN-<what>.png`, add a caption row to `docs/figures/README.md` and link it from `README.md` (and later the report). Screenshots taken only to check something are deleted after use; never commit them.
- No CGPA, phone number or home address anywhere. Contact is the public email on the portfolio only.
- Verify versions and package names against the official ROS 2 Jazzy, Gazebo Harmonic and Nav2 documentation before installing; the docs win over `PLAN.md`.
- Make no safety or life-saving claims; this is a simulation study.
- The external drive can crash. Keep `docs/progress.md` current after every meaningful step (dated session-log line, current state, next steps), and commit and push after each finished step and at least every 30 minutes of work. Gazebo and RViz are already installed on the drive: check with `scripts/check_env.sh`, install only what is missing.
- `PLAN.md` is a starting point, not a fixed path. Actively suggest better designs, experiments, metrics, tools or scope cuts (with the reason and the cost, and one recommended option), especially at each phase gate and after surprising results. The owner decides. Record accepted changes in `PHASES.md` and the "Plan changes" list in `docs/progress.md`; park declined ideas under "Ideas parked". After `docs/protocol.md` is committed, protocol changes are logged as dated changes and never applied silently or backwards.
