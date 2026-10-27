#!/bin/bash
# Independent check of H2b (protocol change (o)): baseline and recovery on the 20 fresh world-B pairs. Results in results/check/ (not results/trials/).
# Do not run while another session is running (run_session.sh stops all simulation processes first). Usage: scripts/run_check.sh
cd "$(dirname "$0")/.." || exit 1
mkdir -p results/check
for C in baseline recovery; do
  if [ -f results/check/${C}_world_b.csv ]; then echo "skip $C: results/check/${C}_world_b.csv exists (move it away to rerun)"; continue; fi
  OUT_DIR=results/check scripts/run_session.sh $C world_b 22 1 1 --pairs configs/pairs_check.yaml
done
echo "done check"
