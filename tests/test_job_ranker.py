from src.jobs.job import Job
from src.jobs.job_parser import parse_job_description
from src.jobs.job_ranker import (
    calculate_experience_score,
    calculate_penalty,
    check_job_eligibility,
    calculate_role_score,
    calculate_skill_summary,
    rank_job,
)


PROFILE = {
    "job_preferences": {
        "experience_range": {
            "preferred_maximum_years": 4
        }
    }
}

SCORING = {
    "experience_match": {
        "within_preferred_range": 15,
        "slightly_above_preferred": 8,
        "significantly_above_preferred": 0,
    },
    "penalties": {
        "senior_role": -20,
        "lead_role": -25,
        "principal_role": -30,
        "architect_role": -25,
        "manager_role": -30,
        "experience_far_above_profile": -30,
    },
}


def create_job(experience):
    return Job(
        job_id=1,
        title="DevOps Engineer",
        company="Example Tech",
        location="Hyderabad",
        description="AWS and Docker experience required.",
        experience_required=experience,
    )


def test_experience_within_preferred_range():
    score = calculate_experience_score(3, PROFILE, SCORING)

    assert score == 15


def test_experience_slightly_above_preferred_range():
    score = calculate_experience_score(6, PROFILE, SCORING)

    assert score == 8


def test_experience_significantly_above_preferred_range():
    score = calculate_experience_score(8, PROFILE, SCORING)

    assert score == 0


def test_missing_experience_gets_no_experience_points():
    score = calculate_experience_score(None, PROFILE, SCORING)

    assert score == 0


def test_missing_experience_does_not_cause_penalty():
    penalty = calculate_penalty(
        "DevOps Engineer",
        None,
        PROFILE,
        SCORING,
    )

    assert penalty == 0


def test_missing_experience_does_not_make_job_ineligible():
    result = check_job_eligibility(
        create_job(None),
        PROFILE,
    )

    assert result["status"] == "ELIGIBLE"
    assert result["reasons"] == []


def test_excessive_experience_makes_job_ineligible():
    result = check_job_eligibility(
        create_job(8),
        PROFILE,
    )

    assert result["status"] == "NOT ELIGIBLE"
    assert "Requires 8+ years of experience" in result["reasons"]


def test_six_years_experience_is_borderline():
    result = check_job_eligibility(
        create_job(6),
        PROFILE,
    )

    assert result["status"] == "BORDERLINE"
    assert (
        "Experience slightly above preferred range (6 years)"
        in result["reasons"]
    )


def test_parsed_eight_year_requirement_makes_job_ineligible():
    job = parse_job_description(
        title="DevOps Engineer",
        company="Trigent Software Private Limited",
        description="Total experience: 8 years",
        known_skills=[],
    )

    result = check_job_eligibility(job, PROFILE)

    assert job.experience_required == 8
    assert result["status"] == "NOT ELIGIBLE"
    assert "Requires 8+ years of experience" in result["reasons"]


def test_staff_title_is_not_eligible():
    job = create_job(None)
    job.title = "Staff DevOps Engineer"

    result = check_job_eligibility(job, PROFILE)

    assert result["status"] == "NOT ELIGIBLE"
    assert "Staff-level role" in result["reasons"]


def test_seniority_matching_uses_word_boundaries():
    job = create_job(None)
    job.title = "Leadership Development Engineer"

    result = check_job_eligibility(job, PROFILE)

    assert result["status"] == "ELIGIBLE"


def test_evidence_tiers_change_skill_score():
    profile = {
        "skills": {
            "cloud": ["AWS", "Terraform", "Python"],
        },
        "skill_evidence": {
            "professional": ["AWS"],
            "personal_project": ["Python"],
            "collaborative_exposure": ["Terraform"],
        },
    }
    scoring = {
        "core_skills": ["AWS", "Terraform"],
        "weights": {
            "core_skill_weight": 2,
            "supporting_skill_weight": 1,
            "skill_match": 25,
        },
        "evidence_multipliers": {
            "professional": 1.0,
            "personal_project": 0.65,
            "collaborative_exposure": 0.40,
        },
    }

    from src.jobs.job_ranker import calculate_skill_score

    score, matched = calculate_skill_score(
        ["AWS", "Terraform", "Python"],
        profile,
        scoring,
    )

    # (2*1.0 + 2*0.4 + 1*0.65) / (2+2+1) * 25
    assert score == 17.25
    assert matched == ["AWS", "Terraform", "Python"]


def test_duplicate_normalized_job_skills_do_not_inflate_score():
    profile = {
        "skills": {"containers": ["Kubernetes"]},
        "skill_evidence": {"professional": ["Kubernetes"]},
    }
    scoring = {
        "core_skills": ["Kubernetes"],
        "weights": {
            "core_skill_weight": 2,
            "supporting_skill_weight": 1,
            "skill_match": 25,
        },
        "evidence_multipliers": {"professional": 1.0},
    }

    from src.jobs.job_ranker import calculate_skill_score

    score, matched = calculate_skill_score(
        ["Kubernetes", "k8s", "KUBERNETES"],
        profile,
        scoring,
    )

    assert score == 25
    assert matched == ["Kubernetes"]


def test_legacy_profile_without_evidence_map_remains_supported():
    profile = {"skills": {"cloud": ["AWS"]}}
    scoring = {
        "core_skills": ["AWS"],
        "weights": {
            "core_skill_weight": 2,
            "supporting_skill_weight": 1,
            "skill_match": 25,
        },
    }

    from src.jobs.job_ranker import calculate_skill_score

    score, matched = calculate_skill_score(["AWS"], profile, scoring)

    assert score == 25
    assert matched == ["AWS"]



# End-to-end ranking scenarios: intentionally exercise the configured profile
# and scoring rules rather than testing isolated scoring helpers only.
def _load_ranking_config():
    import yaml
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    profile = yaml.safe_load((root / "config/profile.yaml").read_text())
    scoring = yaml.safe_load((root / "config/scoring.yaml").read_text())
    return profile, scoring


def _scenario_job(title, skills, description, experience, certification=None):
    return Job(
        job_id=900,
        title=title,
        company="Scenario Test",
        location="Hyderabad",
        description=description,
        skills=skills,
        experience_required=experience,
        certification_requirement=certification,
    )



def test_docker_and_kubernetes_remain_collaborative_exposure():
    from src.jobs.job_ranker import _candidate_skill_evidence

    profile, scoring = _load_ranking_config()
    evidence = _candidate_skill_evidence(profile)

    assert evidence["docker"] == "collaborative_exposure"
    assert evidence["kubernetes"] == "collaborative_exposure"

    job = _scenario_job(
        "DevOps Engineer",
        ["Docker", "Kubernetes"],
        "Container deployment and orchestration.",
        4,
    )

    result = rank_job(job, profile, scoring)

    assert result["skill_summary"]["matched"] == 2
    assert result["skill_summary"]["required"] == 2
    assert result["skill_summary"]["coverage_percentage"] == 100
    assert result["skill_summary"]["evidence_strength_percentage"] == 40

def test_scenario_1_aws_cloud_operations_is_strong_apply():
    profile, scoring = _load_ranking_config()
    job = _scenario_job(
        "AWS Cloud Operations Engineer",
        ["AWS", "EC2", "EKS", "IAM", "S3", "CloudWatch", "SQS", "SNS"],
        "Production Support, Incident Management, Root Cause Analysis, "
        "Troubleshooting, Monitoring, Automation, CI/CD, "
        "Infrastructure as Code.",
        4,
        "preferred",
    )

    result = rank_job(job, profile, scoring)

    assert result["eligibility"]["status"] == "ELIGIBLE"
    assert result["recommendation"] == "STRONG APPLY"
    assert result["skill_summary"]["coverage_percentage"] == 100
    assert result["score"] >= 80


def test_scenario_2_junior_devops_is_apply_with_full_coverage():
    profile, scoring = _load_ranking_config()
    job = _scenario_job(
        "Junior DevOps Engineer",
        ["AWS", "Docker", "Kubernetes", "Linux", "Terraform", "Jenkins"],
        "Production Support, Incident Troubleshooting, Deployment Support, "
        "Monitoring, Automation, CI/CD.",
        4,
    )

    result = rank_job(job, profile, scoring)

    assert result["eligibility"]["status"] == "ELIGIBLE"
    assert result["recommendation"] == "APPLY"
    assert result["skill_summary"]["matched"] == 6
    assert result["skill_summary"]["required"] == 6
    assert result["skill_summary"]["coverage_percentage"] == 100
    assert result["skill_summary"]["evidence_strength_percentage"] < 100


def test_scenario_3_kubernetes_docker_engineer_gets_related_role_credit():
    profile, scoring = _load_ranking_config()
    job = _scenario_job(
        "Kubernetes Docker Engineer",
        ["Docker", "Kubernetes", "AWS", "EKS"],
        "Troubleshooting production containers and monitoring deployments.",
        4,
    )

    result = rank_job(job, profile, scoring)

    assert result["eligibility"]["status"] == "ELIGIBLE"
    assert result["breakdown"]["role"] == scoring["role_match"]["related_role"]
    assert result["recommendation"] == "CONSIDER"
    assert result["score"] > 45


def test_scenario_4_senior_devops_eight_years_remains_rejected():
    profile, scoring = _load_ranking_config()
    job = _scenario_job(
        "Senior DevOps Engineer",
        ["AWS", "Docker", "Kubernetes", "Terraform"],
        "Production Support, Incident Management, Monitoring, "
        "Automation, CI/CD, Root Cause Analysis.",
        8,
        "required",
    )

    result = rank_job(job, profile, scoring)

    assert result["eligibility"]["status"] == "NOT ELIGIBLE"
    assert result["recommendation"] == "SKIP"
    assert result["application_priority"] == "SKIP"


def test_skill_summary_reports_coverage_separately_from_evidence_strength():
    summary = calculate_skill_summary(
        ["AWS", "Docker", "Kubernetes"],
        ["AWS", "Docker", "Kubernetes"],
        skill_score=17.5,
        skill_score_maximum=25,
    )

    assert summary["percentage"] == 100
    assert summary["coverage_percentage"] == 100
    assert summary["evidence_strength_percentage"] == 70


def test_unrelated_title_receives_zero_role_points():
    profile, scoring = _load_ranking_config()

    assert calculate_role_score("Java Backend Developer", profile, scoring) == 0


def test_related_title_matching_does_not_match_substrings():
    profile, scoring = _load_ranking_config()

    assert calculate_role_score("Dockerization Specialist", profile, scoring) == 0


def test_role_score_prefers_exact_target_over_related_keyword():
    profile, scoring = _load_ranking_config()

    assert calculate_role_score("Cloud Operations Engineer", profile, scoring) == 30
    assert calculate_role_score("Kubernetes Docker Engineer", profile, scoring) == 10


def test_seniority_and_experience_both_block_eligibility():
    profile, scoring = _load_ranking_config()
    job = _scenario_job(
        "Staff Cloud Engineer",
        ["AWS"],
        "Cloud operations",
        8,
    )

    result = rank_job(job, profile, scoring)

    assert result["eligibility"]["status"] == "NOT ELIGIBLE"
    assert any("Staff-level" in reason for reason in result["eligibility"]["reasons"])
    assert any("Requires 8+" in reason for reason in result["eligibility"]["reasons"])
