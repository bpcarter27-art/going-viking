from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import random


# ====================================================
# RARITY
# ====================================================

class TraitRarity(str, Enum):
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    LEGENDARY = "Legendary"


# ====================================================
# TRAIT MODEL
# ====================================================

@dataclass(frozen=True)
class Trait:
    name: str
    rarity: TraitRarity
    description: str

    might_bonus: int = 0
    skill_bonus: int = 0
    cunning_bonus: int = 0
    leadership_bonus: int = 0
    courage_bonus: int = 0
    vitality_bonus: int = 0
    agility_bonus: int = 0
    loyalty_bonus: int = 0
    seamanship_bonus: int = 0

    injury_recovery_bonus: float = 0.0


# ====================================================
# COMMON TRAITS
# ====================================================

COMMON_TRAITS = [
    Trait(
        name="Mighty",
        rarity=TraitRarity.COMMON,
        description="+5 Might",
        might_bonus=5,
    ),

    Trait(
        name="Clever",
        rarity=TraitRarity.COMMON,
        description="+5 Cunning",
        cunning_bonus=5,
    ),

    Trait(
        name="Hardy",
        rarity=TraitRarity.COMMON,
        description="+5 Vitality",
        vitality_bonus=5,
    ),

    Trait(
        name="Bold",
        rarity=TraitRarity.COMMON,
        description="+5 Courage",
        courage_bonus=5,
    ),

    Trait(
        name="Sure-Footed",
        rarity=TraitRarity.COMMON,
        description="+5 Agility",
        agility_bonus=5,
    ),

    Trait(
        name="Weathered Sailor",
        rarity=TraitRarity.COMMON,
        description="+5 Seamanship",
        seamanship_bonus=5,
    ),
]


# ====================================================
# UNCOMMON TRAITS
# ====================================================

UNCOMMON_TRAITS = [
    Trait(
        name="Hunter",
        rarity=TraitRarity.UNCOMMON,
        description="+5 Skill, +5 Agility",
        skill_bonus=5,
        agility_bonus=5,
    ),

    Trait(
        name="Silver-Tongued",
        rarity=TraitRarity.UNCOMMON,
        description="+5 Leadership, +5 Cunning",
        leadership_bonus=5,
        cunning_bonus=5,
    ),

    Trait(
        name="Raider's Instinct",
        rarity=TraitRarity.UNCOMMON,
        description="+5 Might, +5 Seamanship",
        might_bonus=5,
        seamanship_bonus=5,
    ),
]


# ====================================================
# RARE TRAITS
# ====================================================

RARE_TRAITS = [
    Trait(
        name="Berserker Spirit",
        rarity=TraitRarity.RARE,
        description="+5 Might, +5 Courage",
        might_bonus=5,
        courage_bonus=5,
    ),

    Trait(
        name="Virile",
        rarity=TraitRarity.RARE,
        description="Recover from injuries 20% faster",
        injury_recovery_bonus=0.20,
    ),

    Trait(
        name="Sea-King",
        rarity=TraitRarity.RARE,
        description="+10 Seamanship, +5 Leadership",
        seamanship_bonus=10,
        leadership_bonus=5,
    ),
]


# ====================================================
# LEGENDARY TRAITS
# ====================================================

LEGENDARY_TRAITS = [
    Trait(
        name="Thor's Might",
        rarity=TraitRarity.LEGENDARY,
        description="+20 Might",
        might_bonus=20,
    ),

    Trait(
        name="Volva's Foresight",
        rarity=TraitRarity.LEGENDARY,
        description="The gods whisper of danger yet to come.",
        cunning_bonus=10,
        leadership_bonus=10,
    ),
]


# ====================================================
# LOOKUPS
# ====================================================

TRAITS_BY_RARITY = {
    TraitRarity.COMMON: COMMON_TRAITS,
    TraitRarity.UNCOMMON: UNCOMMON_TRAITS,
    TraitRarity.RARE: RARE_TRAITS,
    TraitRarity.LEGENDARY: LEGENDARY_TRAITS,
}


# ====================================================
# ROLLING
# ====================================================

RARITY_WEIGHTS = {
    TraitRarity.COMMON: 75,
    TraitRarity.UNCOMMON: 18,
    TraitRarity.RARE: 6,
    TraitRarity.LEGENDARY: 1,
}


def roll_trait_rarity() -> TraitRarity:
    rarities = list(RARITY_WEIGHTS.keys())
    weights = list(RARITY_WEIGHTS.values())

    return random.choices(rarities, weights=weights, k=1)[0]


def roll_random_trait(existing_traits: list[str] | None = None) -> Trait | None:
    existing_traits = existing_traits or []

    rarity = roll_trait_rarity()

    possible = [
        trait
        for trait in TRAITS_BY_RARITY[rarity]
        if trait.name not in existing_traits
    ]

    if not possible:
        return None

    return random.choice(possible)
    
ALL_TRAITS = (
    COMMON_TRAITS
    + UNCOMMON_TRAITS
    + RARE_TRAITS
    + LEGENDARY_TRAITS
)

ALL_TRAITS_BY_NAME = {
    trait.name: trait
    for trait in ALL_TRAITS
}    