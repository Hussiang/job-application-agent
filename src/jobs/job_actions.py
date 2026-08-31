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

    protected_statuses = [
        "SHORTLISTED",
        "APPLIED",
        "REJECTED",
        "ARCHIVED"
    ]

    for result in ranked_jobs:
        job = result["job"]

        if job.status in protected_statuses:
            continue

        if result["recommendation"] in [
            "STRONG APPLY",
            "APPLY"
        ]:
            new_status = "SHORTLISTED"

        else:
            new_status = "ANALYZED"

        if job.status != new_status:
            job_repository.update_job_status(
                jobs,
                job.job_id,
                new_status
            )