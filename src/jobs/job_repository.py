import json
from pathlib import Path

from src.jobs.job import (
    Job,
    VALID_JOB_STATUSES
)
class JobRepository:

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def get_next_job_id(self) -> int:
        if not self.file_path.exists():
            return 1

        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            jobs = json.load(file)

        if not jobs:
            return 1

        return max(
            job["id"]
            for job in jobs
        ) + 1

    def save_jobs(self, jobs: list[Job]) -> None:
        with self.file_path.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                [
                    job.to_dict()
                    for job in jobs
                ],
                file,
                indent=4
            )

    def update_job_status(
        self,
        jobs: list[Job],
        job_id: int,
        new_status: str
    ) -> Job | None:

        new_status = new_status.upper().strip()

        if new_status not in VALID_JOB_STATUSES:
            raise ValueError(
                f"Invalid job status: {new_status}. "
                f"Valid statuses are: "
                f"{', '.join(VALID_JOB_STATUSES)}"
            )

        for job in jobs:
            if job.job_id == job_id:
                job.status = new_status

                self.save_jobs(jobs)

                return job

        return None

    def is_duplicate(
        self,
        new_job: Job,
        jobs: list[Job]
    ) -> bool:

        for job in jobs:
            same_title = (
                job.title.strip().lower()
                == new_job.title.strip().lower()
            )

            same_company = (
                job.company.strip().lower()
                == new_job.company.strip().lower()
            )

            same_url = (
                new_job.job_url
                and job.job_url
                and job.job_url == new_job.job_url
            )

            if same_url or (
                same_title
                and same_company
            ):
                return True

        return False
    