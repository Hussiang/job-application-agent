import pytest
import run_discovery as discovery_runner

from src.jobs.job import Job
from run_discovery import collect_notification_candidates, parse_args


def test_parse_args_uses_safe_defaults():
    args = parse_args([])

    assert args.dry_run is False
    assert args.no_telegram is False
    assert args.limit is None


def test_parse_args_accepts_all_options():
    args = parse_args([
        "--dry-run",
        "--no-telegram",
        "--limit",
        "3",
    ])

    assert args.dry_run is True
    assert args.no_telegram is True
    assert args.limit == 3


def test_parse_args_rejects_zero_limit():
    with pytest.raises(SystemExit):
        parse_args(["--limit", "0"])


def test_parse_args_rejects_negative_limit():
    with pytest.raises(SystemExit):
        parse_args(["--limit", "-1"])

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
def configure_main(monkeypatch, discovery_result):
    captured = {}

    profile = {
        "job_discovery": {
            "locations": ["Hyderabad"],
            "results_per_search": 10,
        },
        "notifications": {
            "telegram": {
                "enabled": True,
                "minimum_score": 45,
            }
        },
    }

    monkeypatch.setattr(
        discovery_runner,
        "load_profile",
        lambda: profile,
    )
    monkeypatch.setattr(
        discovery_runner,
        "load_scoring",
        lambda: {},
    )

    class FakeRepository:
        def __init__(self, path):
            self.saved = False

        def save_jobs(self, jobs):
            self.saved = True

    class FakeJsonSource:
        def __init__(self, path):
            pass

        def fetch_jobs(self):
            return []

    class FakeAdzunaSource:
        def __init__(self, **kwargs):
            pass

    class FakeDiscoveryService:
        def __init__(self, **kwargs):
            pass

        def discover_jobs(self, **kwargs):
            captured.update(kwargs)
            return discovery_result

    monkeypatch.setattr(
        discovery_runner,
        "JobRepository",
        FakeRepository,
    )
    monkeypatch.setattr(
        discovery_runner,
        "JsonJobSource",
        FakeJsonSource,
    )
    monkeypatch.setattr(
        discovery_runner,
        "AdzunaJobSource",
        FakeAdzunaSource,
    )
    monkeypatch.setattr(
        discovery_runner,
        "JobDiscoveryService",
        FakeDiscoveryService,
    )
    monkeypatch.setattr(
        discovery_runner,
        "build_search_queries",
        lambda profile: ["query-1", "query-2", "query-3"],
    )

    def unexpected_telegram(*args, **kwargs):
        raise AssertionError("Telegram must not be initialized")

    monkeypatch.setattr(
        discovery_runner,
        "TelegramNotifier",
        unexpected_telegram,
    )

    return captured
def test_dry_run_disables_persistence_and_notifications(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["run_discovery.py", "--dry-run"],
    )

    captured = configure_main(
        monkeypatch,
        {
            "complete": True,
            "new_jobs": [],
            "changed_jobs": [],
            "failed_queries": [],
        },
    )

    discovery_runner.main()

    assert captured["persist"] is False


def test_no_telegram_keeps_discovery_persistence_enabled(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["run_discovery.py", "--no-telegram"],
    )

    captured = configure_main(
        monkeypatch,
        {
            "complete": True,
            "new_jobs": [],
            "changed_jobs": [],
            "failed_queries": [],
        },
    )

    discovery_runner.main()

    assert captured["persist"] is True


def test_limit_restricts_number_of_discovery_queries(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["run_discovery.py", "--dry-run", "--limit", "2"],
    )

    captured = configure_main(
        monkeypatch,
        {
            "complete": True,
            "new_jobs": [],
            "changed_jobs": [],
            "failed_queries": [],
        },
    )

    discovery_runner.main()

    assert captured["queries"] == ["query-1", "query-2"]


def test_incomplete_discovery_suppresses_notifications(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["run_discovery.py"],
    )

    captured = configure_main(
        monkeypatch,
        {
            "complete": False,
            "new_jobs": [],
            "changed_jobs": [],
            "failed_queries": [
                {
                    "query": "query-1",
                    "error": "Simulated source failure",
                }
            ],
        },
    )

    discovery_runner.main()

    assert captured["persist"] is True