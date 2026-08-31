from src.jobs.job import Job
from src.jobs.job_repository import JobRepository
from src.jobs.job_actions import (
    update_job_statuses_from_ranking
)

def create_sample_jobs():
    return [
        Job(
            job_id=1,
            title="DevOps Engineer",
            company="Example Tech",
            location="Hyderabad",
            description="DevOps role",
            status="NEW"
        ),
        Job(
            job_id=2,
            title="Cloud Engineer",
            company="Cloud Systems",
            location="Bangalore",
            description="Cloud role",
            status="SHORTLISTED"
        )
    ]


def test_duplicate_job_detection():
    jobs = create_sample_jobs()

    duplicate_job = Job(
        job_id=3,
        title="DevOps Engineer",
        company="Example Tech",
        location="Remote",
        description="Another DevOps role"
    )

    repository = JobRepository(
        "data/jobs.json"
    )

    result = repository.is_duplicate(
        duplicate_job,
        jobs
    )

    assert result is True


def test_non_duplicate_job():
    jobs = create_sample_jobs()

    new_job = Job(
        job_id=3,
        title="Platform Engineer",
        company="Startup Labs",
        location="Remote",
        description="Platform role"
    )

    repository = JobRepository(
        "data/jobs.json"
    )

    result = repository.is_duplicate(
        new_job,
        jobs
    )

    assert result is False
def test_shortlisted_job_status_is_protected():
    jobs = create_sample_jobs()

    repository = JobRepository(
        "data/jobs.json"
    )

    ranked_jobs = [
        {
            "job": jobs[1],
            "recommendation": "SKIP"
        }
    ]

    update_job_statuses_from_ranking(
        ranked_jobs,
        jobs,
        repository
    )

    assert jobs[1].status == "SHORTLISTED"
def test_applied_job_status_is_protected():
    jobs = create_sample_jobs()

    jobs[0].status = "APPLIED"

    repository = JobRepository(
        "data/jobs.json"
    )

    ranked_jobs = [
        {
            "job": jobs[0],
            "recommendation": "SKIP"
        }
    ]

    update_job_statuses_from_ranking(
        ranked_jobs,
        jobs,
        repository
    )

    assert jobs[0].status == "APPLIED"    
def test_new_job_strong_apply_moves_to_shortlisted():
    jobs = create_sample_jobs()

    jobs[0].status = "NEW"

    repository = JobRepository(
        "data/jobs.json"
    )

    ranked_jobs = [
        {
            "job": jobs[0],
            "recommendation": "STRONG APPLY"
        }
    ]

    update_job_statuses_from_ranking(
        ranked_jobs,
        jobs,
        repository
    )

    assert jobs[0].status == "SHORTLISTED"


def test_new_job_apply_moves_to_shortlisted():
    jobs = create_sample_jobs()

    jobs[0].status = "NEW"

    repository = JobRepository(
        "data/jobs.json"
    )

    ranked_jobs = [
        {
            "job": jobs[0],
            "recommendation": "APPLY"
        }
    ]

    update_job_statuses_from_ranking(
        ranked_jobs,
        jobs,
        repository
    )

    assert jobs[0].status == "SHORTLISTED"


def test_new_job_skip_moves_to_analyzed():
    jobs = create_sample_jobs()

    jobs[0].status = "NEW"

    repository = JobRepository(
        "data/jobs.json"
    )

    ranked_jobs = [
        {
            "job": jobs[0],
            "recommendation": "SKIP"
        }
    ]

    update_job_statuses_from_ranking(
        ranked_jobs,
        jobs,
        repository
    )

    assert jobs[0].status == "ANALYZED"