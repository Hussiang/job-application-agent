import re
from src.jobs.job import Job
def extract_skills(description, known_skills):
    if not isinstance(description, str):
        return []

    description = description.lower()
    matched_skills = []

    for skill in known_skills or []:
        if not isinstance(skill, str) or not skill.strip():
            continue

        skill = skill.strip()
        pattern = (
            r"(?<![a-zA-Z0-9_])"
            + re.escape(skill.lower())
            + r"(?![a-zA-Z0-9_])"
        )

        if re.search(pattern, description):
            matched_skills.append(skill)

    return matched_skills

def extract_experience(description):
    if not isinstance(description, str):
        return None

    description = description.lower()

    range_match = re.search(
        r"(\d+)\s*(?:-|–|—|to)\s*(\d+)\s+years?",
        description,
    )
    if range_match:
        return int(range_match.group(1))

    patterns = [
        r"(\d+)\+?\s+years?\s+of\s+experience",
        r"minimum\s+of\s+(\d+)\s+years?",
        r"at\s+least\s+(\d+)\s+years?",
        r"(\d+)\+?\s+years?\s+experience",
    ]

    for pattern in patterns:
        match = re.search(pattern, description)
        if match:
            return int(match.group(1))

    return None

def extract_certification_requirement(description):
    if not isinstance(description, str):
        return None

    description = description.lower()

    negative_patterns = [
        r"\bno\s+(?:aws\s+)?certifications?\b",
        r"\bcertifications?\b[^.!?\n]{0,50}"
        r"\b(?:not required|not mandatory|isn't required|"
        r"aren't required|is not required|are not required)\b",
        r"\b(?:not required|not mandatory)\b"
        r"[^.!?\n]{0,50}\bcertifications?\b",
    ]

    if any(re.search(p, description) for p in negative_patterns):
        preferred = re.search(
            r"\bcertifications?\b[^.!?\n]{0,50}"
            r"\b(?:preferred|nice to have|plus)\b",
            description,
        )
        return "preferred" if preferred else None

    required_patterns = [
        r"\bcertifications?\b[^.!?\n]{0,80}\brequired\b",
        r"\bcertifications?\b[^.!?\n]{0,80}\bmandatory\b",
        r"\baws certified\b[^.!?\n]{0,80}\brequired\b",
    ]

    preferred_patterns = [
        r"\bcertifications?\b[^.!?\n]{0,80}\bpreferred\b",
        r"\bcertifications?\b[^.!?\n]{0,80}\bplus\b",
        r"\bcertifications?\b[^.!?\n]{0,80}\bnice to have\b",
        r"\baws certified\b[^.!?\n]{0,80}\bpreferred\b",
    ]

    if any(re.search(p, description) for p in required_patterns):
        return "required"

    if any(re.search(p, description) for p in preferred_patterns):
        return "preferred"

    return None

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