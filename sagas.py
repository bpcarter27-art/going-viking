from __future__ import annotations

from dataclasses import dataclass, field
import uuid


@dataclass
class SagaEntry:
    year: int
    month: int
    week: int
    entry_type: str
    text: str
    viking_ids: list[str] = field(default_factory=list)
    job_id: str | None = None
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "year": self.year,
            "month": self.month,
            "week": self.week,
            "entry_type": self.entry_type,
            "text": self.text,
            "viking_ids": list(self.viking_ids),
            "job_id": self.job_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SagaEntry":
        return cls(
            entry_id=data.get("entry_id", str(uuid.uuid4())),
            year=data.get("year", 1),
            month=data.get("month", 1),
            week=data.get("week", 1),
            entry_type=data.get("entry_type", "general"),
            text=data.get("text", ""),
            viking_ids=list(data.get("viking_ids", [])),
            job_id=data.get("job_id"),
        )


def make_saga_entry(
    *,
    year: int,
    month: int,
    week: int,
    entry_type: str,
    text: str,
    viking_ids: list[str] | None = None,
    job_id: str | None = None,
) -> SagaEntry:
    return SagaEntry(
        year=year,
        month=month,
        week=week,
        entry_type=entry_type,
        text=text,
        viking_ids=viking_ids or [],
        job_id=job_id,
    )