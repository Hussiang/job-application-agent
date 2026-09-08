import os
import time

import requests
from dotenv import load_dotenv

from src.jobs.job import Job


load_dotenv()


class AdzunaJobSource:

    BASE_URL = (
        "https://api.adzuna.com/v1/api/jobs/in/search/1"
    )

    def __init__(
        self,
        locations,
        results_per_search=10,
        max_retries=3,
        retry_delay=2,
    ):
        self.locations = locations
        self.results_per_search = results_per_search
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.app_id = os.getenv(
            "ADZUNA_APP_ID"
        )

        self.app_key = os.getenv(
            "ADZUNA_APP_KEY"
        )

        if not self.app_id:
            raise ValueError(
                "ADZUNA_APP_ID is not configured."
            )

        if not self.app_key:
            raise ValueError(
                "ADZUNA_APP_KEY is not configured."
            )

    def search(
        self,
        query: str,
    ) -> list[Job]:

        location = self._extract_location(
            query
        )

        search_term = self._build_search_term(
            query,
            location,
        )

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": search_term,
            "results_per_page": self.results_per_search,
            "content-type": "application/json",
        }

        if location:
            params["where"] = location

        for attempt in range(
            1,
            self.max_retries + 1,
        ):

            try:
                response = requests.get(
                    self.BASE_URL,
                    params=params,
                    timeout=20,
                )

                if response.status_code == 503:

                    print(
                        f"Adzuna temporarily unavailable "
                        f"(attempt {attempt}/"
                        f"{self.max_retries})"
                    )

                    if attempt < self.max_retries:
                        time.sleep(
                            self.retry_delay
                            * attempt
                        )

                        continue

                    print(
                        "Skipping query after "
                        "repeated 503 errors."
                    )

                    return []

                response.raise_for_status()

                data = response.json()

                return self._normalize_jobs(
                    data.get(
                        "results",
                        [],
                    )
                )

            except requests.RequestException as error:

                print(
                    f"Adzuna request failed "
                    f"(attempt {attempt}/"
                    f"{self.max_retries}): "
                    f"{error}"
                )

                if attempt < self.max_retries:

                    time.sleep(
                        self.retry_delay
                        * attempt
                    )

                    continue

                print(
                    "Skipping query after "
                    "repeated request failures."
                )

                return []

        return []

    def _extract_location(
        self,
        query: str,
    ) -> str | None:

        query_lower = query.lower()

        for location in self.locations:

            if location.lower() in query_lower:
                return location

        return None

    def _build_search_term(
        self,
        query: str,
        location: str | None,
    ) -> str:

        search_term = query

        if location:
            search_term = search_term.replace(
                location,
                "",
            )

            search_term = search_term.replace(
                location.lower(),
                "",
            )

        search_keywords = [
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

        for keyword in search_keywords:

            search_term = search_term.replace(
                keyword,
                "",
            )

            search_term = search_term.replace(
                keyword.lower(),
                "",
            )

        return " ".join(
            search_term.split()
        ).strip()

    def _normalize_jobs(
        self,
        results,
    ) -> list[Job]:

        jobs = []

        for result in results:

            title = (
                result.get("title")
                or "Untitled Job"
            )

            company_data = result.get(
                "company",
                {},
            )

            company = (
                company_data.get("display_name")
                if isinstance(
                    company_data,
                    dict,
                )
                else str(company_data)
            )

            company = (
                company
                or "Unknown Company"
            )

            location_data = result.get(
                "location",
                {},
            )

            location = (
                location_data.get("display_name")
                if isinstance(
                    location_data,
                    dict,
                )
                else str(location_data)
            )

            location = (
                location
                or "Not specified"
            )

            description = (
                result.get("description")
                or ""
            )

            job_url = (
                result.get("redirect_url")
                or result.get("url")
            )

            posted_date = (
                result.get("created")
            )

            job = Job(
                job_id=0,
                title=title,
                company=company,
                location=location,
                description=description,
                skills=[],
                responsibilities=[],
                experience_required=None,
                certification_requirement=None,
                posted_date=posted_date,
                source="Adzuna",
                job_url=job_url,
            )

            jobs.append(job)

        return jobs