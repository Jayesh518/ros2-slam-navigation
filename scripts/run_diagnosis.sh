#!/bin/bash
# Phase 5 diagnosis: re-run chosen start/goal pairs in world B with per-trial traces. Results go to results/diagnosis/ (never to results/trials/,
# so the Phase 4 tables cannot change). Same session seed as Phase 4 for world B (12). Usage: scripts/run_diagnosis.sh <config> <pair,pair,...> [tag]
cd "$(dirname "$0")/.." || exit 1
C=${1:?config}; PAIRS=${2:?comma separated pair ids}; TAG=${3:-diag}
mkdir -p results/diagnosis/traces
OUT_DIR=results/diagnosis scripts/run_session.sh $C world_b 12 1 1 --only $PAIRS --trace-dir results/diagnosis/traces
mv results/diagnosis/${C}_world_b.csv results/diagnosis/${TAG}_${C}_world_b.csv
