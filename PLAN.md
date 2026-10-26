# Project 2 plan: Nav2 configuration study in simulation

Written 2026-10-26 on the Windows laptop, to be read first by whoever (the owner or Claude Code) continues on the Ubuntu drive. Nothing here has been run yet. Everything marked **DRAFT** is finalised and committed in Phase 0, **before any trial is run**.

## 0. The scenario: what we are building and why

**Who and what for.** Jayesh Chaudhari (GitHub `Jayesh518`) is building a research-grade portfolio of three personal AI and robotics projects. The portfolio is read by people judging his ability to do real engineering and research (graduate programme reviewers and professors). Each project must therefore show evidence, not demos: a pre-registered question, controlled experiments, honest uncertainty and a report that says what the results cannot claim. All three projects are fully personal; none uses employer material.

**The three-project arc.**
1. `robust-computer-vision` (finished): how much a pretrained YOLO detector loses in rain, dark and blur, and which cheap fix helps. Its habits are the standard for this project too: phases with gates, hypotheses and decision rules fixed before the runs, confidence intervals, negative results reported, one-command reproduction.
2. **`ros2-slam-navigation` (this project):** the navigation half of a robot, studied in simulation.
3. `autonomous-rescue-rover` (planned): a small, low-speed, personally owned rover that combines a camera detector with range sensing and the navigation approach learned here, tested in a controlled indoor course. It is an independent personal build.

**What we are building here.** A simulated differential-drive robot in Gazebo that builds a map of an unknown world (SLAM Toolbox), localises itself on that map (AMCL) and drives to goals while avoiding obstacles (Nav2). On top of that stack we build four things of our own:
- the robot and world descriptions (the robot with a LiDAR and odometry, three worlds of rising difficulty);
- an **automated trial runner** that sends a goal, watches ground truth, applies a timeout and writes one CSV row per trial;
- one or more **custom ROS 2 nodes** (a waypoint-mission node and a custom recovery behaviour);
- the **experiment and analysis**: how do planner and controller choices and the custom recovery behaviour change navigation success, collisions, time to goal and path length across the worlds.

**Why this project exists.**
- To show that the owner understands how a navigation stack fits together (maps, transforms, sensors, localisation, planning, control) and where it breaks, by measuring it rather than only running a tutorial. Most people can launch Nav2; few can say, with trial counts and intervals, what a configuration change does.
- To produce the tools and knowledge Project 3 needs: the trial-runner design, a tuned Nav2 configuration, the transform-tree layout and the habit of logging every run. Doing it in simulation first means mistakes cost nothing before a real robot is involved.
- To add a second, different kind of evidence to the portfolio: Project 1 is perception on real photographs, this one is planning and control in simulation, and Project 3 joins them on hardware.

**What the finished project looks like.** A public repository where a fresh clone plus one command reproduces the headline results table; trial CSVs, figures and a report that states its limits; a two-page summary; a short demo video; TF and architecture diagrams; and an updated page on the owner's portfolio website (the owner updates that page himself from the results).

**What it is not.** It does not reimplement SLAM or Nav2 (the algorithms are used as published; the work is configuration, integration, custom behaviour, experiments and interpretation). It does not claim real-world performance: simulation hides sensor noise, wheel slip and lighting, and the report must say so. It makes no rescue, safety or life-saving claims.

**This plan is a starting point, not a fixed path.** Nothing in it is a rule except what `CLAUDE.md` lists. Claude Code is expected to think about the project, not just execute it: whenever it sees a better way (a stronger experiment, a simpler design, a missing control, a more useful metric, a better tool, a cheaper way to reach the same evidence, a risk the plan missed), it should say so, with the reason and the cost, and recommend one option. The owner decides. Good moments to propose changes: at every phase gate, when a result surprises, when something takes much longer than planned, and when the work shows that a draft item in section 3 is wrong.

How changes are handled:
- Before the protocol is frozen (Phase 0), anything may change; just keep section 3 consistent.
- After `docs/protocol.md` is committed, a change to the question, metrics, hypotheses or decision rule is allowed but is written down as a dated change (what changed, why, and whether any trial had already been seen), never applied silently or backwards to make a result look better. Results seen before a change are reported as exploratory.
- Every accepted change is recorded in the "Plan changes" list in `docs/progress.md` and in `PHASES.md`, and `PLAN.md` is edited so it always describes the current plan.
- Suggestions that are declined are kept in "Ideas parked" in `docs/progress.md` so they are not proposed again without new reasons.
- Improving the project can also mean cutting scope: say so if a part costs more than the evidence it adds.

**Quality bar and ways of working.** Same as Project 1: work in phases with exit gates, write the protocol before any trial, report mixed or negative results as they are, keep every number traceable to a file in the repo, and commit under the owner's name only. The external drive can crash, so the journal in `docs/progress.md` and frequent pushes (section 9) are part of the job, not extras.

**Handoffs between projects.** From Project 1: the discipline above, and the finding that the pretrained detector is the one to use (Project 3 uses it; this project does not need a detector). To Project 3: the trial runner, the Nav2 configuration, the transform design and, optionally, a simulated thermal camera model in Gazebo (clearly labelled simulated).

## 1. What this project is

A simulated differential-drive robot maps an unknown environment (SLAM Toolbox), localises itself (AMCL) and navigates to goals (Nav2). The study part: **how do Nav2 planner and controller choices and a custom recovery behaviour change navigation success, collisions, time and path length across worlds of rising difficulty?**

Ownership boundary: SLAM Toolbox, AMCL and Nav2 are used as published (configuration, integration and tuning), not reimplemented. The owner's own work is the robot description, launch files, custom ROS 2 nodes, the automated trial runner, the experiment design, the analysis and the report. Fully personal project: no employer code, data, hardware, designs or documents anywhere in this repo.

Part 2 of 3. It follows `robust-computer-vision` (done) and feeds `autonomous-rescue-rover` (planned), which will reuse the navigation approach and the trial-runner design.

## 2. Stack decision (verified 2026-10-26 against REP-2000)

| Item | Choice | Why |
|---|---|---|
| ROS 2 | **Jazzy Jalisco** (LTS, supported until May 2029) | Covers the whole project window and the rover project; Tier 1 on Ubuntu 24.04. Kilted Kaiju ends Nov 2026; Lyrical Luth (May 2026, Ubuntu 26.04) is too new and its Gazebo/Nav2 pairing was not verified from a primary source. |
| Ubuntu | **24.04 LTS (Noble)**, native on an external 500 GB SATA drive | Tier 1 platform for Jazzy. |
| Simulator | **Gazebo Harmonic** (`ros-jazzy-ros-gz`) | The Gazebo release REP-2000 pairs with Jazzy. |
| Navigation | `ros-jazzy-navigation2`, `ros-jazzy-nav2-bringup` | Verify they install before anything else (gate of Phase 1). |
| SLAM | `ros-jazzy-slam-toolbox` | Mapping. |
| Localisation | AMCL (part of Nav2) | Localising on the saved map. |

**Already on the Ubuntu drive (owner, 2026-10-26): Gazebo and RViz.** Do not reinstall them. Run `scripts/check_env.sh` (section 8), record what is there, and install only what is reported missing. Verification rule: before installing anything, open the Jazzy install page and the Nav2 documentation for Jazzy and confirm package names and the Gazebo pairing. Record the exact versions (`ros2 --version` equivalents, `dpkg -l | grep ros-jazzy-navigation2`) in `docs/environment.md`. If something differs from this plan, the docs win and the change is logged in `PHASES.md`.

## 3. Phase 0 content to finalise (DRAFT)

**Question (final wording in Phase 0):** Across several simulated worlds, how do Nav2 planner and controller settings and a custom recovery behaviour change navigation success, collisions, time to goal and path length?

**Worlds (3 or more, rising difficulty):** (A) a mostly open room with a few obstacles; (B) an office-like layout with corridors and doorways; (C) a cluttered or symmetric world that stresses localisation. Fixed seeds, fixed start/goal pairs (about 10 per world, chosen once, committed as a YAML file before any trial).

**Baseline:** default Nav2 parameters for a differential-drive robot (default planner and controller as shipped for Jazzy), map from SLAM Toolbox, AMCL.

**Settings, one change at a time from the baseline (as in Project 1):**
| Factor | Levels |
|---|---|
| Global planner | NavFn (default), SmacPlanner2D, ThetaStar |
| Local controller | DWB (default), Regulated Pure Pursuit, MPPI |
| Recovery | default behaviours, plus a custom recovery node (on/off) |

That is 1 baseline + 2 planner + 2 controller + 1 recovery = 6 configurations x 3 worlds x 20 trials = 360 trials, about 1 to 3 simulated minutes each. Run headless (`gz sim -s`) with `use_sim_time:=true`. Measure the real wall-clock cost in Phase 2 and adjust the grid in Phase 0 if it is too slow; do not extend the grid after seeing results.

**Metrics (what each means, how it is computed):**
- Success: the robot ends within a goal tolerance (draft 0.25 m) before a timeout (draft 120 s simulated).
- Collisions: contact events from a Gazebo contact sensor on the base (preferred), counted per trial.
- Time to goal and path length: from timestamps and the ground-truth pose path; report on successful trials only, and say so.
- Recovery events: count of behaviour-tree recovery activations per trial.
- Localisation error: AMCL pose against Gazebo ground truth, where available.
- Statistics: success rate with a Wilson 95 percent interval; paired comparison against the baseline on the same start/goal pairs; the number of trials always stated.

**Pre-registered hypotheses (DRAFT, to be confirmed or edited in Phase 0):**
- H1: planner choice changes success little in the open world but more in the cluttered world.
- H2: the custom recovery behaviour raises success in the cluttered world at the cost of time.
- H3: localisation error is highest in the most symmetric or feature-poor world, and failures there come mostly from localisation, not planning.

**Decision rule (superseded by `docs/protocol.md` section 8, pair-level paired bootstrap; kept here as the original draft):** a difference counts as real if the success-rate difference to baseline is at least 10 percentage points and its 95 percent interval excludes zero, or for time and path length if the paired difference has a confidence interval that excludes zero and a size above 5 percent of the baseline. Anything else is reported as no clear effect. Unsupported hypotheses are reported as unsupported.

## 4. Phases and exit gates

Follows the standard shape in `PHASES.md`. Work stops at every gate: update `PHASES.md`, commit and push, and ask the owner before starting the next phase.

**Phase 0, scope and protocol.** Deliver: `docs/protocol.md` with the question, worlds, start/goal file, metrics, trial counts, hypotheses and decision rule. Gate: written before any trial; ownership boundary stated; committed.

**Phase 1, environment check and project setup.** Gazebo and RViz already exist, so this phase is a check, not an install. Deliver: `scripts/check_env.sh` output saved to `docs/environment.md` (exact versions, what was missing and what was installed, licences of ROS 2, Gazebo, Nav2 and SLAM Toolbox from their repositories, GPU and driver notes); the colcon workspace builds (`colcon build` on an empty `src/` and then on the first package); a smoke test (a stock Nav2 demo robot navigates one goal in Gazebo, RViz shows scan and map). Gate: the check script reports no missing required item; the smoke test works; versions and licences recorded.

**Phase 2, pipeline and validation.** Deliver: own differential-drive robot description (URDF/SDF with LiDAR and odometry), a bringup launch file, the three worlds, an automated trial runner (sends a goal, watches ground truth, applies timeout, writes one CSV row per trial with the config name, world, pair, seed), unit tests for the metric code, CI (build and test in the `ros:jazzy` container). Gate: the same trial with the same seed gives the same CSV row (or the nondeterminism is measured and written down); tests pass; CI green.

**Phase 3, baseline.** Deliver: SLAM Toolbox maps of the worlds, AMCL working, default Nav2, 20 trials per world, results with intervals. Gate: baseline numbers with trial counts and limits.

**Phase 4, intervention.** Deliver: all configurations in the grid, same pairs, 20 trials each, tables and plots. Gate: controlled comparison; confounds written down; decision rule applied exactly as pre-registered.

**Phase 5, diagnosis.** Explain failures from logs and short rosbag excerpts (rosbags are not committed; keep small excerpts only if approved). Gate: every surprise explained by an experiment or listed as unexplained.

**Phase 6, extension.** The custom mission (waypoint sequencing) node and the custom recovery behaviour (if not already part of Phase 4), effect isolated by the on/off ablation. Optional: a simulated thermal camera in Gazebo for later use by Project 3 (clearly labelled simulated). Gate: cost and complexity reported next to benefit.

**Phase 7, report and release.** Deliver: `docs/report.md`, TF and architecture diagrams, trial logs and plots, a 2-page summary, a demo video (video files are not committed, link them), a container (Dockerfile) so a fresh clone plus one command reproduces the headline table. Gate: the report says what the results cannot say; fresh-clone reproduction works.

## 5. Planned repository layout

```
src/            ROS 2 packages: robot description, bringup/launch, nav2 configs, custom nodes, trial runner
worlds/         Gazebo worlds
maps/           saved maps
configs/        experiment grid, start/goal pairs
results/        trial CSVs (small), figures
scripts/        analysis and table generation
docs/           protocol.md, environment.md, report.md, diagrams/
tests/          metric and runner tests
Dockerfile      one-command reproduction (Phase 7)
```

Large files, rosbags (`*.db3`, `*.mcap`), videos and build output stay out of git (already in `.gitignore`).

## 6. Known risks

- **Graphics on an external-drive Ubuntu.** The laptop has an NVIDIA RTX 3050 (4 GB) and an AMD iGPU (hybrid graphics). Install the NVIDIA proprietary driver for Ubuntu 24.04, or fall back to software rendering; for the trials Gazebo can run headless without any display. Record what worked in `docs/environment.md`.
- **Real-time factor.** Gazebo may run slower than real time on this laptop; the trial timeout must use simulated time, and the wall-clock cost of the grid is measured in Phase 2.
- **Nondeterminism.** Nav2's behaviour tree, AMCL (random particles) and physics are not fully deterministic. Seed where possible, and measure the spread of repeated identical trials (this is why 20 trials per condition, not 1).
- **Nav2 parameters.** Defaults change between releases; always record the parameter file in git with each configuration.
- **The external drive is a single point of failure.** Push to GitHub at the end of every working session.

## 7. Moving to the Ubuntu drive (first session checklist)

1. On Windows: this repo is clean and pushed. Easiest is to `git clone https://github.com/jayesh518/ros2-slam-navigation.git` on the Ubuntu drive; copying the folder (with `.git`) also works.
2. On Ubuntu: `git config user.name "Jayesh chaudhari"` and `git config user.email "127026542+Jayesh518@users.noreply.github.com"`, then sign in to GitHub (`gh auth login`) as `Jayesh518`.
3. Open the folder in VS Code and start Claude Code there. It reads `CLAUDE.md` in this folder, then this plan and `PHASES.md`, and should brief the owner and wait for a go-ahead before starting Phase 0.
4. Phase 0 first (write `docs/protocol.md` from section 3, edited with the owner), then Phase 1.

## 8. Requirements list (project only)

Run `bash scripts/check_env.sh`. It is read-only: it reports each item as OK, MISSING or WRONG and prints the version found. Install only what is MISSING, using the official Jazzy and Nav2 documentation.

| # | Requirement | Needed for | Check |
|---|---|---|---|
| 1 | Ubuntu 24.04 LTS (Noble), 64-bit, on the external drive | everything | `lsb_release -rs` is 24.04 |
| 2 | ROS 2 Jazzy (desktop or base plus RViz) | everything | `/opt/ros/jazzy/setup.bash` exists, `ros2` works |
| 3 | Gazebo Harmonic and the ROS bridge (`ros-jazzy-ros-gz`) | simulation | `gz sim --versions` shows 8.x, `ros-jazzy-ros-gz-sim` installed |
| 4 | RViz 2 | visual checks | `rviz2` found (already on the drive) |
| 5 | Nav2 (`ros-jazzy-navigation2`, `ros-jazzy-nav2-bringup`) | navigation | packages installed |
| 6 | SLAM Toolbox (`ros-jazzy-slam-toolbox`) | mapping | package installed |
| 7 | Build tools: `colcon`, `rosdep`, `pytest`, `git`, `gh` | build, tests, push | commands found |
| 8 | Python analysis: `numpy`, `pandas`, `matplotlib`, `scipy`, `pyyaml` | trial analysis | each imports |
| 9 | At least 20 GB free on the drive | builds, logs | `df -h .` |
| 10 | Network access to GitHub | push | `git ls-remote origin` |
| 11 | NVIDIA driver (optional) | faster rendering; trials can run headless without it | `nvidia-smi` |
| 12 | Docker (optional, Phase 7 only) | one-command reproduction | `docker --version` |

Anything reported MISSING is installed, then the check is re-run and its output saved. If a required item cannot be installed, stop and tell the owner instead of working around it.

## 9. Crash-proofing: the drive can fail

The external drive sometimes crashes. Rules to lose as little as possible:
- **`docs/progress.md` is the journal.** After every meaningful step (a file written, an install done, an experiment run, a decision made), append a dated line to the session log and keep "Current state" and "Next steps" accurate. This is cheaper than reconstructing from memory.
- **Commit and push early and often**: after each finished step and at least every 30 minutes of work, in small commits (the owner's identity only, no attribution lines). The remote on GitHub is the backup.
- **Small result files are committed** (trial CSVs, configs, figures). Large files (rosbags, videos, build output) are not, so keep the commands that regenerate them in `scripts/`.
- **After a crash or re-login**, paste the restore prompt from `docs/restore-prompt.md` into Claude Code. It checks the repository for damage, compares the working tree with GitHub, re-runs the environment check, reads the journal and continues from the recorded next step.
- If the repository is damaged (`git fsck` reports errors), do not repair it in place: clone fresh from GitHub into a new folder, copy over any uncommitted files that are still readable, and record what was lost in the journal.
