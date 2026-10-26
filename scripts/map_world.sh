#!/bin/bash
# Map one world with SLAM Toolbox while Nav2 drives a tour. Usage: scripts/map_world.sh world_a [rtf]
# Result: maps/<world>.pgm and maps/<world>.yaml
cd "$(dirname "$0")/.." || exit 1
W=${1:?world name, e.g. world_a}; RTF=${2:-2}
mkdir -p maps results/logs
bash scripts/stop_sim.sh
(setsid scripts/env.sh ros2 launch nav_study_bringup nav.launch.py world:=$W slam:=True params_file:=$PWD/configs/nav2/mapping.yaml rtf:=$RTF headless:=true > results/logs/map_$W.launch.log 2>&1 &)
scripts/env.sh /usr/bin/python3 scripts/tour.py $W 2>&1 | tee results/logs/map_$W.tour.log
scripts/env.sh ros2 run nav2_map_server map_saver_cli -f maps/$W --ros-args -p save_map_timeout:=10000.0 2>&1 | tail -3
bash scripts/stop_sim.sh
ls -la maps/$W.*
