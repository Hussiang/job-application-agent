
from src.discovery.search_query_builder import build_search_queries


def test_builds_queries_for_high_and_medium_priority_roles():
    profile = {
        "target_roles": {
            "high_priority": ["DevOps Engineer"],
            "medium_priority": ["Site Reliability Engineer"],
        },
        "job_discovery": {
            "locations": ["Hyderabad"],
            "search_keywords": [],
        },
    }

    queries = build_search_queries(profile)

    assert "DevOps Engineer Hyderabad" in queries
    assert "Site Reliability Engineer Hyderabad" in queries
    assert len(queries) == 2


def test_builds_grouped_technical_searches_for_each_location():
    profile = {
        "target_roles": {
            "high_priority": [],
            "medium_priority": [],
        },
        "job_discovery": {
            "locations": ["Hyderabad", "Remote"],
            "search_keywords": [
                "AWS",
                "Linux",
                "Docker",
                "Kubernetes",
            ],
        },
    }

    queries = build_search_queries(profile)

    assert "AWS Linux Docker Hyderabad" in queries
    assert "Kubernetes Hyderabad" in queries
    assert "AWS Linux Docker Remote" in queries
    assert "Kubernetes Remote" in queries
    assert len(queries) == 4


def test_deduplicates_queries_case_insensitively():
    profile = {
        "target_roles": {
            "high_priority": ["DevOps Engineer"],
            "medium_priority": ["devops engineer"],
        },
        "job_discovery": {
            "locations": ["Hyderabad"],
            "search_keywords": [],
        },
    }

    queries = build_search_queries(profile)

    assert queries == ["DevOps Engineer Hyderabad"]


def test_handles_missing_configuration():
    assert build_search_queries({}) == []
