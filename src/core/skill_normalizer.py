SKILL_ALIASES = {
    "k8s": "kubernetes",
    "kubernetes": "kubernetes",
    "iac": "infrastructure as code",
    "infrastructure as code": "infrastructure as code",
    "amazon cloudwatch": "cloudwatch",
    "aws cloudwatch": "cloudwatch",
    "cloudwatch": "cloudwatch",
    "ci/cd pipelines": "ci/cd",
    "cicd": "ci/cd",
    "ci/cd": "ci/cd",
    "root cause analysis": "root cause analysis",
    "rca": "root cause analysis",
    "route53": "route 53",
    "route 53": "route 53",
}


def normalize_skill(skill):
    """Normalize a skill label safely for matching and deduplication."""
    if not isinstance(skill, str):
        return ""

    normalized = " ".join(skill.strip().lower().split())
    return SKILL_ALIASES.get(normalized, normalized)
