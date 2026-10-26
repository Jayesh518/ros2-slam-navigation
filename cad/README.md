# Robot CAD (Fusion 360)

`nav_study_robot_v1.step` is the robot as an assembly of 20 named solids (bottom/middle/top plates, 8 standoffs, 2 wheels, 2 motors, ball caster, battery, controller board, SBC board, LiDAR). Units are millimetres; origin is on the ground under the axle centre; x forward, y left, z up. Overall size 178 x 192 mm in width and height, wheel separation 160 mm, plate length 138 mm (the design basis is the ROBOTIS TurtleBot 3 Burger specification; the layout is our own).

**Open in Fusion 360:** File > Open > Open from my computer > choose the `.step` file (or Upload to a project, then open). The parts arrive as separate bodies/components with their names and colours, so they can be edited, re-dimensioned and exported again. Fusion's default up-axis may differ from this file's (z up); use the ViewCube/Modify > Change Model Orientation if the robot appears lying down. This file has been produced and re-imported with CadQuery (size and solid count checked in `make_robot_cad.py`); it has not yet been opened in Fusion 360 by the owner, so tell Claude if anything looks wrong.

**It is generated, not hand-drawn.** `make_robot_cad.py` builds it from `src/nav_study_robot/config/robot_params.yaml`, the same file that defines the simulation model, so the CAD and the simulated robot cannot drift apart. To change the robot: edit the numbers in the YAML and run `.venv/bin/python cad/make_robot_cad.py`. If you redesign it in Fusion instead, export a new STEP, save it as `nav_study_robot_v2.step`, and copy the changed dimensions back into the YAML so the simulation follows.

**Not in the CAD yet:** wheel-motor brackets, screws, wiring, a camera or thermal sensor mount (Project 3). It is a design-and-simulation model, not a manufacturing drawing.
