from __future__ import annotations

from dataclasses import dataclass, field
from expedition import resolve_expedition
from roster import generate_viking, generate_basic_equipment_for_viking
from models import CrewRole, VikingClass, JobType
from recruits import RecruitPool
from items import Item, WeaponCategory, EquipmentSlot
from village import BuildingType
from sagas import SagaEntry, make_saga_entry
from injury import INJURY_TABLES, InjuryType, InjurySeverity, get_templates, apply_stat_modifiers
from psych import roll_psych_condition, apply_psych_condition, PsychType
from jobs import generate_jobs_for_location
from stories import (
    get_available_story_jobs,
    location_is_unlocked,
    apply_story_completion,
)
import uuid
import random

from models import (
    Viking,
    Ship,
    Job,
    Season,
    get_season_for_month,
    get_month_name,
    WEEKS_PER_MONTH,
)
from village import Village


@dataclass
class Campaign:
    name: str
    ship: Ship
    vikings: dict[str, Viking]
    village: Village

    year: int = 1
    month: int = 1
    week_of_month: int = 1

    silver: int = 50
    food: int = 30
    renown: int = 0
    
    thralls: int = 2
    assigned_thralls: int = 0
    ship_timber: int = 8
    fine_metal: int = 1
    
    inventory: dict[str, Item] = field(default_factory=dict)
    
    recruit_pool: RecruitPool = field(default_factory=RecruitPool)

    completed_jobs: list[dict] = field(default_factory=list)
    available_jobs: list[Job] = field(default_factory=list)
    
    pending_ship_upgrade_part: str | None = None
    pending_ship_upgrade_level: int = 0
    pending_ship_upgrade_name: str | None = None
    pending_ship_weeks_remaining: int = 0    

    campaign_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    odins_hall: list[dict] = field(default_factory=list)
    
    world_flags: set[str] = field(default_factory=set)
    
    retired_vikings: list[dict] = field(default_factory=list)
    
    saga_entries: list[SagaEntry] = field(default_factory=list)
    
    # DEBUG
    debug_skip_birthdays: bool = False
    debug_disable_injuries: bool = False

    @property
    def season(self) -> Season:
        return get_season_for_month(self.month)

    @property
    def month_name(self) -> str:
        return get_month_name(self.month)

    def calendar_label(self) -> str:
        return f"Year {self.year}, {self.month_name}, Week {self.week_of_month}"
        
    def add_item(self, item: Item) -> None:
        self.inventory[item.item_id] = item


    def remove_item(self, item_id: str) -> Item | None:
        return self.inventory.pop(item_id, None)


    def get_inventory_list(self) -> list[Item]:
        return list(self.inventory.values())
        
        
    def get_equipped_item_ids(self) -> set[str]:
        equipped_ids = set()

        for viking in self.vikings.values():
            equipped_ids.update([
                viking.equipment.armor,
                viking.equipment.helm,
                viking.equipment.primary_weapon,
                getattr(viking.equipment, "secondary_weapon", None),
                viking.equipment.shield,
            ])

        equipped_ids.discard(None)
        return equipped_ids


    def get_unequipped_items(self) -> list[Item]:
        equipped_ids = self.get_equipped_item_ids()

        return [
            item for item in self.inventory.values()
            if item.item_id not in equipped_ids
        ]


    def buy_trader_item(self, template_item: Item) -> tuple[bool, str]:
        from items import copy_item

        cost = template_item.value

        if self.silver < cost:
            return False, f"Not enough silver. Need {cost}, have {self.silver}."

        item = copy_item(template_item)
        self.add_item(item)
        self.silver -= cost

        return True, f"Bought {item.name} for {cost} silver."


    def sell_item_to_trader(self, item_id: str) -> tuple[bool, str]:
        equipped_ids = self.get_equipped_item_ids()

        if item_id in equipped_ids:
            return False, "You cannot sell equipped items."

        item = self.inventory.get(item_id)

        if not item:
            return False, "Item not found."

        sale_value = max(1, item.value // 2)

        self.remove_item(item_id)
        self.silver += sale_value

        return True, f"Sold {item.name} for {sale_value} silver."        
        
    def viking_can_equip_item(self, viking: Viking, item: Item) -> tuple[bool, str]:
        if item.item_type.value == "Weapon":
            if viking.viking_class == VikingClass.HERBALIST:
                if item.weapon_category != WeaponCategory.KNIFE:
                    return False, "Herbalists can only equip knives."

            if viking.viking_class == VikingClass.ARCHER:
                if item.weapon_category != WeaponCategory.BOW:
                    return False, "Archers can only equip bows."

            if item.weapon_category == WeaponCategory.BOW:
                if viking.equipment.shield:
                    return False, "A viking cannot equip a bow while using a shield."

        if item.slot == EquipmentSlot.SHIELD:
            primary = self.inventory.get(viking.equipment.primary_weapon)

            if primary and primary.weapon_category == WeaponCategory.BOW:
                return False, "A viking using a bow cannot equip a shield."

            if viking.viking_class in {VikingClass.ARCHER, VikingClass.HERBALIST}:
                return False, f"{viking.viking_class.value}s cannot equip shields."

           #if viking.viking_class == VikingClass.BERSERKER:
            #   return False, "Berserkers cannot equip shields."

        return True, ""    


    def equip_item_to_viking(self, viking_id: str, item_id: str) -> tuple[bool, str]:
        viking = self.vikings.get(viking_id)
        if not viking:
            return False, "No viking found."

        item = self.inventory.get(item_id)
        if not item:
            return False, "No item found."

        if not item.is_equippable() or item.slot is None:
            return False, f"{item.name} cannot be equipped."
            
        can_equip, reason = self.viking_can_equip_item(viking, item)

        if not can_equip:
            return False, reason    

        old_item_id = viking.equipment.get_slot_item_id(item.slot)

        viking.equipment.set_slot_item_id(item.slot, item.item_id)

        if old_item_id:
            return True, f"{viking.name} equipped {item.name}, replacing previous equipment."

        return True, f"{viking.name} equipped {item.name}."


    def unequip_item_from_viking(self, viking_id: str, slot) -> tuple[bool, str]:
        viking = self.vikings.get(viking_id)
        if not viking:
            return False, "No viking found."

        old_item_id = viking.equipment.get_slot_item_id(slot)

        if not old_item_id:
            return False, "Nothing equipped in that slot."

        item = self.inventory.get(old_item_id)
        item_name = item.name if item else "Unknown Item"

        viking.equipment.set_slot_item_id(slot, None)

        return True, f"{viking.name} unequipped {item_name}." 
        
    def item_total_bonus(self, item: Item | None) -> int:
        if not item:
            return 0

        return (
            item.might_bonus
            + item.skill_bonus
            + item.cunning_bonus
            + item.leadership_bonus
            + item.courage_bonus
            + item.vitality_bonus
            + item.loyalty_bonus
            + item.seamanship_bonus
        )


    def auto_equip_best_items(self) -> list[str]:
        logs = []

        vikings = [
            viking for viking in self.vikings.values()
            if viking.status.value not in {"Dead", "Retired"}
        ]

        # Jarl first, then active crew, then reserves.
        vikings.sort(
            key=lambda v: (
                0 if v.is_player else 1,
                0 if v.viking_id in self.ship.crew else 1,
                v.name,
            )
        )

        for viking in vikings:
            improved = True

            while improved:
                improved = False

                unequipped_items = [
                    item for item in self.get_unequipped_items()
                    if item.is_equippable()
                    and item.slot is not None
                    and self.viking_can_equip_item(viking, item)[0]
                ]

                legal_improvements = []

                for item in unequipped_items:
                    current_item_id = viking.equipment.get_slot_item_id(item.slot)
                    current_item = self.inventory.get(current_item_id) if current_item_id else None

                    item_score = self.item_total_bonus(item)
                    current_score = self.item_total_bonus(current_item)

                    if item_score > current_score:
                        legal_improvements.append((item_score, item.value, item))

                if not legal_improvements:
                    continue

                legal_improvements.sort(
                    key=lambda entry: (entry[0], entry[1]),
                    reverse=True,
                )

                _, _, best_item = legal_improvements[0]

                old_item_id = viking.equipment.get_slot_item_id(best_item.slot)
                old_item = self.inventory.get(old_item_id) if old_item_id else None

                viking.equipment.set_slot_item_id(best_item.slot, best_item.item_id)

                if old_item:
                    logs.append(
                        f"{viking.name} equipped {best_item.name}, replacing {old_item.name}."
                    )
                else:
                    logs.append(f"{viking.name} equipped {best_item.name}.")

                improved = True

        if not logs:
            logs.append("No equipment improvements found.")

        return logs        
    
    def add_saga_entry(
        self,
        entry_type: str,
        text: str,
        viking_ids: list[str] | None = None,
        job_id: str | None = None,
    ) -> None:
        self.saga_entries.append(
            make_saga_entry(
                year=self.year,
                month=self.month,
                week=self.week_of_month,
                entry_type=entry_type,
                text=text,
                viking_ids=viking_ids or [],
                job_id=job_id,
            )
        )
        
    def highest_completed_shipyard_level(self) -> int:
        levels = [
            building.level
            for building in self.village.get_buildings(BuildingType.SHIPYARD)
            if not building.is_under_construction
        ]

        return max(levels) if levels else 0


    def highest_completed_carpenters_hut_level(self) -> int:
        levels = [
            building.level
            for building in self.village.get_buildings(BuildingType.CARPENTERS_HUT)
            if not building.is_under_construction
        ]

        return max(levels) if levels else 0


    def start_ship_upgrade(self, part) -> tuple[bool, str]:
        from ship_upgrades import ShipPart, get_next_ship_upgrade

        if isinstance(part, str):
            part = ShipPart(part)

        if part == ShipPart.NAVIGATION:
            return False, "Navigation upgrades are earned through story jobs."

        if self.pending_ship_upgrade_part:
            return False, (
                f"{self.pending_ship_upgrade_name} is already underway "
                f"({self.pending_ship_weeks_remaining} weeks remaining)."
            )

        current_level = self.ship.get_part_level(part)
        upgrade = get_next_ship_upgrade(part, current_level)
        # Sunstone Gate
        if (
            part == ShipPart.SAIL
            and upgrade
            and upgrade.level >= 2
            and "sunstone_navigation_completed" not in self.world_flags
        ):
            return False, (
                "You need Sunstone Navigation before improving your sails "
                "for longer voyages."
            )        

        if not upgrade:
            return False, f"{part.value} is already fully upgraded."

        shipyard_level = self.highest_completed_shipyard_level()
        carpenters_level = self.highest_completed_carpenters_hut_level()

        if shipyard_level < upgrade.required_shipyard_level:
            return False, (
                f"{upgrade.name} requires Shipwright "
                f"Lv.{upgrade.required_shipyard_level}."
            )

        if carpenters_level < upgrade.required_carpenters_hut_level:
            return False, (
                f"{upgrade.name} requires Woodwright "
                f"Lv.{upgrade.required_carpenters_hut_level}."
            )

        if self.silver < upgrade.silver_cost:
            return False, (
                f"Not enough silver. Need {upgrade.silver_cost}, "
                f"have {self.silver}."
            )

        if self.ship_timber < upgrade.ship_timber_cost:
            return False, (
                f"Not enough ship timber. Need {upgrade.ship_timber_cost}, "
                f"have {self.ship_timber}."
            )

        if self.fine_metal < upgrade.fine_metal_cost:
            return False, (
                f"Not enough fine metal. Need {upgrade.fine_metal_cost}, "
                f"have {self.fine_metal}."
            )

        self.silver -= upgrade.silver_cost
        self.ship_timber -= upgrade.ship_timber_cost
        self.fine_metal -= upgrade.fine_metal_cost

        self.pending_ship_upgrade_part = upgrade.part.value
        self.pending_ship_upgrade_level = upgrade.level
        self.pending_ship_upgrade_name = upgrade.name
        self.pending_ship_weeks_remaining = upgrade.build_weeks

        return True, (
            f"Started {upgrade.name}. "
            f"It will take {upgrade.build_weeks} weeks."
        )


    def advance_ship_construction(self) -> str | None:
        from ship_upgrades import ShipPart

        if not self.pending_ship_upgrade_part:
            return None

        self.pending_ship_weeks_remaining -= 1

        if self.pending_ship_weeks_remaining > 0:
            return None

        part = ShipPart(self.pending_ship_upgrade_part)
        self.ship.set_part_level(part, self.pending_ship_upgrade_level)

        finished_name = self.pending_ship_upgrade_name

        self.pending_ship_upgrade_part = None
        self.pending_ship_upgrade_level = 0
        self.pending_ship_upgrade_name = None
        self.pending_ship_weeks_remaining = 0

        return f"Ship upgrade complete: {finished_name}."        
        

    def generate_seasonal_jobs(self) -> None:
        from locations import get_locations_for_ship_range

        locations = get_locations_for_ship_range(self.ship.range)

        generated_jobs: list[Job] = []

        story_jobs = get_available_story_jobs(self)

        if (
            story_jobs
            and "intro_trial_completed" not in self.world_flags
        ):
            self.available_jobs = story_jobs
            return

        generated_jobs.extend(story_jobs)

        for location in locations:
            if not location_is_unlocked(self, location.name):
                continue

            # Story-only locations should not generate normal jobs.
            if location.name == "The High Seat":
                continue

            job_count = 2 + random.randint(2, 4)

            jobs = generate_jobs_for_location(
                location=location,
                month=self.month,
                week_of_month=self.week_of_month,
                ship=self.ship,
                count=job_count,
            )

            generated_jobs.extend(jobs)

        self.available_jobs = generated_jobs


    def maybe_refresh_seasonal_jobs(self) -> None:
        if self.month in {1, 5, 9} and self.week_of_month == 1:
            self.generate_seasonal_jobs()

    def get_available_jobs(self, location=None) -> list[Job]:
        if not self.available_jobs:
            self.generate_seasonal_jobs()

        if location is None:
            return list(self.available_jobs)

        return [
            job for job in self.available_jobs
            if job.location_name == location.name
        ]


    def remove_available_job(self, job: Job) -> None:
        self.available_jobs = [
            available_job for available_job in self.available_jobs
            if available_job.job_id != job.job_id
        ]        

        
    def get_discovered_locations(self):
        from locations import get_locations_for_ship_range
        from stories import location_is_unlocked

        locations = get_locations_for_ship_range(self.ship.range)

        return [
            location for location in locations
            if location_is_unlocked(self, location.name)
        ]      
        
    def refresh_recruit_pool(self) -> None:
        self.recruit_pool.refresh(
        village=self.village,
        year=self.year,
        season=self.season,
    )
    
    def living_roster_count(self) -> int:
        return sum(
            1 for viking in self.vikings.values()
            if viking.status.value not in {"Dead", "Retired"}
        )
        
    def hire_recruit(self, candidate_id: str) -> tuple[bool, str]:
        from village import RECRUIT_COST

        if not self.village.can_recruit_viking(self.living_roster_count()):
            return False, "Your barracks are full."

        if self.silver < RECRUIT_COST:
            return False, f"Not enough silver. Need {RECRUIT_COST}, have {self.silver}."

        candidate = self.recruit_pool.remove_candidate(candidate_id)

        if not candidate:
            return False, "Recruit not found."

        recruit = candidate.viking
        
        basic_items = generate_basic_equipment_for_viking(recruit)

        for item in basic_items:
            self.add_item(item)

        self.vikings[recruit.viking_id] = recruit
        self.add_saga_entry(
            entry_type="recruit_joined",
            text=f"{recruit.name} joined the crew of {self.name}.",
            viking_ids=[recruit.viking_id],
        )
        self.silver -= RECRUIT_COST

        added_to_ship = self.ship.add_crew_member(recruit.viking_id)

        if added_to_ship:
            return True, f"Hired {recruit.name} and added them to the ship."

        return True, f"Hired {recruit.name}. Your ship is full, so they remain in reserve."

    
    def recruit_basic_viking(self) -> tuple[bool, str]:
        from village import RECRUIT_COST
        from models import VikingClass

        if not self.village.can_recruit_viking(self.living_roster_count()):
            return False, "Your barracks are full."

        if self.silver < RECRUIT_COST:
            return False, f"Not enough silver. Need {RECRUIT_COST}, have {self.silver}."

        available_classes = [
            VikingClass.RAIDER,
            VikingClass.SAILOR,
        ]

        recruit_class = random.choice(available_classes)
        recruit = generate_viking(CrewRole.RAIDER, viking_class=recruit_class)
        
        basic_items = generate_basic_equipment_for_viking(recruit)

        for item in basic_items:
            self.add_item(item)

        self.vikings[recruit.viking_id] = recruit
        self.silver -= RECRUIT_COST

        added_to_ship = self.ship.add_crew_member(recruit.viking_id)

        if added_to_ship:
            return True, f"Recruited {recruit.name} and added them to the ship."

        return True, f"Recruited {recruit.name}. Your ship is full, so they remain in reserve."
        
    def active_crew_count(self) -> int:
        return len(self.get_active_crew_list())

    def clamp_food_storage(self) -> None:
        max_food = self.village.food_storage_capacity()
        self.food = min(self.food, max_food)
        
    def clamp_ship_timber_storage(self) -> None:
        self.ship_timber = min(
            self.ship_timber,
            self.village.timber_storage_capacity(),
        )


    def clamp_fine_metal_storage(self) -> None:
        self.fine_metal = min(
            self.fine_metal,
            self.village.fine_metal_storage_capacity(),
        )


    def clamp_physical_resources(self) -> None:
        self.clamp_food_storage()
        self.clamp_thralls_to_capacity()
        self.clamp_ship_timber_storage()
        self.clamp_fine_metal_storage()        
        
    def available_thralls(self) -> int:
        return max(0, self.thralls - self.assigned_thralls)


    def clamp_thralls_to_capacity(self) -> None:
        self.thralls = min(self.thralls, self.village.thrall_capacity())
        self.assigned_thralls = min(self.assigned_thralls, self.thralls)    

    def calculate_food_cost(self, job: Job) -> int:
        base_cost = (self.active_crew_count() * job.duration_weeks) // 2
        reduction = getattr(self.ship, "food_cost_reduction", 0)

        return max(1, base_cost - reduction)


    def calculate_expedition_wage_cost(self, job: Job) -> int:
        return 0

        for viking in self.get_active_crew_list():
            if viking.is_player:
                continue

            total += 1 + (viking.renown // 5)

        return total


    def repair_ship_at_shipyard(self) -> tuple[bool, str]:
        silver_spent, timber_spent, fine_metal_spent, hull_repaired = self.village.repair_ship(
            ship=self.ship,
            silver_available=self.silver,
            ship_timber_available=self.ship_timber,
            fine_metal_available=self.fine_metal,
        )

        if hull_repaired <= 0:
            return False, (
                "No repairs made. "
                "You may lack silver, ship timber, or fine metal."
            )

        self.silver -= silver_spent
        self.ship_timber -= timber_spent
        self.fine_metal -= fine_metal_spent

        return True, (
            f"Repaired {hull_repaired} hull for "
            f"{silver_spent} silver, "
            f"{timber_spent} ship timber, and "
            f"{fine_metal_spent} fine metal."
        )
        
    # DEAD VIKINGS    
    def get_dead_vikings(self) -> list[Viking]:
        return [
            viking for viking in self.vikings.values()
            if viking.status.value == "Dead"
        ]


    def get_reserve_vikings(self) -> list[Viking]:
        ship_ids = set(self.ship.crew)

        return [
            viking for viking in self.vikings.values()
            if viking.viking_id not in ship_ids
            and viking.status.value == "Active"
        ]
        
    def apply_food_shortage_consequences(self, shortage: int) -> list[str]:
        logs = []

        if shortage <= 0:
            return logs

        affected_vikings = [
            viking for viking in self.vikings.values()
            if viking.is_available()
            and not viking.is_player
        ]

        if not affected_vikings:
            return logs

        for viking in affected_vikings:
            viking.loyalty = max(1, viking.loyalty - shortage)

        logs.append(
            f"Food shortage! The crew is short {shortage} food. "
            f"All non-Jarl vikings lose {shortage} loyalty."
        )

        desertion_candidates = sorted(
            affected_vikings,
            key=lambda viking: viking.loyalty,
        )[:shortage]

        for viking in desertion_candidates:
            roll = random.randint(1, 100)

            if roll > viking.loyalty:
                viking.status = type(viking.status).DESERTED

                if self.ship and viking.viking_id in self.ship.crew:
                    self.ship.remove_crew_member(viking.viking_id)

                logs.append(
                    f"{viking.name} deserts after going hungry "
                    f"(roll {roll} vs loyalty {viking.loyalty})."
                )
            else:
                logs.append(
                    f"{viking.name} considers deserting but stays "
                    f"(roll {roll} vs loyalty {viking.loyalty})."
                )

        return logs        
        
    def get_active_crew_by_id(self) -> dict[str, Viking]:
        return {
            viking.viking_id: viking
            for viking in self.get_active_crew_list()
        }    
        
    def process_retirements(self) -> list[str]:
        from development import retirement_chance_for_age

        retirement_logs = []

        # Retirement check once per year at the start of winter.
        if not (self.month == 9 and self.week_of_month == 1):
            return retirement_logs

        for viking in self.vikings.values():
            if viking.status.value != "Active":
                continue

            if viking.is_player:
                continue

            chance = retirement_chance_for_age(viking.age, viking.loyalty)

            if chance <= 0:
                continue

            if random.randint(1, 100) > chance:
                continue

            viking.status = type(viking.status).RETIRED

            if viking.viking_id in self.ship.crew:
                self.ship.remove_crew_member(viking.viking_id)

            entry = {
                "viking_id": viking.viking_id,
                "name": viking.name,
                "age": viking.age,
                "year": self.year,
                "month": self.month,
                "week": self.week_of_month,
                "text": (
                    f"{viking.name} retires at age {viking.age} "
                    f"(retirement chance {chance}%) "
                    f"Year {self.year}, Month {self.month}, Week {self.week_of_month}"
                ),
            }

            self.retired_vikings.append(entry)
            
            self.add_saga_entry(
                entry_type="retirement",
                text=f"{viking.name} retired at age {viking.age}.",
                viking_ids=[viking.viking_id],
            )

            retirement_logs.append(entry["text"])

        return retirement_logs

#### Herbalists

    def apply_herbalists_hut_recovery_bonus(self, vikings: list[Viking]) -> list[str]:
        level = self.village.herbalists_hut_level()
        herbalist_reduction_percent = level * 10
        logs = []

        for viking in vikings:
            for injury in viking.active_injuries:
                if injury.recovery_started:
                    continue

                if injury.weeks_remaining <= 1:
                    continue

                # Herbalist's Hut bonus
                if herbalist_reduction_percent > 0:
                    old_weeks = injury.weeks_remaining
                    reduction = old_weeks * herbalist_reduction_percent // 100

                    if reduction > 0:
                        injury.weeks_remaining = max(1, old_weeks - reduction)

                        logs.append(
                            f"Herbalist's Hut Lv.{level} reduces "
                            f"{viking.display_name()}'s {injury.name} recovery: "
                            f"{old_weeks} -> {injury.weeks_remaining} weeks."
                        )

                # Trait recovery bonus, such as Virile
                trait_recovery_bonus = sum(
                    getattr(trait, "injury_recovery_bonus", 0.0)
                    for trait in viking.traits
                )

                if trait_recovery_bonus > 0 and injury.weeks_remaining > 1:
                    old_weeks = injury.weeks_remaining
                    reduction = int(old_weeks * trait_recovery_bonus)

                    if reduction > 0:
                        injury.weeks_remaining = max(1, old_weeks - reduction)

                        logs.append(
                            f"{viking.display_name()}'s traits reduce "
                            f"{injury.name} recovery by "
                            f"{int(trait_recovery_bonus * 100)}%: "
                            f"{old_weeks} -> {injury.weeks_remaining} weeks."
                        )

            viking.injury_weeks_remaining = max(
                [injury.weeks_remaining for injury in viking.active_injuries],
                default=0,
            )

        return logs

    def retire_viking_for_permanent_injury(self, viking: Viking) -> None:
        if viking.is_player:
            if viking.viking_id in self.ship.crew:
                self.ship.remove_crew_member(viking.viking_id)

            viking.status = type(viking.status).WOUNDED

            if viking.injury_weeks_remaining <= 0:
                viking.injury_weeks_remaining = 8

            return        
        if viking.status.value == "Retired":
            return

        viking.status = type(viking.status).RETIRED

        if viking.viking_id in self.ship.crew:
            self.ship.remove_crew_member(viking.viking_id)

        already_recorded = any(
            entry["viking_id"] == viking.viking_id
            for entry in self.retired_vikings
        )

        if not already_recorded:
            injuries_text = ", ".join(viking.permanent_injuries) or "Permanent Injury"

            self.retired_vikings.append(
                {
                    "viking_id": viking.viking_id,
                    "name": viking.name,
                    "age": viking.age,
                    "year": self.year,
                    "month": self.month,
                    "week": self.week_of_month,
                    "text": (
                        f"{viking.name} retired due to permanent injury "
                        f"({injuries_text}) "
                        f"Year {self.year}, Month {self.month}, Week {self.week_of_month}"
                    ),
                }
            )


    def process_expedition_roster_changes(self) -> list[str]:
        logs = []

        for viking in self.vikings.values():
            if viking.status.value in {"Dead", "Retired"}:
                continue

            if viking.injury_weeks_remaining > 0 and viking.has_blocking_injury():
                already_wounded = viking.status == type(viking.status).WOUNDED
                was_on_ship = viking.viking_id in self.ship.crew

                viking.status = type(viking.status).WOUNDED

                if was_on_ship:
                    self.ship.remove_crew_member(viking.viking_id)

                if not already_wounded and was_on_ship:
                    logs.append(
                        f"{viking.name} is moved to the injured list "
                        f"({viking.injury_weeks_remaining} weeks recovery)."
                    )

        return logs


    def get_injured_vikings(self) -> list[Viking]:
        return [
            viking for viking in self.vikings.values()
            if viking.status.value == "Wounded"
        ]   


    def remove_dead_from_ship(self) -> None:
        living_crew_ids = []

        for viking_id in self.ship.crew:
            viking = self.vikings.get(viking_id)

            if not viking:
                continue

            if viking.status.value == "Dead":
                already_recorded = any(
                    entry["viking_id"] == viking.viking_id
                    for entry in self.odins_hall
                )

                if not already_recorded:
                    self.odins_hall.append(
                        {
                            "viking_id": viking.viking_id,
                            "name": viking.name,
                            "year": self.year,
                            "month": self.month,
                            "week": self.week_of_month,
                            "text": (
                                f"{viking.name}, taken to Valhalla "
                                f"Year {self.year}, Month {self.month}, Week {self.week_of_month}"
                            ),
                        }
                    )

                continue

            living_crew_ids.append(viking_id)

        self.ship.crew = living_crew_ids


    def add_reserve_to_ship(self, viking_id: str) -> tuple[bool, str]:
        viking = self.vikings.get(viking_id)

        if not viking:
            return False, "No viking found with that ID."

        if viking.status.value == "Dead":
            return False, f"{viking.name} is dead."

        if viking.viking_id in self.ship.crew:
            return False, f"{viking.name} is already on the ship."

        if not self.ship.has_room_for_crew():
            return False, "Your ship is full."

        self.ship.add_crew_member(viking.viking_id)
        return True, f"{viking.name} added to the ship."        
                  

    def can_take_job(self, job: Job) -> tuple[bool, str]:
        if not job.is_available_in_season(self.season):
            return False, f"{job.name} is not available in {self.season.value}."

        if not job.time_can_fit(self.month, self.week_of_month):
            return False, f"{job.name} would run too far into the next season."

        if not self.ship.is_usable():
            return False, "Your ship is not usable."

        if self.ship.range < job.required_range:
            return False, f"Your ship does not have enough range for {job.name}."

        active_crew = self.get_active_crew_by_id()

        if len(active_crew) < job.required_min_crew:
            return False, (
                f"Not enough active crew for this job. "
                f"Need {job.required_min_crew}, have {len(active_crew)}."
            )

        active_captains = [
            viking for viking in active_crew.values()
            if viking.role == CrewRole.CAPTAIN
        ]

        if len(active_captains) == 0:
            return False, "You need an active Captain assigned before taking a job."

        if len(active_captains) > 1:
            return False, "Only one active Captain may sail on a job."

        jarl = self.get_player_jarl()

        if (
            jarl
            and jarl.viking_id in active_crew
            and active_captains[0].viking_id != jarl.viking_id
        ):
            return False, "If the Jarl sails, the Jarl must be Captain."

        missing = self.ship.missing_required_roles(active_crew)

        if missing:
            missing_text = ", ".join(
                f"{count} {role.value}" for role, count in missing.items()
            )
            return False, f"Your active crew is missing required roles: {missing_text}."

        return True, "Job can be taken."
        
    def resolve_intro_trial_by_combat(self, job: Job) -> tuple[bool, str]:
        self.remove_available_job(job)

        player = self.get_player_jarl()

        if not player:
            return False, "No player character found."

        old_name = player.name.removeprefix("Jarl ").strip()
        player.name = old_name
        player.title = "Jarl"

        player.renown += 1
        self.renown += 1

        self.world_flags.add("intro_trial_completed")
        self.completed_jobs.append(job.job_id)

        self.add_saga_entry(
            entry_type="campaign_start",
            text=(
                f"{old_name} challenged the old Jarl of {self.village.name} "
                f"to trial by combat, won the duel, and was hailed as "
                f"{player.display_name()}."
            ),
            viking_ids=[player.viking_id],
            job_id=job.job_id,
        )

        self.generate_seasonal_jobs()

        log = [
            f"The old Jarl of {self.village.name} names you oathbreaker, upstart, and traitor.",
            "At sunrise, before the gathered hall, he sentences you to death.",
            "",
            "You invoke the ancient right of trial by combat.",
            "",
            f"{old_name} steps into the ring with shield raised.",
            "The old Jarl strikes first, but age has slowed his hand.",
            "Steel rings. Shields splinter. The hall falls silent.",
            "",
            f"{old_name} drives the old Jarl to his knees and wins the duel.",
            "",
            f"The warriors of {self.village.name} beat their weapons against their shields.",
            f"{player.display_name()} is raised to the high seat.",
            "",
            "+1 Renown",
            "Norway is now open for raids and work.",
        ]

        return True, "\n".join(log)        

    def take_job(self, job: Job) -> tuple[bool, str]:
        if job.job_type == JobType.TRIAL_BY_COMBAT:
            return self.resolve_intro_trial_by_combat(job)    
        can_take, reason = self.can_take_job(job)
        if not can_take:
            return False, reason
        self.remove_available_job(job)            

        start_year = self.year
        start_month = self.month
        start_week = self.week_of_month

        food_cost = self.calculate_food_cost(job)
        wage_cost = 0

        # Expedition resolves first so nodes can alter duration/difficulty mid-job.
        result = resolve_expedition(self, job)
        
        for log in apply_story_completion(self, job, result.success):
            result.log.append(log)
            self.generate_seasonal_jobs()
            
        # Injury Toggle Debug Code
        if self.debug_disable_injuries:
            getattr(result, "injury_records", []).clear()
            result.injuries.clear()
            result.deaths.clear()
            result.permanent_injuries.clear()

            for viking in self.vikings.values():
                viking.active_injuries.clear()
                viking.injuries.clear()
                viking.permanent_injuries.clear()
                viking.injury_weeks_remaining = 0

                if viking.status.value == "Wounded":
                    viking.status = type(viking.status).ACTIVE

            result.log.append("[DEBUG] Injuries disabled.")
        
        # Saga Entry
        for record in getattr(result, "injury_records", []):
            if record["fatal"]:
                text = (
                    f"{record['viking_name']} was killed by {record['injury_name']} "
                    f"during {record['job_name']}."
                )
                entry_type = "death"

            elif record["converted_from_fatal"]:
                text = (
                    f"{record['viking_name']} nearly died during {record['job_name']}, "
                    f"but survived with a permanent injury: {record['injury_name']}."
                )
                entry_type = "permanent_injury"

            elif record["permanent"]:
                text = (
                    f"{record['viking_name']} suffered a permanent injury, "
                    f"{record['injury_name']}, during {record['job_name']}."
                )
                entry_type = "permanent_injury"

            else:
                text = (
                    f"{record['viking_name']} suffered a "
                    f"{record['severity'].lower()} injury, {record['injury_name']}, "
                    f"during {record['job_name']}."
                )
                entry_type = "injury"

            viking = self.vikings.get(record["viking_id"])

            if viking:
                viking.injury_history.append(text)

            self.add_saga_entry(
                entry_type=entry_type,
                text=text,
                viking_ids=[record["viking_id"]],
                job_id=record["job_id"],
            )
        for viking in self.get_active_crew_list():
            viking.start_injury_recovery()
        self.remove_dead_from_ship()
        
               

        self.silver += result.silver_gained
        self.food += result.food_gained
        self.clamp_food_storage()
        
        self.thralls += result.thralls_gained
        self.ship_timber += result.ship_timber_gained
        self.fine_metal += result.fine_metal_gained
        self.clamp_physical_resources()
        
        net_silver = result.silver_gained - wage_cost
        net_food = result.food_gained - food_cost
        net_renown = result.renown_gained if result.success else -(max(1, job.reward_renown // 2))
        
        self.food -= food_cost
        self.silver -= wage_cost

        if self.food < 0:
            shortage = abs(self.food)
            self.food = 0

            shortage_logs = self.apply_food_shortage_consequences(shortage)

            for log in shortage_logs:
                result.log.append(log)
        
        roster_change_logs = self.process_expedition_roster_changes()

        for log in roster_change_logs:
            result.log.append(log) 

        from development import apply_post_job_growth, apply_post_job_aging_wear

        
        growth_logs = apply_post_job_growth(
            self.get_active_crew_list(),
            result.tested_stats,
            result.individual_tested_stats,
            duration_weeks=result.final_duration_weeks,
            chance_multiplier=1.0 if result.success else 0.66,
            )

        for log in growth_logs:
            result.log.append(log)

        aging_wear_logs = apply_post_job_aging_wear(
            self.get_active_crew_list(),
            duration_weeks=result.final_duration_weeks,
            job_success=result.success,
        )
        
        from development import apply_post_job_loyalty_change

        loyalty_logs = apply_post_job_loyalty_change(
            self.get_active_crew_list(),
            result.success,
            result.event_failures,
            result.total_nodes,
        )

        for log in loyalty_logs:
            result.log.append(log)

        for log in aging_wear_logs:
            result.log.append(log)

        # Psychological fallout from failed expeditions.
        # Kept before advance_weeks so temporary conditions begin counting down
        # during the post-expedition time passage.
        if not result.success:
            for viking in self.get_active_crew_list():
                if viking.is_player:
                    continue

                if random.randint(1, 100) <= 8:
                    condition = roll_psych_condition(
                        PsychType.FAILURE,
                        permanent_chance=3,
                    )
                    result.log.append(apply_psych_condition(viking, condition))

        # Time passes after the final duration is known.
        calendar_logs = self.advance_weeks(
            result.final_duration_weeks,
            print_logs=False,
        )

        for log in calendar_logs:
            result.log.append(f"[While Away] {log}")
        
        for viking in self.vikings.values():
            viking.start_injury_recovery()

        end_year = self.year
        end_month = self.month
        end_week = self.week_of_month
        
        captain = self.get_ship_captain()
        captain_name = captain.display_name() if captain else "The crew"

        if result.success:
            self.add_saga_entry(
                entry_type="job_success",
                text=(
                    f"{captain_name} successfully completed {job.name} "
                    f"at {job.location_name}."
                ),
                viking_ids=[
                    viking.viking_id
                    for viking in self.get_active_crew_list()
                ],
                job_id=job.job_id,
            )
        else:
            self.add_saga_entry(
                entry_type="job_failure",
                text=(
                    f"{captain_name} failed {job.name} "
                    f"at {job.location_name}."
                ),
                viking_ids=[
                    viking.viking_id
                    for viking in self.get_active_crew_list()
                ],
                job_id=job.job_id,
            )
        
        for viking in self.get_active_crew_list():
            viking.job_history.append(
                f"Year {start_year}, Month {start_month}, Week {start_week} - "
                f"{job.name} ({job.location_name}) - "
                f"{'Success' if result.success else 'Failure'}"
            )

            viking.expeditions += 1

        jarl = self.get_player_jarl()
        #captain = self.get_ship_captain()

        if result.success:
            jarl_sailed = (
                jarl is not None
                and jarl.viking_id in self.ship.crew
                and jarl.is_available()
            )

            if jarl:
                if jarl_sailed:
                    jarl.renown += result.renown_gained
                else:
                    jarl.renown += result.renown_gained // 2

            if captain and captain != jarl:
                captain.renown += result.renown_gained

        else:
            renown_loss = max(1, job.reward_renown // 2)

            if jarl:
                jarl.renown = max(0, jarl.renown - renown_loss)

            if captain and captain != jarl:
                captain.renown = max(
                    0,
                    captain.renown - max(1, renown_loss // 2)
                )

        # Village renown mirrors the Jarl's renown.
        if jarl:
            self.renown = jarl.renown
            
        self.completed_jobs.append(
            {
                "job_id": job.job_id,
                "job_name": job.name,
                "start_year": start_year,
                "start_month": start_month,
                "start_week": start_week,
                "end_year": end_year,
                "end_month": end_month,
                "end_week": end_week,
                "success": result.success,
                "silver_gained": result.silver_gained,
                "food_gained": result.food_gained,
                "renown_gained": result.renown_gained,
                "thralls_gained": result.thralls_gained,
                "ship_timber_gained": result.ship_timber_gained,
                "fine_metal_gained": result.fine_metal_gained,
                "ship_damage": result.ship_damage,
                "injuries": list(result.injuries),
                "deaths": list(result.deaths),
                "permanent_injuries": list(result.permanent_injuries),
                "items_gained": list(result.items_gained),
                "log": list(result.log),
            }
        )

        result_text = "\n".join(result.log)

        result_text += (
            f"\n\nExpedition Costs"
            f"\nFood Consumed: {food_cost}"
            f"\nCrew Wages Paid: {wage_cost} silver"
)
        result_text += (
            f"\n\nTime passed: {result.final_duration_weeks} weeks"
            f"\nDate: Year {start_year}, Month {start_month}, Week {start_week}"
            f" -> Year {end_year}, Month {end_month}, Week {end_week}"
        )
        
        result_text += (
            f"\n\nNet Expedition Change"
            f"\nSilver: {net_silver:+}"
            f"\nFood: {net_food:+}"
            f"\nThralls: {result.thralls_gained:+}"
            f"\nShip Timber: {result.ship_timber_gained:+}"
            f"\nFine Metal: {result.fine_metal_gained:+}"
            f"\nRenown: {net_renown:+}"
        )

        return True, result_text
        
    # CREW ROLES    
    
    def assign_crew_role(self, viking_id: str, new_role: CrewRole) -> tuple[bool, str]:
        viking = self.vikings.get(viking_id)

        if not viking:
            return False, "No viking found with that ID."

        if viking.status.value == "Dead":
            return False, f"{viking.name} is dead."

        jarl = self.get_player_jarl()

        if (
            new_role == CrewRole.CAPTAIN
            and jarl
            and jarl.viking_id in self.ship.crew
            and jarl.is_available()
            and viking.viking_id != jarl.viking_id
        ):
            return False, "The Jarl is sailing and must remain Captain."

        old_role = viking.role

        if new_role == CrewRole.CAPTAIN:
            for other in self.vikings.values():
                if other.viking_id != viking.viking_id and other.role == CrewRole.CAPTAIN:
                    other.role = CrewRole.RAIDER

        viking.role = new_role

        return True, f"{viking.name} changed role from {old_role.value} to {new_role.value}."


    def get_ship_crew(self) -> list[Viking]:
        return [
            self.vikings[viking_id]
            for viking_id in self.ship.crew
            if viking_id in self.vikings
        ]
 
    def get_player_jarl(self) -> Viking | None:
        for viking in self.vikings.values():
            if viking.is_player:
                return viking
        return None


    def get_ship_captain(self) -> Viking | None:
        for viking_id in self.ship.crew:
            viking = self.vikings.get(viking_id)

            if viking and viking.role == CrewRole.CAPTAIN:
                return viking

        return None 
        
    def remove_crew_member_from_ship(self, viking_id: str) -> tuple[bool, str]:
        viking = self.vikings.get(viking_id)

        if not viking:
            return False, "No viking found with that ID."

        if viking.viking_id not in self.ship.crew:
            return False, f"{viking.name} is not on the ship."

        if viking.is_player:
            self.ship.remove_crew_member(viking.viking_id)
            return True, f"{viking.name} will remain at the village."

        self.ship.remove_crew_member(viking.viking_id)
        return True, f"{viking.name} removed from the ship and placed in reserve."    
            
        
    def calculate_monthly_viking_upkeep(self) -> tuple[int, int]:
        living_vikings = [
            viking for viking in self.vikings.values()
            if viking.status.value not in {"Dead", "Retired"}
        ]

        silver_cost = 0

        for viking in living_vikings:
            if viking.is_player:
                continue

            silver_cost += 1 + (viking.renown // 5)

        food_cost = len(living_vikings)

        return silver_cost, food_cost    
        
    def apply_silver_shortage_penalty(self) -> list[str]:
        logs = []

        if self.silver > 0:
            return logs

        active_crew = self.get_active_crew_list()

        if not active_crew:
            return logs

        logs.append(
            "The silver stores are empty. The crew grumbles over unpaid shares."
        )

        for viking in active_crew:
            if viking.is_player:
                continue

            viking.loyalty = max(1, viking.loyalty - 2)

        logs.append("Crew loyalty falls by 2.")

        return logs    

    def check_low_loyalty_trial_by_combat(self) -> list[str]:
        logs = []

        player = self.get_player_jarl()

        if not player or not player.is_available():
            return logs

        candidates = [
            viking for viking in self.get_active_crew_list()
            if not viking.is_player
            and viking.is_available()
            and viking.loyalty <= 25
        ]

        if not candidates:
            return logs

        random.shuffle(candidates)

        challenger = None

        for viking in candidates:
            # Loyalty 25 = 1%
            # Loyalty 20 = 2%
            # Loyalty 15 = 4%
            # Loyalty 10 = 7%
            # Loyalty 5  = 12%
            chance = max(1, round((26 - viking.loyalty) / 2))

            if random.randint(1, 100) <= chance:
                challenger = viking
                break

        if not challenger:
            return logs

        logs.append(
            f"{challenger.display_name()}'s loyalty breaks. Before the gathered crew, "
            f"{challenger.display_name()} challenges {player.display_name()} to trial by combat."
        )

        player_roll = player.combat_score() + random.randint(-20, 20)
        challenger_roll = challenger.combat_score() + random.randint(-20, 20)

        logs.append(
            f"[Trial Roll] {player.display_name()} {player_roll} vs "
            f"{challenger.name} {challenger_roll}."
        )

        if player_roll >= challenger_roll:
            challenger.status = type(challenger.status).DEAD
            player.renown += 5
            self.renown = player.renown

            for viking in self.get_active_crew_list():
                if not viking.is_player:
                    viking.loyalty = min(100, viking.loyalty + 2)

            logs.append(
                f"{player.display_name()} kills {challenger.display_name()} in the ring. "
                "The challenge ends in blood."
            )
            logs.append("+5 Renown. Crew loyalty rises by 2.")

            return logs

        injury_template = random.choice(
            get_templates(InjuryType.COMBAT, InjurySeverity.PERMANENT)
            + get_templates(InjuryType.GENERIC, InjurySeverity.PERMANENT)
        )

        injury = injury_template.name
        player.suffer_permanent_injury(injury)
        apply_stat_modifiers(player, injury_template)

        recovery_weeks = random.randint(
            injury_template.recovery_weeks_min,
            injury_template.recovery_weeks_max,
        )

        player.add_injury(
            injury_name=injury,
            weeks_remaining=recovery_weeks,
            stat_modifiers={},
            recovery_started=True,
            can_deploy_while_injured=injury_template.can_deploy_while_injured,
        )

        player.injury_weeks_remaining = max(
            player.injury_weeks_remaining,
            recovery_weeks,
        )

        if not injury_template.can_deploy_while_injured:
            player.status = type(player.status).WOUNDED

        renown_loss = min(self.renown, 15)
        silver_loss = max(0, self.silver // 4)

        self.renown -= renown_loss
        self.silver -= silver_loss

        challenger.renown += 5
        challenger.loyalty = min(100, challenger.loyalty + 15)

        for viking in self.get_active_crew_list():
            if not viking.is_player:
                viking.loyalty = max(1, viking.loyalty - 5)

        logs.append(
            f"{challenger.display_name()} defeats {player.display_name()} before the crew. "
            f"{player.display_name()} survives, but suffers a permanent injury: {injury}."
        )
        logs.append(
            f"-{renown_loss} Renown, -{silver_loss} silver, crew loyalty falls by 5."
        )

        return logs

    def process_birthdays_for_current_week(self) -> list[str]:
        if self.debug_skip_birthdays:
            return []
        birthday_logs = []

        for viking in self.vikings.values():
            if viking.status.value == "Dead":
                continue

            if (
                viking.birth_month == self.month
                and viking.birth_week == self.week_of_month
            ):
                viking.age += 1
                birthday_logs.append(f"{viking.name} turns {viking.age}.")
                from development import apply_birthday_development

                for log in apply_birthday_development(viking):
                    birthday_logs.append(log)

                viking.record_stat_history()

        return birthday_logs    

    def resolve_monthly_village_attack(self) -> str | None:
        if self.year < 2:
            return
        silver_pressure = min(25, self.silver // 50)
        defense = self.village.village_defense_rating()

        attack_chance = max(3, 10 + silver_pressure - (defense // 5))

        roll = random.randint(1, 100)

        if roll > attack_chance:
            return None

        attack_strength = random.randint(10, 40) + (self.renown // 2)

        if defense + random.randint(1, 20) >= attack_strength:
            return "A rival Jarl tested your borders, but your village defenses held."

        silver_lost = min(self.silver, random.randint(10, 40))
        self.silver -= silver_lost

        return f"A rival Jarl raided your holding! You lost {silver_lost} silver."        
     

    def advance_weeks(self, weeks: int, print_logs: bool = True) -> list[str]:
        logs = []
        for _ in range(weeks):
            old_month = self.month

            # Weekly systems tick first.
            self.village.advance_week()
            ship_message = self.advance_ship_construction()
            if ship_message:
                logs.append(ship_message)
                if print_logs:
                    print(ship_message)

            for viking in self.vikings.values():
                if not viking.active_injuries:
                    continue

                healed_injuries = []

                for injury in viking.active_injuries:
                    if not injury.recovery_started:
                        continue

                    if injury.weeks_remaining > 0:
                        injury.weeks_remaining -= 1

                    if injury.weeks_remaining <= 0:
                        healed_injuries.append(injury)

                for injury in healed_injuries:
                    viking.active_injuries.remove(injury)

                    if injury.name in viking.injuries:
                        viking.injuries.remove(injury.name)

                    if injury.pending_title and not injury.title_awarded:
                        viking.apply_title(injury.pending_title)
                        injury.title_awarded = True
                        logs.append(
                            f"{viking.name} has recovered from {injury.name} "
                            f"and is now known as {viking.name}."
                        )

                viking.injury_weeks_remaining = max(
                    [injury.weeks_remaining for injury in viking.active_injuries],
                    default=0,
                )

                if (
                    viking.injury_weeks_remaining <= 0
                    and viking.status == type(viking.status).WOUNDED
                ):
                    viking.status = type(viking.status).ACTIVE

            # Then calendar advances.
            self.week_of_month += 1

            birthday_logs = self.process_birthdays_for_current_week()

            for log in birthday_logs:
                logs.append(log)
                if print_logs:
                    print(log)

            retirement_logs = self.process_retirements()

            for log in retirement_logs:
                logs.append(log)
                if print_logs:
                    print(log)
            
            

            if self.week_of_month > WEEKS_PER_MONTH:
                self.week_of_month = 1
                self.month += 1

                food_produced = self.village.produce_monthly_food(
                    get_season_for_month(old_month)
                )
                self.food += food_produced
                self.clamp_food_storage()

                fine_metal_produced = self.village.produce_monthly_fine_metal()
                self.fine_metal += fine_metal_produced
                self.clamp_fine_metal_storage()

                building_upkeep = self.village.monthly_upkeep_cost()
                self.silver -= building_upkeep
                
                village_income = self.village.monthly_income()
                self.silver += village_income

                thrall_food_upkeep = self.thralls // 4

                viking_silver_upkeep, viking_food_upkeep = self.calculate_monthly_viking_upkeep()
                self.silver -= viking_silver_upkeep
                total_food_upkeep = viking_food_upkeep + thrall_food_upkeep
                food_shortage = max(0, total_food_upkeep - self.food)

                self.food = max(0, self.food - total_food_upkeep)
                # silver shortage penalty
                for log in self.apply_silver_shortage_penalty():
                    logs.append(log)
                    if print_logs:
                        print(log)
                # low loyalty trial check
                for log in self.check_low_loyalty_trial_by_combat():
                    logs.append(log)
                    if print_logs:
                        print(log)                    
                    
                shortage_logs = self.apply_food_shortage_consequences(food_shortage)

                for log in shortage_logs:
                    logs.append(log)

                    if print_logs:
                        print(log)

                upkeep_message = (
                    f"Monthly upkeep paid: "
                    f"{building_upkeep} silver for buildings, "
                    f"{viking_silver_upkeep} silver for vikings, "
                    f"{viking_food_upkeep} food for vikings, "
                    f"{thrall_food_upkeep} food for thralls. "
                    f"Produced {food_produced} food and "
                    f"{fine_metal_produced} fine metal."
                )

                logs.append(upkeep_message)

                if print_logs:
                    print(upkeep_message)

                if self.month > 12:
                    self.month = 1
                    self.year += 1
                    
                attack_message = self.resolve_monthly_village_attack()
                if attack_message:
                    logs.append(attack_message)
                    if print_logs:
                        print(attack_message)
                
                if self.month in {1, 5, 9} and self.week_of_month == 1:
                    self.refresh_recruit_pool()   
                self.maybe_refresh_seasonal_jobs()  
                    
        return logs

    def advance_to_next_month(self) -> None:
        self.month += 1
        self.week_of_month = 1

        if self.month > 12:
            self.month = 1
            self.year += 1

    def advance_to_next_season(self) -> None:
        if self.month <= 4:
            self.month = 5
        elif self.month <= 8:
            self.month = 9
        else:
            self.month = 1
            self.year += 1

        self.week_of_month = 1
    
    def advance_one_year_debug_no_upkeep(self) -> list[str]:
        logs = []

        for _ in range(48):
            # Process the current week before advancing.
            birthday_logs = self.process_birthdays_for_current_week()
            logs.extend(birthday_logs)

            self.week_of_month += 1

            if self.week_of_month > WEEKS_PER_MONTH:
                self.week_of_month = 1
                self.month += 1

                if self.month > 12:
                    self.month = 1
                    self.year += 1

                self.refresh_recruit_pool()
                self.maybe_refresh_seasonal_jobs()

        return logs
    
    def purchase_village_tile(self) -> tuple[bool, str]:
        cost = self.village.next_tile_purchase_cost()

        if self.silver < cost:
            return False, f"Not enough silver. Need {cost}, have {self.silver}."

        tile = self.village.add_new_tile()

        if tile is None:
            return False, "No more land can be purchased."

        self.silver -= cost
        return True, f"Purchased new land at tile ({tile.x}, {tile.y}) for {cost} silver."


    def conquer_village_tile_debug(self) -> tuple[bool, str]:
        tile = self.village.add_new_tile()

        if tile is None:
            return False, "No more land can be conquered."

        return True, f"Conquered new land at tile ({tile.x}, {tile.y})."   
        
    

    def build_village_facility(self, x: int, y: int, building_type) -> tuple[bool, str]:
        required_thralls = 0

        if building_type != BuildingType.THRALL_QUARTERS:
            required_thralls = self.village.thralls_required_for_building_level(1)

        if self.available_thralls() < required_thralls:
            return False, (
                f"Not enough available thralls. "
                f"Need {required_thralls}, have {self.available_thralls()}."
            )

        success, message, cost = self.village.build_facility(x, y, building_type)

        if not success:
            return False, message

        if self.silver < cost:
            tile = self.village.tiles.get((x, y))
            if tile:
                tile.building = None

            return False, f"Not enough silver. Need {cost}, have {self.silver}."

        self.silver -= cost
        self.assigned_thralls += required_thralls

        return True, (
            f"{message} Cost: {cost} silver. "
            f"Assigned Thralls: {required_thralls}."
        )


    def upgrade_village_building(self, x: int, y: int) -> tuple[bool, str]:
        tile = self.village.tiles.get((x, y))

        if not tile or not tile.building:
            return False, "No building on that tile."

        current_level = tile.building.level
        new_level = current_level + 1
        required_thralls = 0

        if tile.building.building_type != BuildingType.THRALL_QUARTERS:
            required_thralls = self.village.thralls_required_for_building_level(new_level)

        if self.available_thralls() < required_thralls:
            return False, (
                f"Not enough available thralls. "
                f"Need {required_thralls}, have {self.available_thralls()}."
            )

        success, message, cost = self.village.upgrade_building_at(x, y)

        if not success:
            return False, message

        if self.silver < cost:
            tile = self.village.tiles.get((x, y))
            if tile and tile.building:
                tile.building.level -= 1
                tile.building.is_under_construction = False
                tile.building.weeks_remaining = 0

            return False, f"Not enough silver. Need {cost}, have {self.silver}."

        self.silver -= cost
        self.assigned_thralls += required_thralls

        return True, (
            f"{message} Cost: {cost} silver. "
            f"Assigned Thralls: {required_thralls}."
        )
        
    def has_smithy(self) -> bool:
        from village import BuildingType

        return self.village.completed_building_exists(BuildingType.SMITHY)

    def item_is_equipped(self, item_id: str) -> bool:
        for viking in self.vikings.values():
            equipped_ids = [
                viking.equipment.armor,
                viking.equipment.helm,
                viking.equipment.primary_weapon,
                viking.equipment.shield,
            ]

            if item_id in equipped_ids:
                return True

        return False    


    def get_crew_list(self) -> list[Viking]:
        return [
            self.vikings[viking_id]
            for viking_id in self.ship.crew
            if viking_id in self.vikings
        ]

    def get_active_crew_list(self) -> list[Viking]:
        return [
            viking for viking in self.get_crew_list()
            if viking.is_available()
        ]

    def summary(self) -> str:
        return (
            f"{self.name}\n"
            f"{self.calendar_label()} ({self.season.value})\n"
            f"Village: {self.village.name}\n"
            f"Silver: {self.silver} | "
            f"Food: {self.food}/{self.village.food_storage_capacity()} | "            
            f"Thralls: {self.thralls}/{self.village.thrall_capacity()} "
            f"({self.available_thralls()} available) | "
            f"Ship Timber: {self.ship_timber}/{self.village.timber_storage_capacity()} | "
            f"Fine Metal: {self.fine_metal}/{self.village.fine_metal_storage_capacity()} | "
            f"Renown: {self.renown}\n"
            f"Ship: {self.ship.name} "
            f"Hull: {self.ship.hull}/{self.ship.max_hull} | "
            f"Crew: {len(self.ship.crew)}/{self.ship.max_crew}"
        )

    def to_dict(self) -> dict:
        return {
            "campaign_id": self.campaign_id,
            "name": self.name,
            "village": self.village.to_dict(),
            "year": self.year,
            "month": self.month,
            "week_of_month": self.week_of_month,
            "silver": self.silver,
            "food": self.food,
            "thralls": self.thralls,
            "ship_timber": self.ship_timber,
            "fine_metal": self.fine_metal,
            "assigned_thralls": self.assigned_thralls,
            "renown": self.renown,
            "available_jobs": [
                job.to_dict()
                for job in self.available_jobs
            ],
            "ship": self.ship.to_dict(),
            "pending_ship_upgrade_part": self.pending_ship_upgrade_part,
            "pending_ship_upgrade_level": self.pending_ship_upgrade_level,
            "pending_ship_upgrade_name": self.pending_ship_upgrade_name,
            "pending_ship_weeks_remaining": self.pending_ship_weeks_remaining,            
            "vikings": {
                viking_id: viking.to_dict()
                for viking_id, viking in self.vikings.items()
            },
            "inventory": {
                item_id: item.to_dict()
                for item_id, item in self.inventory.items()
            },
            "saga_entries": [
                entry.to_dict()
                for entry in self.saga_entries
            ],
            "odins_hall": list(self.odins_hall),
            "retired_vikings": list(self.retired_vikings),
            "recruit_pool": self.recruit_pool.to_dict(),
            "completed_jobs": list(self.completed_jobs),
            "world_flags": sorted(self.world_flags),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Campaign":
        vikings = {
            viking_id: Viking.from_dict(viking_data)
            for viking_id, viking_data in data.get("vikings", {}).items()
        }

        return cls(
            campaign_id=data.get("campaign_id", str(uuid.uuid4())),
            name=data["name"],
            year=data.get("year", 1),
            month=data.get("month", 1),
            week_of_month=data.get("week_of_month", 1),
            silver=data.get("silver", 100),
            food=data.get("food", 50),
            thralls=data.get("thralls", 0),
            ship_timber=data.get("ship_timber", 0),
            fine_metal=data.get("fine_metal", 0),
            assigned_thralls=data.get("assigned_thralls", 0),
            renown=data.get("renown", 0),
            available_jobs=[
                Job.from_dict(job_data)
                for job_data in data.get("available_jobs", [])
            ],            
            ship=Ship.from_dict(data["ship"]),
            pending_ship_upgrade_part=data.get("pending_ship_upgrade_part"),
            pending_ship_upgrade_level=data.get("pending_ship_upgrade_level", 0),
            pending_ship_upgrade_name=data.get("pending_ship_upgrade_name"),
            pending_ship_weeks_remaining=data.get("pending_ship_weeks_remaining", 0),            
            vikings=vikings,
            inventory={
                item_id: Item.from_dict(item_data)
                for item_id, item_data in data.get("inventory", {}).items()
            },
            saga_entries=[
                SagaEntry.from_dict(entry_data)
                for entry_data in data.get("saga_entries", [])
            ],
            odins_hall=list(data.get("odins_hall", [])),
            retired_vikings=list(data.get("retired_vikings", [])),
            recruit_pool=RecruitPool.from_dict(data.get("recruit_pool", {})),
            village=Village.from_dict(data["village"]),
            completed_jobs=list(data.get("completed_jobs", [])),
            world_flags=set(data.get("world_flags", [])),            
        )