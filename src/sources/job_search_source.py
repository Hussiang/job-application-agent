from abc import ABC, abstractmethod

from src.jobs.job import Job


class JobSearchSource(ABC):

    @abstractmethod
    def search(
        self,
        query: str,
    ) -> list[Job]:
        """
        Search for jobs using a query and return
        normalized Job objects.
        """
        pass
