from src.applications.application_tracker import (
    add_application,
    get_application,
    update_application_status
)
from src.application_package.package_generator import (
    generate_application_package
)

from src.application_package.package_display import (
    show_application_package
)
from src.jobs.job_actions import (
    update_job_status
)

from src.jobs.job_repository import (
    JobRepository
)

def handle_application_actions(
    ranked_jobs,
    jobs,
    job_repository
):
    print("\nAPPLICATION ACTIONS")

    available_results = []

    for result in ranked_jobs:
        job = result["job"]

        if job.status == "SHORTLISTED":
            existing_application = get_application(
                job.job_id
            )

            if not existing_application:
                available_results.append(result)

    if not available_results:
        print(
            "\nNo jobs with SHORTLISTED status are "
            "available to mark as applied."
        )
        return

    print("\nAVAILABLE JOBS TO APPLY\n")

    print(
        f"{'Job ID':<10}"
        f"{'Role':<30}"
        f"{'Company'}"
    )

    print("-" * 70)

    for result in available_results:
        job = result["job"]

        print(
            f"{job.job_id:<10}"
            f"{job.title:<30}"
            f"{job.company}"
        )

    job_id_input = input(
        "\nEnter Job ID to prepare application "
        "(or press Enter to skip): "
    ).strip()

    if not job_id_input:
        return

    if not job_id_input.isdigit():
        print(
            "\nInvalid Job ID. "
            "Please enter a number."
        )
        return

    job_id = int(job_id_input)

    selected_result = next(
        (
            result
            for result in available_results
            if result["job"].job_id == job_id
        ),
        None
    )

    if selected_result is None:
        print(
            "\nThat Job ID is not available "
            "for application."
        )
        return

    package = generate_application_package(
        selected_result
    )

    show_application_package(package)

    confirm = input(
        "\nMark this application as applied? "
        "(y/n): "
    ).strip().lower()

    if confirm != "y":
        print(
            "\nApplication was not tracked."
        )
        return

    application = add_application(
    selected_result["job"]
)

    if application:
     updated_job = update_job_status(
        jobs,
        job_repository,
        selected_result["job"].job_id,
        "APPLIED"
    )

    print(
        "\nApplication tracked: "
        f"{application.company} - "
        f"{application.title}"
    )

    if updated_job:
        print(
            f"Job status updated to: "
            f"{updated_job.status}"
        )

    else:
     print(
        "\nThis job is already "
        "being tracked."
    )


def handle_status_update():
    print("\nUPDATE APPLICATION STATUS")

    job_id = input(
        "Enter job ID to update "
        "(or press Enter to skip): "
    ).strip()

    if job_id:
        try:
            job_id = int(job_id)

        except ValueError:
            print(
                "\nInvalid Job ID. "
                "Please enter a numeric Job ID."
            )

        else:
            new_status = input(
                "Enter new status "
                "(APPLIED/INTERVIEW/OFFER/REJECTED): "
            ).strip().upper()

            updated_application = update_application_status(
                job_id,
                new_status
            )

            if updated_application == "INVALID_STATUS":
                print("\nInvalid status.")

                print(
                    "Valid statuses: "
                    "APPLIED, INTERVIEW, OFFER, REJECTED"
                )

            elif updated_application:
                print(
                    f"\nApplication updated: "
                    f"{updated_application.company} - "
                    f"{updated_application.title}"
                )

                print(
                    f"New status: "
                    f"{updated_application.status}"
                )

            else:
                print(
                    "\nNo application found "
                    "with that Job ID."
                )