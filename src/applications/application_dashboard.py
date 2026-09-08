from src.applications.application_tracker import (
    load_applications,
)


def show_application_dashboard():

    applications = load_applications()

    print("\n" + "=" * 55)
    print("              APPLICATION DASHBOARD")
    print("=" * 55)

    total = len(applications)

    counts = {
        "APPLIED": 0,
        "INTERVIEW": 0,
        "OFFER": 0,
        "REJECTED": 0,
        "WITHDRAWN": 0,
    }

    for application in applications:

        status = application.status

        if status in counts:
            counts[status] += 1

    applied = counts["APPLIED"]
    interviews = counts["INTERVIEW"]
    offers = counts["OFFER"]
    rejected = counts["REJECTED"]
    withdrawn = counts["WITHDRAWN"]

    completed_outcomes = (
        interviews
        + offers
        + rejected
        + withdrawn
    )

    response_rate = (
        (
            completed_outcomes
            / total
        )
        * 100
        if total
        else 0
    )

    interview_rate = (
        (
            interviews
            / total
        )
        * 100
        if total
        else 0
    )

    offer_rate = (
        (
            offers
            / total
        )
        * 100
        if total
        else 0
    )

    print("\nAPPLICATION FUNNEL\n")

    print(
        f"Total Applications : {total}"
    )

    print(
        f"Applied            : {applied}"
    )

    print(
        f"Interviews         : {interviews}"
    )

    print(
        f"Offers             : {offers}"
    )

    print(
        f"Rejected           : {rejected}"
    )

    print(
        f"Withdrawn          : {withdrawn}"
    )

    print("\nMETRICS\n")

    print(
        f"Response Rate      : {response_rate:.1f}%"
    )

    print(
        f"Interview Rate     : {interview_rate:.1f}%"
    )

    print(
        f"Offer Rate         : {offer_rate:.1f}%"
    )

    if not applications:
        print(
            "\nNo applications are currently tracked."
        )
        return

    print("\nAPPLICATION DETAILS\n")

    print(
        f"{'Job ID':<8}"
        f"{'Company':<22}"
        f"{'Role':<32}"
        f"{'Status':<12}"
        f"{'Applied':<12}"
        f"{'Interview'}"
    )

    print("-" * 105)

    for application in applications:

        company = application.company[:21]
        title = application.title[:31]

        print(
            f"{application.job_id:<8}"
            f"{company:<22}"
            f"{title:<32}"
            f"{application.status:<12}"
            f"{str(application.applied_date):<12}"
            f"{str(application.interview_date)}"
        )

        if application.follow_up_date:
            print(
                f"         Follow-up: "
                f"{application.follow_up_date}"
            )

        if application.notes:
            print(
                f"         Notes: "
                f"{application.notes}"
            )

        print()