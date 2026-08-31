from dataclasses import dataclass
from typing import Optional


@dataclass
class Application:
    job_id: int
    title: str
    company: str

    status: str = "APPLIED"

    applied_date: Optional[str] = None

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "status": self.status,
            "applied_date": self.applied_date
        }