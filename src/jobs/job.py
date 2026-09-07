from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


VALID_JOB_STATUSES = [
    "NEW",
    "ANALYZED",
    "SHORTLISTED",
    "APPLIED",
    "REJECTED",
    "ARCHIVED",
]


@dataclass
class Job:
    job_id: int
    title: str
    company: str
    location: str
    description: str

    skills: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)

    experience_required: Optional[float] = None
    certification_requirement: Optional[str] = None

    posted_date: Optional[str] = None
    source: Optional[str] = None
    job_url: Optional[str] = None

    is_active: bool = True

    discovered_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    first_seen: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    last_seen: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    active: bool = True

    telegram_notified: bool = False

    status: str = "NEW"

    def __post_init__(self):
        self._validate_required_fields()
        self._normalize_fields()

    def _validate_required_fields(self):
        required_fields = {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
        }

        missing_fields = [
            field_name
            for field_name, value in required_fields.items()
            if (
                value is None
                or (
                    isinstance(value, str)
                    and not value.strip()
                )
            )
        ]

        if missing_fields:
            raise ValueError(
                "Missing or invalid required fields: "
                + ", ".join(missing_fields)
            )

        normalized_status = (
            self.status or ""
        ).upper().strip()

        if normalized_status not in VALID_JOB_STATUSES:
            raise ValueError(
                f"Invalid job status: {self.status}. "
                f"Valid statuses are: "
                f"{', '.join(VALID_JOB_STATUSES)}"
            )

    def _normalize_fields(self):
        self.title = self.title.strip()
        self.company = self.company.strip()
        self.location = self.location.strip()
        self.description = self.description.strip()

        self.skills = [
            skill.strip()
            for skill in self.skills
            if isinstance(skill, str)
            and skill.strip()
        ]

        self.responsibilities = [
            responsibility.strip()
            for responsibility in self.responsibilities
            if (
                isinstance(responsibility, str)
                and responsibility.strip()
            )
        ]

        if self.certification_requirement:
            self.certification_requirement = (
                self.certification_requirement.strip()
            )

        if self.source:
            self.source = self.source.strip()

        if self.job_url:
            self.job_url = self.job_url.strip()

        self.status = self.status.upper().strip()

    def to_dict(self) -> dict:
        return {
            "id": self.job_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "skills": self.skills,
            "responsibilities": self.responsibilities,
            "experience_required": self.experience_required,
            "certification_requirement": (
                self.certification_requirement
            ),
            "posted_date": self.posted_date,
            "source": self.source,
            "job_url": self.job_url,
            "is_active": self.is_active,
            "discovered_at": self.discovered_at,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "active": self.active,
            "telegram_notified": self.telegram_notified,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            job_id=data["id"],
            title=data["title"],
            company=data["company"],
            location=data.get(
                "location",
                "Not specified",
            ),
            description=data["description"],
            skills=data.get(
                "skills",
                [],
            ),
            responsibilities=data.get(
                "responsibilities",
                [],
            ),
            experience_required=data.get(
                "experience_required"
            ),
            certification_requirement=data.get(
                "certification_requirement"
            ),
            posted_date=data.get(
                "posted_date"
            ),
            source=data.get(
                "source"
            ),
            job_url=data.get(
                "job_url"
            ),
            is_active=data.get(
                "is_active",
                True,
            ),
            discovered_at=data.get(
                "discovered_at",
                datetime.now().isoformat(),
            ),
            first_seen=data.get(
                "first_seen",
                data.get(
                    "discovered_at",
                    datetime.now().isoformat(),
                ),
            ),
            last_seen=data.get(
                "last_seen",
                data.get(
                    "discovered_at",
                    datetime.now().isoformat(),
                ),
            ),
            active=data.get(
                "active",
                True,
            ),
            telegram_notified=data.get(
                "telegram_notified",
                False,
            ),
            status=data.get(
                "status",
                "NEW",
            ),
        )