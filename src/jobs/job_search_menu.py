from src.core.config_loader import (
    load_profile,
    load_scoring,
)
from src.jobs.job_filters import (
    filter_active_jobs,
    filter_jobs_by_min_score,
    filter_jobs_by_recommendation,
    filter_jobs_by_status,
    search_jobs,
)
from src.jobs.job_ranker import rank_job


def show_jobs(
    jobs,
):
    if not jobs:
        print("\nNo jobs found.")
        return

    print()

    print(
        f"{'Job ID':<8}"
        f"{'Role':<32}"
        f"{'Company':<22}"
        f"{'Location':<18}"
        f"{'Status'}"
    )

    print("-" * 95)

    for job in jobs:

        role = job.title[:31]
        company = job.company[:21]
        location = job.location[:17]

        print(
            f"{job.job_id:<8}"
            f"{role:<32}"
            f"{company:<22}"
            f"{location:<18}"
            f"{job.status}"
        )


def show_ranked_jobs(
    ranked_jobs,
):
    if not ranked_jobs:
        print("\nNo jobs found.")
        return

    print()

    print(
        f"{'Job ID':<8}"
        f"{'Role':<32}"
        f"{'Company':<22}"
        f"{'Score':<10}"
        f"{'Recommendation'}"
    )

    print("-" * 95)

    for result in ranked_jobs:

        job = result["job"]

        role = job.title[:31]
        company = job.company[:21]

        print(
            f"{job.job_id:<8}"
            f"{role:<32}"
            f"{company:<22}"
            f"{result['score']:<10}"
            f"{result['recommendation']}"
        )


def handle_job_search(
    jobs,
):

    profile = load_profile()
    scoring = load_scoring()

    ranked_jobs = [
        rank_job(
            job,
            profile,
            scoring,
        )
        for job in jobs
    ]

    while True:

        print("\nJOB SEARCH & FILTER")

        print("1. Search by keyword")
        print("2. Filter by status")
        print("3. Show active jobs")
        print("4. Filter by minimum score")
        print("5. Filter by recommendation")
        print("6. Show all jobs")
        print("7. Exit")

        choice = input(
            "\nChoose an option: "
        ).strip()

        if choice == "1":

            keyword = input(
                "Enter keyword "
                "(role/company/location/skill): "
            )

            results = search_jobs(
                jobs,
                keyword,
            )

            show_jobs(results)

        elif choice == "2":

            status = input(
                "Enter status "
                "(NEW/ANALYZED/SHORTLISTED/"
                "APPLIED/REJECTED/ARCHIVED): "
            )

            results = filter_jobs_by_status(
                jobs,
                status,
            )

            show_jobs(results)

        elif choice == "3":

            results = filter_active_jobs(
                jobs
            )

            show_jobs(results)

        elif choice == "4":

            score_input = input(
                "Enter minimum score: "
            ).strip()

            try:
                minimum_score = float(
                    score_input
                )
            except ValueError:
                print(
                    "\nInvalid score."
                )
                continue

            results = filter_jobs_by_min_score(
                ranked_jobs,
                minimum_score,
            )

            show_ranked_jobs(results)

        elif choice == "5":

            recommendation = input(
                "Enter recommendation "
                "(STRONG APPLY/APPLY/CONSIDER/SKIP): "
            )

            results = filter_jobs_by_recommendation(
                ranked_jobs,
                recommendation,
            )

            show_ranked_jobs(results)

        elif choice == "6":

            show_jobs(jobs)

        elif choice == "7":

            break

        else:

            print(
                "\nInvalid option. "
                "Please try again."
            )