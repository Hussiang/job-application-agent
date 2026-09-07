import json
from pathlib import Path

from src.jobs.job import (
    Job,
    VALID_JOB_STATUSES,
)


class JobRepository:

    def __init__(
        self,
        file_path: str,
    ):
        self.file_path = Path(file_path)

    def get_next_job_id(
        self,
    ) -> int:

        if not self.file_path.exists():
            return 1

        with self.file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            jobs = json.load(file)

        if not jobs:
            return 1

        return (
            max(
                job["id"]
                for job in jobs
            )
            + 1
        )

    def save_jobs(
        self,
        jobs: list[Job],
    ) -> None:

        with self.file_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                [
                    job.to_dict()
                    for job in jobs
                ],
                file,
                indent=4,
            )

    def update_job_status(
        self,
        jobs: list[Job],
        job_id: int,
        new_status: str,
    ) -> Job | None:

        new_status = (
            new_status.upper()
            .strip()
        )

        if new_status not in VALID_JOB_STATUSES:
            raise ValueError(
                f"Invalid job status: "
                f"{new_status}. "
                f"Valid statuses are: "
                f"{', '.join(VALID_JOB_STATUSES)}"
            )

        for job in jobs:
            if job.job_id == job_id:
                job.status = new_status

                self.save_jobs(
                    jobs
                )

                return job

        return None

    def _normalize_text(
        self,
        value: str | None,
    ) -> str:

        if not value:
            return ""

        return " ".join(
            value.lower().split()
        )

    def find_duplicate(
        self,
        new_job: Job,
        jobs: list[Job],
    ) -> Job | None:

        new_title = self._normalize_text(
            new_job.title
        )

        new_company = self._normalize_text(
            new_job.company
        )

        new_url = (
            new_job.job_url.strip()
            if new_job.job_url
            else ""
        )

        for job in jobs:

            existing_url = (
                job.job_url.strip()
                if job.job_url
                else ""
            )

            if (
                new_url
                and existing_url
                and new_url == existing_url
            ):
                return job

            existing_title = (
                self._normalize_text(
                    job.title
                )
            )

            existing_company = (
                self._normalize_text(
                    job.company
                )
            )

            if (
                new_title == existing_title
                and new_company == existing_company
            ):
                return job

        return None

    def is_duplicate(
        self,
        new_job: Job,
        jobs: list[Job],
    ) -> bool:

        duplicate = self.find_duplicate(
            new_job,
            jobs,
        )

        return duplicate is not None