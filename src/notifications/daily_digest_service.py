from datetime import datetime

from src.notifications.telegram_notifier import TelegramNotifier


class DailyDigestService:

    def __init__(
        self,
        notifier: TelegramNotifier,
    ):
        self.notifier = notifier

    def send_digest(
        self,
        ranked_jobs,
        applications,
        minimum_score=45,
    ) -> bool:

        qualifying_jobs = [
            result
            for result in ranked_jobs
            if (
                result["score"] >= minimum_score
                and result["recommendation"]
                != "SKIP"
            )
        ]

        strong_apply = sum(
            1
            for result in qualifying_jobs
            if result["recommendation"]
            == "STRONG APPLY"
        )

        apply_count = sum(
            1
            for result in qualifying_jobs
            if result["recommendation"]
            == "APPLY"
        )

        consider_count = sum(
            1
            for result in qualifying_jobs
            if result["recommendation"]
            == "CONSIDER"
        )

        top_jobs = qualifying_jobs[:5]

        today = datetime.now().strftime(
            "%Y-%m-%d"
        )

        message = (
            "📋 DAILY JOB DIGEST\n\n"
            f"Date: {today}\n\n"
            f"New/relevant jobs: "
            f"{len(qualifying_jobs)}\n"
            f"🔥 Strong Apply: {strong_apply}\n"
            f"✅ Apply: {apply_count}\n"
            f"🟡 Consider: {consider_count}\n\n"
            "TOP OPPORTUNITIES\n"
        )

        if not top_jobs:
            message += "\nNo qualifying jobs found today."

        else:
            for index, result in enumerate(
                top_jobs,
                start=1,
            ):
                job = result["job"]

                message += (
                    f"\n{index}. {job.title}\n"
                    f"   {job.company}\n"
                    f"   {job.location}\n"
                    f"   Score: {result['score']}\n"
                    f"   {result['recommendation']}\n"
                )

                if job.job_url:
                    message += (
                        f"   Apply: {job.job_url}\n"
                    )

        message += (
            "\nAPPLICATION STATUS\n"
            f"Tracked applications: "
            f"{len(applications)}\n"
        )

        for status in [
            "APPLIED",
            "INTERVIEW",
            "OFFER",
            "REJECTED",
            "WITHDRAWN",
        ]:
            count = sum(
                1
                for application in applications
                if application.status == status
            )

            message += (
                f"{status}: {count}\n"
            )

        return self.notifier.send_message(
            message
        )