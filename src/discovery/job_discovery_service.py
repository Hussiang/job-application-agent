from datetime import datetime

from src.discovery.job_relevance_filter import JobRelevanceFilter
from src.jobs.job_parser import parse_job_description


class JobDiscoveryService:

    def __init__(self, job_source, job_repository, profile):
        self.job_source = job_source
        self.job_repository = job_repository
        self.relevance_filter = JobRelevanceFilter(profile)

        skills_by_category = profile.get("skills", {})
        self.known_skills = [
            skill
            for category_skills in skills_by_category.values()
            for skill in category_skills
        ]

    def discover_jobs(self, queries, existing_jobs):
        new_jobs = []
        changed_jobs = []
        failed_queries = []
        successful_queries = 0

        next_job_id = self.job_repository.get_next_job_id()
        total_jobs_found = 0
        rejected_count = 0
        duplicate_count = 0
        updated_count = 0
        current_time = datetime.now().isoformat()

        for query in queries:
            print(f"\nSearching jobs for: {query}")
            search_result = self.job_source.search(query)

            # Structured sources explicitly report success/failure. Retain
            # list compatibility for existing test doubles and other sources.
            if hasattr(search_result, "success") and hasattr(search_result, "jobs"):
                if not search_result.success:
                    failed_queries.append({
                        "query": query,
                        "error": search_result.error or "Source search failed",
                    })
                    print(f"Search failed: {query}")
                    continue
                jobs = search_result.jobs
            elif isinstance(search_result, list):
                jobs = search_result
            else:
                failed_queries.append({
                    "query": query,
                    "error": "Source returned an unsupported result",
                })
                continue

            successful_queries += 1
            total_jobs_found += len(jobs)

            for job in jobs:
                parsed_job = parse_job_description(
                    job.title,
                    job.company,
                    job.description,
                    self.known_skills,
                )

                job.skills = list(dict.fromkeys(
                    (job.skills or []) + (parsed_job.skills or [])
                ))
                job.responsibilities = list(dict.fromkeys(
                    (job.responsibilities or [])
                    + (parsed_job.responsibilities or [])
                ))

                if parsed_job.experience_required is not None:
                    job.experience_required = parsed_job.experience_required
                if parsed_job.certification_requirement is not None:
                    job.certification_requirement = (
                        parsed_job.certification_requirement
                    )

                is_relevant, reason = self.relevance_filter.is_relevant(job)
                if not is_relevant:
                    rejected_count += 1
                    print(f"Rejected: {job.title} - {reason}")
                    continue

                existing_job = self.job_repository.find_duplicate(
                    job,
                    existing_jobs,
                )

                if existing_job:
                    duplicate_count += 1
                    fields_changed = self._update_existing_job(
                        existing_job,
                        job,
                        current_time,
                    )
                    if fields_changed:
                        changed_jobs.append(existing_job)
                        print(
                            f"Job changed: {existing_job.title} - "
                            f"{existing_job.company}"
                        )
                    else:
                        print(
                            f"Duplicate updated: {job.title} - {job.company}"
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
                print(f"New job discovered: {job.title} - {job.company}")

        complete = not failed_queries and successful_queries == len(queries)

        # Do not commit any in-memory changes from an incomplete run. The next
        # complete run can rediscover these jobs and notify them safely.
        if complete and (new_jobs or changed_jobs or updated_count):
            self.job_repository.save_jobs(existing_jobs)

        print("\n========== DISCOVERY SUMMARY ==========")
        print(f"Search queries: {len(queries)}")
        print(f"Successful queries: {successful_queries}")
        print(f"Failed queries: {len(failed_queries)}")
        print(f"Jobs returned: {total_jobs_found}")
        print(f"New jobs added: {len(new_jobs)}")
        print(f"Changed jobs: {len(changed_jobs)}")
        print(f"Duplicates updated: {duplicate_count}")
        print(f"Rejected: {rejected_count}")

        return {
            "new_jobs": new_jobs,
            "changed_jobs": changed_jobs,
            "complete": complete,
            "total_queries": len(queries),
            "successful_queries": successful_queries,
            "failed_queries": failed_queries,
            "jobs_returned": total_jobs_found,
        }

    def _update_existing_job(
        self,
        existing_job,
        new_job,
        current_time,
    ) -> bool:
        fields_changed = False
        fields_to_update = [
            "title",
            "company",
            "location",
            "description",
            "skills",
            "responsibilities",
            "experience_required",
            "certification_requirement",
            "posted_date",
            "source",
            "job_url",
        ]

        for field_name in fields_to_update:
            old_value = getattr(existing_job, field_name)
            new_value = getattr(new_job, field_name)

            if new_value is None or new_value == "":
                continue
            if isinstance(new_value, list) and not new_value:
                continue
            if field_name == "location" and new_value == "Not specified":
                continue

            if old_value != new_value:
                setattr(existing_job, field_name, new_value)
                fields_changed = True

        existing_job.last_seen = current_time
        if not existing_job.active:
            existing_job.active = True
            fields_changed = True

        return fields_changed
