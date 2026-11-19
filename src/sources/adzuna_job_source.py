import os
import re
import time
from dataclasses import dataclass, field

import requests
from dotenv import load_dotenv

from src.jobs.job import Job


load_dotenv()


@dataclass
class JobSearchResult:
    """Explicit outcome of one source query; empty success differs from failure."""
    query: str
    success: bool
    jobs: list[Job] = field(default_factory=list)
    error: str | None = None


class AdzunaJobSource:
    BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"

    def __init__(
        self,
        locations,
        results_per_search=10,
        max_retries=3,
        retry_delay=2,
        request_interval=1.0,
    ):
        self.locations = locations
        self.results_per_search = results_per_search
        self.max_retries = max(1, int(max_retries))
        self.retry_delay = retry_delay
        self.request_interval = request_interval
        self._last_request_at = None

        self.app_id = os.getenv("ADZUNA_APP_ID")
        self.app_key = os.getenv("ADZUNA_APP_KEY")

        if not self.app_id:
            raise ValueError("ADZUNA_APP_ID is not configured.")
        if not self.app_key:
            raise ValueError("ADZUNA_APP_KEY is not configured.")

    def _wait_for_request_interval(self):
        if self._last_request_at is not None:
            elapsed = time.monotonic() - self._last_request_at
            remaining = self.request_interval - elapsed
            if remaining > 0:
                time.sleep(remaining)
        self._last_request_at = time.monotonic()

    def _failure(self, query: str, message: str) -> JobSearchResult:
        print(f"Adzuna search failed for '{query}': {message}")
        return JobSearchResult(query=query, success=False, error=message)

    def search(self, query: str) -> JobSearchResult:
        location = self._extract_location(query)
        search_term = self._build_search_term(query, location)

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": search_term,
            "results_per_page": self.results_per_search,
            "content-type": "application/json",
        }
        if location:
            params["where"] = location

        for attempt in range(1, self.max_retries + 1):
            self._wait_for_request_interval()
            try:
                response = requests.get(
                    self.BASE_URL,
                    params=params,
                    timeout=20,
                )
                status = response.status_code

                if status == 429 or 500 <= status <= 599:
                    if attempt == self.max_retries:
                        return self._failure(
                            query,
                            f"HTTP {status} after {attempt} attempts",
                        )

                    retry_after = response.headers.get("Retry-After")
                    try:
                        delay = float(retry_after)
                    except (TypeError, ValueError):
                        delay = self.retry_delay * attempt
                    delay = max(0, min(delay, 60))
                    print(
                        f"Adzuna returned HTTP {status}. Retrying in "
                        f"{delay:.1f} seconds ({attempt}/{self.max_retries})."
                    )
                    time.sleep(delay)
                    continue

                response.raise_for_status()

                try:
                    data = response.json()
                except ValueError:
                    return self._failure(query, "Invalid JSON response")

                if not isinstance(data, dict):
                    return self._failure(query, "Unexpected response format")

                results = data.get("results")
                if not isinstance(results, list):
                    return self._failure(query, "Missing valid results list")

                return JobSearchResult(
                    query=query,
                    success=True,
                    jobs=self._normalize_jobs(results),
                )

            except requests.HTTPError as error:
                return self._failure(query, f"HTTP request rejected: {error}")
            except requests.RequestException as error:
                if attempt == self.max_retries:
                    return self._failure(
                        query,
                        f"Request failed after {attempt} attempts: {error}",
                    )
                delay = self.retry_delay * attempt
                print(
                    f"Adzuna request error. Retrying in {delay} seconds "
                    f"({attempt}/{self.max_retries})."
                )
                time.sleep(delay)

        return self._failure(query, "Retry loop ended without a response")

    def _extract_location(self, query: str) -> str | None:
        query_lower = query.lower()
        for location in self.locations:
            if location.lower() in query_lower:
                return location
        return None

    def _build_search_term(self, query: str, location: str | None) -> str:
        search_term = query
        if location:
            search_term = re.sub(
                re.escape(location),
                "",
                search_term,
                flags=re.IGNORECASE,
            )
        return " ".join(search_term.split()).strip()

    def _normalize_jobs(self, results) -> list[Job]:
        jobs = []
        for result in results:
            if not isinstance(result, dict):
                continue

            title = result.get("title") or "Untitled Job"
            company_data = result.get("company", {})
            company = (
                company_data.get("display_name")
                if isinstance(company_data, dict)
                else str(company_data)
            ) or "Unknown Company"

            location_data = result.get("location", {})
            location = (
                location_data.get("display_name")
                if isinstance(location_data, dict)
                else str(location_data)
            ) or "Not specified"

            job = Job(
                job_id=0,
                title=title,
                company=company,
                location=location,
                description=result.get("description") or "",
                skills=[],
                responsibilities=[],
                experience_required=None,
                certification_requirement=None,
                posted_date=result.get("created"),
                source="Adzuna",
                job_url=result.get("redirect_url") or result.get("url"),
            )
            jobs.append(job)
        return jobs
