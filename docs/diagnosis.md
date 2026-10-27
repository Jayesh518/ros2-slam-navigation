# Phase 5: diagnosis of the world-B failures

Status: scope fixed 2026-10-27 before any diagnosis trial; findings are added below it as they come.

## Question and status of the evidence
Why do trials fail in world B (office), and why do the configurations fail differently? Phase 4 left three observations (`docs/results.md`): smac2d mostly ends in Nav2 aborts, dwb and rpp coincide with large AMCL error, thetastar rarely fails. This phase is **exploratory and descriptive**: it explains individual failures from traces; it makes no new significance claims and does not change any Phase 4 number.

## What was already visible without new trials (Phase 4 CSVs)
All 32 world-B failures are long crossings of the office: every failed pair has a straight-line distance of 9.4 m or more and a baseline path of 14 to 21 m; no pair under 9 m ever failed in any configuration. Failures are pair-specific, not random: b02 failed in 5 of 5 configurations, b11 and b04 in 4 of 5, b09, b06 and b14 in 3.

## Method (fixed now)
- The trial runner gets an optional `--trace-dir`: a 5 Hz trace per trial (ground-truth pose, AMCL pose in world frame, commanded velocity, nearest LiDAR return, collision-monitor state) and an event log (behaviour-tree status changes with their times, each new global plan with its length and end point). Off by default; with it off the runner is unchanged.
- Re-runs: every world-B trial that failed in Phase 4 (32 trials: baseline 4, smac2d 9, dwb 9, rpp 9, thetastar 1) plus, for contrast, the baseline on b06, b14, b15 and b16 (long pairs it solved). One trial per pair and configuration, session seed 12 (as in Phase 4), real-time factor 1, same maps and configs.
- Outputs go to `results/diagnosis/` (CSV rows and `traces/`), never to `results/trials/`, so the Phase 4 tables cannot change. Re-run outcomes are reported next to the Phase 4 outcome; because Nav2 and AMCL are not seedable, a re-run may differ from the original (that is itself information about how deterministic a failure is).
- Reading the traces: where the robot stops or loops (position against the map and walls), which behaviour-tree node was active, whether the plan end moved, AMCL error over time, nearest obstacle at the moment of the stall, collision-monitor state.
- Traces (small CSVs) are committed; rosbags are not used.

## Findings
(to be filled in)
