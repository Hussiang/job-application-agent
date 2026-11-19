from src.core.config_loader import load_profile, load_scoring
from src.jobs.job_repository import JobRepository
from src.sources.json_job_source import JsonJobSource
from src.discovery.job_discovery_service import JobDiscoveryService
from src.sources.adzuna_job_source import AdzunaJobSource
from src.jobs.job_ranker import rank_job
from src.jobs.job_shortlist import show_top_jobs
from src.notifications.telegram_notifier import TelegramNotifier
from src.notifications.job_notification_service import JobNotificationService
from src.discovery.search_query_builder import build_search_queries
from src.applications.application_tracker import load_applications
from src.notifications.daily_digest_service import DailyDigestService


DATA_FILE = "data/jobs.json"


def collect_notification_candidates(existing_jobs, discovered_jobs):
    """Return changed/new jobs plus active, source-backed pending jobs.

    Jobs without source metadata are excluded from automatic retries because
    legacy/sample records cannot be established as discovered listings.
    """
    candidates = []
    seen_ids = set()

    for job in discovered_jobs:
        if job.job_id not in seen_ids:
            candidates.append(job)
            seen_ids.add(job.job_id)

    for job in existing_jobs:
        if (
            job.active
            and job.source
            and not job.telegram_notified
            and job.job_id not in seen_ids
        ):
            candidates.append(job)
            seen_ids.add(job.job_id)

    return candidates


def main():
    profile = load_profile()
    scoring = load_scoring()
    repository = JobRepository(DATA_FILE)
    jobs = JsonJobSource(DATA_FILE).fetch_jobs()

    discovery_config = profile.get("job_discovery", {})
    locations = discovery_config.get("locations", [])
    results_per_search = discovery_config.get("results_per_search", 10)
    notification_config = (
        profile.get("notifications", {}).get("telegram", {})
    )

    queries = build_search_queries(profile)
    if not queries:
        print("No discovery queries were generated. Nothing to do.")
        return

    print(
        f"Starting automated discovery with {len(queries)} searches..."
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

    if not discovery_result["complete"]:
        print(
            "\nDISCOVERY INCOMPLETE — notifications suppressed. "
            "Existing jobs database was not updated."
        )
        for failure in discovery_result["failed_queries"]:
            print(f"- {failure['query']}: {failure['error']}")
        return

    new_jobs = discovery_result["new_jobs"]
    changed_jobs = discovery_result["changed_jobs"]
    discovered_jobs = new_jobs + changed_jobs

    print(f"\nNew jobs discovered: {len(new_jobs)}")
    print(f"Changed jobs detected: {len(changed_jobs)}")

    notifier = TelegramNotifier()
    applications = load_applications()

    ranked_discovered_jobs = [
        rank_job(job, profile, scoring)
        for job in discovered_jobs
    ]
    ranked_discovered_jobs.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    # Retry source-backed jobs that were not successfully notified on an
    # earlier complete run. Changed jobs remain candidates even if previously
    # notified; the notification hash decides whether a new message is needed.
    notification_candidates = collect_notification_candidates(
        jobs,
        discovered_jobs,
    )
    ranked_notification_candidates = [
        rank_job(job, profile, scoring)
        for job in notification_candidates
    ]
    ranked_notification_candidates.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    if ranked_notification_candidates:
        notification_service = JobNotificationService(
            notifier=notifier,
            notification_config=notification_config,
        )
        notifications_sent = notification_service.notify_new_jobs(
            ranked_notification_candidates
        )

        # Persist successful delivery flags. Failed sends remain pending.
        repository.save_jobs(jobs)
        print(f"\nTelegram notifications sent: {notifications_sent}")
    else:
        print("No eligible new, changed, or pending jobs to notify.")

    if ranked_discovered_jobs:
        print("\n========== AUTOMATED RECOMMENDATIONS ==========")
        show_top_jobs(
            ranked_discovered_jobs,
            limit=len(ranked_discovered_jobs),
        )
    else:
        print("No new or changed jobs to rank.")

    digest_service = DailyDigestService(
        notifier,
        notification_config,
    )
    digest_sent = digest_service.send_digest(
        ranked_discovered_jobs,
        applications,
        minimum_score=notification_config.get("minimum_score", 45),
        discovery_complete=True,
    )
    print(f"Daily digest sent: {digest_sent}")


if __name__ == "__main__":
    main()
