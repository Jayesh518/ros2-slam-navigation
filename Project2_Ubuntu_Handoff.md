# Project 2 handoff: what to do when you go to the Ubuntu drive

Saved 2026-10-26 on the Windows laptop. Self-contained: everything you need is in this file. Nothing for Project 2 has been run yet; the plan, rules and tools are written and pushed to GitHub.

## What we are doing (one paragraph)
Project 2 of 3 in your personal research-grade AI and robotics portfolio: a Nav2 configuration study in simulation. A differential-drive robot in Gazebo builds maps (SLAM Toolbox), localises (AMCL) and navigates (Nav2). You build the robot and worlds, an automated trial runner and custom ROS 2 nodes, then measure how planner, controller and recovery choices change success, collisions, time to goal and path length. It also prepares Project 3 (a physical rover). Full scenario: `PLAN.md` section 0 in the repo.

## Where everything is
- Repo (public): https://github.com/jayesh518/ros2-slam-navigation (branch `main`, latest commit when this was written: `605951b`).
- Inside the repo: `CLAUDE.md` (rules for Claude Code), `PLAN.md` (scenario, stack, draft experiment, phases, requirements, crash rules), `PHASES.md`, `docs/progress.md` (the journal), `docs/restore-prompt.md`, `scripts/check_env.sh` (read-only environment check).
- GitHub account: `Jayesh518`. Git identity to use: name `Jayesh chaudhari`, email `127026542+Jayesh518@users.noreply.github.com`.

## Steps on Ubuntu (in order)
1. Make sure the basics exist: `git --version`, and the GitHub CLI `gh --version` (if missing: `sudo apt update && sudo apt install git gh`).
2. Sign in to GitHub: `gh auth login` (GitHub.com, HTTPS, log in with the browser) as `Jayesh518`.
3. Choose where the project lives (on the external drive, with at least 20 GB free) and clone it:
   `git clone https://github.com/jayesh518/ros2-slam-navigation.git`
4. Set the identity inside the repo:
   `cd ros2-slam-navigation`
   `git config user.name "Jayesh chaudhari"`
   `git config user.email "127026542+Jayesh518@users.noreply.github.com"`
5. Check the environment (read-only, installs nothing):
   `bash scripts/check_env.sh | tee docs/environment-check.txt`
   Gazebo and RViz are already on the drive. Anything marked MISSING gets installed later by Claude Code after it confirms package names in the official docs. Expected ones to check: ROS 2 Jazzy, Gazebo Harmonic (`gz sim --versions` should show 8.x), `ros-jazzy-ros-gz`, Nav2, SLAM Toolbox, colcon, the Python analysis packages.
6. Open the folder in VS Code (`code .`) and start Claude Code in its terminal (install it the same way you did before if it is not there).
7. Paste the prompt in the next section as your first message. It works for the very first session and for every restart after a crash.

## The prompt to paste (first message, every new session)
```text
Restore the Project 2 (ros2-slam-navigation) context and continue the work.

Do this in order, without asking me anything that is already decided in the files:

1. Read CLAUDE.md, PLAN.md (section 0 explains what we are building and why), PHASES.md and docs/progress.md completely. They are the source of truth; treat the decisions listed in docs/progress.md as settled.
2. Check the repository for damage: run `git status`, `git log --oneline -10`, `git fsck --no-dangling` and `git fetch`. Compare with origin/main: tell me if I have uncommitted files, unpushed commits or if the remote is ahead. If git reports corruption, follow the crash rules in PLAN.md section 9 (clone fresh into a new folder, do not repair in place).
3. Run `bash scripts/check_env.sh` and compare with the environment recorded in docs/environment.md (if it exists). Tell me what changed or is missing. Install only what is missing and only after you have confirmed the package names in the official docs.
4. Look for work that was in progress when the drive failed: files newer than the last commit, half-written results, a build folder that is stale. Do not delete anything; list it and tell me what you propose.
5. Give me a short briefing: current phase, what is done, what was lost or is uncertain, and the exact next step from docs/progress.md.
6. Then continue from that next step. Work in small steps. After each finished step: append a dated line to the session log in docs/progress.md, update "Current state" and "Next steps", then `git add`, commit (my identity only, no Co-Authored-By or any AI attribution line) and `git push origin main`.
7. Obey the phase rules: stop at each exit gate, update PHASES.md, push, and ask before starting the next phase. Fix the protocol, metrics and hypotheses in docs/protocol.md before running any trial.

Remember the plan is not a fixed path: if you see a better design, experiment, metric or tool, or a part that is not worth its cost, tell me with a recommendation and record what I accept in docs/progress.md (Plan changes) and PHASES.md. Never change the protocol silently once docs/protocol.md exists.

Be efficient: do not re-explain the plan back to me, do not re-run steps already recorded as done unless step 2 or 3 shows they are broken, and prefer one clear question over many.
```

## What should happen next
- Claude Code reads the files, checks the repo and the environment, briefs you, and proposes Phase 0.
- Phase 0 is writing `docs/protocol.md`: the question, three worlds, start/goal pairs, metrics, trial counts, hypotheses and the decision rule. The draft is in `PLAN.md` section 3. Edit it with Claude Code, commit it, and only then run any trial.
- Then Phase 1 (environment check and smoke test), Phase 2 (robot, worlds, trial runner, tests, CI), and so on. Claude Code stops at every phase gate and asks before continuing.

## Rules to keep (also in the repo's CLAUDE.md)
- Commits and pushes under your name only: no `Co-Authored-By` or any AI attribution line. Never force-push.
- Fully personal project: no employer code, data, hardware or documents.
- No CGPA, phone number or home address anywhere.
- Do not commit rosbags (`*.db3`, `*.mcap`), videos, build output or secrets.
- The plan is a starting point, not a fixed path: Claude Code should suggest better designs and experiments; you decide; accepted changes go in `docs/progress.md` and `PHASES.md`; after the protocol is committed, changes are logged, never applied silently.
- The drive can crash: the journal `docs/progress.md` is updated after every step, and work is committed and pushed after each finished step and at least every 30 minutes.

## If something is wrong
- `git fsck` reports errors after a crash: do not repair in place. Clone fresh into a new folder, copy back any readable uncommitted files, and note the loss in the journal.
- Package names or versions differ from the plan: the official docs win; log the change.
- Gazebo is slow or the graphics fail: record it in `docs/environment.md`; trials can run headless (`gz sim -s`).

## Things you do later on Windows (not on Ubuntu)
- The portfolio website (private repo `engineering-portfolio`, never deployed until you say the full site is final): when Project 2 has real results, its page and the Project 2 diagrams are updated from the report. Project 2 is marked Planned until it is finished.
- The workspace notes live in the private repo `masters-workspace` (`docs/progress.md` there tracks all projects). After Project 2 phases are done on Ubuntu, bring that repo up to date from the Windows laptop.

## State of the other work (for reference)
- Project 1 `robust-computer-vision`: complete and public.
- Portfolio website: interactive project pages, diagrams, results board, resume and contact footer done; not deployed; more optimisation planned later.
- Project 3 `autonomous-rescue-rover`: planned, not started; waits for Project 2.
