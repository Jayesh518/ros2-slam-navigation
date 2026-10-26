# Restore prompt

Use this after a crash, a re-login or a fresh Claude Code session on the Ubuntu drive. Open the project folder in VS Code, start Claude Code there, and paste everything inside the box below as your first message.

```text
Restore the Project 2 (ros2-slam-navigation) context and continue the work.

Do this in order, without asking me anything that is already decided in the files:

1. Read CLAUDE.md, PLAN.md, PHASES.md and docs/progress.md completely. They are the source of truth; treat the decisions listed in docs/progress.md as settled.
2. Check the repository for damage: run `git status`, `git log --oneline -10`, `git fsck --no-dangling` and `git fetch`. Compare with origin/main: tell me if I have uncommitted files, unpushed commits or if the remote is ahead. If git reports corruption, follow the crash rules in PLAN.md section 9 (clone fresh into a new folder, do not repair in place).
3. Run `bash scripts/check_env.sh` and compare with the environment recorded in docs/environment.md (if it exists). Tell me what changed or is missing. Install only what is missing and only after you have confirmed the package names in the official docs.
4. Look for work that was in progress when the drive failed: files newer than the last commit, half-written results, a build folder that is stale. Do not delete anything; list it and tell me what you propose.
5. Give me a short briefing: current phase, what is done, what was lost or is uncertain, and the exact next step from docs/progress.md.
6. Then continue from that next step. Work in small steps. After each finished step: append a dated line to the session log in docs/progress.md, update "Current state" and "Next steps", then `git add`, commit (my identity only, no Co-Authored-By or any AI attribution line) and `git push origin main`.
7. Obey the phase rules: stop at each exit gate, update PHASES.md, push, and ask before starting the next phase. Fix the protocol, metrics and hypotheses in docs/protocol.md before running any trial.

Be efficient: do not re-explain the plan back to me, do not re-run steps already recorded as done unless step 2 or 3 shows they are broken, and prefer one clear question over many.
```

## Notes
- The prompt only works if `docs/progress.md` is kept current, so Claude Code is told to update it after every step.
- Keep the journal and results pushed to GitHub: a crash loses only what was not yet pushed.
