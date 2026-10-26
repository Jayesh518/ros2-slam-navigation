# Figures

One final screenshot per phase, named `phaseN-<what>.png`, for the README and the technical report. Each row says what it shows and how it was produced, so a figure can be reproduced. Screenshots are cropped to the application window (no desktop, no personal items). Temporary screenshots taken while working are deleted after use.

| File | Phase | What it shows | How it was made |
|---|---|---|---|
| `phase1-smoke-test-rviz.png` | 1, setup | RViz 2 during the stock Nav2 TurtleBot 3 smoke test (Jazzy, Gazebo Harmonic 8.15.0, Nav2 1.3.13): map, costmaps, laser scan, AMCL particle cloud; Navigation and Localization both active. This is the stock demo, not our own robot or worlds. | `scripts/smoke_test.sh`, initial pose and one goal sent from the command line, 2026-10-26 |
| `world-plans.png` | 2, pipeline | Top-down plans of the three study worlds (A1 open room, B1 office, C1 pillar grid). A drawing generated from the SDF files by `scripts/plot_worlds.py`, not a screenshot. | `python3 scripts/plot_worlds.py` |
| `maps-slam.png` | 2, pipeline | The three saved SLAM Toolbox maps (white free, grey unknown, black occupied). Slight rotation (about 1 to 2 degrees) and unobserved patches are real SLAM limits, not drawing errors. | `scripts/map_world.sh world_x 2`, then `python3 scripts/plot_maps.py` |
| `phase2-robot-in-world-b.png` | 2, pipeline (final figure) | Gazebo Sim 3D view: our own Burger-based robot (body, LiDAR, two wheels) in the corridor of world B1 (office). Cropped to the 3D view. | `ros2 launch nav_study_bringup sim.launch.py world:=world_b headless:=false x:=-3.0`, camera moved with `gz service /gui/move_to/pose`, 2026-10-26 |

