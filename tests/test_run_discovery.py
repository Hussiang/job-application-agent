from src.jobs.job import Job
from run_discovery import collect_notification_candidates


def make_job(job_id, *, source="Adzuna", active=True, notified=False):
    return Job(
        job_id=job_id,
        title=f"DevOps Engineer {job_id}",
        company="Example Tech",
        location="Hyderabad",
        description="AWS and Linux role",
        source=source,
        job_url=f"https://example.com/jobs/{job_id}",
        active=active,
        telegram_notified=notified,
    )


def test_pending_source_backed_active_jobs_are_included_for_retry():
    pending = make_job(1)
    legacy_sample = make_job(2, source=None)
    inactive = make_job(3, active=False)
    already_notified = make_job(4, notified=True)

    candidates = collect_notification_candidates(
        [pending, legacy_sample, inactive, already_notified],
        [],
    )

    assert candidates == [pending]


def test_new_and_changed_jobs_are_included_and_deduplicated():
    new_job = make_job(1)
    changed_job = make_job(2, notified=True)
    pending_job = make_job(3)

    candidates = collect_notification_candidates(
        [new_job, changed_job, pending_job],
        [new_job, changed_job],
    )

    assert candidates == [new_job, changed_job, pending_job]
    assert len({job.job_id for job in candidates}) == 3


def test_failed_delivery_stays_eligible_until_successful_retry():
    from src.notifications.job_notification_service import JobNotificationService

    class SequenceNotifier:
        def __init__(self):
            self.results = [False, True]

        def send_message(self, message):
            return self.results.pop(0)

    job = make_job(10)
    ranked = [{"job": job, "score": 60, "recommendation": "APPLY"}]
    notifier = SequenceNotifier()
    service = JobNotificationService(
        notifier,
        {"enabled": True, "minimum_score": 45},
    )

    first_candidates = collect_notification_candidates([job], [])
    assert first_candidates == [job]
    assert service.notify_new_jobs(ranked) == 0
    assert collect_notification_candidates([job], []) == [job]

    assert service.notify_new_jobs(ranked) == 1
    assert collect_notification_candidates([job], []) == []
