
from src.sources.adzuna_job_source import AdzunaJobSource


def test_preserves_technical_keywords():
    source = object.__new__(AdzunaJobSource)

    result = source._build_search_term(
        "AWS Linux Docker Hyderabad",
        "Hyderabad",
    )

    assert result == "AWS Linux Docker"


def test_removes_location_case_insensitively():
    source = object.__new__(AdzunaJobSource)

    result = source._build_search_term(
        "AWS DevOps HYDERABAD",
        "Hyderabad",
    )

    assert result == "AWS DevOps"


def test_handles_query_without_location():
    source = object.__new__(AdzunaJobSource)

    result = source._build_search_term(
        "Kubernetes Terraform",
        None,
    )

    assert result == "Kubernetes Terraform"
