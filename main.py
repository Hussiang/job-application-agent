from src.applications.application_actions import (
    handle_application_actions,
    handle_status_update,
)
from src.applications.application_dashboard import (
    show_application_dashboard,
)
from src.core.config_loader import (
    load_profile,
    load_scoring,
)
from src.intake.job_intake import collect_job_posting
from src.intake.job_metadata_extractor import (
    extract_job_metadata,
)
from src.jobs.job_actions import (
    update_job_statuses_from_ranking,
)
from src.jobs.job_display import (
    show_job_details,
    show_ranking_summary,
)
from src.jobs.job_parser import parse_job_description
from src.jobs.job_ranker import rank_job
from src.jobs.job_repository import JobRepository
from src.jobs.job_search_menu import handle_job_search
from src.jobs.job_shortlist import show_top_jobs
from src.sources.json_job_source import JsonJobSource


def load_jobs():
    source = JsonJobSource(
        "data/jobs.json"
    )

    return source.fetch_jobs()


def get_new_job(
    known_skills,
    job_repository,
):
    job_posting = collect_job_posting()

    metadata = extract_job_metadata(
        job_posting
    )

    title = metadata["title"]

    if not title:
        title = input(
            "\nJob title not detected. "
            "Enter job title: "
        )

    company = metadata["company"]

    if not company:
        company = input(
            "Company not detected. "
            "Enter company: "
        )

    new_job = parse_job_description(
        title=title,
        company=company,
        description=metadata["description"],
        known_skills=known_skills,
    )

    new_job.job_id = (
        job_repository.get_next_job_id()
    )

    new_job.location = (
        metadata["location"]
        or "Not specified"
    )

    return new_job


def add_new_job(
    jobs,
    known_skills,
    job_repository,
):
    new_job = get_new_job(
        known_skills,
        job_repository,
    )

    if job_repository.is_duplicate(
        new_job,
        jobs,
    ):
        print(
            "\nDuplicate job detected. "
            "Job was not added."
        )
        return

    jobs.append(new_job)

    job_repository.save_jobs(
        jobs
    )

    print(
        f"\nNew job added successfully "
        f"with ID: {new_job.job_id}"
    )


def rank_all_jobs(
    jobs,
    profile,
    scoring,
    job_repository,
):
    if not jobs:
        print(
            "\nNo jobs available for ranking."
        )
        return []

    ranked_jobs = [
        rank_job(
            job,
            profile,
            scoring,
        )
        for job in jobs
    ]

    ranked_jobs.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    update_job_statuses_from_ranking(
        ranked_jobs,
        jobs,
        job_repository,
    )

    show_top_jobs(
        ranked_jobs,
        limit=5,
    )

    show_ranking_summary(
        ranked_jobs
    )

    show_job_details(
        ranked_jobs
    )

    return ranked_jobs


def show_main_menu():
    print("\n" + "=" * 40)
    print("      JOB APPLICATION AGENT")
    print("=" * 40)

    print("1. Add and analyze a new job")
    print("2. Rank all jobs")
    print("3. Manage applications")
    print("4. Update application status")
    print("5. View application dashboard")
    print("6. Search and filter jobs")
    print("7. Exit")


def main():
    profile = load_profile()
    scoring = load_scoring()
    jobs = load_jobs()

    job_repository = JobRepository(
        "data/jobs.json"
    )

    known_skills = []

    for skills in profile["skills"].values():
        known_skills.extend(skills)

    ranked_jobs = None

    while True:
        show_main_menu()

        choice = input(
            "\nChoose an option: "
        ).strip()

        if choice == "1":
            add_new_job(
                jobs,
                known_skills,
                job_repository,
            )

        elif choice == "2":
            ranked_jobs = rank_all_jobs(
                jobs,
                profile,
                scoring,
                job_repository,
            )

        elif choice == "3":
            if ranked_jobs is None:
                ranked_jobs = rank_all_jobs(
                    jobs,
                    profile,
                    scoring,
                    job_repository,
                )

            handle_application_actions(
                ranked_jobs,
                jobs,
                job_repository,
            )

        elif choice == "4":
            handle_status_update()

        elif choice == "5":
            show_application_dashboard()

        elif choice == "6":
            handle_job_search(jobs)

        elif choice == "7":
            print(
                "\nExiting Job Application Agent."
            )
            break

        else:
            print(
                "\nInvalid option. "
                "Please try again."
            )


if __name__ == "__main__":
    main()