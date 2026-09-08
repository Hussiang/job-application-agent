from src.core.config_loader import load_profile, load_scoring
from src.jobs.job_repository import JobRepository
from src.sources.json_job_source import JsonJobSource
from src.discovery.job_discovery_service import JobDiscoveryService
from src.sources.adzuna_job_source import AdzunaJobSource
from src.jobs.job_ranker import rank_job
from src.jobs.job_shortlist import show_top_jobs
from src.notifications.telegram_notifier import TelegramNotifier
from src.notifications.job_notification_service import (
    JobNotificationService,
)
from main import build_search_queries
from src.applications.application_tracker import (
    load_applications,
)
from src.notifications.daily_digest_service import (
    DailyDigestService,
)

DATA_FILE = "data/jobs.json"


def main():
    profile = load_profile()
    scoring = load_scoring()

    repository = JobRepository(DATA_FILE)

    jobs = JsonJobSource(DATA_FILE).fetch_jobs()

    discovery_config = profile.get(
        "job_discovery",
        {},
    )

    locations = discovery_config.get(
        "locations",
        [],
    )

    results_per_search = discovery_config.get(
        "results_per_search",
        10,
    )

    notification_config = (
        profile
        .get("notifications", {})
        .get("telegram", {})
    )

    queries = build_search_queries(profile)

    print(
        f"Starting automated discovery "
        f"with {len(queries)} searches..."
    )

    source = AdzunaJobSource(
        locations=locations,
        results_per_search=results_per_search,
    )

    discovery_service = JobDiscoveryService(
        job_source=source,
        job_repository=repository,
        profile=profile,
    )

    discovery_result = discovery_service.discover_jobs(
    queries=queries,
    existing_jobs=jobs,
)

    new_jobs = discovery_result["new_jobs"]
    changed_jobs = discovery_result["changed_jobs"]

    discovered_jobs = new_jobs + changed_jobs

    print(
    f"\nNew jobs discovered: "
    f"{len(new_jobs)}"
)

    print(
    f"Changed jobs detected: "
    f"{len(changed_jobs)}"
    )

    if not discovered_jobs:
     print(
        "No new or changed jobs to rank or notify."
    )
    return

    ranked_discovered_jobs = [
    rank_job(
        job,
        profile,
        scoring,
    )
    for job in discovered_jobs
]

    ranked_discovered_jobs.sort(
    key=lambda item: item["score"],
    reverse=True,
)

    notifier = TelegramNotifier()

    notification_service = JobNotificationService(
        notifier=notifier,
        notification_config=notification_config,
    )

    notifications_sent = (
        notification_service.notify_new_jobs(
            ranked_discovered_jobs
        )
    )

    # Persist new jobs and notification flags.
    repository.save_jobs(jobs)

    print(
        f"\nTelegram notifications sent: "
        f"{notifications_sent}"
    )

    print(
        "\n========== AUTOMATED RECOMMENDATIONS =========="
    )

    show_top_jobs(
        ranked_jobs,
        limit=len(ranked_jobs),
    )

    applications = load_applications()

    digest_service = DailyDigestService(
    notifier
)

    digest_sent = digest_service.send_digest(
    ranked_discovered_jobs,
    applications,
    minimum_score=notification_config.get(
        "minimum_score",
        45,
    ),
)

    print(
    f"Daily digest sent: {digest_sent}"
)
    if not discovered_jobs:
     print(
        "No new or changed jobs found."
    )

    applications = load_applications()

    notifier = TelegramNotifier()

    digest_service = DailyDigestService(
        notifier
    )

    digest_sent = digest_service.send_digest(
        [],
        applications,
        minimum_score=notification_config.get(
            "minimum_score",
            45,
        ),
    )

    print(
        f"Daily digest sent: {digest_sent}"
    )

    return