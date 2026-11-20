import copy
from src.discovery.job_discovery_service import JobDiscoveryService
from src.jobs.job import Job


def test_incomplete_duplicate_does_not_erase_existing_data():
    service = JobDiscoveryService(
        job_source=None,
        job_repository=None,
        profile={},
    )

    existing_job = Job(
        job_id=1,
        title="DevOps Engineer",
        company="Example Tech",
        location="Hyderabad",
        description="AWS, Docker and Kubernetes experience",
        skills=["AWS", "Docker", "Kubernetes"],
        responsibilities=["Deployment", "Monitoring"],
        experience_required=3,
        certification_requirement="preferred",
    )

    incoming_job = Job(
        job_id=0,
        title="DevOps Engineer",
        company="Example Tech",
        location="Not specified",
        description="Updated job listing",
        skills=[],
        responsibilities=[],
        experience_required=None,
        certification_requirement=None,
    )

    service._update_existing_job(
        existing_job,
        incoming_job,
        "2026-11-16T15:30:00",
    )

    assert existing_job.skills == ["AWS", "Docker", "Kubernetes"]
    assert existing_job.responsibilities == ["Deployment", "Monitoring"]
    assert existing_job.experience_required == 3
    assert existing_job.certification_requirement == "preferred"
    assert existing_job.location == "Hyderabad"
    assert existing_job.description == "Updated job listing"
    assert existing_job.last_seen == "2026-11-16T15:30:00"


def test_duplicate_job_accepts_meaningful_new_data():
    service = JobDiscoveryService(
        job_source=None,
        job_repository=None,
        profile={},
    )

    existing_job = Job(
        job_id=1,
        title="DevOps Engineer",
        company="Example Tech",
        location="Hyderabad",
        description="Old description",
        skills=["AWS"],
    )

    incoming_job = Job(
        job_id=0,
        title="DevOps Engineer",
        company="Example Tech",
        location="Bengaluru",
        description="Updated description",
        skills=["AWS", "Docker"],
    )

    service._update_existing_job(
        existing_job,
        incoming_job,
        "2026-11-16T15:30:00",
    )

    assert existing_job.location == "Bengaluru"
    assert existing_job.description == "Updated description"
    assert existing_job.skills == ["AWS", "Docker"]


def test_discovery_parses_job_description_before_filtering():
    class FakeJobSource:
        def search(self, query):
            return [Job(
                job_id=0,
                title="DevOps Engineer",
                company="Example Tech",
                location="Hyderabad",
                description=(
                    "We need AWS, Docker and Kubernetes experience. "
                    "Minimum of 3 years of experience. "
                    "Responsibilities include deployment, monitoring "
                    "and incident management."
                ),
                source="Adzuna",
                job_url="https://example.com/jobs/1",
            )]

    class FakeJobRepository:
        def get_next_job_id(self):
            return 1

        def find_duplicate(self, job, existing_jobs):
            return None

        def save_jobs(self, jobs):
            self.saved_jobs = jobs

    profile = {
        "skills": {
            "cloud": ["AWS"],
            "containers": ["Docker", "Kubernetes"],
        },
        "job_preferences": {
            "required_title_keywords": ["DevOps"],
            "exclude_title_keywords": ["Senior", "Lead"],
            "exclude_keywords": [],
        },
    }

    repository = FakeJobRepository()

    service = JobDiscoveryService(
        job_source=FakeJobSource(),
        job_repository=repository,
        profile=profile,
    )

    result = service.discover_jobs(
        queries=["DevOps Hyderabad"],
        existing_jobs=[],
    )

    assert len(result["new_jobs"]) == 1

    discovered_job = result["new_jobs"][0]

    assert discovered_job.skills == [
        "AWS",
        "Docker",
        "Kubernetes",
    ]
    assert "deployment" in discovered_job.responsibilities
    assert "monitoring" in discovered_job.responsibilities
    assert "incident management" in discovered_job.responsibilities
    assert discovered_job.experience_required == 3
    assert discovered_job.certification_requirement is None

    # Original source metadata must survive parsing.
    assert discovered_job.location == "Hyderabad"
    assert discovered_job.source == "Adzuna"
    assert discovered_job.job_url == "https://example.com/jobs/1"

    assert repository.saved_jobs == result["new_jobs"]


def test_discovery_reports_partial_failure_and_does_not_persist():
    from src.sources.adzuna_job_source import JobSearchResult

    class FakeSource:
        def search(self, query):
            if query == "failed":
                return JobSearchResult(
                    query=query,
                    success=False,
                    error="HTTP 503 after retries",
                )
            return JobSearchResult(
                query=query,
                success=True,
                jobs=[],
            )

    class FakeRepository:
        def __init__(self):
            self.saved = False

        def get_next_job_id(self):
            return 1

        def save_jobs(self, jobs):
            self.saved = True

        def find_duplicate(self, job, existing_jobs):
            return None

    repository = FakeRepository()
    service = JobDiscoveryService(FakeSource(), repository, {})
    result = service.discover_jobs(["successful-empty", "failed"], [])

    assert result["complete"] is False
    assert result["total_queries"] == 2
    assert result["successful_queries"] == 1
    assert result["failed_queries"] == [
        {"query": "failed", "error": "HTTP 503 after retries"}
    ]
    assert result["jobs_returned"] == 0
    assert repository.saved is False


def test_all_successful_empty_queries_are_complete():
    from src.sources.adzuna_job_source import JobSearchResult

    class FakeSource:
        def search(self, query):
            return JobSearchResult(query=query, success=True, jobs=[])

    class FakeRepository:
        def get_next_job_id(self):
            return 1

        def save_jobs(self, jobs):
            raise AssertionError("No changes should require persistence")

    service = JobDiscoveryService(FakeSource(), FakeRepository(), {})
    result = service.discover_jobs(["query-one", "query-two"], [])

    assert result["complete"] is True
    assert result["successful_queries"] == 2
    assert result["failed_queries"] == []



def test_successful_query_results_are_not_saved_when_another_query_fails():
    from src.sources.adzuna_job_source import JobSearchResult

    discovered = Job(
        job_id=0,
        title="DevOps Engineer",
        company="Example Tech",
        location="Hyderabad",
        description="AWS and Linux role",
        source="Adzuna",
        job_url="https://example.com/jobs/partial",
    )

    class FakeSource:
        def search(self, query):
            if query == "failed":
                return JobSearchResult(
                    query=query,
                    success=False,
                    error="Temporary API failure",
                )
            return JobSearchResult(
                query=query,
                success=True,
                jobs=[discovered],
            )

    class FakeRepository:
        def __init__(self):
            self.saved = False

        def get_next_job_id(self):
            return 1

        def find_duplicate(self, job, existing_jobs):
            return None

        def save_jobs(self, jobs):
            self.saved = True

    profile = {
        "skills": {"cloud": ["AWS", "Linux"]},
        "job_preferences": {
            "required_title_keywords": ["DevOps"],
            "exclude_title_keywords": [],
            "exclude_keywords": [],
        },
    }
    repository = FakeRepository()
    service = JobDiscoveryService(FakeSource(), repository, profile)

    result = service.discover_jobs(["successful", "failed"], [])

    assert result["complete"] is False
    assert len(result["new_jobs"]) == 1
    assert repository.saved is False


def test_incomplete_discovery_does_not_append_jobs_to_existing_collection():
    from src.sources.adzuna_job_source import JobSearchResult

    discovered = Job(
        job_id=0,
        title="DevOps Engineer",
        company="Example Tech",
        location="Hyderabad",
        description="AWS and Linux role",
        source="Adzuna",
        job_url="https://example.com/jobs/new",
    )

    class FakeSource:
        def search(self, query):
            if query == "failed":
                return JobSearchResult(
                    query=query,
                    success=False,
                    error="Temporary API failure",
                )
            return JobSearchResult(
                query=query,
                success=True,
                jobs=[discovered],
            )

    class FakeRepository:
        def get_next_job_id(self):
            return 10

        def find_duplicate(self, job, existing_jobs):
            return None

        def save_jobs(self, jobs):
            raise AssertionError("Incomplete discovery must not save")

    profile = {
        "skills": {"cloud": ["AWS", "Linux"]},
        "job_preferences": {
            "required_title_keywords": ["DevOps"],
            "exclude_title_keywords": [],
            "exclude_keywords": [],
        },
    }

    existing_jobs = []
    service = JobDiscoveryService(FakeSource(), FakeRepository(), profile)

    result = service.discover_jobs(
        ["successful", "failed"],
        existing_jobs,
    )

    assert result["complete"] is False
    assert len(result["new_jobs"]) == 1
    assert existing_jobs == []


def test_incomplete_discovery_does_not_modify_existing_duplicate():
    from src.sources.adzuna_job_source import JobSearchResult

    existing_job = Job(
        job_id=1,
        title="DevOps Engineer",
        company="Example Tech",
        location="Hyderabad",
        description="Original description",
        skills=["AWS"],
        last_seen="2026-11-01T10:00:00",
    )

    incoming_job = Job(
        job_id=0,
        title="DevOps Engineer",
        company="Example Tech",
        location="Bengaluru",
        description="Updated description",
        skills=["AWS", "Docker"],
        source="Adzuna",
    )

    class FakeSource:
        def search(self, query):
            if query == "failed":
                return JobSearchResult(
                    query=query,
                    success=False,
                    error="Temporary API failure",
                )
            return JobSearchResult(
                query=query,
                success=True,
                jobs=[incoming_job],
            )

    class FakeRepository:
        def get_next_job_id(self):
            return 2

        def find_duplicate(self, job, existing_jobs):
            for candidate in existing_jobs:
                if (
                    candidate.title == job.title
                    and candidate.company == job.company
                ):
                    return candidate

            return None

        def save_jobs(self, jobs):
            raise AssertionError("Incomplete discovery must not save")

    profile = {
        "skills": {"cloud": ["AWS", "Docker"]},
        "job_preferences": {
            "required_title_keywords": ["DevOps"],
            "exclude_title_keywords": [],
            "exclude_keywords": [],
        },
    }

    existing_jobs = [existing_job]
    original_state = existing_job.to_dict()

    service = JobDiscoveryService(FakeSource(), FakeRepository(), profile)

    result = service.discover_jobs(
        ["successful", "failed"],
        existing_jobs,
    )

    assert result["complete"] is False
    assert existing_job.to_dict() == original_state
    assert existing_jobs == [existing_job]


def test_persist_false_does_not_modify_existing_collection():
    discovered = Job(
        job_id=0,
        title="DevOps Engineer",
        company="Example Tech",
        location="Hyderabad",
        description="AWS and Linux role",
        source="Adzuna",
    )

    class FakeSource:
        def search(self, query):
            return [discovered]

    class FakeRepository:
        def get_next_job_id(self):
            return 10

        def find_duplicate(self, job, existing_jobs):
            return None

        def save_jobs(self, jobs):
            raise AssertionError("persist=False must not save")

    profile = {
        "skills": {"cloud": ["AWS", "Linux"]},
        "job_preferences": {
            "required_title_keywords": ["DevOps"],
            "exclude_title_keywords": [],
            "exclude_keywords": [],
        },
    }

    existing_jobs = []
    service = JobDiscoveryService(FakeSource(), FakeRepository(), profile)

    result = service.discover_jobs(
        ["successful"],
        existing_jobs,
        persist=False,
    )

    assert result["complete"] is True
    assert len(result["new_jobs"]) == 1
    assert existing_jobs == []

def test_failed_persistence_does_not_modify_existing_collection():
    discovered = Job(
        job_id=0,
        title="DevOps Engineer",
        company="Example Tech",
        location="Hyderabad",
        description="AWS and Linux role",
        source="Adzuna",
    )

    class FakeSource:
        def search(self, query):
            return [discovered]

    class FakeRepository:
        def get_next_job_id(self):
            return 10

        def find_duplicate(self, job, existing_jobs):
            return None

        def save_jobs(self, jobs):
            raise OSError("Simulated persistence failure")

    profile = {
        "skills": {"cloud": ["AWS", "Linux"]},
        "job_preferences": {
            "required_title_keywords": ["DevOps"],
            "exclude_title_keywords": [],
            "exclude_keywords": [],
        },
    }

    existing_job = Job(
        job_id=1,
        title="Cloud Engineer",
        company="Existing Tech",
        location="Hyderabad",
        description="Existing description",
    )
    existing_jobs = [existing_job]
    original_state = existing_job.to_dict()

    service = JobDiscoveryService(
        FakeSource(),
        FakeRepository(),
        profile,
    )

    import pytest

    with pytest.raises(OSError, match="Simulated persistence failure"):
        service.discover_jobs(["successful"], existing_jobs)

    assert len(existing_jobs) == 1
    assert existing_jobs[0] is existing_job
    assert existing_job.to_dict() == original_state


def test_discovery_does_not_mutate_source_job():
    discovered = Job(
        job_id=0,
        title="DevOps Engineer",
        company="Example Tech",
        location="Hyderabad",
        description="AWS and Linux role",
        source="Adzuna",
    )
    original_state = discovered.to_dict()

    class FakeSource:
        def search(self, query):
            return [discovered]

    class FakeRepository:
        def get_next_job_id(self):
            return 10

        def find_duplicate(self, job, existing_jobs):
            return None

        def save_jobs(self, jobs):
            pass

    profile = {
        "skills": {"cloud": ["AWS", "Linux"]},
        "job_preferences": {
            "required_title_keywords": ["DevOps"],
            "exclude_title_keywords": [],
            "exclude_keywords": [],
        },
    }

    service = JobDiscoveryService(
        FakeSource(),
        FakeRepository(),
        profile,
    )

    result = service.discover_jobs(["successful"], [])

    assert result["complete"] is True
    assert discovered.to_dict() == original_state
