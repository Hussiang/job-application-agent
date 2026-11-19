import pytest

from src.jobs.job_parser import (
    extract_skills,
    extract_experience,
    extract_certification_requirement,
    extract_responsibilities,
    parse_job_description,
)


def test_extract_skills_matches_known_skills():
    result = extract_skills(
        "We use AWS, Docker and Kubernetes.",
        ["AWS", "Docker", "Kubernetes"],
    )

    assert result == ["AWS", "Docker", "Kubernetes"]


def test_extract_skills_does_not_match_partial_words():
    result = extract_skills(
        "The company has a strong ongoing engineering culture.",
        ["Go"],
    )

    assert result == []


@pytest.mark.parametrize(
    ("description", "expected"),
    [
        ("3 years of experience required", 3),
        ("Minimum of 4 years", 4),
        ("At least 5 years of experience", 5),
        ("4-6 years of experience", 4),
        ("No experience requirement mentioned", None),
    ],
)
def test_extract_experience(description, expected):
    assert extract_experience(description) == expected


@pytest.mark.parametrize(
    ("description", "expected"),
    [
        ("AWS certification is required", "required"),
        ("AWS certification is mandatory", "required"),
        ("AWS certification is preferred", "preferred"),
        ("AWS certification is not required", None),
        ("No certification requirement mentioned", None),
    ],
)
def test_extract_certification_requirement(description, expected):
    assert extract_certification_requirement(description) == expected


def test_extract_responsibilities():
    result = extract_responsibilities(
        "Responsibilities include deployment, monitoring "
        "and incident management."
    )

    assert "deployment" in result
    assert "monitoring" in result
    assert "incident management" in result


def test_parse_job_description_returns_job():
    job = parse_job_description(
        title="DevOps Engineer",
        company="Example Tech",
        description=(
            "AWS, Docker and Kubernetes experience. "
            "Minimum of 3 years of experience. "
            "Monitoring and deployment responsibilities."
        ),
        known_skills=["AWS", "Docker", "Kubernetes"],
    )

    assert job.title == "DevOps Engineer"
    assert job.company == "Example Tech"
    assert job.location == "Not specified"
    assert job.skills == ["AWS", "Docker", "Kubernetes"]
    assert job.experience_required == 3
    assert "monitoring" in job.responsibilities
    assert "deployment" in job.responsibilities
