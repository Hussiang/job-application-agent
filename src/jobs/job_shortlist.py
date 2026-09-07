def get_top_jobs(
    ranked_jobs,
    limit=5,
):
    eligible_jobs = [
        result
        for result in ranked_jobs
        if result["recommendation"] in [
            "STRONG APPLY",
            "APPLY",
            "CONSIDER",
        ]
        and result["job"].active
    ]

    return eligible_jobs[:limit]


def show_top_jobs(
    ranked_jobs,
    limit=5,
):
    top_jobs = get_top_jobs(
        ranked_jobs,
        limit,
    )

    print("\nTOP JOB OPPORTUNITIES\n")

    if not top_jobs:
        print(
            "No active relevant jobs found "
            "for the current profile."
        )
        return

    print(
        f"{'Rank':<6}"
        f"{'Job ID':<8}"
        f"{'Role':<30}"
        f"{'Company':<22}"
        f"{'Score':<10}"
        f"{'Recommendation'}"
    )

    print("-" * 100)

    for position, result in enumerate(
        top_jobs,
        start=1,
    ):
        job = result["job"]

        role = job.title[:29]

        print(
            f"{position:<6}"
            f"{job.job_id:<8}"
            f"{role:<30}"
            f"{job.company:<22}"
            f"{result['score']:<10}"
            f"{result['recommendation']}"
        )