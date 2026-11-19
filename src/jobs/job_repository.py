import json
import os
import tempfile
from pathlib import Path

from src.jobs.job import (
    Job,
    VALID_JOB_STATUSES,
)


class JobRepository:

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def get_next_job_id(self) -> int:
        if not self.file_path.exists():
            return 1

        with self.file_path.open("r", encoding="utf-8") as file:
            jobs = json.load(file)

        if not jobs:
            return 1

        return max(job["id"] for job in jobs) + 1

    def save_jobs(self, jobs: list[Job]) -> None:
        """Persist jobs without truncating the last valid database on failure."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [job.to_dict() for job in jobs]
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=self.file_path.parent,
                prefix=f".{self.file_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as file:
                temp_path = Path(file.name)
                json.dump(payload, file, indent=4)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())

            # The temporary file is on the same filesystem, so replacement
            # is atomic on supported local filesystems.
            os.replace(temp_path, self.file_path)
            temp_path = None
        finally:
            if temp_path is not None:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError:
                    pass

    def update_job_status(
        self,
        jobs: list[Job],
        job_id: int,
        new_status: str,
    ) -> Job | None:
        new_status = new_status.upper().strip()

        if new_status not in VALID_JOB_STATUSES:
            raise ValueError(
                f"Invalid job status: {new_status}. "
                f"Valid statuses are: {', '.join(VALID_JOB_STATUSES)}"
            )

        for job in jobs:
            if job.job_id == job_id:
                job.status = new_status
                self.save_jobs(jobs)
                return job

        return None

    def _normalize_text(self, value: str | None) -> str:
        if not value:
            return ""
        return " ".join(value.lower().split())

    def find_duplicate(
        self,
        new_job: Job,
        jobs: list[Job],
    ) -> Job | None:
        new_title = self._normalize_text(new_job.title)
        new_company = self._normalize_text(new_job.company)
        new_url = new_job.job_url.strip() if new_job.job_url else ""

        for job in jobs:
            existing_url = job.job_url.strip() if job.job_url else ""

            if new_url and existing_url and new_url == existing_url:
                return job

            existing_title = self._normalize_text(job.title)
            existing_company = self._normalize_text(job.company)

            if new_title == existing_title and new_company == existing_company:
                return job

        return None

    def is_duplicate(self, new_job: Job, jobs: list[Job]) -> bool:
        return self.find_duplicate(new_job, jobs) is not None
