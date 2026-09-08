from src.notifications.daily_digest_service import (
    DailyDigestService,
)


class FakeNotifier:

    def __init__(self):
        self.messages = []

    def send_message(self, message):
        self.messages.append(message)
        return True


def test_daily_digest_sends_summary():

    notifier = FakeNotifier()

    service = DailyDigestService(
        notifier
    )

    ranked_jobs = [
        {
            "job": type(
                "JobObject",
                (),
                {
                    "title": "DevOps Engineer",
                    "company": "Test Company",
                    "location": "Hyderabad",
                    "job_url": "https://example.com/job",
                },
            )(),
            "score": 60,
            "recommendation": "APPLY",
        },
        {
            "job": type(
                "JobObject",
                (),
                {
                    "title": "Cloud Engineer",
                    "company": "Cloud Co",
                    "location": "Remote",
                    "job_url": "https://example.com/cloud",
                },
            )(),
            "score": 45,
            "recommendation": "CONSIDER",
        },
        {
            "job": type(
                "JobObject",
                (),
                {
                    "title": "Senior Engineer",
                    "company": "Skip Co",
                    "location": "Hyderabad",
                    "job_url": "",
                },
            )(),
            "score": 20,
            "recommendation": "SKIP",
        },
    ]

    applications = []

    sent = service.send_digest(
        ranked_jobs,
        applications,
    )

    assert sent is True
    assert len(notifier.messages) == 1

    message = notifier.messages[0]

    assert "DAILY JOB DIGEST" in message
    assert "DevOps Engineer" in message
    assert "Cloud Engineer" in message
    assert "Senior Engineer" not in message