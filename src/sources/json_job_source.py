import json
from pathlib import Path

from src.jobs.job import Job
from src.sources.job_source import JobSource


class JsonJobSource(JobSource):

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def fetch_jobs(self) -> list[Job]:
        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            raw_jobs = json.load(file)

        return [
            Job.from_dict(raw_job)
            for raw_job in raw_jobs
        ]