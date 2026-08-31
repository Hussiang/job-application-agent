from src.jobs.job import Job
from src.jobs.job_filters import (
    filter_jobs_by_status,
    search_jobs
)


def create_sample_jobs():
    return [
        Job(
            job_id=1,
            title="DevOps Engineer",
            company="Example Tech",
            location="Hyderabad",
            description="DevOps role",
            status="APPLIED"
        ),
        Job(
            job_id=2,
            title="Cloud Support Engineer",
            company="Cloud Systems",
            location="Bangalore",
            description="Cloud support role",
            status="SHORTLISTED"
        ),
        Job(
            job_id=3,
            title="Platform Engineer",
            company="Startup Labs",
            location="Remote",
            description="Platform engineering role",
            status="ANALYZED"
        )
    ]


def test_filter_jobs_by_status():
    jobs = create_sample_jobs()

    results = filter_jobs_by_status(
        jobs,
        "APPLIED"
    )

    assert len(results) == 1
    assert results[0].job_id == 1


def test_search_jobs_by_title():
    jobs = create_sample_jobs()

    results = search_jobs(
        jobs,
        "DevOps"
    )

    assert len(results) == 1
    assert results[0].title == "DevOps Engineer"


def test_search_jobs_by_company():
    jobs = create_sample_jobs()

    results = search_jobs(
        jobs,
        "Cloud"
    )

    assert len(results) == 1
    assert results[0].company == "Cloud Systems"