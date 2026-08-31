from src.applications.application_tracker import load_applications


def show_application_dashboard():
    applications = load_applications()

    print("\nAPPLICATION SUMMARY\n")

    total = len(applications)

    applied = sum(
        1
        for application in applications
        if application.status == "APPLIED"
    )

    interview = sum(
        1
        for application in applications
        if application.status == "INTERVIEW"
    )

    offer = sum(
        1
        for application in applications
        if application.status == "OFFER"
    )

    rejected = sum(
        1
        for application in applications
        if application.status == "REJECTED"
    )

    print(f"Total Applications: {total}")
    print(f"Applied: {applied}")
    print(f"Interview: {interview}")
    print(f"Offer: {offer}")
    print(f"Rejected: {rejected}")

    print("\nAPPLICATIONS\n")

    for application in applications:
        print(f"Job ID: {application.job_id}")
        print(f"Company: {application.company}")
        print(f"Role: {application.title}")
        print(f"Status: {application.status}")
        print(
            f"Applied Date: "
            f"{application.applied_date}"
        )
        print()