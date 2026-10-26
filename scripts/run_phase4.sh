#!/bin/bash
# Phase 4: baseline in world D (A to C already done in Phase 3), then each configuration over all four worlds, serially at real-time factor 1.
# Existing result files are skipped, so the script can be restarted after a crash. Usage: scripts/run_phase4.sh [config ...]
cd "$(dirname "$0")/.." || exit 1
for C in ${@:-baseline smac2d thetastar dwb rpp}; do
  scripts/run_config.sh $C
done
echo "phase4 done"
