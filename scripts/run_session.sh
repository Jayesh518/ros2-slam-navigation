#!/bin/bash
# Run one (configuration, world) session: start the simulation + Nav2 + AMCL on the saved map, run the trial runner, stop everything.
# Usage: scripts/run_session.sh <config> <world> <seed> <rtf> <repeats> [extra run_trials args, e.g. --only a01,a02]
# Output: ${OUT_DIR:-results/trials}/<config>_<world>.csv (appended; one row per trial). Logs: results/logs/session_<config>_<world>.*
cd "$(dirname "$0")/.." || exit 1
C=${1:?config}; W=${2:?world}; SEED=${3:-1}; RTF=${4:-1}; REP=${5:-1}; shift 5
mkdir -p results/trials results/logs
bash scripts/stop_sim.sh
(setsid scripts/env.sh ros2 launch nav_study_bringup nav.launch.py world:=$W map:=$PWD/maps/$W.yaml params_file:=$PWD/configs/nav2/$C.yaml \
   rtf:=$RTF seed:=$SEED headless:=true guard:=$([ "$C" = recovery ] && echo true || echo false) > results/logs/session_${C}_$W.launch.log 2>&1 &)
# AMCL publishes map->odom only after an initial pose, and Nav2's global costmap needs that transform to activate: publish the spawn pose until active
read SX SY SYAW < <(/usr/bin/python3 scripts/spawn_pose_map.py $W)
INITMSG="{header: {frame_id: map}, pose: {pose: {position: {x: $SX, y: $SY}, orientation: {z: $(/usr/bin/python3 -c "import math;print(math.sin($SYAW/2))"), w: $(/usr/bin/python3 -c "import math;print(math.cos($SYAW/2))")}}, covariance: [0.05,0,0,0,0,0, 0,0.05,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0.02]}}"
(setsid scripts/env.sh ros2 topic pub -r 1 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "$INITMSG" > /dev/null 2>&1 &)
# wait for the navigation lifecycle manager to report the stack active (localisation + navigation)
for i in $(seq 1 120); do
  [ "$(grep -c 'Managed nodes are active' results/logs/session_${C}_$W.launch.log)" -ge 2 ] && break; sleep 2
done
sleep 3
pkill -f "topic pub -r 1 /initialpose" 2>/dev/null
scripts/env.sh ros2 run nav_study_trials run_trials --config $C --world $W --repeats $REP --seed $SEED $([ "$C" = recovery ] && echo --guard) --out ${OUT_DIR:-results/trials}/${C}_$W.csv "$@" 2>&1 \
  | tee results/logs/session_${C}_$W.runner.log
bash scripts/stop_sim.sh
