import json
from datetime import datetime

from src.applications.application_model import Application
from src.jobs.job import Job


APPLICATIONS_FILE = "data/applications.json"

VALID_STATUSES = [
    "APPLIED",
    "INTERVIEW",
    "OFFER",
    "REJECTED"
]


def load_applications() -> list[Application]:
    with open(
        APPLICATIONS_FILE,
        "r"
    ) as file:
        applications = json.load(file)

    return [
        Application(**application)
        for application in applications
    ]


def save_applications(
    applications: list[Application]
) -> None:
    with open(
        APPLICATIONS_FILE,
        "w"
    ) as file:
        json.dump(
            [
    application.to_dict()
    for application in applications
],
            file,
            indent=4
        )


def add_application(
    job: Job
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
        )
    )

    applications.append(application)

    save_applications(applications)

    return application


def update_application_status(
    job_id,
    new_status
):
    if new_status not in VALID_STATUSES:
        return "INVALID_STATUS"

    applications = load_applications()

    for application in applications:
        if application.job_id == job_id:
            application.status = new_status

            save_applications(applications)

            return application

    return None


def get_application(
    job_id
) -> Application | None:
    applications = load_applications()

    for application in applications:
        if application.job_id == job_id:
            return application

    return None