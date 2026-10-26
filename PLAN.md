# Project 2 plan: Nav2 configuration study in simulation

Written 2026-10-26 on the Windows laptop, to be read first by whoever (the owner or Claude Code) continues on the Ubuntu drive. Nothing here has been run yet. Everything marked **DRAFT** is finalised and committed in Phase 0, **before any trial is run**.

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

Verification rule: before installing, open the Jazzy install page and the Nav2 documentation for Jazzy and confirm package names and the Gazebo pairing. Record the exact versions (`ros2 --version` equivalents, `dpkg -l | grep ros-jazzy-navigation2`) in `docs/environment.md`. If something differs from this plan, the docs win and the change is logged in `PHASES.md`.

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

**Decision rule (DRAFT):** a difference counts as real if the success-rate difference to baseline is at least 10 percentage points and its 95 percent interval excludes zero, or for time and path length if the paired difference has a confidence interval that excludes zero and a size above 5 percent of the baseline. Anything else is reported as no clear effect. Unsupported hypotheses are reported as unsupported.

## 4. Phases and exit gates

Follows the standard shape in `PHASES.md`. Work stops at every gate: update `PHASES.md`, commit and push, and ask the owner before starting the next phase.

**Phase 0, scope and protocol.** Deliver: `docs/protocol.md` with the question, worlds, start/goal file, metrics, trial counts, hypotheses and decision rule. Gate: written before any trial; ownership boundary stated; committed.

**Phase 1, setup.** Deliver: Ubuntu 24.04 external drive working, ROS 2 Jazzy, Gazebo Harmonic, Nav2 and SLAM Toolbox installed; `docs/environment.md` with exact versions and licences (ROS 2, Gazebo, Nav2 and SLAM Toolbox are open source: record each licence from its repository); a smoke test (a stock Nav2 demo robot navigates one goal in Gazebo, RViz shows scan and map). Gate: the smoke test works; versions and licences recorded; GPU/driver notes recorded.

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

1. On Windows: this repo is clean and pushed (it is, as of the commit that added this file). Easiest is to `git clone https://github.com/jayesh518/ros2-slam-navigation.git` on the Ubuntu drive; copying the folder (with `.git`) also works.
2. On Ubuntu: `git config user.name "Jayesh chaudhari"` and `git config user.email "127026542+Jayesh518@users.noreply.github.com"`, then sign in to GitHub (`gh auth login`) as `Jayesh518`.
3. Open the folder in VS Code and start Claude Code there. It reads `CLAUDE.md` in this folder, then this plan and `PHASES.md`, and should brief the owner and wait for a go-ahead before starting Phase 0.
4. Phase 0 first (write `docs/protocol.md` from section 3, edited with the owner), then Phase 1.
