# called-it (working repo for the Annual Prediction Review project)

Read `AGENTS.md` for the layout and the division of labour and `research/` for the source
inventories. The skill contract is
`skills/called-it/SKILL.md`.

## Working rules for this repo

- The name `called-it` is the recommended pick and is used throughout; a rename is `git mv` on the
  skill folder plus `NAME` in `skills/called-it/scripts/lib/config.py` plus the manifests.
- Jev is pinned to `jev-1.14.0` (what `jev-latest` resolved to on 2026-10-24). Never pin an alias.
  Every cached answer records the model that answered.
- Standard library only in `skills/called-it/scripts`. If a dependency seems necessary, ask first.
- Prose written for humans (reports, README, article) carries no em or en dashes.
- Run tests with `python3 -m unittest discover -s tests` from the repo root.
- Worktree sessions: shell commands that redirect git elsewhere or that contain complex loops are
  refused by the guard. Write helper scripts to the job's tmp dir and run them with a plain command.
- X API reads cost money (about $0.005 a post on this account). Estimate before reading; the ledger
  in each run's `cache/x/` is the record.
- `yt-dlp` is on this machine; captions for podcast episodes are the source text for spoken predictions.
