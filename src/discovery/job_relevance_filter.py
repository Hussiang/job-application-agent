import re


class JobRelevanceFilter:

    def __init__(
        self,
        profile,
    ):
        self.profile = profile

        self.exclude_keywords = (
            self._get_preference_list(
                "exclude_keywords"
            )
        )

        self.required_title_keywords = (
            self._get_preference_list(
                "required_title_keywords"
            )
        )

        self.exclude_title_keywords = (
            self._get_preference_list(
                "exclude_title_keywords"
            )
        )

    def is_relevant(
        self,
        job,
    ) -> tuple[bool, str]:

        title = job.title.lower()

        excluded_reason = (
            self._matches_any_keyword(
                title,
                self.exclude_keywords,
            )
        )

        if excluded_reason:
            return (
                False,
                f"Excluded keyword: "
                f"{excluded_reason}",
            )

        excluded_title_reason = (
            self._matches_any_keyword(
                title,
                self.exclude_title_keywords,
            )
        )

        if excluded_title_reason:
            return (
                False,
                f"Excluded title keyword: "
                f"{excluded_title_reason}",
            )

        required_reason = (
            self._matches_any_keyword(
                title,
                self.required_title_keywords,
            )
        )

        if not required_reason:
            return (
                False,
                "Title does not match "
                "required keywords",
            )

        return (
            True,
            "Relevant job",
        )

    def _get_preference_list(
        self,
        key,
    ) -> list[str]:

        preferences = self.profile.get(
            "job_preferences",
            {},
        )

        return preferences.get(
            key,
            [],
        )

    def _matches_any_keyword(
        self,
        title,
        keywords,
    ) -> str | None:

        for keyword in keywords:

            pattern = (
                r"\b"
                + re.escape(
                    keyword.lower()
                )
                + r"\b"
            )

            if re.search(
                pattern,
                title,
            ):
                return keyword

        return None