from datetime import datetime

from src.discovery.job_relevance_filter import JobRelevanceFilter


class JobDiscoveryService:

    def __init__(
        self,
        job_source,
        job_repository,
        profile,
    ):
        self.job_source = job_source
        self.job_repository = job_repository
        self.relevance_filter = JobRelevanceFilter(profile)

    def discover_jobs(
        self,
        queries,
        existing_jobs,
    ):
        new_jobs = []
        changed_jobs = []

        next_job_id = (
            self.job_repository.get_next_job_id()
        )

        total_jobs_found = 0
        rejected_count = 0
        duplicate_count = 0
        updated_count = 0

        current_time = datetime.now().isoformat()

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
                        f"{job.title} - {reason}"
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

                    fields_changed = (
                        self._update_existing_job(
                            existing_job,
                            job,
                            current_time,
                        )
                    )

                    if fields_changed:
                        changed_jobs.append(
                            existing_job
                        )

                        print(
                            f"Job changed: "
                            f"{existing_job.title} - "
                            f"{existing_job.company}"
                        )
                    else:
                        print(
                            f"Duplicate updated: "
                            f"{job.title} - "
                            f"{job.company}"
                        )

                    updated_count += 1

                    continue

                job.job_id = next_job_id
                job.first_seen = current_time
                job.last_seen = current_time
                job.active = True

                next_job_id += 1

                existing_jobs.append(job)
                new_jobs.append(job)

                print(
                    f"New job discovered: "
                    f"{job.title} - "
                    f"{job.company}"
                )

        if new_jobs or changed_jobs or updated_count:
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
            f"New jobs added: {len(new_jobs)}"
        )

        print(
            f"Changed jobs: {len(changed_jobs)}"
        )

        print(
            f"Duplicates updated: {duplicate_count}"
        )

        print(
            f"Rejected: {rejected_count}"
        )

        return {
            "new_jobs": new_jobs,
            "changed_jobs": changed_jobs,
        }

    def _update_existing_job(
        self,
        existing_job,
        new_job,
        current_time,
    ) -> bool:

        meaningful_fields = [
        "title",
        "company",
        "location",
        "skills",
        "responsibilities",
        "experience_required",
        "certification_requirement",
        ]

        fields_changed = False

        for field_name in meaningful_fields:

            old_value = getattr(
            existing_job,
            field_name,
            )

            new_value = getattr(
            new_job,
            field_name,
            )

            if old_value != new_value:
                fields_changed = True

        # Always refresh source data.
        existing_job.title = new_job.title
        existing_job.company = new_job.company
        existing_job.location = new_job.location
        existing_job.description = new_job.description
        existing_job.skills = new_job.skills
        existing_job.responsibilities = new_job.responsibilities
        existing_job.experience_required = (
            new_job.experience_required
        )
        existing_job.certification_requirement = (
            new_job.certification_requirement
        )
        existing_job.posted_date = new_job.posted_date
        existing_job.source = new_job.source
        existing_job.job_url = new_job.job_url

        existing_job.last_seen = current_time

        if not existing_job.active:
            existing_job.active = True
            fields_changed = True

        return fields_changed