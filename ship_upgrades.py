# ship_upgrades.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# ====================================================
# SHIP PARTS
# ====================================================

class ShipPart(str, Enum):
    HULL = "Hull"
    CARGO = "Cargo"
    CREW = "Crew"
    SAIL = "Sail"
    NAVIGATION = "Navigation"


# ====================================================
# SHIP UPGRADE MODEL
# ====================================================

@dataclass(frozen=True)
class ShipUpgrade:
    part: ShipPart
    level: int
    name: str

    silver_cost: int = 0
    ship_timber_cost: int = 0
    fine_metal_cost: int = 0

    build_weeks: int = 1

    required_shipyard_level: int = 0
    required_carpenters_hut_level: int = 0

    hull_bonus: int = 0
    cargo_bonus: int = 0
    crew_bonus: int = 0
    sail_bonus: int = 0
    navigation_bonus: int = 0
    range_bonus: int = 0

    food_cost_reduction: int = 0
    duration_reduction_chance: int = 0

    description: str = ""


# ====================================================
# HULL UPGRADES
# ====================================================

HULL_UPGRADES = {
    1: ShipUpgrade(
        part=ShipPart.HULL,
        level=1,
        name="Hull I",

        silver_cost=25,
        ship_timber_cost=8,
        build_weeks=2,

        hull_bonus=20,

        description=(
            "Basic repairs and reinforcement improve the ship's durability."
        ),
    ),

    2: ShipUpgrade(
        part=ShipPart.HULL,
        level=2,
        name="Hull II",

        silver_cost=55,
        ship_timber_cost=16,
        fine_metal_cost=2,
        build_weeks=3,

        required_shipyard_level=1,
        required_carpenters_hut_level=1,

        hull_bonus=30,

        description=(
            "A stronger hull fit for rougher seas and longer voyages."
        ),
    ),

    3: ShipUpgrade(
        part=ShipPart.HULL,
        level=3,
        name="Hull III",

        silver_cost=100,
        ship_timber_cost=28,
        fine_metal_cost=5,
        build_weeks=4,

        required_shipyard_level=2,
        required_carpenters_hut_level=2,

        hull_bonus=40,

        description=(
            "Heavy bracing and deeper construction improve seaworthiness."
        ),
    ),

    4: ShipUpgrade(
        part=ShipPart.HULL,
        level=4,
        name="Hull IV",

        silver_cost=170,
        ship_timber_cost=44,
        fine_metal_cost=9,
        build_weeks=5,

        required_shipyard_level=3,
        required_carpenters_hut_level=3,

        hull_bonus=55,

        description=(
            "A hardened deep-water hull built for dangerous seas."
        ),
    ),

    5: ShipUpgrade(
        part=ShipPart.HULL,
        level=5,
        name="Hull V",

        silver_cost=260,
        ship_timber_cost=65,
        fine_metal_cost=15,
        build_weeks=6,

        required_shipyard_level=4,
        required_carpenters_hut_level=4,

        hull_bonus=75,

        description=(
            "A legendary hull worthy of distant saga voyages."
        ),
    ),
}


# ====================================================
# CARGO UPGRADES
# ====================================================

CARGO_UPGRADES = {
    1: ShipUpgrade(
        part=ShipPart.CARGO,
        level=1,
        name="Cargo I",

        silver_cost=20,
        ship_timber_cost=6,
        build_weeks=1,

        cargo_bonus=8,

        description=(
            "Simple storage improvements increase carrying capacity."
        ),
    ),

    2: ShipUpgrade(
        part=ShipPart.CARGO,
        level=2,
        name="Cargo II",

        silver_cost=45,
        ship_timber_cost=12,
        build_weeks=2,

        required_shipyard_level=1,
        required_carpenters_hut_level=1,

        cargo_bonus=12,

        description=(
            "Better storage allows more food, loot, and supplies."
        ),
    ),

    3: ShipUpgrade(
        part=ShipPart.CARGO,
        level=3,
        name="Cargo III",

        silver_cost=80,
        ship_timber_cost=22,
        fine_metal_cost=3,
        build_weeks=3,

        required_shipyard_level=2,
        required_carpenters_hut_level=2,

        cargo_bonus=16,

        description=(
            "Expanded holds support larger expeditions."
        ),
    ),

    4: ShipUpgrade(
        part=ShipPart.CARGO,
        level=4,
        name="Cargo IV",

        silver_cost=135,
        ship_timber_cost=34,
        fine_metal_cost=6,
        build_weeks=4,

        required_shipyard_level=3,
        required_carpenters_hut_level=3,

        cargo_bonus=22,

        description=(
            "Well-built compartments reduce wasted storage space."
        ),
    ),

    5: ShipUpgrade(
        part=ShipPart.CARGO,
        level=5,
        name="Cargo V",

        silver_cost=210,
        ship_timber_cost=50,
        fine_metal_cost=10,
        build_weeks=5,

        required_shipyard_level=4,
        required_carpenters_hut_level=4,

        cargo_bonus=30,

        description=(
            "Massive storage fit for treasure, timber, and captives."
        ),
    ),
}


# ====================================================
# CREW UPGRADES
# ====================================================

CREW_UPGRADES = {
    1: ShipUpgrade(
        part=ShipPart.CREW,
        level=1,
        name="Crew I",

        silver_cost=25,
        ship_timber_cost=8,
        build_weeks=2,

        crew_bonus=2,

        description=(
            "Additional benches allow more crew aboard."
        ),
    ),

    2: ShipUpgrade(
        part=ShipPart.CREW,
        level=2,
        name="Crew II",

        silver_cost=55,
        ship_timber_cost=16,
        fine_metal_cost=2,
        build_weeks=3,

        required_shipyard_level=1,
        required_carpenters_hut_level=1,

        crew_bonus=3,

        description=(
            "Improved layout supports a larger rowing crew."
        ),
    ),

    3: ShipUpgrade(
        part=ShipPart.CREW,
        level=3,
        name="Crew III",

        silver_cost=95,
        ship_timber_cost=26,
        fine_metal_cost=4,
        build_weeks=4,

        required_shipyard_level=2,
        required_carpenters_hut_level=2,

        crew_bonus=4,

        description=(
            "More benches and stronger fittings carry a larger war-band."
        ),
    ),

    4: ShipUpgrade(
        part=ShipPart.CREW,
        level=4,
        name="Crew IV",

        silver_cost=155,
        ship_timber_cost=40,
        fine_metal_cost=8,
        build_weeks=5,

        required_shipyard_level=3,
        required_carpenters_hut_level=3,

        crew_bonus=5,

        description=(
            "The ship now supports a serious raiding force."
        ),
    ),

    5: ShipUpgrade(
        part=ShipPart.CREW,
        level=5,
        name="Crew V",

        silver_cost=240,
        ship_timber_cost=60,
        fine_metal_cost=14,
        build_weeks=6,

        required_shipyard_level=4,
        required_carpenters_hut_level=4,

        crew_bonus=6,

        description=(
            "A massive crew can row, raid, and fight together."
        ),
    ),
}


# ====================================================
# SAIL UPGRADES
# ====================================================

SAIL_UPGRADES = {
    1: ShipUpgrade(
        part=ShipPart.SAIL,
        level=1,
        name="Sail I",

        silver_cost=60,
        ship_timber_cost=10,
        fine_metal_cost=2,
        build_weeks=4,

        sail_bonus=1,
        range_bonus=1,

        food_cost_reduction=1,
        duration_reduction_chance=10,

        description=(
            "A crude first sail. The world begins to open."
        ),
    ),

    2: ShipUpgrade(
        part=ShipPart.SAIL,
        level=2,
        name="Sail II",

        silver_cost=105,
        ship_timber_cost=18,
        fine_metal_cost=4,
        build_weeks=4,

        required_shipyard_level=1,
        required_carpenters_hut_level=1,

        sail_bonus=1,
        range_bonus=1,

        food_cost_reduction=2,
        duration_reduction_chance=15,

        description=(
            "A stronger sail improves speed and reduces strain."
        ),
    ),

    3: ShipUpgrade(
        part=ShipPart.SAIL,
        level=3,
        name="Sail III",

        silver_cost=165,
        ship_timber_cost=30,
        fine_metal_cost=7,
        build_weeks=5,

        required_shipyard_level=2,
        required_carpenters_hut_level=2,

        sail_bonus=1,
        range_bonus=1,

        food_cost_reduction=3,
        duration_reduction_chance=20,

        description=(
            "Reliable rigging makes longer voyages practical."
        ),
    ),

    4: ShipUpgrade(
        part=ShipPart.SAIL,
        level=4,
        name="Sail IV",

        silver_cost=250,
        ship_timber_cost=46,
        fine_metal_cost=12,
        build_weeks=6,

        required_shipyard_level=3,
        required_carpenters_hut_level=3,

        sail_bonus=1,
        range_bonus=1,

        food_cost_reduction=4,
        duration_reduction_chance=25,

        description=(
            "A powerful deep-sea sail fit for open water."
        ),
    ),

    5: ShipUpgrade(
        part=ShipPart.SAIL,
        level=5,
        name="Sail V",

        silver_cost=360,
        ship_timber_cost=70,
        fine_metal_cost=20,
        build_weeks=8,

        required_shipyard_level=4,
        required_carpenters_hut_level=4,

        sail_bonus=1,
        range_bonus=1,

        food_cost_reduction=5,
        duration_reduction_chance=30,

        description=(
            "Masterwork sailcraft worthy of western voyages."
        ),
    ),
}


# ====================================================
# NAVIGATION UPGRADES
# ====================================================

NAVIGATION_UPGRADES = {
    1: ShipUpgrade(
        part=ShipPart.NAVIGATION,
        level=1,
        name="Sunstone Navigation",

        build_weeks=1,

        navigation_bonus=1,
        range_bonus=1,

        description=(
            "A sunstone and the knowledge to read it allow the crew "
            "to find the hidden sun through cloud, mist, and open sea."
        ),
    ),

    2: ShipUpgrade(
        part=ShipPart.NAVIGATION,
        level=2,
        name="Navigation II",

        build_weeks=1,

        required_shipyard_level=1,
        required_carpenters_hut_level=1,

        navigation_bonus=1,
        range_bonus=1,

        description=(
            "Improved sea knowledge opens farther waters."
        ),
    ),

    3: ShipUpgrade(
        part=ShipPart.NAVIGATION,
        level=3,
        name="Navigation III",

        build_weeks=1,

        required_shipyard_level=2,
        required_carpenters_hut_level=2,

        navigation_bonus=1,
        range_bonus=1,

        description=(
            "Experienced navigation reduces the dangers of storms and fog."
        ),
    ),

    4: ShipUpgrade(
        part=ShipPart.NAVIGATION,
        level=4,
        name="Navigation IV",

        build_weeks=1,

        required_shipyard_level=3,
        required_carpenters_hut_level=3,

        navigation_bonus=1,
        range_bonus=1,

        description=(
            "Rare route knowledge reveals hidden waters and opportunities."
        ),
    ),

    5: ShipUpgrade(
        part=ShipPart.NAVIGATION,
        level=5,
        name="Navigation V",

        build_weeks=1,

        required_shipyard_level=4,
        required_carpenters_hut_level=4,

        navigation_bonus=1,
        range_bonus=1,

        description=(
            "Legendary navigation fit for saga voyages into the unknown."
        ),
    ),
}


# ====================================================
# MASTER LOOKUP
# ====================================================

SHIP_UPGRADES = {
    ShipPart.HULL: HULL_UPGRADES,
    ShipPart.CARGO: CARGO_UPGRADES,
    ShipPart.CREW: CREW_UPGRADES,
    ShipPart.SAIL: SAIL_UPGRADES,
    ShipPart.NAVIGATION: NAVIGATION_UPGRADES,
}


# ====================================================
# HELPERS
# ====================================================

def get_ship_upgrade(
    part: ShipPart,
    level: int,
) -> ShipUpgrade | None:
    return SHIP_UPGRADES.get(part, {}).get(level)


def get_next_ship_upgrade(
    part: ShipPart,
    current_level: int,
) -> ShipUpgrade | None:
    return get_ship_upgrade(part, current_level + 1)


def get_all_upgrades_for_part(
    part: ShipPart,
) -> list[ShipUpgrade]:
    return list(
        SHIP_UPGRADES.get(part, {}).values()
    )