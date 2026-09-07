from src.notifications.telegram_notifier import TelegramNotifier


class JobNotificationService:

    def __init__(
        self,
        notifier: TelegramNotifier,
        notification_config: dict,
    ):
        self.notifier = notifier

        self.enabled = notification_config.get(
            "enabled",
            True,
        )

        self.minimum_score = notification_config.get(
            "minimum_score",
            45,
        )

        self.allowed_recommendations = set(
            notification_config.get(
                "recommendations",
                [
                    "STRONG APPLY",
                    "APPLY",
                    "CONSIDER",
                ],
            )
        )

    def notify_new_jobs(
        self,
        ranked_jobs,
    ) -> int:

        if not self.enabled:
            print(
                "Telegram notifications are disabled."
            )
            return 0

        notification_count = 0

        for result in ranked_jobs:

            job = result["job"]
            recommendation = result["recommendation"]
            score = result["score"]

            if score < self.minimum_score:
                continue

            if recommendation not in (
                self.allowed_recommendations
            ):
                continue

            if job.telegram_notified:
                continue

            message = self._build_message(
                job,
                result,
            )

            success = self.notifier.send_message(
                message
            )

            if success:
                job.telegram_notified = True
                notification_count += 1

                print(
                    f"Telegram notification sent: "
                    f"{job.title} - {job.company}"
                )

        return notification_count

    def _build_message(
        self,
        job,
        result,
    ) -> str:

        location = getattr(
            job,
            "location",
            "Not specified",
        )

        source = getattr(
            job,
            "source",
            "Unknown",
        )

        job_url = getattr(
            job,
            "job_url",
            "",
        )

        return (
            "🔥 JOB APPLICATION AGENT\n\n"
            f"{result['recommendation']}\n\n"
            f"Role: {job.title}\n"
            f"Company: {job.company}\n"
            f"Location: {location}\n"
            f"Score: {result['score']}\n"
            f"Source: {source}\n\n"
            f"Apply:\n{job_url}"
        )