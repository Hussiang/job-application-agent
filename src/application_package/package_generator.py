def generate_application_package(result):
    job = result["job"]

    tailoring = result["resume_tailoring"]

    return {
        "job_id": job.job_id,
        "title": job.title,
        "company": job.company,
        "recommendation": result["recommendation"],
        "priority": result["application_priority"],
        "skills_to_emphasize": (
            tailoring["skills_to_emphasize"]
        ),
        "responsibilities_to_emphasize": (
            tailoring["responsibilities_to_emphasize"]
        ),
        "missing_skills": tailoring["missing_skills"],
    }