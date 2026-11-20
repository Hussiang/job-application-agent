
import pytest

import src.applications.application_actions as actions
import src.applications.application_tracker as tracker
from src.applications.application_model import Application
from src.jobs.job import Job


def create_job():
    return Job(
        job_id=1,
        title="DevOps Engineer",
        company="Example Tech",
        location="Hyderabad",
        description="DevOps role",
        status="SHORTLISTED",
    )


def test_track_application_updates_both_records(monkeypatch):
    job = create_job()
    jobs = [job]
    saved_applications = []

    monkeypatch.setattr(
        actions,
        "get_application",
        lambda job_id: None,
    )

    def fake_add_application(selected_job):
        application = Application(
            job_id=selected_job.job_id,
            title=selected_job.title,
            company=selected_job.company,
        )
        saved_applications.append(application)
        return application

    def fake_update_job_status(
        current_jobs,
        repository,
        job_id,
        new_status,
    ):
        assert current_jobs is jobs
        assert job_id == 1
        job.status = new_status
        return job

    monkeypatch.setattr(
        actions,
        "add_application",
        fake_add_application,
    )
    monkeypatch.setattr(
        actions,
        "update_job_status",
        fake_update_job_status,
    )

    result = actions.track_application(
        job,
        jobs,
        object(),
    )

    assert result is saved_applications[0]
    assert job.status == "APPLIED"
    assert len(saved_applications) == 1


def test_track_application_rolls_back_when_job_update_fails(
    monkeypatch,
):
    job = create_job()
    jobs = [job]
    original_applications = []

    monkeypatch.setattr(
        actions,
        "get_application",
        lambda job_id: None,
    )

    def fake_add_application(selected_job):
        application = Application(
            job_id=selected_job.job_id,
            title=selected_job.title,
            company=selected_job.company,
        )
        original_applications.append(application)
        return application

    def fake_update_job_status(*args):
        raise OSError("simulated job save failure")

    def fake_restore_applications(applications):
        original_applications.clear()
        original_applications.extend(applications)

    monkeypatch.setattr(
        actions,
        "add_application",
        fake_add_application,
    )
    monkeypatch.setattr(
        actions,
        "update_job_status",
        fake_update_job_status,
    )
    monkeypatch.setattr(
        tracker,
        "load_applications",
        lambda: [],
    )
    monkeypatch.setattr(
        tracker,
        "save_applications",
        fake_restore_applications,
    )

    with pytest.raises(OSError, match="simulated job save failure"):
        actions.track_application(
            job,
            jobs,
            object(),
        )

    assert original_applications == []
    assert job.status == "SHORTLISTED"


def test_track_application_does_not_duplicate_existing_application(
    monkeypatch,
):
    job = create_job()

    existing_application = Application(
        job_id=job.job_id,
        title=job.title,
        company=job.company,
    )

    monkeypatch.setattr(
        actions,
        "get_application",
        lambda job_id: existing_application,
    )

    def unexpected_add(*args, **kwargs):
        raise AssertionError("Duplicate application must not be added")

    def unexpected_job_update(*args, **kwargs):
        raise AssertionError("Job must not be updated")

    monkeypatch.setattr(
        actions,
        "add_application",
        unexpected_add,
    )
    monkeypatch.setattr(
        actions,
        "update_job_status",
        unexpected_job_update,
    )

    result = actions.track_application(
        job,
        [job],
        object(),
    )

    assert result is None
    assert job.status == "SHORTLISTED"
