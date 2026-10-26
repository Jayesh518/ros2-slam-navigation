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
- Not yet checked by eye: that RViz shows the scan and map (the owner confirms on the screen).

**Problem found and fixed: GUI crash under the snap VS Code terminal.** The first launch died with `symbol lookup error: /snap/core20/current/lib/x86_64-linux-gnu/libpthread.so.0: undefined symbol __libc_pthread_init` in both `rviz2` and `gz sim -g`. Cause: the integrated terminal of the snap-packaged VS Code exports `GTK_PATH`, `GTK_EXE_PREFIX`, `LOCPATH`, `XDG_DATA_DIRS` and similar variables pointing into `/snap/code/...`, which pull snap libraries into GUI programs. Fix: run with a clean environment (`env -i` with only `HOME`, `DISPLAY`, `XAUTHORITY`, `XDG_RUNTIME_DIR`, `PATH`), as `scripts/smoke_test.sh` does. A normal system terminal avoids the problem too. Headless trials (`gz sim -s`, no GUI) were not affected.
