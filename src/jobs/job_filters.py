from src.jobs.job import Job


def filter_jobs_by_status(
    jobs: list[Job],
    status: str
) -> list[Job]:

    status = status.upper().strip()

    return [
        job
        for job in jobs
        if job.status == status
    ]


def search_jobs(
    jobs: list[Job],
    keyword: str
) -> list[Job]:

    keyword = keyword.lower().strip()

    return [
        job
        for job in jobs
        if (
            keyword in job.title.lower()
            or keyword in job.company.lower()
        )
    ]