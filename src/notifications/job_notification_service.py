import hashlib

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

            if recommendation not in self.allowed_recommendations:
                continue

            current_hash = self._build_notification_hash(
                job,
                result,
            )

            if (
                job.telegram_notified
                and job.notification_hash == current_hash
            ):
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
                job.notification_hash = current_hash

                notification_count += 1

                print(
                    f"Telegram notification sent: "
                    f"{job.title} - {job.company}"
                )

        return notification_count

    def _build_notification_hash(
        self,
        job,
        result,
    ) -> str:

        fingerprint_data = "|".join(
    [
        str(job.title).strip().lower(),
        str(job.company).strip().lower(),
        str(job.location).strip().lower(),
        str(job.description or "").strip().lower(),
        ",".join(
            sorted(
                skill.strip().lower()
                for skill in job.skills
                if skill
            )
        ),
        ",".join(
            sorted(
                responsibility.strip().lower()
                for responsibility in job.responsibilities
                if responsibility
            )
        ),
        str(job.experience_required),
        str(
            job.certification_requirement
            or ""
        ).strip().lower(),
        str(result["recommendation"]),
        str(result["score"]),
    ]
)

        return hashlib.sha256(
            fingerprint_data.encode("utf-8")
        ).hexdigest()

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

        message = (
            "🔥 JOB APPLICATION AGENT\n\n"
            f"{result['recommendation']}\n\n"
            f"Role: {job.title}\n"
            f"Company: {job.company}\n"
            f"Location: {location}\n"
            f"Score: {result['score']}\n"
            f"Source: {source}\n"
        )

        if job_url:
            message += (
                f"\nApply:\n{job_url}\n"
            )

        return message