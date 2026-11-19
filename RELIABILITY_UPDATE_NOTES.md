# Job Application Agent — Reliability Update

This patch contains coordinated updates for:

- Atomic `data/jobs.json` writes using a temporary file in the same directory and `os.replace`.
- Structured Adzuna query outcomes (`JobSearchResult`) so successful empty results differ from API failures.
- Discovery completion tracking with successful/failed query counts and failure details.
- No persistence of any discovery changes when at least one query fails. This deliberately allows a later complete run to rediscover and notify those jobs instead of silently losing notifications.
- Suppression of individual notifications and the daily digest for incomplete discovery runs.
- Regression tests for the new behavior.

## Apply

Extract the archive into the project root, preserving its folder structure. Before extraction, back up the nine existing files listed in the archive. Do not replace `.env`, `.git`, or your `data/jobs.json` manually; the patch does not include them.

## Verify

Run from the project root:

```bash
python -m pytest -q
python -m compileall -q .
git diff --check
```

Expected test result from the patch workspace: **83 passed**.

No live Adzuna requests or Telegram messages were sent while developing or testing this patch.

## Important behavior

- All queries succeed with zero jobs: this is a complete run; a zero-results digest may be sent.
- Any query fails: the run is partial; no discovery changes are persisted and no Telegram notifications or digest are sent.
- All queries succeed with jobs: discovery changes are saved; notifications are processed; notification flags are saved afterward.

Atomic replacement protects against a partial file write on supported local filesystems. It does not provide a multi-file transaction or guarantee exactly-once Telegram delivery if the process crashes after Telegram accepts a message but before the notification flag is saved.
