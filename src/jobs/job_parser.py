import re
from src.jobs.job import Job
def extract_skills(description, known_skills):
    description = description.lower()

    matched_skills = []

    for skill in known_skills:
        if skill.lower() in description:
            matched_skills.append(skill)

    return matched_skills


def extract_experience(description):
    description = description.lower()

    patterns = [
        r"(\d+)\+?\s+years?\s+of\s+experience",
        r"minimum\s+of\s+(\d+)\s+years?",
        r"at\s+least\s+(\d+)\s+years?",
        r"(\d+)\+?\s+years?\s+experience"
    ]

    for pattern in patterns:
        match = re.search(pattern, description)

        if match:
            return int(match.group(1))

    return 0


def extract_certification_requirement(description):
    description = description.lower()

    required_patterns = [
        r"certification.*required",
        r"certification.*mandatory",
        r"aws.*certification.*required",
        r"aws certified.*required"
    ]

    preferred_patterns = [
        r"certification.*preferred",
        r"certification.*plus",
        r"certification.*nice to have",
        r"aws.*certification.*preferred",
        r"aws certified.*preferred"
    ]

    for pattern in required_patterns:
        if re.search(pattern, description):
            return "required"

    for pattern in preferred_patterns:
        if re.search(pattern, description):
            return "preferred"

    return "none"


def extract_responsibilities(description):
    description = description.lower()

    known_responsibilities = [
        "ci/cd",
        "deployment",
        "deployments",
        "monitoring",
        "incident management",
        "production support",
        "root cause analysis",
        "troubleshooting",
        "infrastructure as code",
        "automation",
        "cloud infrastructure",
        "kubernetes"
    ]

    matched_responsibilities = []

    for responsibility in known_responsibilities:
        if responsibility in description:
            matched_responsibilities.append(
                responsibility
            )

    return matched_responsibilities


def parse_job_description(
    title,
    company,
    description,
    known_skills
):
    skills = extract_skills(
        description,
        known_skills
    )

    experience_required = extract_experience(
        description
    )

    certification_requirement = (
        extract_certification_requirement(
            description
        )
    )

    responsibilities = extract_responsibilities(
        description
    )

    return Job(
    job_id=0,
    title=title,
    company=company,
    location="Not specified",
    description=description,
    skills=skills,
    responsibilities=responsibilities,
    experience_required=experience_required,
    certification_requirement=(
        certification_requirement
    ),
)