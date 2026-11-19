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

def test_save_jobs_atomically_preserves_previous_file_on_write_failure(
    tmp_path,
    monkeypatch,
):
    import json
    import pytest
    import src.jobs.job_repository as repository_module

    target = tmp_path / "jobs.json"
    original_content = '[{"id": 99, "title": "preserve"}]'
    target.write_text(original_content, encoding="utf-8")

    def fail_dump(*args, **kwargs):
        raise OSError("simulated disk write failure")

    monkeypatch.setattr(repository_module.json, "dump", fail_dump)
    repository = JobRepository(str(target))

    with pytest.raises(OSError, match="simulated disk write failure"):
        repository.save_jobs(create_sample_jobs())

    assert target.read_text(encoding="utf-8") == original_content
    assert list(tmp_path.glob(".jobs.json.*.tmp")) == []


def test_atomic_save_writes_valid_json(tmp_path):
    import json

    target = tmp_path / "nested" / "jobs.json"
    repository = JobRepository(str(target))
    jobs = create_sample_jobs()

    repository.save_jobs(jobs)

    saved = json.loads(target.read_text(encoding="utf-8"))
    assert [item["id"] for item in saved] == [1, 2]
    assert list(target.parent.glob(".jobs.json.*.tmp")) == []
