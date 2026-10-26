# Environment (Project 2)

Recorded 2026-10-26 on the Ubuntu external drive. Source: `scripts/check_env.sh` (saved in `docs/environment-check.txt`) and the commands below. The official Jazzy install notes and the packages from `packages.ros.org` win over `PLAN.md` if they differ.

## Machine
| Item | Value |
|---|---|
| OS | Ubuntu 24.04.5 LTS (Noble), kernel 7.0.0-38-generic, native on an external SATA drive |
| CPU / RAM | 16 logical cores, 15 GiB RAM |
| Disk | 468 GB drive, 399 GB free |
| GPUs | NVIDIA GeForce RTX 3050 Laptop (4 GB, driver 580.178.04) and AMD Cezanne Vega iGPU (hybrid) |
| Display | X11 (`DISPLAY=:1`) |

## Software versions
| Item | Version | Licence (from package metadata) |
|---|---|---|
| ROS 2 | Jazzy Jalisco (`ROS_DISTRO=jazzy`) | Apache-2.0 (core packages, e.g. `rclcpp`) |
| Gazebo Harmonic (`gz sim`) | 8.15.0 (vendored under `/opt/ros/jazzy/opt/gz_*_vendor`) | Apache-2.0 |
| `ros_gz_sim` / `ros_gz_bridge` | 1.0.24 | Apache-2.0 |
| RViz 2 | 14.1.24 | BSD |
| Nav2 (`navigation2`, `nav2_bringup`) | 1.3.13 | Apache-2.0 (`nav2_amcl`: LGPL-2.1-or-later) |
| `nav2_minimal_tb3_sim` | 1.0.1 (used for the smoke test) | see package |
| SLAM Toolbox | 2.8.5 | LGPL |
| pandas (system, `python3-pandas`) | 2.1.4 | BSD |
| colcon | `colcon build` on an empty `src/` works (0 packages) | |

Nav2 planners and controllers needed by the protocol are installed with `navigation2`: NavFn, SmacPlanner2D (`nav2_smac_planner`), ThetaStar, DWB, Regulated Pure Pursuit, MPPI.

Installed on 2026-10-26 with `sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-bringup ros-jazzy-slam-toolbox python3-pandas` (130 packages, no errors). Everything else was already present.

## Things to know
- **`~/.bashrc` sources another workspace.** It runs `source ~/articuno_ws/install/setup.bash`, which sets `GZ_SIM_RESOURCE_PATH`, `GZ_SIM_SYSTEM_PLUGIN_PATH` and ament paths for an unrelated project. To keep this study reproducible, Project 2 commands run in a clean environment (the smoke test uses `env -i` and sources only `/opt/ros/jazzy/setup.bash`). `~/.bashrc` is not edited. A `scripts/env.sh` for the project is a Phase 2 item.
- **Python:** the repo has a `.venv` (git-ignored). Inside it `python3` resolves there; pandas came from apt, so scripts that need pandas must use a Python that can see it (`/usr/bin/python3`, or the venv if it has it). The check reported pandas found with the venv active.
- **Graphics:** hybrid NVIDIA + AMD. Trials run headless (`gz sim -s`), so the GPU is only needed for the GUI and the smoke test.
- **Docker:** not installed; needed only in Phase 7 (optional until then).

## Smoke test (2026-10-26)
Command: `scripts/smoke_test.sh` (launches `nav2_bringup tb3_simulation_launch.py headless:=False` in a clean environment), then initial pose and one `NavigateToPose` goal sent from the command line.
- Gazebo Harmonic, RViz 2, Nav2 (localisation and navigation lifecycle managers both reported "Managed nodes are active") started with no crashes.
- Goal (0.5, 1.0) from start (-2.0, -0.5): action result `SUCCEEDED`, `error_code: 0`. AMCL pose afterwards (0.45, 0.72), inside the default goal tolerance.
- `/scan` published at 5.0 Hz.
- Visual check (second run, screenshot of the desktop taken by Claude): RViz showed the map (hexagonal room with 9 pillars), costmaps, laser scan and the AMCL particle cloud; the Navigation 2 panel read Navigation: active and Localization: active. A second goal to (1.5, 0.0) also finished `SUCCEEDED`, with no process deaths.
- An earlier run launched by the owner ended after about a minute with RViz and the Nav2 container exiting (-6) right after the Gazebo GUI closed. It had not reached a goal (AMCL was still waiting for an initial pose). Read as a shutdown cascade after the window closed; not reproduced in the second run.

**Problem found and fixed: GUI crash under the snap VS Code terminal.** The first launch died with `symbol lookup error: /snap/core20/current/lib/x86_64-linux-gnu/libpthread.so.0: undefined symbol __libc_pthread_init` in both `rviz2` and `gz sim -g`. Cause: the integrated terminal of the snap-packaged VS Code exports `GTK_PATH`, `GTK_EXE_PREFIX`, `LOCPATH`, `XDG_DATA_DIRS` and similar variables pointing into `/snap/code/...`, which pull snap libraries into GUI programs. Fix: run with a clean environment (`env -i` with only `HOME`, `DISPLAY`, `XAUTHORITY`, `XDG_RUNTIME_DIR`, `PATH`), as `scripts/smoke_test.sh` does. A normal system terminal avoids the problem too. Headless trials (`gz sim -s`, no GUI) were not affected.

## Timing (Phase 2, 2026-10-26, stock TurtleBot 3 world, headless, 16 cores, no RViz)
- Default Gazebo real-time factor is capped at 1.0: one 3.5 m goal took 59.8 s wall for 59 s simulated time.
- The cap can be lifted at run time: `gz service -s /world/default/set_physics --reqtype gz.msgs.Physics --reptype gz.msgs.Boolean --timeout 3000 --req 'real_time_factor: 10'`. Measured real-time factor 10.0; the return goal then took 5.7 s wall for 56 s simulated time.
- Consequence: a 120 s simulated timeout costs about 12 s wall at factor 10. The 360-trial grid is about 1.2 h of trial time plus stack start-up (about 30 s per launch; reuse one running stack per configuration and world rather than relaunching per trial). Higher factors, and whether results change with the physics step at high factors, are to be checked before the baseline.
- Open check: a higher real-time factor can change controller behaviour if the CPU cannot keep up (sensor and control rates are in simulated time, but the Nav2 nodes use the wall CPU). Compare success on a fixed set of trials at factor 1 and factor 10 before using factor 10 for the grid.

### Real-time factor check on the stock robot (`scripts/rtf_compare.sh`, `results/rtf_compare.csv`, 2026-10-26)
Same 6 goals in a fixed cycle (3 distinct goals, each twice), stock Nav2 TurtleBot 3, headless, default Nav2 parameters, one run per factor. Sample is small (6 goals per factor, one run each), so it detects only large effects.
| Factor | Goals reached | Wall time for the 6 goals |
|---|---|---|
| 1 | 6 of 6 | 183 s |
| 2 | 6 of 6 | 84 s |
| 4 | 6 of 6 | 46 s |
| 10 | 3 of 6 (an earlier run: 2 of 6) | 34 s |
Reading: factor 10 changes navigation outcomes, so it is out. Factors 2 and 4 matched factor 1 on this sample. The value for the study is chosen after repeating this with our own robot and the baseline configuration (Phase 2), with more goals.

### Robot checks (2026-10-26, headless test arena)
`/scan` 5.0 Hz, `/imu` 200 Hz, `/odom` and `/ground_truth` about 28 Hz (in the 30 Hz range, wall-clock limited), `/joint_states` about 28 Hz. Driving straight at 0.2 m/s reached the far wall; odometry and ground truth agreed. The Gazebo drive plugin keeps the last velocity command with no timeout, so the trial runner must publish an explicit zero at the end of a trial. Contact sensors publish on scoped topics (`/world/default/model/nav_study_robot/link/<link>/sensor/<name>/contact`), bridged to `/contact/base`, `/contact/lidar`, `/contact/wheel_left`, `/contact/wheel_right`; a wheel touching a wall appears as `walls::link::e`, ground contact as `ground_plane::link::collision`.
