def show_ranking_summary(ranked_jobs):
    print("\nJOB RANKING SUMMARY\n")

    print(
        f"{'Rank':<6}"
        f"{'Job ID':<8}"
        f"{'Role':<28}"
        f"{'Company':<22}"
        f"{'Score':<10}"
        f"{'Status':<10}"
        f"{'Recommendation'}"
    )

    print("-" * 115)

    for position, result in enumerate(ranked_jobs, start=1):
        job = result["job"]

        print(
            f"{position:<6}"
            f"{job.job_id:<8}"
            f"{job.title:<28}"
            f"{job.company:<22}"
            f"{result['score']:<10}"
            f"{job.status:<14}"
            f"{result['recommendation']}"
        )


def show_job_details(ranked_jobs):
    print("\nJOB RANKINGS\n")

    for position, result in enumerate(ranked_jobs, start=1):
        job = result["job"]

        print(f"{position}. {job.title}")
        print(f"   Job ID: {job.job_id}")
        print(f"   Company: {job.company}")
        print(f"   Job Status: {job.status}")
        print(f"   Score: {result['score']}/100")

        print(
            f"   Recommendation: "
            f"{result['recommendation']}"
        )

        eligibility = result["eligibility"]

        print(
            f"   Eligibility: "
            f"{eligibility['status']}"
        )

        if eligibility["reasons"]:
            print(
                f"   Eligibility Reasons: "
                f"{', '.join(eligibility['reasons'])}"
            )

        print(
            f"   Role Score: "
            f"{result['breakdown']['role']}"
        )

        print(
            f"   Skill Score: "
            f"{result['breakdown']['skills']}"
        )

        print(
            f"   Responsibility Score: "
            f"{result['breakdown']['responsibilities']}"
        )

        print(
            f"   Experience Score: "
            f"{result['breakdown']['experience']}"
        )

        print(
            f"   Certification Score: "
            f"{result['breakdown']['certification']}"
        )

        print(
            f"   Bonus Score: "
            f"{result['breakdown']['bonus']}"
        )

        print(
            f"   Penalty: "
            f"{result['breakdown']['penalty']}"
        )

        print("\n   SKILL ANALYSIS")

        summary = result["skill_summary"]

        print(
            f"   Skill Match: "
            f"{summary['matched']}/{summary['required']} "
            f"({summary['percentage']}%)"
        )

        print(
            f"   Strengths: "
            f"{', '.join(result['matched_skills']) or 'None'}"
        )

        print(
            f"   Skill Gaps: "
            f"{', '.join(result['missing_skills']) or 'None'}"
        )

        print(
            f"   Matched Responsibilities: "
            f"{', '.join(result['matched_responsibilities']) or 'None'}"
        )

        print(
            f"   Matched Bonus Keywords: "
            f"{', '.join(result['matched_bonus_keywords']) or 'None'}"
        )

        fit = result["fit_explanation"]

        print()
        print("   WHY THIS JOB")

        if fit["strengths"]:
            print(
                "   Strengths: "
                + "; ".join(fit["strengths"])
            )

        if fit["concerns"]:
            print(
                "   Concerns: "
                + "; ".join(fit["concerns"])
            )

        print(
            "   Verdict: "
            + fit["verdict"]
        )

        print()
        print("   FINAL DECISION")

        print(
            f"   Priority: "
            f"{result['application_priority']}"
        )

        print(
            f"   Action: "
            f"{result['recommended_action']}"
        )

        tailoring = result["resume_tailoring"]

        if tailoring["skills_to_emphasize"]:
            print(
                "   Resume Skills to Emphasize: "
                + ", ".join(
                    tailoring["skills_to_emphasize"]
                )
            )

        if tailoring["responsibilities_to_emphasize"]:
            print(
                "   Resume Experience to Emphasize: "
                + ", ".join(
                    tailoring[
                        "responsibilities_to_emphasize"
                    ]
                )
            )

        if tailoring["missing_skills"]:
            print(
                "   Resume Caution - Do Not Claim: "
                + ", ".join(
                    tailoring["missing_skills"]
                )
            )