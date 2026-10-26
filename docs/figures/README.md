# Figures

One final screenshot per phase, named `phaseN-<what>.png`, for the README and the technical report. Each row says what it shows and how it was produced, so a figure can be reproduced. Screenshots are cropped to the application window (no desktop, no personal items). Temporary screenshots taken while working are deleted after use.

| File | Phase | What it shows | How it was made |
|---|---|---|---|
| `phase1-smoke-test-rviz.png` | 1, setup | RViz 2 during the stock Nav2 TurtleBot 3 smoke test (Jazzy, Gazebo Harmonic 8.15.0, Nav2 1.3.13): map, costmaps, laser scan, AMCL particle cloud; Navigation and Localization both active. This is the stock demo, not our own robot or worlds. | `scripts/smoke_test.sh`, initial pose and one goal sent from the command line, 2026-10-26 |
