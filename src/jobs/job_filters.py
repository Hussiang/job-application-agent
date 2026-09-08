from src.jobs.job import Job


def filter_jobs_by_status(
    jobs: list[Job],
    status: str,
) -> list[Job]:

    status = status.upper().strip()

    return [
        job
        for job in jobs
        if job.status == status
    ]


def filter_active_jobs(
    jobs: list[Job],
) -> list[Job]:

    return [
        job
        for job in jobs
        if job.active
    ]


def filter_jobs_by_min_score(
    ranked_jobs: list[dict],
    minimum_score: float,
) -> list[dict]:

    return [
        result
        for result in ranked_jobs
        if result["score"] >= minimum_score
    ]


def filter_jobs_by_recommendation(
    ranked_jobs: list[dict],
    recommendation: str,
) -> list[dict]:

    recommendation = (
        recommendation
        .upper()
        .strip()
    )

    return [
        result
        for result in ranked_jobs
        if result["recommendation"] == recommendation
    ]


def search_jobs(
    jobs: list[Job],
    keyword: str,
) -> list[Job]:

    keyword = keyword.lower().strip()

    if not keyword:
        return jobs

    return [
        job
        for job in jobs
        if (
            keyword in job.title.lower()
            or keyword in job.company.lower()
            or keyword in job.location.lower()
            or keyword in job.description.lower()
            or any(
                keyword in skill.lower()
                for skill in job.skills
            )
        )
    ]