from src.jobs.job import Job
from src.notifications.job_notification_service import (
    JobNotificationService,
)


class FakeNotifier:

    def __init__(self):
        self.messages = []

    def send_message(self, message):
        self.messages.append(message)
        return True


def create_job():
    return Job(
        job_id=1,
        title="DevOps Engineer",
        company="Test Company",
        location="Hyderabad",
        description="AWS and Kubernetes role",
        skills=[
            "AWS",
            "Linux",
            "Docker",
        ],
        responsibilities=[
            "Maintain CI/CD pipelines",
        ],
        source="Test",
        job_url="https://example.com/job/1",
    )


def create_service():
    notifier = FakeNotifier()

    service = JobNotificationService(
        notifier=notifier,
        notification_config={
            "enabled": True,
            "minimum_score": 45,
            "recommendations": [
                "STRONG APPLY",
                "APPLY",
                "CONSIDER",
            ],
        },
    )

    return service, notifier


def test_new_qualifying_job_is_notified():
    service, notifier = create_service()

    job = create_job()

    ranked_job = {
        "job": job,
        "score": 60,
        "recommendation": "APPLY",
    }

    sent = service.notify_new_jobs(
        [ranked_job]
    )

    assert sent == 1
    assert job.telegram_notified is True
    assert job.notification_hash is not None
    assert len(notifier.messages) == 1


def test_same_job_is_not_notified_twice():
    service, notifier = create_service()

    job = create_job()

    ranked_job = {
        "job": job,
        "score": 60,
        "recommendation": "APPLY",
    }

    first_sent = service.notify_new_jobs(
        [ranked_job]
    )

    second_sent = service.notify_new_jobs(
        [ranked_job]
    )

    assert first_sent == 1
    assert second_sent == 0
    assert len(notifier.messages) == 1


def test_meaningful_change_creates_new_notification():
    service, notifier = create_service()

    job = create_job()

    ranked_job = {
        "job": job,
        "score": 60,
        "recommendation": "APPLY",
    }

    first_sent = service.notify_new_jobs(
        [ranked_job]
    )

    original_hash = job.notification_hash

    job.skills.append("Kubernetes")

    second_sent = service.notify_new_jobs(
        [ranked_job]
    )

    assert first_sent == 1
    assert second_sent == 1
    assert job.notification_hash != original_hash
    assert len(notifier.messages) == 2


def test_url_only_change_does_not_trigger_notification():
    service, notifier = create_service()

    job = create_job()

    ranked_job = {
        "job": job,
        "score": 60,
        "recommendation": "APPLY",
    }

    first_sent = service.notify_new_jobs(
        [ranked_job]
    )

    original_hash = job.notification_hash

    job.job_url = (
        "https://example.com/different-redirect"
    )

    second_sent = service.notify_new_jobs(
        [ranked_job]
    )

    assert first_sent == 1
    assert second_sent == 0
    assert job.notification_hash == original_hash
    assert len(notifier.messages) == 1
def test_score_below_threshold_is_not_notified():
    service, notifier = create_service()

    job = create_job()

    ranked_job = {
        "job": job,
        "score": 44.99,
        "recommendation": "CONSIDER",
    }

    sent = service.notify_new_jobs(
        [ranked_job]
    )

    assert sent == 0
    assert job.telegram_notified is False
    assert job.notification_hash is None
    assert len(notifier.messages) == 0


def test_consider_at_threshold_is_notified():
    service, notifier = create_service()

    job = create_job()

    ranked_job = {
        "job": job,
        "score": 45,
        "recommendation": "CONSIDER",
    }

    sent = service.notify_new_jobs(
        [ranked_job]
    )

    assert sent == 1
    assert job.telegram_notified is True
    assert job.notification_hash is not None
    assert len(notifier.messages) == 1    