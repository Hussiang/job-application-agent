# Pending Telegram Notification Retry Update

## Files in this patch

- `src/notifications/job_notification_service.py`
- `run_discovery.py`
- `tests/test_job_notifications.py`
- `tests/test_run_discovery.py`

## Behavior

- New and changed jobs remain notification candidates.
- On every complete discovery run, active jobs with a non-empty source and `telegram_notified == False` are also considered for notification.
- Legacy/sample records without source metadata are not automatically retried.
- Jobs below the configured score threshold or outside allowed recommendations remain unnotified and can be reconsidered if their ranking later changes.
- A successful notifier response sets `telegram_notified` and `notification_hash`.
- A false response or exception leaves the job pending for a future complete run.
- Already-notified jobs with the same notification hash are skipped.
- The existing run-level save persists notification state after notification attempts.

## Apply

From the project root, back up the four target paths, then extract this ZIP into the project root and overwrite matching files.

No `.env`, `.git`, `data/jobs.json`, or existing backups are included.

## Offline verification

The merged project passed:

- `python -m pytest -q` — 88 passed
- `python -m compileall -q .` — passed
- Python trailing-whitespace scan — passed

No Adzuna API requests or Telegram messages were sent during testing.
