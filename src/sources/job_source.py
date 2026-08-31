from abc import ABC, abstractmethod

from src.jobs.job import Job


class JobSource(ABC):

    @abstractmethod
    def fetch_jobs(self) -> list[Job]:
        """
        Fetch jobs from the source and return normalized Job objects.
        """
        pass