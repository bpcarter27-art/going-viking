# models.py
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from items import EquipmentSlot
from traits import Trait
import uuid


class FavoredGod(str, Enum):
    ODIN = "Odin"
    THOR = "Thor"
    FREYJA = "Freyja"
    NJORD = "Njord"
    LOKI = "Loki"
    TYR = "Tyr"
    HEIMDALL = "Heimdall"
    FRIGG = "Frigg"
    BALDR = "Baldr"
    SKADI = "Skadi"
    
    
#====================================================
# CALENDAR / SEASONS
#====================================================

class Season(str, Enum):
    SPRING = "Spring"
    SUMMER = "Summer"
    WINTER = "Winter"


MONTH_NAMES = {
    1: "Early Spring",
    2: "Mid Spring",
    3: "Late Spring",
    4: "Planting Month",
    5: "Early Summer",
    6: "High Summer",
    7: "Late Summer",
    8: "Harvest Month",
    9: "Early Winter",
    10: "Deepening Winter",
    11: "Long Night",
    12: "Yule Month",
}


WEEKS_PER_MONTH = 4
MONTHS_PER_SEASON = 4
WEEKS_PER_SEASON = WEEKS_PER_MONTH * MONTHS_PER_SEASON
WEEKS_PER_YEAR = 48
MAX_SEASON_SPILLOVER_WEEKS = 3


def get_week_of_season(month: int, week_of_month: int) -> int:
    """
    Returns week 1-16 within the current season.
    Months 1-4 = Spring
    Months 5-8 = Summer
    Months 9-12 = Winter
    """
    if not 1 <= month <= 12:
        raise ValueError("month must be 1-12")

    if not 1 <= week_of_month <= 4:
        raise ValueError("week_of_month must be 1-4")

    season_month_index = ((month - 1) % MONTHS_PER_SEASON) + 1
    return ((season_month_index - 1) * WEEKS_PER_MONTH) + week_of_month


def get_season_for_month(month: int) -> Season:
    if 1 <= month <= 4:
        return Season.SPRING
    if 5 <= month <= 8:
        return Season.SUMMER
    if 9 <= month <= 12:
        return Season.WINTER

    raise ValueError(f"Invalid month: {month}. Month must be 1-12.")


def get_month_name(month: int) -> str:
    return MONTH_NAMES.get(month, f"Month {month}")


#====================================================
# CREW ROLES
#====================================================

class CrewRole(str, Enum):
    CAPTAIN = "Captain"
    RAIDER = "Raider"


#====================================================
# VIKING CLASSES
#====================================================

class VikingClass(str, Enum):
    RAIDER = "Drengr"               # Might
    ARCHER = "Archer"               # Skill
    TRICKSTER = "Trickster"         # Cunning
    HERSIR = "Hersir"               # Leadership
    SHIELDMAIDEN = "Shieldmaiden"   # Courage
    HERBALIST = "Bone-Setter"       # Vitality
    SCOUT = "Tracker"               # Agility
    SAILOR = "Oarsman"              # Seamanship

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
    
    
TITLE_EFFECTS = {
   # "Arrow-Lamed": {"renown": 6, "courage": 5},
    "Arrow-Scarred": {"renown": 6, "courage": 5},
    "Ash-Eye": {"renown": 6, "leadership": 5},
    "Battle-Mad": {"courage": 8, "cunning": -4, "renown": 7},
    "Bear-Kissed": {"renown": 6, "vitality": 7},
    "Bent-Back": {"renown": 5, "courage": 5},
    "Black-Hand": {"renown": 6, "courage": 5},
    "Boar-Torn": {"renown": 6, "courage": 5},
  #  "Broken-Jaw": {"renown": 5, "courage": 5},
    "Burn-Face": {"renown": 6, "courage": 5},
    "Claw-Face": {"renown": 5, "courage": 5},
    "Cloud-Eye": {"renown": 5, "leadership": 5},
    "Cold-Foot": {"courage": 5, "renown": 5},
    "Crack-Skull": {"renown": 5, "courage": 5},
    "Crooked-Hand": {"renown": 4},
    "Crooked-Nose": {"renown": 4},
    "Deadeye": {"courage": 7},
  #  "Fever-Touched": {"renown": 5, "cunning": 5},
    "Flame-Kissed": {"courage": 7, "renown": 7},
    # "Flat-Hand": {"renown": 5},
    "Frost-Bitten": {"courage": 5, "renown": 5},
   # "Frost-Toes": {"renown": 5},
   # "Half-Ear": {"renown": 4},
    "Half-Hand": {"renown": 5},
    "Hollow-Chest": {"renown": 5, "courage": 5},
    "Ice-Born": {"renown": 5, "courage": 4},
    "Ice-Leg": {"renown": 5, "courage": 4},
    "Iron-Foot": {"renown": 6, "courage": 5},
    "One-Eye": {"leadership": 7, "renown": 8},
    "One-Hand": {"renown": 7, "leadership": 6},
    "Salt-Eye": {"renown": 6, "leadership": 5},
    "Scar-Face": {"courage": 5, "renown": 6},
   # "Shaking-Hand": {"renown": 4},
  #  "Short-Leg": {"renown": 4},
    "Storm-Broken": {"courage": 5, "renown": 6},
  # "Storm-Lamed": {"renown": 6, "courage": 5},
    "Stone-Hand": {"renown": 5},
    "the Determined": {"leadership": 4, "cunning": 6},
   # "the Doubtful": {"courage": -4},
  #  "the Lame": {"renown": 5, "courage": 5},
  #  "the Limping": {"renown": 5, "courage": 4},
    "the Pale": {"renown": 4, "cunning": 5},
    "the Scarred": {"renown": 5},
    "the Withered": {"renown": 4, "cunning": 4},
  #  "Thin-Breath": {"renown": 4},
    "Wave-Mad": {"renown": 6, "courage": 6, "cunning": -4},
  #  "White-Hand": {"renown": 5},
    "Winter-Shaken": {"renown": 5, "courage": 5},
    "Wolf-Bitten": {"courage": 6, "renown": 6},
}    

@dataclass
class ActiveInjury:
    name: str
    weeks_remaining: int
    stat_modifiers: dict[str, int] = field(default_factory=dict)
    recovery_started: bool = False
    can_deploy_while_injured: bool = True
    pending_title: str | None = None
    title_awarded: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "weeks_remaining": self.weeks_remaining,
            "stat_modifiers": dict(self.stat_modifiers),
            "recovery_started": self.recovery_started,
            "can_deploy_while_injured": self.can_deploy_while_injured,
            "pending_title": self.pending_title,
            "title_awarded": self.title_awarded,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ActiveInjury":
        return cls(
            name=data["name"],
            weeks_remaining=data.get("weeks_remaining", 0),
            stat_modifiers=dict(data.get("stat_modifiers", {})),
            recovery_started=data.get("recovery_started", True),
            can_deploy_while_injured=data.get("can_deploy_while_injured", True),
            pending_title=data.get("pending_title"),
            title_awarded=data.get("title_awarded", False),
        )
        

@dataclass
class EquipmentSlots:
    armor: str | None = None
    helm: str | None = None
    primary_weapon: str | None = None
    shield: str | None = None

    def get_slot_item_id(self, slot: EquipmentSlot) -> str | None:
        if slot == EquipmentSlot.ARMOR:
            return self.armor
        if slot == EquipmentSlot.HELM:
            return self.helm
        if slot == EquipmentSlot.PRIMARY_WEAPON:
            return self.primary_weapon
        if slot == EquipmentSlot.SHIELD:
            return self.shield
        return None

    def set_slot_item_id(self, slot: EquipmentSlot, item_id: str | None) -> None:
        if slot == EquipmentSlot.ARMOR:
            self.armor = item_id
        elif slot == EquipmentSlot.HELM:
            self.helm = item_id
        elif slot == EquipmentSlot.PRIMARY_WEAPON:
            self.primary_weapon = item_id
        elif slot == EquipmentSlot.SHIELD:
            self.shield = item_id
    


@dataclass
class Viking:
    name: str
    age: int
   
    # Core ratings, expected range 1-100 for now.
    # General category for stats:
    # Physical: Might, Skill, Vitality, Agility, Seamanship
    # Mental: Cunning, Leadership, Courage, Loyalty, Seamanship
    # Seamanship fits in both categories as it implies physical capacity and mental capacity at sea
    might: int
    skill: int
    cunning: int
    leadership: int
    courage: int
    vitality: int
    agility: int
    loyalty: int
    seamanship: int
    
    

    favored_god: FavoredGod
    
    title: str = ""    
    
    birth_month: int = 1
    birth_week: int = 1

    viking_class: VikingClass = VikingClass.RAIDER
    role: CrewRole = CrewRole.RAIDER
    
    original_stats: dict[str, int] = field(default_factory=dict)
    
    traits: list[Trait] = field(default_factory=list)
    equipment: EquipmentSlots = field(default_factory=EquipmentSlots)

    status: VikingStatus = VikingStatus.ACTIVE
    # INJURIES
    is_player: bool = False
    permanent_injuries: list[str] = field(default_factory=list)
    injuries: list[str] = field(default_factory=list)
    active_injuries: list[ActiveInjury] = field(default_factory=list)
    
    stat_potential: dict[str, int] = field(default_factory=dict)

    injury_weeks_remaining: int = 0
    
    stat_history: list[dict] = field(default_factory=list)
    injury_history: list[str] = field(default_factory=list)
    job_history: list[str] = field(default_factory=list)

    silver_wage: int = 1
    renown: int = 0
    kills: int = 0
    expeditions: int = 0

    viking_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def record_stat_history(self):
        self.stat_history.append({
            "age": self.age,
            "might": self.might,
            "skill": self.skill,
            "cunning": self.cunning,
            "leadership": self.leadership,
            "courage": self.courage,
            "vitality": self.vitality,
            "agility": self.agility,
            "seamanship": self.seamanship,
            "overall": self.overall_grade(),
            "potential": self.potential_overall_grade(),
        })
    
    def display_name(self) -> str:
        title = getattr(self, "title", "")

        if title:
            return f"{title} {self.name}"

        return self.name

    def has_blocking_injury(self) -> bool:
        return any(
            injury.weeks_remaining > 0
            and not injury.can_deploy_while_injured
            for injury in self.active_injuries
        )


    def is_available(self) -> bool:
        if self.status in {
            VikingStatus.DEAD,
            VikingStatus.DESERTED,
            VikingStatus.RETIRED,
        }:
            return False

        return not self.has_blocking_injury()
        
    def temporary_injury_modifier(self, stat_name: str) -> int:
        return sum(
            injury.stat_modifiers.get(stat_name, 0)
            for injury in self.active_injuries
            if injury.weeks_remaining > 0
        )


    def effective_stat(self, stat_name: str) -> int:
        base = getattr(self, stat_name)
        modifier = self.temporary_injury_modifier(stat_name)
        trait_bonus = self.get_trait_bonus(stat_name)

        return max(1, min(100, base + modifier + trait_bonus))

    def combat_score(self) -> int:
        might = self.effective_stat("might")
        skill = self.effective_stat("skill")
        courage = self.effective_stat("courage")

        return ((might * 2) + skill + courage) // 4

    def morale_score(self) -> int:
        courage = self.effective_stat("courage")
        loyalty = self.effective_stat("loyalty")
        leadership = self.effective_stat("leadership")
        
        return (courage + loyalty + leadership) // 3
            

    def scouting_score(self) -> int:
        cunning = self.effective_stat("cunning")
        skill = self.effective_stat("skill")
        
        return (cunning + skill) // 2

    def sailing_score(self) -> int:
        seamanship = self.effective_stat("seamanship")
        cunning = self.effective_stat("cunning")
        vitality = self.effective_stat("vitality")
    
        return ((seamanship * 2) + cunning + vitality) // 4

    def evasion_score(self) -> int:
        agility = self.effective_stat("agility")
        vitality = self.effective_stat("vitality")
        
        return ((agility * 2) + vitality) // 3

    def social_score(self) -> int:
        leadership = self.effective_stat("leadership")
        cunning = self.effective_stat("cunning")
        renown_bonus = min(100, 25 + self.renown * 5)

        return (
            leadership
            + cunning
            + renown_bonus
        ) // 3


    def command_score(self) -> int:
        leadership = self.effective_stat("leadership")
        courage = self.effective_stat("courage")
        renown_bonus = min(100, 25 + self.renown * 5)

        return (
            leadership
            + courage
            + renown_bonus
        ) // 3

    def endurance_score(self) -> int:
        vitality = self.effective_stat("vitality")
        courage = self.effective_stat("courage")
        might = self.effective_stat("might")
        
        return ((vitality * 2) + courage + might) // 4

    def skirmish_score(self) -> int:
        agility = self.effective_stat("agility")
        skill = self.effective_stat("skill")
        cunning = self.effective_stat("cunning")
        
        return (agility + skill + cunning) // 3

    def raiding_score(self) -> int:
        might = self.effective_stat("might")
        skill = self.effective_stat("skill")
        courage = self.effective_stat("courage")
        agility = self.effective_stat("agility")
    
        return (might + skill + courage + agility) // 4

    def navigation_score(self) -> int:
        seamanship = self.effective_stat("seamanship")
        cunning = self.effective_stat("cunning")
        skill = self.effective_stat("skill")
        
        return ((seamanship * 2) + cunning + skill) // 4

    def survival_score(self) -> int:
        vitality = self.effective_stat("vitality")
        cunning = self.effective_stat("cunning")
        seamanship = self.effective_stat("seamanship")
    
        return (vitality + cunning + seamanship) // 3 
        
    def overall_grade(self) -> str:
        avg = (
            self.effective_stat("might")
            + self.effective_stat("skill")
            + self.effective_stat("cunning")
            + self.effective_stat("leadership")
            + self.effective_stat("courage")
            + self.effective_stat("vitality")
            + self.effective_stat("agility")
            + self.effective_stat("seamanship")
        ) // 8

        if avg >= 95:
            return "S+"
        if avg >= 92:
            return "S"

        if avg >= 88:
            return "A+"
        if avg >= 84:
            return "A"
        if avg >= 80:
            return "A-"

        if avg >= 75:
            return "B+"
        if avg >= 68:
            return "B"
        if avg >= 62:
            return "B-"

        if avg >= 54:
            return "C+"
        if avg >= 46:
            return "C"
        if avg >= 38:
            return "C-"

        if avg >= 32:
            return "D+"
        if avg >= 26:
            return "D"
        if avg >= 20:
            return "D-"

        return "F" 

    @staticmethod
    def grade_from_score(score: int) -> str:
        if score >= 95:
            return "S+"
        if score >= 92:
            return "S"
        if score >= 88:
            return "A+"
        if score >= 84:
            return "A"
        if score >= 80:
            return "A-"
        if score >= 75:
            return "B+"
        if score >= 68:
            return "B"
        if score >= 62:
            return "B-"
        if score >= 54:
            return "C+"
        if score >= 46:
            return "C"
        if score >= 38:
            return "C-"
        if score >= 32:
            return "D+"
        if score >= 26:
            return "D"
        if score >= 20:
            return "D-"
        return "F"


    def potential_overall_grade(self) -> str:
        if not self.stat_potential:
            return "???"

        avg = (
            self.stat_potential.get("might", self.might)
            + self.stat_potential.get("skill", self.skill)
            + self.stat_potential.get("cunning", self.cunning)
            + self.stat_potential.get("leadership", self.leadership)
            + self.stat_potential.get("courage", self.courage)
            + self.stat_potential.get("vitality", self.vitality)
            + self.stat_potential.get("agility", self.agility)
            + self.stat_potential.get("seamanship", self.seamanship)
        ) // 8

        return self.grade_from_score(avg)      

    def add_injury(
        self,
        injury_name: str,
        weeks_remaining: int = 0,
        stat_modifiers: dict[str, int] | None = None,
        recovery_started: bool = False,
        can_deploy_while_injured: bool = True,
        pending_title: str | None = None,
        title_awarded: bool = False,
    ) -> None:
        self.injuries.append(injury_name)

        if weeks_remaining > 0:
            self.active_injuries.append(
                ActiveInjury(
                    name=injury_name,
                    weeks_remaining=weeks_remaining,
                    stat_modifiers=dict(stat_modifiers or {}),
                    recovery_started=recovery_started,
                    can_deploy_while_injured=can_deploy_while_injured,
                    pending_title=pending_title,
                    title_awarded=title_awarded,
                )
            )

        self.injury_weeks_remaining = max(
            [injury.weeks_remaining for injury in self.active_injuries],
            default=0,
        )
                
    def suffer_permanent_injury(self, injury_name: str) -> None:
        self.permanent_injuries.append(injury_name)
        self.status = VikingStatus.WOUNDED    
        
    def start_injury_recovery(self) -> None:
        for injury in self.active_injuries:
            injury.recovery_started = True    

    def tick_injuries(self) -> list[str]:
        healed = []

        for injury in self.active_injuries:
            if not injury.recovery_started:
                continue

            injury.weeks_remaining -= 1

            if injury.weeks_remaining <= 0:
                healed.append(injury.name)

        title_logs = self.reveal_recovered_titles()

        self.active_injuries = [
            injury for injury in self.active_injuries
            if injury.weeks_remaining > 0
        ]

        self.injury_weeks_remaining = max(
            [injury.weeks_remaining for injury in self.active_injuries],
            default=0,
        )

        self.injuries = [
            injury.name
            for injury in self.active_injuries
        ]

        if not self.active_injuries:
            if self.status == VikingStatus.WOUNDED:
                self.status = VikingStatus.ACTIVE

        return healed + title_logs

    def recover_from_injuries(self) -> None:
        self.injuries.clear()
        self.active_injuries.clear()
        self.injury_weeks_remaining = 0

        if self.status == VikingStatus.WOUNDED:
            self.status = VikingStatus.ACTIVE
  
    def get_trait_bonus(self, stat_name: str) -> int:
        total = 0

        for trait in self.traits:
            total += getattr(trait, f"{stat_name}_bonus", 0)

        return total
  
    def apply_title_effects(self, title: str) -> dict[str, int]:
        effects = TITLE_EFFECTS.get(title, {})

        for stat_name, bonus in effects.items():
            if stat_name == "renown":
                self.renown += bonus
                continue

            current = getattr(self, stat_name)
            setattr(self, stat_name, max(1, min(100, current + bonus)))

        return effects
    
    def reveal_recovered_titles(self) -> list[str]:
        logs = []

        for injury in self.active_injuries:
            if injury.weeks_remaining > 0:
                continue

            if not injury.pending_title:
                continue

            if injury.title_awarded:
                continue

            title = injury.pending_title
            old_name = self.name

            parts = self.name.split()
            base_name = parts[0] if parts else self.name

            if parts and parts[0] == "Jarl" and len(parts) >= 2:
                base_name = " ".join(parts[:2])

            if title.startswith("the "):
                self.name = f"{base_name} {title}"
            else:
                self.name = f"{base_name} {title}"

          
            effects = self.apply_title_effects(title)
            injury.title_awarded = True

            if effects:
                effect_text = ", ".join(
                    f"{stat} {bonus:+}"
                    for stat, bonus in effects.items()
                )

                logs.append(
                    f"{old_name} has recovered, but not unchanged. "
                    f"They are now known as {self.name}. "
                    f"Title effects: {effect_text}."
                )
            else:
                logs.append(
                    f"{old_name} has recovered, but not unchanged. "
                    f"They are now known as {self.name}."
                )

        return logs        
            
    def is_combat_class(self) -> bool:
        return self.viking_class in {
            VikingClass.RAIDER,
            VikingClass.SHIELDMAIDEN,
            VikingClass.ARCHER,
        }

    def is_support_class(self) -> bool:
        return self.viking_class in {
            VikingClass.HERBALIST,
            VikingClass.SAILOR,
            VikingClass.SCOUT,
            VikingClass.TRICKSTER,
            VikingClass.HERSIR,
        }            

    def to_dict(self) -> dict:
        return {
            "viking_id": self.viking_id,
            "name": self.name,
            "age": self.age,
            "birth_month": self.birth_month,
            "birth_week": self.birth_week,
            "might": self.might,
            "skill": self.skill,
            "cunning": self.cunning,
            "leadership": self.leadership,
            "courage": self.courage,
            "vitality": self.vitality,
            "agility": self.agility,
            "loyalty": self.loyalty,
            "seamanship": self.seamanship,
            "original_stats": dict(self.original_stats),
            "favored_god": self.favored_god.value,
            "title": self.title,            
            "viking_class": self.viking_class.value,
            "role": self.role.value,
            "traits": [trait.name for trait in self.traits],
            "equipment": {
                "armor": self.equipment.armor,
                "helm": self.equipment.helm,
                "primary_weapon": self.equipment.primary_weapon,
                "shield": self.equipment.shield,
            },
            "status": self.status.value,
            "injuries": list(self.injuries),
            "injury_weeks_remaining": self.injury_weeks_remaining,
            "active_injuries": [
                injury.to_dict()
                for injury in self.active_injuries
            ],
            "stat_potential": dict(self.stat_potential),
            "stat_history": self.stat_history,
            "injury_history": self.injury_history,
            "job_history": self.job_history,
            "is_player": self.is_player,
            "permanent_injuries": list(self.permanent_injuries),
            "silver_wage": self.silver_wage,
            "renown": self.renown,
            "kills": self.kills,
            "expeditions": self.expeditions,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Viking":
        equipment_data = data.get("equipment", {})
        from traits import ALL_TRAITS_BY_NAME

        return cls(
            viking_id=data.get("viking_id", str(uuid.uuid4())),
            name=data["name"],
            age=data["age"],
            birth_month=data.get("birth_month", 1),
            birth_week=data.get("birth_week", 1),
            might=data["might"],
            skill=data["skill"],
            cunning=data["cunning"],
            leadership=data.get("leadership", 5),
            courage=data["courage"],
            vitality=data.get("vitality", 5),
            agility=data.get("agility", data.get("vitality", 50)),
            loyalty=data["loyalty"],
            seamanship=data.get("seamanship", 5),
            original_stats=dict(data.get("original_stats", {})),
            favored_god=FavoredGod(data["favored_god"]),
            title=data.get("title", ""),            
            viking_class=VikingClass(data.get("viking_class", "Raider")),
            role=CrewRole(data.get("role", "Raider")),
            traits=[
                ALL_TRAITS_BY_NAME[name]
                for name in data.get("traits", [])
                if name in ALL_TRAITS_BY_NAME
            ],
            equipment=EquipmentSlots(
                armor=equipment_data.get("armor"),
                helm=equipment_data.get("helm"),
                primary_weapon=equipment_data.get("primary_weapon"),
                shield=equipment_data.get("shield"),
            ),
            status=VikingStatus(data.get("status", VikingStatus.ACTIVE.value)),
            injuries=list(data.get("injuries", [])),
            injury_weeks_remaining=data.get("injury_weeks_remaining", 0),
            active_injuries=[
                ActiveInjury.from_dict(injury_data)
                for injury_data in data.get("active_injuries", [])
            ],
            stat_potential=dict(data.get("stat_potential", {})),
            stat_history=data.get("stat_history", []),
            injury_history=data.get("injury_history", []),
            job_history=data.get("job_history", []),
            is_player=data.get("is_player", False),
            permanent_injuries=list(data.get("permanent_injuries", [])),
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

    # Crew stores Viking IDs.
    crew: list[str] = field(default_factory=list)

    hull: int | None = None
    status: ShipStatus = ShipStatus.READY

    hull_level: int = 0
    cargo_level: int = 0
    crew_level: int = 0
    sail_level: int = 0
    navigation_level: int = 0

    ship_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    BASE_RANGE = 1
    BASE_HULL = 30
    BASE_CARGO = 16
    BASE_CREW = 6
    MIN_CREW = 1

    def __post_init__(self) -> None:
        if self.hull is None:
            self.hull = self.max_hull

        self.hull = min(self.hull, self.max_hull)

        if self.hull <= 0:
            self.status = ShipStatus.LOST

    def upgrade_levels(self) -> dict:
        return {
            "hull": self.hull_level,
            "cargo": self.cargo_level,
            "crew": self.crew_level,
            "sail": self.sail_level,
            "navigation": self.navigation_level,
        }

    def _upgrades_for_levels(self):
        from ship_upgrades import ShipPart, get_ship_upgrade

        level_by_part = {
            ShipPart.HULL: self.hull_level,
            ShipPart.CARGO: self.cargo_level,
            ShipPart.CREW: self.crew_level,
            ShipPart.SAIL: self.sail_level,
            ShipPart.NAVIGATION: self.navigation_level,
        }

        upgrades = []

        for part, level in level_by_part.items():
            for upgrade_level in range(1, level + 1):
                upgrade = get_ship_upgrade(part, upgrade_level)

                if upgrade:
                    upgrades.append(upgrade)

        return upgrades

    def _sum_upgrade_attr(self, attr_name: str) -> int:
        return sum(
            getattr(upgrade, attr_name, 0)
            for upgrade in self._upgrades_for_levels()
        )

    @property
    def max_hull(self) -> int:
        return self.BASE_HULL + self._sum_upgrade_attr("hull_bonus")

    @property
    def min_crew(self) -> int:
        return self.MIN_CREW

    @property
    def max_crew(self) -> int:
        return self.BASE_CREW + self._sum_upgrade_attr("crew_bonus")

    @property
    def cargo_capacity(self) -> int:
        return self.BASE_CARGO + self._sum_upgrade_attr("cargo_bonus")

    @property
    def range(self) -> int:
        return self.BASE_RANGE + self._sum_upgrade_attr("range_bonus")

    @property
    def sail(self) -> int:
        return self._sum_upgrade_attr("sail_bonus")

    @property
    def navigation(self) -> int:
        return self._sum_upgrade_attr("navigation_bonus")

    @property
    def food_cost_reduction(self) -> int:
        return self._sum_upgrade_attr("food_cost_reduction")

    @property
    def duration_reduction_chance(self) -> int:
        return self._sum_upgrade_attr("duration_reduction_chance")

    def get_part_level(self, part) -> int:
        from ship_upgrades import ShipPart

        if part == ShipPart.HULL:
            return self.hull_level

        if part == ShipPart.CARGO:
            return self.cargo_level

        if part == ShipPart.CREW:
            return self.crew_level

        if part == ShipPart.SAIL:
            return self.sail_level

        if part == ShipPart.NAVIGATION:
            return self.navigation_level

        return 0

    def set_part_level(self, part, level: int) -> None:
        from ship_upgrades import ShipPart

        level = max(0, level)

        old_max_hull = self.max_hull

        if part == ShipPart.HULL:
            self.hull_level = level
        elif part == ShipPart.CARGO:
            self.cargo_level = level
        elif part == ShipPart.CREW:
            self.crew_level = level
        elif part == ShipPart.SAIL:
            self.sail_level = level
        elif part == ShipPart.NAVIGATION:
            self.navigation_level = level

        if part == ShipPart.HULL:
            hull_gain = self.max_hull - old_max_hull
            if hull_gain > 0 and self.hull is not None:
                self.hull = min(self.max_hull, self.hull + hull_gain)

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

        required_roles = {
            CrewRole.CAPTAIN: 1,
        }

        missing: dict[CrewRole, int] = {}

        for required_role, required_count in required_roles.items():
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
        if amount <= 0:
            return

        self.hull = min(self.max_hull, self.hull + amount)

        if self.hull >= self.max_hull:
            self.status = ShipStatus.READY
        elif self.hull > 0:
            self.status = ShipStatus.DAMAGED
        else:
            self.status = ShipStatus.LOST

    def is_usable(self) -> bool:
        return (
            self.status in {ShipStatus.READY, ShipStatus.DAMAGED}
            and self.hull is not None
            and self.hull > 0
        )

    def to_dict(self) -> dict:
        return {
            "ship_id": self.ship_id,
            "name": self.name,
            "crew": list(self.crew),
            "hull": self.hull,
            "status": self.status.value,

            "hull_level": self.hull_level,
            "cargo_level": self.cargo_level,
            "crew_level": self.crew_level,
            "sail_level": self.sail_level,
            "navigation_level": self.navigation_level,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Ship":
        """
        Supports both the new upgrade-based ship save format and old saves
        that still included ship_class.
        """
        legacy_ship_class = data.get("ship_class", {})

        return cls(
            ship_id=data.get("ship_id", str(uuid.uuid4())),
            name=data.get("name", legacy_ship_class.get("name", "Sea Wolf")),
            crew=list(data.get("crew", [])),
            hull=data.get("hull"),
            status=ShipStatus(data.get("status", ShipStatus.READY.value)),

            hull_level=data.get("hull_level", 0),
            cargo_level=data.get("cargo_level", 0),
            crew_level=data.get("crew_level", 0),
            sail_level=data.get("sail_level", 0),
            navigation_level=data.get("navigation_level", 0),
        )


#====================================================
# JOBS
#====================================================

class JobType(str, Enum):
    # Special Jobs
    TRIAL_BY_COMBAT = "Trial by Combat"

    # Scandinavian Jobs
    BLOOD_FEUD = "Blood Feud"
    THING_GUARD = "Thing Guard"
    SACRED_HUNT = "Sacred Hunt"
    SETTLER_ESCORT = "Settler Escort"
    OATH_COLLECTION = "Oath Collection"
    OUTLAW_HUNT = "Outlaw Hunt"
    FUNERAL_VOYAGE = "Funeral Voyage"
    
    COASTAL_RAID = "Coastal Raid"
    RIVER_RAID = "River Raid"
    # Special Job
    LINDISFARNE_RAID = "Lindisfarne Raid"
    
    MONASTERY_RAID = "Monastery Raid"
    ESCORT_VOYAGE = "Escort Voyage"
    TRIBUTE_COLLECTION = "Tribute Collection"
    JOIN_JARL_WARBAND = "Join Jarl's Warband"
    SCOUT_COASTLINE = "Scout Coastline"
    FEUD_ATTACK = "Feud Attack"
    RESCUE_CAPTIVE = "Rescue Captive"
    TRADE_VOYAGE = "Trade Voyage"
    
    LIVESTOCK_RAID = "Livestock Raid"
    THRALL_RAID = "Thrall Raid"
    TIMBER_EXPEDITION = "Timber Expedition"
    SALVAGE_EXPEDITION = "Salvage Expedition"
    FISHING_EXPEDITION = "Fishing Expedition"
    
    WINTER_HUNT = "Winter Hunt"
    TIMBER_WORK = "Timber Work"
    GUARD_DUTY = "Guard Duty"
    LOCAL_TRADE = "Local Trade"    


class JobRisk(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    EXTREME = "Extreme"
    
class TravelType(str, Enum):
    COASTAL = "Coastal Waters"
    RIVER = "Rivers"
    OVERLAND = "Overland"
    OPEN_OCEAN = "Open Ocean"
    DEEP_SEA = "Deep Sea"
    FROZEN = "Frozen Waters"    


@dataclass
class Job:
    name: str
    job_type: JobType

    allowed_seasons: list[Season]
    duration_weeks: int

    required_range: int
    required_min_crew: int

    difficulty: int
    danger: int

    guaranteed_silver: int
    guaranteed_food: int
    reward_renown: int
    
    reward_thralls: int = 0
    reward_ship_timber: int = 0
    reward_fine_metal: int = 0

    location_name: str = ""
    travel_type: TravelType = TravelType.COASTAL

    guaranteed_item_rewards: list[str] = field(default_factory=list)
    possible_item_rewards: list[str] = field(default_factory=list)

    random_silver_min: int = 0
    random_silver_max: int = 0
    random_food_min: int = 0
    random_food_max: int = 0

   # possible_item_rewards: list[str] = field(default_factory=list)

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

    def time_can_fit(
        self,
        month: int,
        week_of_month: int,
        max_spillover_weeks: int = MAX_SEASON_SPILLOVER_WEEKS,
    ) -> bool:
        current_season = get_season_for_month(month)

        if current_season not in self.allowed_seasons:
            return False

        week_of_season = get_week_of_season(month, week_of_month)
        weeks_remaining_in_season = WEEKS_PER_SEASON - week_of_season + 1

        if self.duration_weeks <= weeks_remaining_in_season:
            return True

        spillover_weeks = self.duration_weeks - weeks_remaining_in_season
        return spillover_weeks <= max_spillover_weeks

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "name": self.name,
            "job_type": self.job_type.value,
            "location_name": self.location_name,
            "travel_type": self.travel_type.value,
            "allowed_seasons": [season.value for season in self.allowed_seasons],
            "duration_weeks": self.duration_weeks,
            "required_range": self.required_range,
            "required_min_crew": self.required_min_crew,
            "difficulty": self.difficulty,
            "danger": self.danger,
            "guaranteed_silver": self.guaranteed_silver,
            "guaranteed_food": self.guaranteed_food,
            "reward_renown": self.reward_renown,
            "random_silver_min": self.random_silver_min,
            "random_silver_max": self.random_silver_max,
            "random_food_min": self.random_food_min,
            "random_food_max": self.random_food_max,
            "reward_thralls": self.reward_thralls,
            "reward_ship_timber": self.reward_ship_timber,
            "reward_fine_metal": self.reward_fine_metal,
            "guaranteed_item_rewards": list(self.guaranteed_item_rewards),
            "possible_item_rewards": list(self.possible_item_rewards),
            "employer": self.employer,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        return cls(
            job_id=data.get("job_id", str(uuid.uuid4())),
            name=data["name"],
            job_type=JobType(data["job_type"]),
            location_name=data.get("location_name", ""),            
            travel_type=TravelType(data.get("travel_type", TravelType.COASTAL.value)),
            allowed_seasons=[Season(season) for season in data["allowed_seasons"]],
            duration_weeks=data["duration_weeks"],
            required_range=data["required_range"],
            required_min_crew=data["required_min_crew"],
            difficulty=data["difficulty"],
            danger=data["danger"],
            guaranteed_silver=data["guaranteed_silver"],
            guaranteed_food=data["guaranteed_food"],
            reward_renown=data["reward_renown"],
            random_silver_min=data.get("random_silver_min", 0),
            random_silver_max=data.get("random_silver_max", 0),
            random_food_min=data.get("random_food_min", 0),
            random_food_max=data.get("random_food_max", 0),
            reward_thralls=data.get("reward_thralls", 0),
            reward_ship_timber=data.get("reward_ship_timber", 0),
            reward_fine_metal=data.get("reward_fine_metal", 0),
            guaranteed_item_rewards=list(data.get("guaranteed_item_rewards", [])),            
            possible_item_rewards=list(data.get("possible_item_rewards", [])),
            employer=data.get("employer"),
            description=data.get("description", ""),
        )