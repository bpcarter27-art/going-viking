from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import random
import uuid


from models import VikingClass, CrewRole, Season




class BuildingType(str, Enum):
    FARM = "Farm" # Grows food
    LONGHOUSE = "Longhouse" # HQ
    BARRACKS = "Warrior Lodge" # Unlocks Drengr
    SHIPYARD = "Shipwright" # Unlocks Oarsman
    TRADER = "Market" #Buy/Sell items, passive income

    FLETCHER = "Bowyer" # Unlocks Archers
    GREAT_HALL = "Mead Hall" # Unlocks Hersir
    SHRINE_OF_ODIN = "Hörgr" # -> Ritual Shrine? Offer Sacrifices to different gods for different raid bonuses
    HERBALISTS_HUT = "Bone-Setter's Hut" # Unlocks Bone-Setter. Chance for faster healing
    CARPENTERS_HUT = "Woodwright" # Unlocks some ship upgrades. Not available yet
    HUNTERS_SHACK = "Hunter's Lodge" # Unlocks Tracker
    SEERS_HUT = "Völva's Hut" # Unlocks Trickster
    TRAINING_GROUNDS = "Fighting Circle" # Improves recruit quality, Unlocks Shieldmaiden
    
    THRALL_QUARTERS = "Thrall Pens" # How many thralls can be held at one time
    SMITHY = "Smithy"
    MINE = "Mine"
    
    
BUILDING_COSTS = {
    BuildingType.FARM: 40,
    BuildingType.FLETCHER: 40,
    BuildingType.GREAT_HALL: 60,
    BuildingType.SHRINE_OF_ODIN: 80,
    BuildingType.HERBALISTS_HUT: 50,
    BuildingType.CARPENTERS_HUT: 45,
    BuildingType.HUNTERS_SHACK: 45,
    BuildingType.SEERS_HUT: 70,
    BuildingType.TRAINING_GROUNDS: 70,
    BuildingType.THRALL_QUARTERS: 60,
    BuildingType.SMITHY: 90,
    BuildingType.MINE: 80,
}

BUILDING_BUILD_WEEKS = {
    BuildingType.FARM: 4,
    BuildingType.FLETCHER: 4,
    BuildingType.GREAT_HALL: 6,
    BuildingType.SHRINE_OF_ODIN: 8,
    BuildingType.HERBALISTS_HUT: 5,
    BuildingType.CARPENTERS_HUT: 5,
    BuildingType.HUNTERS_SHACK: 4,
    BuildingType.SEERS_HUT: 7,
    BuildingType.TRAINING_GROUNDS: 6,
    BuildingType.THRALL_QUARTERS: 4,
    BuildingType.SMITHY: 6,
    BuildingType.MINE: 6,
}

BUILDING_UPGRADE_BASE_COST = 50
BUILDING_UPGRADE_WEEKS = 6

BASE_TILE_PURCHASE_COST = 75
TILE_PURCHASE_COST_INCREASE = 25


CLASS_UNLOCK_BUILDINGS = {
    VikingClass.RAIDER: BuildingType.BARRACKS,
    VikingClass.SAILOR: BuildingType.SHIPYARD,
    VikingClass.ARCHER: BuildingType.FLETCHER,
    VikingClass.TRICKSTER: BuildingType.SEERS_HUT,
    VikingClass.HERSIR: BuildingType.GREAT_HALL,
    VikingClass.SHIELDMAIDEN: BuildingType.TRAINING_GROUNDS,
    VikingClass.HERBALIST: BuildingType.HERBALISTS_HUT,
    VikingClass.SCOUT: BuildingType.HUNTERS_SHACK,
}


  
    
BUILDING_MONTHLY_UPKEEP = {
    BuildingType.FARM: 1,
    BuildingType.LONGHOUSE: 2,
    BuildingType.BARRACKS: 2,
    BuildingType.SHIPYARD: 3,
    BuildingType.TRADER: 1,

    BuildingType.FLETCHER: 2,
    BuildingType.GREAT_HALL: 4,
    BuildingType.SHRINE_OF_ODIN: 5,
    BuildingType.HERBALISTS_HUT: 3,
    BuildingType.CARPENTERS_HUT: 3,
    BuildingType.HUNTERS_SHACK: 2,
    BuildingType.SEERS_HUT: 4,
    BuildingType.TRAINING_GROUNDS: 4,
    BuildingType.THRALL_QUARTERS: 4,
    BuildingType.SMITHY: 3,
    BuildingType.MINE: 3
}

TRADER_MONTHLY_INCOME_BY_LEVEL = {
    1: 4,
    2: 8,
    3: 16,
    4: 32,
}

BUILDING_SYMBOLS = {
    BuildingType.FARM: "FARM",
    BuildingType.LONGHOUSE: "LONG",
    BuildingType.BARRACKS: "WARR",
    BuildingType.SHIPYARD: "SHIP",
    BuildingType.TRADER: "MARK",

    BuildingType.FLETCHER: "BOWR",
    BuildingType.GREAT_HALL: "MEAD",
    BuildingType.SHRINE_OF_ODIN: "HORG",
    BuildingType.HERBALISTS_HUT: "BONE",
    BuildingType.CARPENTERS_HUT: "WOOD",
    BuildingType.HUNTERS_SHACK: "HUNT",
    BuildingType.SEERS_HUT: "VLVA",
    BuildingType.TRAINING_GROUNDS: "FIGT",
    BuildingType.THRALL_QUARTERS: "THRAL",
    BuildingType.SMITHY: "SMTH",
    BuildingType.MINE: "MINE",
}

LONGHOUSE_BASE_CAPACITY = 10
BARRACKS_CAPACITY_PER_LEVEL = 8
RECRUIT_COST = 10
SHIP_REPAIR_COST_PER_HULL = 1
BASE_FOOD_STORAGE = 40
FOOD_STORAGE_PER_FARM_LEVEL = 40

BASE_TIMBER_STORAGE = 20
TIMBER_STORAGE_PER_WOODWRIGHT_LEVEL = 15

BASE_FINE_METAL_STORAGE = 5
FINE_METAL_STORAGE_PER_MINE_LEVEL = 10
FINE_METAL_MONTHLY_PRODUCTION_PER_LEVEL = 2
MINE_MAX_LEVEL = 4

THRALL_CAPACITY_BASE = 4
THRALL_CAPACITY_PER_QUARTERS_LEVEL = 6

@dataclass
class Building:
    building_type: BuildingType
    level: int = 1
    is_under_construction: bool = False
    weeks_remaining: int = 0

    building_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def display_name(self) -> str:
        if self.is_under_construction:
            return f"{self.building_type.value} Lv.{self.level} ({self.weeks_remaining}w)"
        return f"{self.building_type.value} Lv.{self.level}"

    def advance_week(self) -> None:
        if not self.is_under_construction:
            return

        self.weeks_remaining -= 1

        if self.weeks_remaining <= 0:
            self.weeks_remaining = 0
            self.is_under_construction = False

    def to_dict(self) -> dict:
        return {
            "building_id": self.building_id,
            "building_type": self.building_type.value,
            "level": self.level,
            "is_under_construction": self.is_under_construction,
            "weeks_remaining": self.weeks_remaining,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Building":
        return cls(
            building_id=data.get("building_id", str(uuid.uuid4())),
            building_type=BuildingType(data["building_type"]),
            level=data.get("level", 1),
            is_under_construction=data.get("is_under_construction", False),
            weeks_remaining=data.get("weeks_remaining", 0),
        )


@dataclass
class VillageTile:
    x: int
    y: int
    building: Building | None = None
    is_unlocked: bool = True

    def is_empty(self) -> bool:
        return self.is_unlocked and self.building is None

    def display_symbol(self) -> str:
        if not self.is_unlocked:
            return "-xx-"

        if self.building is None:
            return "----"

        symbol = BUILDING_SYMBOLS.get(self.building.building_type, "BLDG")

        if self.building.is_under_construction:
            return f"{symbol}*"

        return symbol

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "is_unlocked": self.is_unlocked,
            "building": self.building.to_dict() if self.building else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VillageTile":
        building_data = data.get("building")

        return cls(
            x=data["x"],
            y=data["y"],
            is_unlocked=data.get("is_unlocked", True),
            building=Building.from_dict(building_data) if building_data else None,
        )


@dataclass
class Village:
    name: str
    width: int = 5
    height: int = 5

    tiles: dict[tuple[int, int], VillageTile] = field(default_factory=dict)
    village_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        if not self.tiles:
            self.tiles = {}

            for y in range(1, self.height + 1):
                for x in range(1, self.width + 1):
                    self.tiles[(x, y)] = VillageTile(
                        x=x,
                        y=y,
                        is_unlocked=False,
                    )

            # Starting 3x3 center-left grid.
            for y in range(2, 5):
                for x in range(1, 4):
                    self.tiles[(x, y)].is_unlocked = True
 
    def monthly_income(self) -> int:
        total = 0

        for trader in self.get_buildings(BuildingType.TRADER):
            if trader.is_under_construction:
                continue

            if trader.level <= 4:
                total += TRADER_MONTHLY_INCOME_BY_LEVEL.get(trader.level, 0)
            else:
                total += 32 + ((trader.level - 4) * 8)

        return total
 
                    
    def unlocked_tile_count(self) -> int:
        return sum(1 for tile in self.tiles.values() if tile.is_unlocked)
        
    @staticmethod
    def thralls_required_for_building_level(level: int) -> int:
        return max(1, level)    

    def next_tile_purchase_cost(self) -> int:
        extra_tiles = max(0, self.unlocked_tile_count() - 9)
        return BASE_TILE_PURCHASE_COST + (extra_tiles * TILE_PURCHASE_COST_INCREASE)


    def add_new_tile(self) -> VillageTile | None:
        """
        Unlocks one locked tile adjacent to already unlocked land.
        Max village size is currently 5x5.
        """
        candidates: list[VillageTile] = []

        for tile in self.tiles.values():
            if tile.is_unlocked:
                continue

            neighbors = [
                (tile.x, tile.y - 1),
                (tile.x, tile.y + 1),
                (tile.x - 1, tile.y),
                (tile.x + 1, tile.y),
            ]

            if any(
                self.tiles.get(pos) and self.tiles[pos].is_unlocked
                for pos in neighbors
            ):
                candidates.append(tile)

        if not candidates:
            return None

        # Prefer top-to-bottom, left-to-right for predictable expansion.
        candidates.sort(key=lambda t: (t.y, t.x))

        tile = candidates[0]
        tile.is_unlocked = True
        return tile


    def village_defense_rating(self) -> int:
        defense = 0

        for building in self.get_buildings():
            if building.is_under_construction:
                continue

            if building.building_type == BuildingType.LONGHOUSE:
                defense += 5 * building.level
            elif building.building_type == BuildingType.BARRACKS:
                defense += 8 * building.level
            elif building.building_type == BuildingType.SHIPYARD:
                defense += 3 * building.level
            elif building.building_type == BuildingType.GREAT_HALL:
                defense += 5 * building.level

        return defense         

    def has_active_construction(self) -> bool:
        return any(
            building.is_under_construction
            for building in self.get_buildings()
        )        

    def place_building(self, x: int, y: int, building: Building) -> bool:
        tile = self.tiles.get((x, y))

        if not tile:
            return False

        if not tile.is_empty():
            return False

        tile.building = building
        return True

    def get_buildings(self, building_type: BuildingType | None = None) -> list[Building]:
        buildings: list[Building] = []

        for tile in self.tiles.values():
            if tile.building is None:
                continue

            if building_type is None or tile.building.building_type == building_type:
                buildings.append(tile.building)

        return buildings

    def has_building(self, building_type: BuildingType) -> bool:
        return bool(self.get_buildings(building_type))
        
        
    def completed_building_exists(self, building_type: BuildingType) -> bool:
        for building in self.get_buildings(building_type):
            if not building.is_under_construction:
                return True
        return False


    def class_is_unlocked(self, viking_class: VikingClass) -> bool:
        if viking_class in {VikingClass.RAIDER, VikingClass.SAILOR}:
            return True

        required_building = CLASS_UNLOCK_BUILDINGS.get(viking_class)

        if required_building is None:
            return False

        return self.completed_building_exists(required_building)


    def role_is_unlocked(self, crew_role: CrewRole) -> bool:
        return crew_role == CrewRole.CAPTAIN or crew_role == CrewRole.RAIDER
        
    def unlock_summary(self) -> str:
        unlocked_classes = [
            viking_class.value
            for viking_class in VikingClass
            if self.class_is_unlocked(viking_class)
        ]

        unlocked_roles = [
            role.value
            for role in CrewRole
            if self.role_is_unlocked(role)
        ]

        return "Unlocked Classes: " + ", ".join(unlocked_classes)     
        
    def building_can_be_built_on_tile(
        self,
        building_type: BuildingType,
        x: int,
        y: int,
    ) -> tuple[bool, str]:
        # Ship-based buildings must be on coastline.
        if building_type == BuildingType.SHIPYARD and x != 1:
            return False, "Shipyards must be built on coastline tiles."

        # Farms cannot be built on coastline.
        if building_type == BuildingType.FARM and x == 1:
            return False, "Farms cannot be built on coastline tiles."
        
        # Mines cannot be built on coastline.
        if building_type == BuildingType.MINE and x == 1:
            return False, "Mines cannot be built on coastline tiles."    

        return True, ""    


    def build_facility(self, x: int, y: int, building_type: BuildingType) -> tuple[bool, str, int]:
        tile = self.tiles.get((x, y))

        if self.has_active_construction():
            return False, "Only one building can be under construction at a time.", 0

        if not tile:
            return False, "Invalid tile.", 0

        if not tile.is_empty():
            return False, "That tile is not empty.", 0
            
        can_build, reason = self.building_can_be_built_on_tile(building_type, x, y)

        if not can_build:
            return False, reason, 0    

        cost = BUILDING_COSTS.get(building_type)
        weeks = BUILDING_BUILD_WEEKS.get(building_type)

        if cost is None or weeks is None:
            return False, f"{building_type.value} cannot be built this way.", 0

        tile.building = Building(
            building_type=building_type,
            level=1,
            is_under_construction=True,
            weeks_remaining=weeks,
        )

        return True, f"Started building {building_type.value}. It will take {weeks} weeks.", cost
        
    def thrall_capacity(self) -> int:
        total = THRALL_CAPACITY_BASE

        for quarters in self.get_buildings(BuildingType.THRALL_QUARTERS):
            if quarters.is_under_construction:
                continue

            total += quarters.level * THRALL_CAPACITY_PER_QUARTERS_LEVEL

        return total    

    def highest_completed_level(self, building_type: BuildingType) -> int:
        levels = [
            building.level
            for building in self.get_buildings(building_type)
            if not building.is_under_construction
        ]

        return max(levels) if levels else 0
        
    def training_grounds_level(self) -> int:
        levels = [
            building.level
            for building in self.get_buildings(BuildingType.TRAINING_GROUNDS)
            if not building.is_under_construction
        ]

        return min(3, max(levels) if levels else 0)  

    def herbalists_hut_level(self) -> int:
        levels = [
            building.level
            for building in self.get_buildings(BuildingType.HERBALISTS_HUT)
            if not building.is_under_construction
        ]

        return min(4, max(levels) if levels else 0)


    def herbalists_hut_recovery_reduction_percent(self) -> int:
        return self.herbalists_hut_level() * 10        


    def upgrade_building_at(self, x: int, y: int) -> tuple[bool, str, int]:
        tile = self.tiles.get((x, y))
        
        if self.has_active_construction():
            return False, "Only one building can be under construction at a time.", 0        

        if not tile or not tile.building:
            return False, "No building on that tile.", 0

        building = tile.building
        if building.building_type == BuildingType.TRAINING_GROUNDS and building.level >= 3:
            return False, "Training Grounds is already at max level.", 0

        if building.building_type == BuildingType.MINE and building.level >= MINE_MAX_LEVEL:
            return False, "Mine is already at max level.", 0
            
        if building.is_under_construction:
            return False, "That building is already under construction.", 0

        cost = BUILDING_UPGRADE_BASE_COST * building.level
        building.level += 1
        building.is_under_construction = True
        building.weeks_remaining = BUILDING_UPGRADE_WEEKS

        return True, f"Started upgrading {building.building_type.value} to level {building.level}.", cost    

    def advance_week(self) -> None:
        for tile in self.tiles.values():
            if tile.building:
                tile.building.advance_week()
                
    def monthly_upkeep_cost(self) -> int:
        total = 0

        for building in self.get_buildings():
            if building.is_under_construction:
                continue

            base_cost = BUILDING_MONTHLY_UPKEEP.get(building.building_type, 0)
            total += base_cost * building.level

        return total

    def food_storage_capacity(self) -> int:
        total = BASE_FOOD_STORAGE

        for farm in self.get_buildings(BuildingType.FARM):
            if farm.is_under_construction:
                continue

            total += farm.level * FOOD_STORAGE_PER_FARM_LEVEL

        return total

    def timber_storage_capacity(self) -> int:
        total = BASE_TIMBER_STORAGE

        for woodwright in self.get_buildings(BuildingType.CARPENTERS_HUT):
            if woodwright.is_under_construction:
                continue

            total += woodwright.level * TIMBER_STORAGE_PER_WOODWRIGHT_LEVEL

        return total


    def fine_metal_storage_capacity(self) -> int:
        total = BASE_FINE_METAL_STORAGE

        for mine in self.get_buildings(BuildingType.MINE):
            if mine.is_under_construction:
                continue

            total += mine.level * FINE_METAL_STORAGE_PER_MINE_LEVEL

        return total


    def produce_monthly_fine_metal(self) -> int:
        total = 0

        for mine in self.get_buildings(BuildingType.MINE):
            if mine.is_under_construction:
                continue

            total += mine.level * FINE_METAL_MONTHLY_PRODUCTION_PER_LEVEL

        return total
        
    def barracks_capacity(self) -> int:
        total = 0

        if self.has_building(BuildingType.LONGHOUSE):
            total += LONGHOUSE_BASE_CAPACITY

        for barracks in self.get_buildings(BuildingType.BARRACKS):
            if barracks.is_under_construction:
                continue

            total += barracks.level * BARRACKS_CAPACITY_PER_LEVEL

        return total


    def can_recruit_viking(self, current_viking_count: int) -> bool:
        return current_viking_count < self.barracks_capacity()


    def repair_ship(
        self,
        ship,
        silver_available: int,
        ship_timber_available: int,
        fine_metal_available: int,
    ) -> tuple[int, int, int, int]:
        """
        Returns:
        (silver_spent, timber_spent, fine_metal_spent, hull_repaired)
        """
        import math

        if not self.has_building(BuildingType.SHIPYARD):
            return 0, 0, 0, 0

        missing_hull = ship.max_hull - ship.hull

        if missing_hull <= 0:
            return 0, 0, 0, 0

        max_affordable_repair = min(
            missing_hull,
            silver_available,
            ship_timber_available * 5,
        )

        while max_affordable_repair > 0:
            fine_metal_needed = max_affordable_repair // 25

            if fine_metal_needed <= fine_metal_available:
                break

            max_affordable_repair -= 1

        if max_affordable_repair <= 0:
            return 0, 0, 0, 0

        old_hull = ship.hull
        ship.repair(max_affordable_repair)

        actual_repaired = ship.hull - old_hull

        if actual_repaired <= 0:
            return 0, 0, 0, 0

        silver_spent = actual_repaired
        timber_spent = math.ceil(actual_repaired / 5)
        fine_metal_spent = actual_repaired // 25

        return silver_spent, timber_spent, fine_metal_spent, actual_repaired
          

    def produce_monthly_food(self, season: Season) -> int:
        """
        Farms produce food at the end of Spring and Summer months.
        Winter farms produce nothing for now.
        """
        total_food = 0

        # ------------------------------------------
        # Farms produce in Spring and Summer
        # ------------------------------------------
        if season in {Season.SPRING, Season.SUMMER}:
            for farm in self.get_buildings(BuildingType.FARM):
                if farm.is_under_construction:
                    continue

                total_food += 6 + (farm.level * 6)

        # ------------------------------------------
        # Hunter's Lodge produces during Winter
        # ------------------------------------------
        if season == Season.WINTER:
            for lodge in self.get_buildings(BuildingType.HUNTERS_SHACK):
                if lodge.is_under_construction:
                    continue

                total_food += 5 + (lodge.level * 3)

        return total_food

    def display_grid(self) -> str:
        rows: list[str] = []

        header = "      " + " ".join(f"{x:>6}" for x in range(1, self.width + 1))
        rows.append(header)

        for y in range(1, self.height + 1):
            row = [f"{y:>3} "]

            for x in range(1, self.width + 1):
                tile = self.tiles[(x, y)]
                row.append(f"[{tile.display_symbol():^4}]")

            rows.append(" ".join(row))

        return "\n".join(rows)

    def summary(self) -> str:
        lines = [
            f"Village: {self.name}",
            self.display_grid(),
            "",
            "Buildings:",
        ]

        for tile in self.tiles.values():
            if tile.building:
                lines.append(
                    f"({tile.x}, {tile.y}) - {tile.building.display_name()}"
                )
        lines.append("")
        lines.append(self.unlock_summary())        

        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "village_id": self.village_id,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "tiles": [
                tile.to_dict()
                for tile in self.tiles.values()
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Village":
        village = cls(
            village_id=data.get("village_id", str(uuid.uuid4())),
            name=data["name"],
            width=data.get("width", 3),
            height=data.get("height", 3),
        )

        village.tiles = {}

        for tile_data in data.get("tiles", []):
            tile = VillageTile.from_dict(tile_data)
            village.tiles[(tile.x, tile.y)] = tile

        return village


def create_starting_village(village_name: str) -> Village:
    village = Village(name=village_name)

    village.place_building(1, 3, Building(BuildingType.SHIPYARD))
    village.place_building(2, 2, Building(BuildingType.TRADER))
    village.place_building(2, 3, Building(BuildingType.LONGHOUSE))
    village.place_building(3, 3, Building(BuildingType.FARM))
    village.place_building(2, 4, Building(BuildingType.BARRACKS))

    return village