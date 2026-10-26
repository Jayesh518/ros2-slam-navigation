#!/bin/bash
# Run one configuration over all four worlds (20 pairs x 1 trial each), one session per world, serially at real-time factor 1.
# Usage: scripts/run_config.sh <config>      e.g. scripts/run_config.sh baseline
# Session seeds are fixed here (11, 12, 13, 14) so a run can be repeated exactly as designed. Output: results/trials/<config>_<world>.csv
cd "$(dirname "$0")/.." || exit 1
C=${1:?config name (baseline, smac2d, thetastar, dwb, rpp, recovery)}
i=0
for W in world_a world_b world_c world_d; do
  i=$((i+1))
  if [ -f results/trials/${C}_$W.csv ]; then echo "skip $C $W: results/trials/${C}_$W.csv exists (move it away to rerun)"; continue; fi
  scripts/run_session.sh $C $W $((10+i)) 1 1
done
echo "done $C"
