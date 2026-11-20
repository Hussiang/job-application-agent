
import argparse
from copy import deepcopy
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


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Discover and rank relevant job opportunities."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Search and rank jobs without saving or sending notifications.",
    )

    parser.add_argument(
        "--no-telegram",
        action="store_true",
        help="Suppress job notifications and the daily digest.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of search queries.",
    )

    args = parser.parse_args(argv)

    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1.")

    return args


def main():
    args = parse_args()

    profile = load_profile()
    scoring = load_scoring()

    repository = JobRepository(DATA_FILE)
    stored_jobs = JsonJobSource(DATA_FILE).fetch_jobs()

# Dry-run must never mutate the objects representing stored jobs.
    jobs = deepcopy(stored_jobs) if args.dry_run else stored_jobs
    discovery_config = profile.get("job_discovery", {})
    locations = discovery_config.get("locations", [])
    results_per_search = discovery_config.get("results_per_search", 10)

    notification_config = (
        profile.get("notifications", {}).get("telegram", {})
    )

    # Build search queries.
    queries = build_search_queries(profile)

    if not queries:
        print("No discovery queries were generated. Nothing to do.")
        return

    if args.limit is not None:
        queries = queries[:args.limit]

    print(
        f"Starting automated discovery with {len(queries)} searches..."
    )

    if args.dry_run:
        print("DRY RUN MODE: database writes and notifications are disabled.")

    # Initialize job source.
    source = AdzunaJobSource(
        locations=locations,
        results_per_search=results_per_search,
    )

    # Initialize discovery service.
    discovery_service = JobDiscoveryService(
        job_source=source,
        job_repository=repository,
        profile=profile,
    )

    # Discover jobs.
    discovery_result = discovery_service.discover_jobs(
        queries=queries,
        existing_jobs=jobs,
        persist=not args.dry_run,
    )

    # Stop if discovery was incomplete.
    if not discovery_result["complete"]:
        print(
            "\nDISCOVERY INCOMPLETE — notifications suppressed. "
            "Existing jobs database was not updated."
        )

        for failure in discovery_result["failed_queries"]:
            print(
                f"- {failure['query']}: {failure['error']}"
            )

        return

    new_jobs = discovery_result["new_jobs"]
    changed_jobs = discovery_result["changed_jobs"]
    discovered_jobs = new_jobs + changed_jobs

    print(f"\nNew jobs discovered: {len(new_jobs)}")
    print(f"Changed jobs detected: {len(changed_jobs)}")

    # Rank discovered jobs.
    ranked_discovered_jobs = [
        rank_job(job, profile, scoring)
        for job in discovered_jobs
    ]

    ranked_discovered_jobs.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    # Display recommendations before notification handling.
    if ranked_discovered_jobs:
        show_top_jobs(ranked_discovered_jobs)
    else:
        print("\nNo new or changed relevant jobs found.")

    # Suppress notifications in dry-run or no-telegram mode.
    if args.dry_run or args.no_telegram:
        print(
            "\nTelegram notifications and daily digest suppressed."
        )
        return

    # Respect notification configuration.
    if not notification_config.get("enabled", True):
        print(
            "\nTelegram notifications are disabled in profile configuration."
        )
        return

    # Initialize notification dependencies.
    notifier = TelegramNotifier()
    applications = load_applications()

    # Collect new, changed, and pending jobs.
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

    # Send individual job notifications.
    if ranked_notification_candidates:
        notification_service = JobNotificationService(
            notifier=notifier,
            notification_config=notification_config,
        )

        notifications_sent = notification_service.notify_new_jobs(
            ranked_notification_candidates
        )

        repository.save_jobs(jobs)

        print(
            f"\nTelegram notifications sent: {notifications_sent}"
        )
    else:
        print(
            "\nNo eligible new, changed, or pending jobs to notify."
        )

    # Send daily digest only after complete discovery.
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
