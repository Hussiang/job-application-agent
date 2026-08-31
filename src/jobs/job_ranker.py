from src.core.skill_normalizer import normalize_skill
from src.jobs.job import Job

def calculate_role_score(job_title, profile, scoring):
    job_title = job_title.lower()

    high_priority_roles = [
        role.lower()
        for role in profile["target_roles"]["high_priority"]
    ]

    medium_priority_roles = [
        role.lower()
        for role in profile["target_roles"]["medium_priority"]
    ]

    senior_keywords = [
        "senior",
        "lead",
        "principal",
        "staff",
        "architect",
        "manager"
    ]

    if any(
        keyword in job_title
        for keyword in senior_keywords
    ):
        return scoring["role_match"]["related_role"]

    for role in high_priority_roles:
        if role in job_title:
            return scoring["role_match"]["high_priority"]

    for role in medium_priority_roles:
        if role in job_title:
            return scoring["role_match"]["medium_priority"]

    return scoring["role_match"]["related_role"]


def calculate_skill_score(job_skills, profile, scoring):
    candidate_skills = []

    for category, skills in profile["skills"].items():
        candidate_skills.extend(skills)

    candidate_skills = [
        normalize_skill(skill)
        for skill in candidate_skills
    ]

    core_skills = [
        normalize_skill(skill)
        for skill in scoring["core_skills"]
    ]

    core_weight = scoring["weights"]["core_skill_weight"]
    supporting_weight = scoring["weights"]["supporting_skill_weight"]

    matched_skills = []
    matched_weight = 0
    total_weight = 0

    for skill in job_skills:
        normalized_skill = normalize_skill(skill)

        if normalized_skill in core_skills:
            total_weight += core_weight
        else:
            total_weight += supporting_weight

        if normalized_skill in candidate_skills:
            matched_skills.append(skill)

            if normalized_skill in core_skills:
                matched_weight += core_weight
            else:
                matched_weight += supporting_weight

    if not job_skills or total_weight == 0:
        return 0, matched_skills

    match_percentage = matched_weight / total_weight

    score = (
        match_percentage
        * scoring["weights"]["skill_match"]
    )

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
    penalty = 0

    title = job_title.lower()

    if "senior" in title:
        penalty += scoring["penalties"]["senior_role"]

    if "lead" in title:
        penalty += scoring["penalties"]["lead_role"]

    if "principal" in title:
        penalty += scoring["penalties"]["principal_role"]

    if "architect" in title:
        penalty += scoring["penalties"]["architect_role"]

    if "manager" in title:
        penalty += scoring["penalties"]["manager_role"]

    preferred_maximum = (
        profile["job_preferences"]["experience_range"]
        ["preferred_maximum_years"]
    )

    if job_experience > preferred_maximum + 2:
        penalty += scoring["penalties"][
            "experience_far_above_profile"
        ]

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
    candidate_skills = []

    for category, skills in profile["skills"].items():
        candidate_skills.extend(skills)

    normalized_candidate_skills = {
        normalize_skill(skill)
        for skill in candidate_skills
    }

    missing_skills = []

    for skill in job_skills:
        normalized_skill = normalize_skill(skill)

        if normalized_skill not in normalized_candidate_skills:
            missing_skills.append(skill)

    return missing_skills


def calculate_skill_summary(
    job_skills,
    matched_skills
):
    total_required = len(job_skills)
    total_matched = len(matched_skills)

    if total_required == 0:
        return {
            "matched": 0,
            "required": 0,
            "percentage": 0
        }

    percentage = (
        total_matched / total_required
    ) * 100

    return {
        "matched": total_matched,
        "required": total_required,
        "percentage": round(percentage, 2)
    }


def check_job_eligibility(job: Job, profile):
    reasons = []
    major_mismatch = False

    title = job.title.lower()

    major_role_keywords = [
        "senior",
        "lead",
        "principal",
        "architect",
        "manager"
    ]

    for keyword in major_role_keywords:
        if keyword in title:
            reasons.append(
                f"{keyword.title()}-level role"
            )
            major_mismatch = True

    preferred_maximum = (
        profile["job_preferences"]["experience_range"]
        ["preferred_maximum_years"]
    )

    job_experience = job.experience_required or 0

    if job_experience > preferred_maximum + 2:
        reasons.append(
            f"Requires {job_experience}+ years of experience"
        )
        major_mismatch = True

    elif job_experience > preferred_maximum:
        reasons.append(
            f"Experience slightly above preferred range "
            f"({job_experience} years)"
        )

    if major_mismatch:
        status = "NOT ELIGIBLE"
    elif reasons:
        status = "BORDERLINE"
    else:
        status = "ELIGIBLE"

    return {
        "status": status,
        "reasons": reasons
    }


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
    if skill_summary["percentage"] == 100:
        strengths.append(
            "All required skills matched"
        )
    elif skill_summary["percentage"] >= 80:
        strengths.append(
            f"Strong skill match "
            f"({skill_summary['percentage']}%)"
        )
    else:
        concerns.append(
            f"Skill match is only "
            f"{skill_summary['percentage']}%"
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
        matched_skills
    )

    responsibility_score, matched_responsibilities = (
        calculate_responsibility_score(
            job.description,
            profile,
            scoring
        )
    )

    experience_score = calculate_experience_score(
        job.experience_required or 0,
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
        job.experience_required or 0,
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
        skill_summary["percentage"]
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