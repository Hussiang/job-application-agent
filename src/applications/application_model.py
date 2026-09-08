from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Application:
    job_id: int
    title: str
    company: str

    status: str = "APPLIED"

    applied_date: Optional[str] = None
    interview_date: Optional[str] = None
    follow_up_date: Optional[str] = None
    notes: str = ""
    resume_version: Optional[str] = None
    application_url: Optional[str] = None
    last_updated: str = ""

    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()

        self.status = (
            self.status or "APPLIED"
        ).upper().strip()

        self.notes = (
            self.notes or ""
        ).strip()

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "status": self.status,
            "applied_date": self.applied_date,
            "interview_date": self.interview_date,
            "follow_up_date": self.follow_up_date,
            "notes": self.notes,
            "resume_version": self.resume_version,
            "application_url": self.application_url,
            "last_updated": self.last_updated,
        }