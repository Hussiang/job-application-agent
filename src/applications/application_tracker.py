import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.applications.application_model import Application
from src.jobs.job import Job


APPLICATIONS_FILE = Path(
    "data/applications.json"
)


VALID_STATUSES = [
    "APPLIED",
    "INTERVIEW",
    "OFFER",
    "REJECTED",
    "WITHDRAWN",
]


def load_applications() -> list[Application]:
    if not APPLICATIONS_FILE.exists():
        return []

    with APPLICATIONS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        applications = json.load(file)

    return [
        Application(
            job_id=application["job_id"],
            title=application["title"],
            company=application["company"],
            status=application.get(
                "status",
                "APPLIED",
            ),
            applied_date=application.get(
                "applied_date"
            ),
            interview_date=application.get(
                "interview_date"
            ),
            follow_up_date=application.get(
                "follow_up_date"
            ),
            notes=application.get(
                "notes",
                "",
            ),
            resume_version=application.get(
                "resume_version"
            ),
            application_url=application.get(
                "application_url"
            ),
            last_updated=application.get(
                "last_updated",
                "",
            ),
        )
        for application in applications
    ]


def save_applications(
    applications: list[Application],
) -> None:

    APPLICATIONS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with APPLICATIONS_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            [
                application.to_dict()
                for application in applications
            ],
            file,
            indent=4,
        )


def add_application(
    job: Job,
    resume_version: Optional[str] = None,
    application_url: Optional[str] = None,
) -> Application | None:

    applications = load_applications()

    for application in applications:
        if application.job_id == job.job_id:
            return None

    application = Application(
        job_id=job.job_id,
        title=job.title,
        company=job.company,
        status="APPLIED",
        applied_date=datetime.now().strftime(
            "%Y-%m-%d"
        ),
        resume_version=resume_version,
        application_url=(
            application_url
            or job.job_url
        ),
    )

    applications.append(
        application
    )

    save_applications(
        applications
    )

    return application


def update_application_status(
    job_id: int,
    new_status: str,
):
    new_status = (
        new_status
        .upper()
        .strip()
    )

    if new_status not in VALID_STATUSES:
        return "INVALID_STATUS"

    applications = load_applications()

    for application in applications:

        if application.job_id == job_id:

            application.status = new_status
            application.last_updated = (
                datetime.now().isoformat()
            )

            save_applications(
                applications
            )

            return application

    return None


def update_application_details(
    job_id: int,
    interview_date: Optional[str] = None,
    follow_up_date: Optional[str] = None,
    notes: Optional[str] = None,
):
    applications = load_applications()

    for application in applications:

        if application.job_id == job_id:

            if interview_date is not None:
                application.interview_date = (
                    interview_date
                )

            if follow_up_date is not None:
                application.follow_up_date = (
                    follow_up_date
                )

            if notes is not None:
                application.notes = (
                    notes.strip()
                )

            application.last_updated = (
                datetime.now().isoformat()
            )

            save_applications(
                applications
            )

            return application

    return None


def get_application(
    job_id: int,
) -> Application | None:

    applications = load_applications()

    for application in applications:

        if application.job_id == job_id:
            return application

    return None