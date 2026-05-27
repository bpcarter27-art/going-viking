from __future__ import annotations

from dataclasses import dataclass, field
import uuid

from models import Viking, VikingClass, CrewRole, Season
from roster import generate_viking
from village import Village, BuildingType


MAX_SEASONS_WAITING = 3

RECRUITABLE_CLASSES = [
    VikingClass.RAIDER,
    VikingClass.SAILOR,
    VikingClass.ARCHER,
    VikingClass.TRICKSTER,
    VikingClass.HERSIR,
    VikingClass.SHIELDMAIDEN,
    VikingClass.HERBALIST,
    VikingClass.SCOUT,
]


@dataclass
class RecruitCandidate:
    viking: Viking
    seasons_waiting: int = 0
    candidate_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "seasons_waiting": self.seasons_waiting,
            "viking": self.viking.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RecruitCandidate":
        return cls(
            candidate_id=data.get("candidate_id", str(uuid.uuid4())),
            seasons_waiting=data.get("seasons_waiting", 0),
            viking=Viking.from_dict(data["viking"]),
        )


@dataclass
class RecruitPool:
    candidates: list[RecruitCandidate] = field(default_factory=list)
    last_refresh_year: int = 0
    last_refresh_season: str = ""

    def capacity(self, village: Village) -> int:
        completed_buildings = [
            building for building in village.get_buildings()
            if not building.is_under_construction
        ]

        return 4 + len(completed_buildings)

    def available_classes(self, village: Village) -> list[VikingClass]:
        classes = [
            viking_class for viking_class in RECRUITABLE_CLASSES
            if village.class_is_unlocked(viking_class)
        ]

        if not classes:
            return [VikingClass.RAIDER, VikingClass.SAILOR]

        return classes

    def refresh(
        self,
        village: Village,
        year: int,
        season: Season,
    ) -> None:
        season_name = season.value

        if self.last_refresh_year == year and self.last_refresh_season == season_name:
            return

        self.last_refresh_year = year
        self.last_refresh_season = season_name

        remaining_candidates = []

        for candidate in self.candidates:
            candidate.seasons_waiting += 1

            # Always leave after the hard limit.
            if candidate.seasons_waiting > MAX_SEASONS_WAITING:
                continue

            # Otherwise, older candidates may move on.
            if candidate.seasons_waiting == 1:
                leave_chance = 0.10
            elif candidate.seasons_waiting == 2:
                leave_chance = 0.25
            else:
                leave_chance = 0.50

            if __import__("random").random() < leave_chance:
                continue

            remaining_candidates.append(candidate)

        self.candidates = remaining_candidates

        cap = self.capacity(village)
        available_classes = self.available_classes(village)

        while len(self.candidates) < cap:
            viking_class = __import__("random").choice(available_classes)

            recruit = generate_viking(
                role=CrewRole.RAIDER,
                viking_class=viking_class,
                training_level=village.training_grounds_level(),
                shrine_level=village.highest_completed_level(BuildingType.SHRINE_OF_ODIN),
            )

            self.candidates.append(
                RecruitCandidate(viking=recruit)
            )

    def remove_candidate(self, candidate_id: str) -> RecruitCandidate | None:
        for candidate in self.candidates:
            if candidate.candidate_id == candidate_id:
                self.candidates.remove(candidate)
                return candidate

        return None

    def to_dict(self) -> dict:
        return {
            "last_refresh_year": self.last_refresh_year,
            "last_refresh_season": self.last_refresh_season,
            "candidates": [
                candidate.to_dict()
                for candidate in self.candidates
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RecruitPool":
        return cls(
            last_refresh_year=data.get("last_refresh_year", 0),
            last_refresh_season=data.get("last_refresh_season", ""),
            candidates=[
                RecruitCandidate.from_dict(candidate_data)
                for candidate_data in data.get("candidates", [])
            ],
        )