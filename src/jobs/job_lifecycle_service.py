from datetime import datetime, timedelta


class JobLifecycleService:

    def __init__(
        self,
        stale_after_days: int = 30,
    ):
        self.stale_after_days = stale_after_days

    def mark_stale_jobs(
        self,
        jobs,
    ) -> list:

        current_time = datetime.now()

        cutoff_time = (
            current_time
            - timedelta(
                days=self.stale_after_days
            )
        )

        stale_jobs = []

        for job in jobs:

            if not job.active:
                continue

            try:
                last_seen = datetime.fromisoformat(
                    job.last_seen
                )
            except (
                ValueError,
                TypeError,
            ):
                continue

            if last_seen < cutoff_time:
                job.active = False
                stale_jobs.append(job)

        return stale_jobs

    def reactivate_job(
        self,
        job,
    ) -> None:

        job.active = True
        job.last_seen = datetime.now().isoformat()