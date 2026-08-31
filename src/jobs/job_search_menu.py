from src.jobs.job_filters import (
    filter_jobs_by_status,
    search_jobs
)


def show_jobs(jobs):
    if not jobs:
        print("\nNo jobs found.")
        return

    print()

    print(
        f"{'Job ID':<10}"
        f"{'Role':<30}"
        f"{'Company':<25}"
        f"{'Status'}"
    )

    print("-" * 85)

    for job in jobs:
        print(
            f"{job.job_id:<10}"
            f"{job.title:<30}"
            f"{job.company:<25}"
            f"{job.status}"
        )


def handle_job_search(jobs):
    while True:
        print("\nJOB SEARCH & FILTER")

        print("1. Search by keyword")
        print("2. Filter by status")
        print("3. Show all jobs")
        print("4. Exit")

        choice = input(
            "\nChoose an option: "
        ).strip()

        if choice == "1":
            keyword = input(
                "Enter role or company keyword: "
            )

            results = search_jobs(
                jobs,
                keyword
            )

            show_jobs(results)

        elif choice == "2":
            status = input(
                "Enter status "
                "(NEW/ANALYZED/SHORTLISTED/APPLIED/REJECTED/ARCHIVED): "
            )

            results = filter_jobs_by_status(
                jobs,
                status
            )

            show_jobs(results)

        elif choice == "3":
            show_jobs(jobs)

        elif choice == "4":
            break

        else:
            print(
                "\nInvalid option. Please try again."
            )