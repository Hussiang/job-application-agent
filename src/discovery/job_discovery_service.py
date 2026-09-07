from datetime import datetime

from src.discovery.job_relevance_filter import (
    JobRelevanceFilter,
)


class JobDiscoveryService:

    def __init__(
        self,
        job_source,
        job_repository,
        profile,
    ):
        self.job_source = job_source
        self.job_repository = job_repository

        self.relevance_filter = (
            JobRelevanceFilter(profile)
        )

    def discover_jobs(
        self,
        queries,
        existing_jobs,
    ):
        discovered_jobs = []

        next_job_id = (
            self.job_repository.get_next_job_id()
        )

        total_jobs_found = 0
        rejected_count = 0
        duplicate_count = 0
        updated_count = 0

        current_time = (
            datetime.now().isoformat()
        )

        for query in queries:
            print(
                f"\nSearching jobs for: {query}"
            )

            jobs = self.job_source.search(
                query
            )

            total_jobs_found += len(jobs)

            for job in jobs:

                is_relevant, reason = (
                    self.relevance_filter.is_relevant(
                        job
                    )
                )

                if not is_relevant:
                    rejected_count += 1

                    print(
                        f"Rejected: "
                        f"{job.title} - "
                        f"{reason}"
                    )

                    continue

                existing_job = (
                    self.job_repository.find_duplicate(
                        job,
                        existing_jobs,
                    )
                )

                if existing_job:
                    duplicate_count += 1
                    existing_job.last_seen = current_time

                    if not existing_job.active:
                        existing_job.active = True
                        print(
                            f"Reactivated job: "
                            f"{existing_job.title} - "
                            f"{existing_job.company}"
                        )
                    else:
                        print(
                            f"Duplicate updated: "
                            f"{job.title} - {job.company}"
                        )

                    updated_count += 1
                    continue

                job.job_id = next_job_id

                job.first_seen = current_time
                job.last_seen = current_time

                next_job_id += 1

                existing_jobs.append(job)
                discovered_jobs.append(job)

                print(
                    f"New job discovered: "
                    f"{job.title} - "
                    f"{job.company}"
                )

        if discovered_jobs or updated_count:
            self.job_repository.save_jobs(
                existing_jobs
            )

        print(
            "\n========== DISCOVERY SUMMARY =========="
        )

        print(
            f"Search queries: {len(queries)}"
        )

        print(
            f"Jobs returned: {total_jobs_found}"
        )

        print(
            f"New jobs added: {len(discovered_jobs)}"
        )

        print(
            f"Duplicates updated: {duplicate_count}"
        )

        print(
            f"Rejected: {rejected_count}"
        )

        return discovered_jobs