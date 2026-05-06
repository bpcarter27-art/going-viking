# models.py
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid


class FavoredGod(str, Enum):
    ODIN = "Odin"
    THOR = "Thor"
    FREYJA = "Freyja"
    TYR = "Tyr"
    LOKI = "Loki"
    NJORD = "Njord"
    HEIMDALL = "Heimdall"
    BALDR = "Baldr"
    FRIGG = "Frigg"
    FREYR = "Freyr"
    IDUNN = "Idunn"
    HEL = "Hel"
    SKADI = "Skadi"
    BRAGI = "Bragi"
    SIF = "Sif"
    
    
#====================================================
# SEASONS / CAMPAIGN TIME
#====================================================

class Season(str, Enum):
    SPRING = "Spring"
    SUMMER = "Summer"
    WINTER = "Winter"


SEASON_TIME_LIMITS = {
    Season.SPRING: 10,
    Season.SUMMER: 10,
    Season.WINTER: 0,
}


#====================================================
# CREW ROLES
#====================================================

class CrewRole(str, Enum):
    CAPTAIN = "Captain"
    NAVIGATOR = "Navigator"
    CARPENTER = "Carpenter"
    RAIDER = "Raider"
    SCOUT = "Scout"
    SAILOR = "Sailor"
    HEALER = "Healer"
    SKALD = "Skald"


#====================================================
# SHIP CLASSES
#====================================================

@dataclass
class ShipClass:
    name: str
    min_crew: int
    max_crew: int
    required_roles: dict[CrewRole, int]

    base_hull: int
    cargo_capacity: int
    range: int

    speed: int
    seaworthiness: int
    stealth: int

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "min_crew": self.min_crew,
            "max_crew": self.max_crew,
            "required_roles": {
                role.value: count for role, count in self.required_roles.items()
            },
            "base_hull": self.base_hull,
            "cargo_capacity": self.cargo_capacity,
            "range": self.range,
            "speed": self.speed,
            "seaworthiness": self.seaworthiness,
            "stealth": self.stealth,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ShipClass":
        return cls(
            name=data["name"],
            min_crew=data["min_crew"],
            max_crew=data["max_crew"],
            required_roles={
                CrewRole(role): count
                for role, count in data.get("required_roles", {}).items()
            },
            base_hull=data["base_hull"],
            cargo_capacity=data["cargo_capacity"],
            range=data["range"],
            speed=data["speed"],
            seaworthiness=data["seaworthiness"],
            stealth=data["stealth"],
        )    
    
#====================================================
# VIKINGS
#===================================================

class VikingStatus(str, Enum):
    ACTIVE = "Active"
    WOUNDED = "Wounded"
    DEAD = "Dead"
    DESERTED = "Deserted"
    RETIRED = "Retired"


@dataclass
class EquipmentSlots:
    armor: Optional[str] = None
    helm: Optional[str] = None
    primary_weapon: Optional[str] = None
    shield: Optional[str] = None
    


@dataclass
class Viking:
    name: str
    age: int

    # Core ratings, expected range 1-10 for now.
    might: int
    skill: int
    cunning: int
    courage: int
    loyalty: int

    favored_god: FavoredGod
    
    role: CrewRole = CrewRole.RAIDER

    traits: list[str] = field(default_factory=list)
    equipment: EquipmentSlots = field(default_factory=EquipmentSlots)

    status: VikingStatus = VikingStatus.ACTIVE
    wounds: list[str] = field(default_factory=list)

    silver_wage: int = 1
    renown: int = 0
    kills: int = 0
    expeditions: int = 0

    viking_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def is_available(self) -> bool:
        return self.status == VikingStatus.ACTIVE

    def combat_score(self) -> int:
        """
        Basic combat value.
        Equipment and traits can modify this later.
        """
        return (self.might * 2) + self.skill + self.courage

    def challenge_score(self) -> int:
        """
        General non-combat expedition usefulness.
        """
        return self.skill + self.cunning + self.courage

    def morale_score(self) -> int:
        return self.courage + self.loyalty

    def scouting_score(self) -> int:
        return self.cunning + self.skill

    def add_wound(self, wound_name: str) -> None:
        self.wounds.append(wound_name)
        self.status = VikingStatus.WOUNDED

    def recover_from_wounds(self) -> None:
        self.wounds.clear()
        if self.status == VikingStatus.WOUNDED:
            self.status = VikingStatus.ACTIVE

    def to_dict(self) -> dict:
        return {
            "viking_id": self.viking_id,
            "name": self.name,
            "age": self.age,
            "might": self.might,
            "skill": self.skill,
            "cunning": self.cunning,
            "courage": self.courage,
            "loyalty": self.loyalty,
            "favored_god": self.favored_god.value,
            "traits": list(self.traits),
            "equipment": {
                "armor": self.equipment.armor,
                "helm": self.equipment.helm,
                "primary_weapon": self.equipment.primary_weapon,
                "shield": self.equipment.shield,
            },
            "status": self.status.value,
            "wounds": list(self.wounds),
            "silver_wage": self.silver_wage,
            "renown": self.renown,
            "kills": self.kills,
            "expeditions": self.expeditions,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Viking":
        equipment_data = data.get("equipment", {})

        return cls(
            viking_id=data.get("viking_id", str(uuid.uuid4())),
            name=data["name"],
            age=data["age"],
            might=data["might"],
            skill=data["skill"],
            cunning=data["cunning"],
            courage=data["courage"],
            loyalty=data["loyalty"],
            favored_god=FavoredGod(data["favored_god"]),
            traits=list(data.get("traits", [])),
            equipment=EquipmentSlots(
                armor=equipment_data.get("armor"),
                helm=equipment_data.get("helm"),
                primary_weapon=equipment_data.get("primary_weapon"),
                shield=equipment_data.get("shield"),
            ),
            status=VikingStatus(data.get("status", VikingStatus.ACTIVE.value)),
            wounds=list(data.get("wounds", [])),
            silver_wage=data.get("silver_wage", 1),
            renown=data.get("renown", 0),
            kills=data.get("kills", 0),
            expeditions=data.get("expeditions", 0),
        )
        
        
#=======================================================
# SHIPS
#=======================================================        

class ShipStatus(str, Enum):
    READY = "Ready"
    DAMAGED = "Damaged"
    UNDER_REPAIR = "Under Repair"
    LOST = "Lost"


@dataclass
class Ship:
    name: str
    ship_class: ShipClass

    # Crew stores Viking IDs.
    crew: list[str] = field(default_factory=list)

    hull: int | None = None
    status: ShipStatus = ShipStatus.READY

    ship_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        if self.hull is None:
            self.hull = self.ship_class.base_hull

    @property
    def max_hull(self) -> int:
        return self.ship_class.base_hull

    @property
    def min_crew(self) -> int:
        return self.ship_class.min_crew

    @property
    def max_crew(self) -> int:
        return self.ship_class.max_crew

    @property
    def cargo_capacity(self) -> int:
        return self.ship_class.cargo_capacity
        
    @property
    def range(self) -> int:
        return self.ship_class.range        

    def available_crew_slots(self) -> int:
        return max(0, self.max_crew - len(self.crew))

    def has_room_for_crew(self, count: int = 1) -> bool:
        return self.available_crew_slots() >= count

    def add_crew_member(self, viking_id: str) -> bool:
        if not self.has_room_for_crew():
            return False

        if viking_id in self.crew:
            return False

        self.crew.append(viking_id)
        return True

    def remove_crew_member(self, viking_id: str) -> bool:
        if viking_id not in self.crew:
            return False

        self.crew.remove(viking_id)
        return True

    def has_minimum_crew(self) -> bool:
        return len(self.crew) >= self.min_crew

    def missing_required_roles(self, crew_by_id: dict[str, Viking]) -> dict[CrewRole, int]:
        role_counts: dict[CrewRole, int] = {}

        for viking_id in self.crew:
            viking = crew_by_id.get(viking_id)
            if not viking:
                continue

            role = getattr(viking, "role", None)
            if role:
                role_counts[role] = role_counts.get(role, 0) + 1

        missing: dict[CrewRole, int] = {}

        for required_role, required_count in self.ship_class.required_roles.items():
            current_count = role_counts.get(required_role, 0)
            if current_count < required_count:
                missing[required_role] = required_count - current_count

        return missing

    def is_fully_staffed(self, crew_by_id: dict[str, Viking]) -> bool:
        return self.has_minimum_crew() and not self.missing_required_roles(crew_by_id)

    def damage(self, amount: int) -> None:
        self.hull = max(0, self.hull - amount)

        if self.hull <= 0:
            self.status = ShipStatus.LOST
        elif self.hull < self.max_hull:
            self.status = ShipStatus.DAMAGED

    def repair(self, amount: int) -> None:
        if self.status == ShipStatus.LOST:
            return

        self.hull = min(self.max_hull, self.hull + amount)

        if self.hull >= self.max_hull:
            self.status = ShipStatus.READY
        else:
            self.status = ShipStatus.DAMAGED

    def is_usable(self) -> bool:
        return self.status in {ShipStatus.READY, ShipStatus.DAMAGED} and self.hull > 0

    def to_dict(self) -> dict:
        return {
            "ship_id": self.ship_id,
            "name": self.name,
            "ship_class": self.ship_class.to_dict(),
            "crew": list(self.crew),
            "hull": self.hull,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Ship":
        return cls(
            ship_id=data.get("ship_id", str(uuid.uuid4())),
            name=data["name"],
            ship_class=ShipClass.from_dict(data["ship_class"]),
            crew=list(data.get("crew", [])),
            hull=data.get("hull"),
            status=ShipStatus(data.get("status", ShipStatus.READY.value)),
        )
        


    @classmethod
    def from_dict(cls, data: dict) -> "ShipClass":
        return cls(
            name=data["name"],
            min_crew=data["min_crew"],
            max_crew=data["max_crew"],
            required_roles={
                CrewRole(role): count
                for role, count in data.get("required_roles", {}).items()
            },
            base_hull=data["base_hull"],
            cargo_capacity=data["cargo_capacity"],
            range=data["range"],  # NEW
            speed=data["speed"],
            seaworthiness=data["seaworthiness"],
            stealth=data["stealth"],
        )  

#====================================================
# JOBS
#====================================================

class JobType(str, Enum):
    COASTAL_RAID = "Coastal Raid"
    RIVER_RAID = "River Raid"
    MONASTERY_RAID = "Monastery Raid"
    ESCORT_VOYAGE = "Escort Voyage"
    TRIBUTE_COLLECTION = "Tribute Collection"
    JOIN_JARL_WARBAND = "Join Jarl's Warband"
    SCOUT_COASTLINE = "Scout Coastline"
    FEUD_ATTACK = "Feud Attack"
    RESCUE_CAPTIVE = "Rescue Captive"
    TRADE_VOYAGE = "Trade Voyage"


class JobRisk(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    EXTREME = "Extreme"


@dataclass
class Job:
    name: str
    job_type: JobType

    allowed_seasons: list[Season]
    time_cost: int

    required_range: int
    required_min_crew: int

    difficulty: int
    danger: int

    reward_silver: int
    reward_renown: int
    cargo_reward: int = 0

    employer: Optional[str] = None
    description: str = ""

    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def is_available_in_season(self, season: Season) -> bool:
        return season in self.allowed_seasons

    def ship_can_take_job(self, ship: Ship) -> bool:
        return (
            ship.is_usable()
            and ship.range >= self.required_range
            and len(ship.crew) >= self.required_min_crew
        )

    def time_can_fit(self, time_remaining: int) -> bool:
        return self.time_cost <= time_remaining

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "name": self.name,
            "job_type": self.job_type.value,
            "allowed_seasons": [season.value for season in self.allowed_seasons],
            "time_cost": self.time_cost,
            "required_range": self.required_range,
            "required_min_crew": self.required_min_crew,
            "difficulty": self.difficulty,
            "danger": self.danger,
            "reward_silver": self.reward_silver,
            "reward_renown": self.reward_renown,
            "cargo_reward": self.cargo_reward,
            "employer": self.employer,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        return cls(
            job_id=data.get("job_id", str(uuid.uuid4())),
            name=data["name"],
            job_type=JobType(data["job_type"]),
            allowed_seasons=[Season(season) for season in data["allowed_seasons"]],
            time_cost=data["time_cost"],
            required_range=data["required_range"],
            required_min_crew=data["required_min_crew"],
            difficulty=data["difficulty"],
            danger=data["danger"],
            reward_silver=data["reward_silver"],
            reward_renown=data["reward_renown"],
            cargo_reward=data.get("cargo_reward", 0),
            employer=data.get("employer"),
            description=data.get("description", ""),
        )