#!/bin/bash
# Phase 2 gate: does the same trial with the same seed in a FRESH session give the same CSV row? Runs N fresh sessions of baseline / world A / pair a01.
# Output: results/validation/determinism_fresh_session_<i>.csv. Usage: scripts/determinism_check.sh [N]
cd "$(dirname "$0")/.." || exit 1
mkdir -p results/validation
for i in $(seq 1 ${1:-3}); do
  rm -f results/trials/baseline_world_a.csv
  scripts/run_session.sh baseline world_a 1 1 1 --only a01
  mv results/trials/baseline_world_a.csv results/validation/determinism_fresh_session_$i.csv
done
