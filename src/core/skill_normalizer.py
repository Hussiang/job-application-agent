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
}


def normalize_skill(skill):
    normalized = skill.strip().lower()

    return SKILL_ALIASES.get(
        normalized,
        normalized
    )