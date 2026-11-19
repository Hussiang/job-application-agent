import re

from src.core.skill_normalizer import normalize_skill
from src.jobs.job import Job

def _contains_term(text, term):
    """Match a complete term rather than an accidental substring."""
    return bool(re.search(rf"\b{re.escape(term.lower())}\b", text.lower()))


def _seniority_keywords(scoring):
    return (
        "senior",
        "lead",
        "principal",
        "staff",
        "architect",
        "manager",
    )


def calculate_role_score(job_title, profile, scoring):
    title = (job_title or "").strip().lower()

    if any(_contains_term(title, keyword) for keyword in _seniority_keywords(scoring)):
        return scoring["role_match"]["related_role"]

    high_priority_roles = profile["target_roles"]["high_priority"]
    medium_priority_roles = profile["target_roles"]["medium_priority"]

    if any(_contains_term(title, role) for role in high_priority_roles):
        return scoring["role_match"]["high_priority"]

    if any(_contains_term(title, role) for role in medium_priority_roles):
        return scoring["role_match"]["medium_priority"]

    related_title_keywords = scoring.get(
        "related_title_keywords",
        (
            "kubernetes", "docker", "container", "infrastructure",
            "systems", "system", "operations", " sre ",
        ),
    )
    if any(_contains_term(title, keyword.strip()) for keyword in related_title_keywords):
        return scoring["role_match"].get("related_role", 10)

    return scoring["role_match"].get("unrelated_role", 0)


def _candidate_skill_evidence(profile):
    """Return normalized skills mapped to their strongest declared evidence tier."""
    evidence = profile.get("skill_evidence")
    if not evidence:
        # Backward compatibility for profiles created before evidence tiers.
        return {
            normalize_skill(skill): "professional"
            for skills in profile.get("skills", {}).values()
            for skill in skills
            if normalize_skill(skill)
        }

    evidence_rank = {
        "collaborative_exposure": 1,
        "personal_project": 2,
        "professional": 3,
    }
    result = {}
    for tier, skills in evidence.items():
        if tier not in evidence_rank:
            continue
        for skill in skills or []:
            normalized = normalize_skill(skill)
            if normalized and evidence_rank[tier] > evidence_rank.get(result.get(normalized), 0):
                result[normalized] = tier
    return result


def calculate_skill_score(job_skills, profile, scoring):
    evidence_by_skill = _candidate_skill_evidence(profile)
    core_skills = {
        normalize_skill(skill)
        for skill in scoring.get("core_skills", [])
        if normalize_skill(skill)
    }

    core_weight = scoring["weights"]["core_skill_weight"]
    supporting_weight = scoring["weights"]["supporting_skill_weight"]
    evidence_multipliers = scoring.get(
        "evidence_multipliers",
        {"professional": 1.0, "personal_project": 1.0, "collaborative_exposure": 1.0},
    )

    # Duplicate aliases in a job description must not inflate the score.
    unique_job_skills = []
    seen = set()
    for skill in job_skills or []:
        normalized = normalize_skill(skill)
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique_job_skills.append((skill, normalized))

    matched_skills = []
    matched_weight = 0.0
    total_weight = 0.0

    for original_skill, normalized_skill in unique_job_skills:
        base_weight = core_weight if normalized_skill in core_skills else supporting_weight
        total_weight += base_weight

        evidence_tier = evidence_by_skill.get(normalized_skill)
        if evidence_tier:
            matched_skills.append(original_skill)
            multiplier = evidence_multipliers.get(evidence_tier, 0.0)
            matched_weight += base_weight * multiplier

    if not unique_job_skills or total_weight == 0:
        return 0, matched_skills

    score = (matched_weight / total_weight) * scoring["weights"]["skill_match"]
    return round(score, 2), matched_skills


def calculate_experience_score(
    job_experience,
    profile,
    scoring
):
    preferred_maximum = (
        profile["job_preferences"]["experience_range"]
        ["preferred_maximum_years"]
    )

    # Missing experience information should not earn or lose points.
    if job_experience is None:
        return 0

    if job_experience <= preferred_maximum:
        return scoring["experience_match"]["within_preferred_range"]

    if job_experience <= preferred_maximum + 2:
        return scoring["experience_match"][
            "slightly_above_preferred"
        ]

    return scoring["experience_match"][
        "significantly_above_preferred"
    ]


def calculate_responsibility_score(
    job_description,
    profile,
    scoring
):
    description = job_description.lower()

    candidate_keywords = [
        keyword.lower()
        for keyword in profile["experience_keywords"]
    ]

    matched_keywords = [
        keyword
        for keyword in candidate_keywords
        if keyword in description
    ]

    match_count = len(matched_keywords)

    if match_count == 0:
        score = 0
    elif match_count == 1:
        score = 3
    elif match_count == 2:
        score = 6
    elif match_count == 3:
        score = 8
    else:
        score = scoring["weights"]["responsibilities_match"]

    return score, matched_keywords


def calculate_penalty(
    job_title,
    job_experience,
    profile,
    scoring
):
    title = (job_title or "").strip().lower()
    penalty = 0
    penalty_keys = {
        "senior": "senior_role",
        "lead": "lead_role",
        "principal": "principal_role",
        "staff": "staff_role",
        "architect": "architect_role",
        "manager": "manager_role",
    }

    for keyword, config_key in penalty_keys.items():
        if _contains_term(title, keyword):
            penalty += scoring["penalties"].get(config_key, 0)

    preferred_maximum = (
        profile["job_preferences"]["experience_range"]["preferred_maximum_years"]
    )
    if job_experience is not None and job_experience > preferred_maximum + 2:
        penalty += scoring["penalties"]["experience_far_above_profile"]

    return penalty


def calculate_certification_score(
    job: Job,
    profile,
    scoring
):
    requirement = (
        job.certification_requirement or "none"
    ).lower()

    candidate_certifications = [
        certification.lower()
        for certification in profile.get(
            "certifications",
            []
        )
    ]

    has_aws_certification = any(
        "aws" in certification
        for certification in candidate_certifications
    )

    if not has_aws_certification:
        return scoring["certification_match"][
            "no_certification_match"
        ]

    if requirement == "required":
        return scoring["certification_match"][
            "aws_required_or_preferred"
        ]

    if requirement == "preferred":
        return scoring["certification_match"][
            "aws_relevant"
        ]

    return scoring["certification_match"][
        "no_certification_match"
    ]


def calculate_missing_skills(job_skills, profile):
    candidate_skills = {
        normalize_skill(skill)
        for skills in profile.get("skills", {}).values()
        for skill in skills
        if normalize_skill(skill)
    }
    # Evidence tiers are authoritative when present, including project-only skills.
    candidate_skills.update(_candidate_skill_evidence(profile).keys())

    missing_skills = []
    seen = set()
    for skill in job_skills or []:
        normalized = normalize_skill(skill)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        if normalized not in candidate_skills:
            missing_skills.append(skill)

    return missing_skills


def calculate_skill_summary(
    job_skills,
    matched_skills,
    skill_score=None,
    skill_score_maximum=None,
):
    unique_required = {
        normalize_skill(skill)
        for skill in (job_skills or [])
        if normalize_skill(skill)
    }
    unique_matched = {
        normalize_skill(skill)
        for skill in (matched_skills or [])
        if normalize_skill(skill)
    }
    total_required = len(unique_required)
    total_matched = len(unique_matched & unique_required)

    # Coverage answers "does the profile list this skill?".
    # Evidence strength separately discounts project/collaborative exposure.
    coverage_percentage = (
        (total_matched / total_required) * 100
        if total_required else 0
    )
    evidence_percentage = (
        (skill_score / skill_score_maximum) * 100
        if skill_score is not None and skill_score_maximum
        else coverage_percentage
    )

    return {
        "matched": total_matched,
        "required": total_required,
        "percentage": round(coverage_percentage, 2),
        "coverage_percentage": round(coverage_percentage, 2),
        "evidence_strength_percentage": round(evidence_percentage, 2),
    }


def check_job_eligibility(job: Job, profile):
    reasons = []
    major_mismatch = False
    title = (job.title or "").strip().lower()

    for keyword in _seniority_keywords({}):
        if _contains_term(title, keyword):
            reasons.append(f"{keyword.title()}-level role")
            major_mismatch = True

    preferred_maximum = (
        profile["job_preferences"]["experience_range"]["preferred_maximum_years"]
    )
    job_experience = job.experience_required

    if job_experience is not None:
        if job_experience > preferred_maximum + 2:
            reasons.append(f"Requires {job_experience}+ years of experience")
            major_mismatch = True
        elif job_experience > preferred_maximum:
            reasons.append(
                f"Experience slightly above preferred range ({job_experience} years)"
            )

    if major_mismatch:
        status = "NOT ELIGIBLE"
    elif reasons:
        status = "BORDERLINE"
    else:
        status = "ELIGIBLE"

    return {"status": status, "reasons": reasons}


def calculate_bonus_score(
    job: Job,
    profile,
    scoring
):
    bonus_keywords = [
        keyword.lower()
        for keyword in scoring["bonus_keywords"]
    ]

    job_text = " ".join(
    job.skills
).lower()

    job_text += " " + job.description.lower()

    matched_bonus_keywords = [
        keyword
        for keyword in bonus_keywords
        if keyword in job_text
    ]

    if not bonus_keywords:
        return 0, matched_bonus_keywords

    match_percentage = (
        len(matched_bonus_keywords)
        / len(bonus_keywords)
    )

    bonus_score = (
        match_percentage
        * scoring["weights"]["bonus"]
    )

    return round(
        bonus_score,
        2
    ), matched_bonus_keywords


def get_recommendation(
    score,
    eligibility,
    skill_percentage
):
    if eligibility["status"] == "NOT ELIGIBLE":
        return "SKIP"

    if (
        score >= 80
        and skill_percentage >= 80
        and eligibility["status"] == "ELIGIBLE"
    ):
        return "STRONG APPLY"

    if score >= 65:
        return "APPLY"

    if score >= 45:
        return "CONSIDER"

    return "SKIP"
def generate_fit_explanation(
    job,
    result
):
    strengths = []
    concerns = []

    breakdown = result["breakdown"]
    skill_summary = result["skill_summary"]
    eligibility = result["eligibility"]

    # Role alignment
    if breakdown["role"] >= 30:
        strengths.append(
            "Strong role alignment"
        )
    elif breakdown["role"] >= 20:
        strengths.append(
            "Relevant role alignment"
        )
    else:
        concerns.append(
            "Role is outside the primary target"
        )

    # Skills
    if skill_summary["coverage_percentage"] == 100:
        strengths.append("All required skills are present in the profile")
    elif skill_summary["coverage_percentage"] >= 80:
        strengths.append(
            f"Strong skill coverage ({skill_summary['coverage_percentage']}%)"
        )
    else:
        concerns.append(
            f"Skill coverage is {skill_summary['coverage_percentage']}%"
        )

    if skill_summary["evidence_strength_percentage"] < skill_summary["coverage_percentage"]:
        concerns.append(
            "Some matched skills have project-based or collaborative evidence "
            f"(evidence strength: {skill_summary['evidence_strength_percentage']}%)"
        )

    # Missing skills
    missing_skills = result["missing_skills"]

    if missing_skills:
        concerns.append(
            "Missing skills: "
            + ", ".join(missing_skills)
        )

    # Responsibilities
    matched_responsibilities = (
        result["matched_responsibilities"]
    )

    if len(matched_responsibilities) >= 3:
        strengths.append(
            "Strong responsibility alignment"
        )
    elif len(matched_responsibilities) > 0:
        strengths.append(
            "Some relevant responsibility alignment"
        )
    else:
        concerns.append(
            "No relevant responsibility matches"
        )

    # Certification
    if breakdown["certification"] >= 10:
        strengths.append(
            "Relevant AWS certification"
        )

    # Eligibility
    if eligibility["status"] != "ELIGIBLE":
        concerns.extend(
            eligibility["reasons"]
        )

    # Final verdict
    recommendation = result["recommendation"]

    if (
        recommendation == "STRONG APPLY"
        and eligibility["status"] == "ELIGIBLE"
    ):
        verdict = (
            "Strong overall fit. Prioritize this application."
        )

    elif (
    recommendation == "APPLY"
    and eligibility["status"] == "ELIGIBLE"
):
     if missing_skills:
        verdict = (
            "Good match. Apply, but review the "
            "identified skill gaps."
        )
     else:
        verdict = (
            "Good overall fit. Your profile matches "
            "the required skills."
        )

    elif eligibility["status"] == "BORDERLINE":
        verdict = (
            "Possible fit, but role level or experience "
            "requirements need careful consideration."
        )

    else:
        verdict = (
            "Technical overlap exists, but the overall role "
            "is not a strong fit."
        )

    return {
        "strengths": strengths,
        "concerns": concerns,
        "verdict": verdict
    }
def get_application_priority(result):
    score = result["score"]
    eligibility = result["eligibility"]["status"]
    recommendation = result["recommendation"]

    if eligibility == "NOT ELIGIBLE":
        return "SKIP"

    if recommendation == "STRONG APPLY" and score >= 85:
        return "HIGH"

    if recommendation in ["STRONG APPLY", "APPLY"]:
        return "MEDIUM"

    return "LOW"


def get_recommended_action(result):
    priority = result["application_priority"]
    missing_skills = result["missing_skills"]

    if priority == "HIGH":
        return "Apply immediately and tailor your resume."

    if priority == "MEDIUM":
        if missing_skills:
            return (
                "Apply after tailoring your resume and reviewing "
                "the identified skill gaps."
            )

        return "Apply after tailoring your resume to the job."

    if priority == "LOW":
        return (
            "Apply only if the role aligns with your broader "
            "career goals."
        )

    return (
        "Skip this role unless you have additional relevant "
        "experience not included in your profile."
    )


def generate_resume_tailoring(result):
    skills_to_emphasize = result["matched_skills"]

    responsibilities_to_emphasize = (
        result["matched_responsibilities"]
    )

    missing_skills = result["missing_skills"]

    suggestions = []

    if skills_to_emphasize:
        suggestions.append(
            "Emphasize matched skills: "
            + ", ".join(skills_to_emphasize)
        )

    if responsibilities_to_emphasize:
        suggestions.append(
            "Highlight relevant experience: "
            + ", ".join(responsibilities_to_emphasize)
        )

    if missing_skills:
        suggestions.append(
            "Do not claim these skills unless you actually have them: "
            + ", ".join(missing_skills)
        )

    return {
        "skills_to_emphasize": skills_to_emphasize,
        "responsibilities_to_emphasize": (
            responsibilities_to_emphasize
        ),
        "missing_skills": missing_skills,
        "suggestions": suggestions
    }

def rank_job(
    job: Job,
    profile,
    scoring
):
    eligibility = check_job_eligibility(
        job,
        profile
    )

    role_score = calculate_role_score(
        job.title,
        profile,
        scoring
    )

    skill_score, matched_skills = calculate_skill_score(
        job.skills,
        profile,
        scoring
    )

    missing_skills = calculate_missing_skills(
        job.skills,
        profile
    )

    skill_summary = calculate_skill_summary(
        job.skills,
        matched_skills,
        skill_score=skill_score,
        skill_score_maximum=scoring["weights"]["skill_match"],
    )

    responsibility_score, matched_responsibilities = (
        calculate_responsibility_score(
            job.description,
            profile,
            scoring
        )
    )

    experience_score = calculate_experience_score(
        job.experience_required,
        profile,
        scoring
    )

    certification_score = calculate_certification_score(
        job,
        profile,
        scoring
    )

    bonus_score, matched_bonus_keywords = (
        calculate_bonus_score(
            job,
            profile,
            scoring
        )
    )

    penalty = calculate_penalty(
        job.title,
        job.experience_required,
        profile,
        scoring
    )

    total_score = (
        role_score
        + skill_score
        + responsibility_score
        + experience_score
        + certification_score
        + bonus_score
        + penalty
    )

    recommendation = get_recommendation(
        total_score,
        eligibility,
        skill_summary["evidence_strength_percentage"]
    )

    result = {
        "job": job,
        "score": round(max(total_score, 0), 2),
        "recommendation": recommendation,
        "eligibility": eligibility,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_summary": skill_summary,
        "matched_responsibilities": matched_responsibilities,
        "matched_bonus_keywords": matched_bonus_keywords,

        "breakdown": {
            "role": role_score,
            "skills": skill_score,
            "responsibilities": responsibility_score,
            "experience": experience_score,
            "certification": certification_score,
            "bonus": bonus_score,
            "penalty": penalty
        }
    }

    result["fit_explanation"] = (
        generate_fit_explanation(
            job,
            result
        )
    )

    result["application_priority"] = (
        get_application_priority(result)
    )

    result["recommended_action"] = (
        get_recommended_action(result)
    )

    result["resume_tailoring"] = (
        generate_resume_tailoring(result)
    )

    return result