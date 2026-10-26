#!/bin/bash
# Phase 2 check with our own robot and the baseline configuration: does the real-time factor change trial outcomes?
# Same 6 trials (pairs a01..a06 of world A, one repeat, same seed) at each factor. Output: results/validation/rtf_robot_f<factor>.csv
# Usage: scripts/rtf_check_robot.sh [factor ...]   (default 1 2 4)
cd "$(dirname "$0")/.." || exit 1
mkdir -p results/validation
for F in ${@:-1 2 4}; do
  rm -f results/trials/baseline_world_a.csv
  scripts/run_session.sh baseline world_a 7 $F 1 --only a01,a02,a03,a04,a05,a06
  mv results/trials/baseline_world_a.csv results/validation/rtf_robot_f$F.csv
done
