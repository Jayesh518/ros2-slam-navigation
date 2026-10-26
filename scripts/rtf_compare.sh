#!/bin/bash
# Phase 2 check: does the Gazebo real-time factor change navigation outcomes?
# Runs the stock Nav2 TurtleBot 3 sim headless at each factor, sends the same 6 goals in a fixed cycle,
# writes results/rtf_compare.csv (factor, goal index, goal x y, status, wall_s, sim_s).
# Usage: scripts/rtf_compare.sh [factor ...]   (default: 1 10)
cd "$(dirname "$0")/.." || exit 1
if pgrep -f "gz sim|component_container" >/dev/null; then echo "stale simulation processes running; stop them first" >&2; exit 1; fi
E=scripts/env.sh
OUT=results/rtf_compare.csv
LOG=$(mktemp -d)
echo "factor,goal,x,y,status,wall_s,sim_s" > "$OUT"
simt(){ $E bash -c 'timeout 5 gz topic -e -t /stats -n 1' 2>&1 | awk '/sim_time/{f=1} f&&/^ *sec:/{s=$2} f&&/nsec:/{print s+$2/1e9; exit}'; }
GOALS=("1.5 0.0" "0.5 1.0" "-2.0 -0.5" "1.5 0.0" "0.5 1.0" "-2.0 -0.5")
for F in ${@:-1 10}; do
  ( setsid $E ros2 launch nav2_bringup tb3_simulation_launch.py headless:=True use_rviz:=False > "$LOG/launch_$F.log" 2>&1 & )
  until [ "$(grep -c 'Managed nodes are active' "$LOG/launch_$F.log")" -ge 1 ]; do sleep 1; done
  $E ros2 topic pub --once -w 1 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "{header: {frame_id: map}, pose: {pose: {position: {x: -2.0, y: -0.5, z: 0.0}, orientation: {w: 1.0}}, covariance: [0.25,0,0,0,0,0, 0,0.25,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0.07]}}" >/dev/null 2>&1
  until [ "$(grep -c 'Managed nodes are active' "$LOG/launch_$F.log")" -ge 2 ]; do sleep 1; done
  $E gz service -s /world/default/set_physics --reqtype gz.msgs.Physics --reptype gz.msgs.Boolean --timeout 3000 --req "real_time_factor: $F" >/dev/null 2>&1
  sleep 3
  i=0
  for G in "${GOALS[@]}"; do
    set -- $G; i=$((i+1))
    t0=$(date +%s.%N); s0=$(simt)
    r=$($E ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map}, pose: {position: {x: $1, y: $2, z: 0.0}, orientation: {w: 1.0}}}}" 2>&1 | grep -o -E "SUCCEEDED|ABORTED|CANCELED|REJECTED" | tail -1)
    t1=$(date +%s.%N); s1=$(simt)
    echo "$F,$i,$1,$2,${r:-UNKNOWN},$(echo "$t1-$t0" | bc),$(echo "$s1-$s0" | bc)" >> "$OUT"
  done
  pkill -INT -f "ros2 launch nav2_bringup"; sleep 8
  for n in "ros2 launch nav2_bringup" "gz sim" component_container robot_state_publisher parameter_bridge; do pkill -9 -f "$n"; done; sleep 3
done
echo "wrote $OUT"
