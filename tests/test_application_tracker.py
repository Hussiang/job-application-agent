
import pytest

import src.applications.application_tracker as tracker
from src.applications.application_model import Application


def create_sample_applications():
    return [
        Application(
            job_id=1,
            title="DevOps Engineer",
            company="Example Tech",
            status="APPLIED",
            notes="Initial application",
        ),
        Application(
            job_id=2,
            title="Cloud Engineer",
            company="Cloud Systems",
            status="INTERVIEW",
            notes="Technical round",
        ),
    ]


def test_save_applications_preserves_previous_file_on_write_failure(
    tmp_path,
    monkeypatch,
):
    target = tmp_path / "applications.json"
    original_content = '[{"job_id": 99, "title": "preserve"}]'
    target.write_text(original_content, encoding="utf-8")

    def fail_dump(*args, **kwargs):
        raise OSError("simulated disk write failure")

    monkeypatch.setattr(tracker.json, "dump", fail_dump)
    monkeypatch.setattr(tracker, "APPLICATIONS_FILE", target)

    with pytest.raises(OSError, match="simulated disk write failure"):
        tracker.save_applications(create_sample_applications())

    assert target.read_text(encoding="utf-8") == original_content


def test_save_applications_writes_valid_json(tmp_path, monkeypatch):
    import json

    target = tmp_path / "nested" / "applications.json"
    monkeypatch.setattr(tracker, "APPLICATIONS_FILE", target)

    tracker.save_applications(create_sample_applications())

    saved = json.loads(target.read_text(encoding="utf-8"))

    assert len(saved) == 2
    assert saved[0]["job_id"] == 1
    assert saved[1]["job_id"] == 2


def test_failed_application_status_save_preserves_original_file(
    tmp_path,
    monkeypatch,
):
    target = tmp_path / "applications.json"
    monkeypatch.setattr(tracker, "APPLICATIONS_FILE", target)

    applications = create_sample_applications()
    tracker.save_applications(applications)

    original_content = target.read_text(encoding="utf-8")

    def fail_save(_applications):
        raise OSError("simulated disk write failure")

    monkeypatch.setattr(tracker, "save_applications", fail_save)

    with pytest.raises(OSError, match="simulated disk write failure"):
        tracker.update_application_status(1, "INTERVIEW")

    assert target.read_text(encoding="utf-8") == original_content


def test_invalid_application_status_does_not_save(
    tmp_path,
    monkeypatch,
):
    target = tmp_path / "applications.json"
    monkeypatch.setattr(tracker, "APPLICATIONS_FILE", target)

    def fail_save(_applications):
        raise AssertionError("Invalid status must not save")

    monkeypatch.setattr(tracker, "save_applications", fail_save)

    result = tracker.update_application_status(1, "INVALID")

    assert result == "INVALID_STATUS"


def test_missing_application_update_does_not_save(
    tmp_path,
    monkeypatch,
):
    target = tmp_path / "applications.json"
    monkeypatch.setattr(tracker, "APPLICATIONS_FILE", target)

    def fail_save(_applications):
        raise AssertionError("Missing application must not save")

    monkeypatch.setattr(tracker, "save_applications", fail_save)

    result = tracker.update_application_status(999, "INTERVIEW")

    assert result is None

def test_failed_application_details_save_preserves_original_file(
    tmp_path,
    monkeypatch,
):
    target = tmp_path / "applications.json"
    monkeypatch.setattr(tracker, "APPLICATIONS_FILE", target)

    tracker.save_applications(create_sample_applications())
    original_content = target.read_text(encoding="utf-8")

    def fail_save(_applications):
        raise OSError("simulated disk write failure")

    monkeypatch.setattr(tracker, "save_applications", fail_save)

    with pytest.raises(OSError, match="simulated disk write failure"):
        tracker.update_application_details(
            job_id=1,
            interview_date="2026-11-25",
            notes="Updated interview notes",
        )

    assert target.read_text(encoding="utf-8") == original_content


def test_successful_application_status_update_is_persisted(
    tmp_path,
    monkeypatch,
):
    import json

    target = tmp_path / "applications.json"
    monkeypatch.setattr(tracker, "APPLICATIONS_FILE", target)

    tracker.save_applications(create_sample_applications())

    result = tracker.update_application_status(1, "INTERVIEW")

    saved = json.loads(target.read_text(encoding="utf-8"))

    assert result.status == "INTERVIEW"
    assert saved[0]["status"] == "INTERVIEW"
    assert saved[0]["last_updated"]
def test_replace_failure_preserves_previous_file_and_cleans_temp(
    tmp_path,
    monkeypatch,
):
    applications_file = tmp_path / "applications.json"
    applications_file.write_text(
        '[{"job_id": 99}]',
        encoding="utf-8",
    )

    monkeypatch.setattr(
        tracker,
        "APPLICATIONS_FILE",
        applications_file,
    )

    def fail_replace(source, destination):
        raise OSError("Simulated replace failure")

    monkeypatch.setattr(tracker.os, "replace", fail_replace)

    with pytest.raises(OSError, match="Simulated replace failure"):
        tracker.save_applications(create_sample_applications())

    assert applications_file.read_text(encoding="utf-8") == (
        '[{"job_id": 99}]'
    )

    assert list(tmp_path.glob(".applications.json.*.tmp")) == []