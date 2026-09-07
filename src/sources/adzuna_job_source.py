import os

import requests
from dotenv import load_dotenv

from src.jobs.job import Job
from src.sources.job_search_source import JobSearchSource


class AdzunaJobSource(JobSearchSource):

    BASE_URL = (
        "https://api.adzuna.com/"
        "v1/api/jobs/in/search/1"
    )

    def __init__(
        self,
        locations,
        results_per_search=10,
    ):
        load_dotenv()

        self.app_id = os.getenv(
            "ADZUNA_APP_ID"
        )

        self.app_key = os.getenv(
            "ADZUNA_APP_KEY"
        )

        if not self.app_id or not self.app_key:
            raise RuntimeError(
                "ADZUNA_APP_ID or ADZUNA_APP_KEY "
                "is missing."
            )

        self.locations = locations
        self.results_per_search = results_per_search

    def search(
        self,
        query: str,
    ) -> list[Job]:

        role_query = self._remove_location(
            query
        )

        location = self._extract_location(
            query
        )

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": role_query,
            "results_per_page": (
                self.results_per_search
            ),
            "content-type": (
                "application/json"
            ),
        }

        if location:
            params["where"] = location

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        return self._normalize_jobs(
            data.get("results", [])
        )

    def _extract_location(
        self,
        query: str,
    ) -> str | None:

        query_lower = query.lower()

        for location in self.locations:
            if location.lower() in query_lower:
                return location

        return None

    def _remove_location(
        self,
        query: str,
    ) -> str:

        cleaned_query = query

        for location in self.locations:
            cleaned_query = cleaned_query.replace(
                location,
                "",
            )

        keywords_to_remove = [
            "AWS",
            "Linux",
            "Docker",
            "Kubernetes",
            "Terraform",
            "Jenkins",
            "CI/CD",
            "Python",
            "Monitoring",
        ]

        for keyword in keywords_to_remove:
            cleaned_query = cleaned_query.replace(
                keyword,
                "",
            )

        return " ".join(
            cleaned_query.split()
        )

    def _normalize_jobs(
        self,
        raw_jobs,
    ) -> list[Job]:

        normalized_jobs = []

        for raw_job in raw_jobs:

            company = raw_job.get(
                "company",
                {},
            ).get(
                "display_name",
                "Unknown Company",
            )

            location = raw_job.get(
                "location",
                {},
            ).get(
                "display_name",
                "Not specified",
            )

            description = raw_job.get(
                "description",
                "",
            )

            if not description.strip():
                continue

            job = Job(
                job_id=0,
                title=raw_job.get(
                    "title",
                    "Unknown Title",
                ),
                company=company,
                location=location,
                description=description,
                skills=[],
                responsibilities=[],
                experience_required=None,
                certification_requirement=None,
                posted_date=raw_job.get(
                    "created",
                ),
                source="Adzuna",
                job_url=raw_job.get(
                    "redirect_url",
                ),
                is_active=True,
                status="NEW",
            )

            normalized_jobs.append(job)

        return normalized_jobs