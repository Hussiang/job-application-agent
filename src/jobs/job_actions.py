import copy

from src.jobs.job_repository import JobRepository
from src.jobs.job import Job


def update_job_status(
    jobs: list[Job],
    job_repository: JobRepository,
    job_id: int,
    new_status: str
) -> Job | None:

    return job_repository.update_job_status(
        jobs,
        job_id,
        new_status
    )



def update_job_statuses_from_ranking(
    ranked_jobs,
    jobs: list[Job],
    job_repository: JobRepository
) -> None:

    protected_statuses = {
        "SHORTLISTED",
        "APPLIED",
        "REJECTED",
        "ARCHIVED",
    }

    # Stage all changes in an independent collection.
    staged_jobs = copy.deepcopy(jobs)
    changed = False

    for result in ranked_jobs:
        ranked_job = result["job"]

        # Match the ranked job to the staged repository record.
        staged_job = next(
            (
                item for item in staged_jobs
                if item.job_id == ranked_job.job_id
            ),
            None,
        )

        if staged_job is None:
            continue

        if staged_job.status in protected_statuses:
            continue

        recommendation = result["recommendation"]

        if recommendation in ("STRONG APPLY", "APPLY"):
            new_status = "SHORTLISTED"
        else:
            new_status = "ANALYZED"

        if staged_job.status != new_status:
            staged_job.status = new_status
            changed = True

    # No changes means no disk write is necessary.
    if not changed:
        return

    # Persist the complete batch exactly once.
    job_repository.save_jobs(staged_jobs)

    # Update original objects only after persistence succeeds.
    for original_job, staged_job in zip(jobs, staged_jobs):
        original_job.status = staged_job.status
