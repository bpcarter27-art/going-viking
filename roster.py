from __future__ import annotations

import random

from models import Viking, FavoredGod, CrewRole, VikingClass, Ship
from traits import roll_random_trait

from items import (
    Item,
    copy_item,
    BASIC_AXE,
    BASIC_KNIFE,
    BASIC_HAMMER,
    BASIC_SPEAR,
    BASIC_SWORD,
    BASIC_SHIELD,
    BASIC_ARMOR,
    BASIC_BOW,
    BASIC_HELM,
)


MALE_NAMES = [
    "Agnar",
    "Arne",
    "Asbjorn",
    "Askell",
    "Atli",
    "Baggi",
    "Bersi",
    "Bjarke",
    "Bjorn",
    "Bodvar",
    "Brandr",
    "Dag",
    "Egil",
    "Einar",
    "Eirik",
    "Erland",
    "Eskil",
    "Finn",
    "Floki",
    "Frode",
    "Geirmund",
    "Gorm",
    "Gudmund",
    "Gunnar",
    "Halfdan",
    "Hallbjorn",
    "Hallstein",
    "Harald",
    "Harek",
    "Hemming",
    "Herleif",
    "Hjalmar",
    "Hrolf",
    "Hrothgar",
    "Hvitserk",
    "Ingolf",
    "Ivar",
    "Jorund",
    "Ketil",
    "Kjell",
    "Knut",
    "Leif",
    "Magnus",
    "Njall",
    "Odd",
    "Olaf",
    "Orm",
    "Ragnar",
    "Ragnvald",
    "Roald",
    "Rolf",
    "Sigfred",
    "Sigmund",
    "Sigurd",
    "Skarde",
    "Snorri",
    "Sten",
    "Styrbjorn",
    "Sven",
    "Thjolf",
    "Thorald",
    "Thorbjorn",
    "Thord",
    "Thorfinn",
    "Thorgrim",
    "Thorir",
    "Thorleif",
    "Thorolf",
    "Toki",
    "Trygve",
    "Ubbe",
    "Ulf",
    "Valgard",
    "Vidar",
    "Viggo",
]

FEMALE_NAMES = [
    "Alfhild",
    "Asa",
    "Aslaug",
    "Astrid",
    "Brynhild",
    "Dagmar",
    "Eira",
    "Estrid",
    "Freydis",
    "Frida",
    "Geira",
    "Gudrun",
    "Gunnhild",
    "Halfhild",
    "Hallbera",
    "Helga",
    "Hilda",
    "Inga",
    "Ingibjorg",
    "Ingrid",
    "Jorunn",
    "Katla",
    "Lagertha",
    "Liv",
    "Ragna",
    "Rannveig",
    "Runa",
    "Sif",
    "Signy",
    "Sigrid",
    "Solveig",
    "Svanhild",
    "Thora",
    "Thorunn",
    "Torvi",
    "Tyra",
    "Unn",
    "Valdis",
    "Ylva",
    "Yrsa",
]

NICKNAMES = [
    "the Red",
    "the Black",
    "the White",
    "the Grim",
    "the Bold",
    "the Lucky",
    "the Quiet",
    "the Swift",
    "the Wanderer",
    "the Scarred",
    "the Tall",
    "the Stout",
    "the Young",
    "the Old",
    "the Fearless",
    "Ironhand",
    "Wolf-Eyed",
    "Broadshield",
    "Stormborn",
    "Axe-Biter",
    "Strongarm",
    "Blacktooth",
    "Ravensbane",
    "Skullsplitter",
    "Oathbreaker",
    "Oathkeeper",
    "Sea-Wolf",
    "Frostborn",
    "Whalebone",
    "Longbraid",
    "Hammerfist",
    "Iceblood",
    "Shieldbreaker",
    "Deepwater",
    "Redblade",
    "Croweye",
]

def display_name(viking) -> str:
    if hasattr(viking, "display_name"):
        return viking.display_name()
    return viking.name

def roll_rating(min_value: int = 20, max_value: int = 80) -> int:
    return random.randint(min_value, max_value)


def pick_name(viking_class: VikingClass) -> str:
    if viking_class == VikingClass.SHIELDMAIDEN:
        name = random.choice(FEMALE_NAMES)
    else:
        name = random.choice(MALE_NAMES)

    if random.random() < 0.12:
        name = f"{name} {random.choice(NICKNAMES)}"

    return name
    
def random_birth_date() -> tuple[int, int]:
    return random.randint(1, 12), random.randint(1, 4)    


def random_starting_class() -> VikingClass:
    return random.choice([
        VikingClass.RAIDER,
        VikingClass.SAILOR,
    ])


GOD_STAT_BONUSES = {
    FavoredGod.ODIN: "leadership",
    FavoredGod.THOR: "might",
    FavoredGod.FREYJA: "courage",
    FavoredGod.NJORD: "seamanship",
    FavoredGod.LOKI: "cunning",
    FavoredGod.TYR: "loyalty",
    FavoredGod.HEIMDALL: "skill",
    FavoredGod.FRIGG: "vitality",
    FavoredGod.BALDR: "renown",
    FavoredGod.SKADI: "agility",
}

CORE_STATS = [
    "might",
    "skill",
    "cunning",
    "leadership",
    "courage",
    "vitality",
    "agility",
    "seamanship",
]

def record_original_stats(viking: Viking) -> None:
    viking.original_stats = {
        stat: getattr(viking, stat)
        for stat in CORE_STATS
    }


def roll_recruit_age() -> int:
    roll = random.randint(1, 100)

    if roll <= 70:
        return random.randint(16, 24)

    if roll <= 90:
        return random.randint(25, 32)

    return random.randint(33, 42)


def stat_range_for_age(age: int, base_min: int, base_max: int) -> tuple[int, int]:
    if age <= 20:
        return max(1, base_min - 5), max(1, base_max - 5)

    if age <= 24:
        return base_min, base_max

    if age <= 32:
        return base_min + 7, base_max + 7

    if age <= 36:
        return base_min + 15, base_max + 8

    # Very old recruits are proven, but close to decline/retirement.
    return base_min + 20, base_max + 5

def roll_stat_potential_for_viking(viking: Viking) -> dict[str, int]:
    return {
        stat: random.randint(getattr(viking, stat), 100)
        for stat in CORE_STATS
    }

def apply_god_bonus(viking: Viking) -> None:
    stat = GOD_STAT_BONUSES.get(viking.favored_god)

    if not stat:
        return

    bonus = random.randint(5, 10)

    if stat == "renown":
        viking.renown += bonus
    else:
        current_value = getattr(viking, stat)
        setattr(viking, stat, current_value + bonus)


def god_bonus_text(viking: Viking) -> str:
    stat = GOD_STAT_BONUSES.get(viking.favored_god)

    if not stat:
        return viking.favored_god.value

    label = stat.upper()[:3]

    return f"{viking.favored_god.value}({label})"


def create_player_jarl(player_name: str, favored_god: FavoredGod) -> Viking:
    birth_month, birth_week = random_birth_date()

    jarl = Viking(
        name=player_name,
        age=20,
        birth_month=birth_month,
        birth_week=birth_week,
        might=random.randint(50, 70),
        skill=random.randint(50, 70),
        cunning=random.randint(50, 70),
        leadership=random.randint(50, 70),
        courage=random.randint(50, 70),
        vitality=random.randint(50, 70),
        agility=random.randint(50, 70),
        loyalty=100,
        seamanship=random.randint(50, 70),
        favored_god=favored_god,
        viking_class=VikingClass.RAIDER,
        role=CrewRole.CAPTAIN,
        silver_wage=0,
        is_player=True,
    )

    apply_god_bonus(jarl)
    jarl.stat_potential = {
        stat: 100
        for stat in CORE_STATS
    }    
    return jarl

def generate_basic_equipment_for_viking(viking: Viking) -> list[Item]:
    generated_items: list[Item] = []

    def equip(template: Item, slot_name: str) -> None:
        item = copy_item(template)
        generated_items.append(item)
        setattr(viking.equipment, slot_name, item.item_id)

    # Most vikings get basic armor.
    equip(BASIC_ARMOR, "armor")

    if viking.viking_class == VikingClass.RAIDER:
        equip(random.choice([BASIC_AXE, BASIC_SWORD, BASIC_SPEAR]), "primary_weapon")
        equip(BASIC_SHIELD, "shield")

        if random.random() < 0.50:
            equip(BASIC_HELM, "helm")

    elif viking.viking_class == VikingClass.SAILOR:
        equip(random.choice([BASIC_AXE, BASIC_SPEAR, BASIC_KNIFE]), "primary_weapon")

        if random.random() < 0.35:
            equip(BASIC_SHIELD, "shield")

    elif viking.viking_class == VikingClass.ARCHER:
        equip(BASIC_BOW, "primary_weapon")

        if random.random() < 0.50:
            equip(BASIC_HELM, "helm")

    elif viking.viking_class == VikingClass.TRICKSTER:
        equip(BASIC_KNIFE, "primary_weapon")

        if random.random() < 0.25:
            equip(BASIC_HELM, "helm")

    elif viking.viking_class == VikingClass.HERSIR:
        equip(random.choice([BASIC_SWORD, BASIC_SPEAR, BASIC_AXE]), "primary_weapon")
        equip(BASIC_SHIELD, "shield")
        equip(BASIC_HELM, "helm")

    elif viking.viking_class == VikingClass.SHIELDMAIDEN:
        equip(random.choice([BASIC_SPEAR, BASIC_SWORD, BASIC_AXE]), "primary_weapon")
        equip(BASIC_SHIELD, "shield")

        if random.random() < 0.75:
            equip(BASIC_HELM, "helm")

    elif viking.viking_class == VikingClass.HERBALIST:
        equip(BASIC_KNIFE, "primary_weapon")

    elif viking.viking_class == VikingClass.SCOUT:
        equip(random.choice([BASIC_BOW, BASIC_SPEAR, BASIC_KNIFE]), "primary_weapon")

        if random.random() < 0.25:
            equip(BASIC_HELM, "helm")

    else:
        equip(random.choice([BASIC_AXE, BASIC_SWORD, BASIC_SPEAR]), "primary_weapon")

    return generated_items

def generate_viking(
    role: CrewRole = CrewRole.RAIDER,
    viking_class: VikingClass | None = None,
    training_level: int = 0,
    shrine_level: int = 0,
) -> Viking:
    viking_class = viking_class or random_starting_class()
    birth_month, birth_week = random_birth_date()

    age = roll_recruit_age()

    training_level = max(0, min(3, training_level))

    base_ranges_by_training = {
        0: (10, 45),
        1: (15, 50),
        2: (20, 55),
        3: (25, 60),
    }

    base_min, base_max = base_ranges_by_training[training_level]

    base_min, base_max = stat_range_for_age(age, base_min, base_max)

    favored_god = random.choice(list(FavoredGod))
    favored_stat = GOD_STAT_BONUSES[favored_god]

    def roll_recruit_stat(stat_name: str) -> int:
        low = base_min
        high = base_max

        if stat_name == favored_stat and stat_name != "renown":
            low += 5
            high += 10

        return random.randint(max(1, low), min(100, high))

    might = roll_recruit_stat("might")
    skill = roll_recruit_stat("skill")
    cunning = roll_recruit_stat("cunning")
    leadership = roll_recruit_stat("leadership")
    courage = roll_recruit_stat("courage")
    vitality = roll_recruit_stat("vitality")
    agility = roll_recruit_stat("agility")
    loyalty = random.randint(35, 75)
    seamanship = roll_recruit_stat("seamanship")

    class_bonus_low = 5 + (training_level)
    class_bonus_high = 8 + (training_level * 2)

    if viking_class == VikingClass.RAIDER:
        might += random.randint(class_bonus_low, class_bonus_high)

    elif viking_class == VikingClass.ARCHER:
        skill += random.randint(class_bonus_low, class_bonus_high)

    elif viking_class == VikingClass.TRICKSTER:
        cunning += random.randint(class_bonus_low, class_bonus_high)

    elif viking_class == VikingClass.HERSIR:
        leadership += random.randint(class_bonus_low, class_bonus_high)

    elif viking_class == VikingClass.SHIELDMAIDEN:
        courage += random.randint(class_bonus_low, class_bonus_high)

    elif viking_class == VikingClass.HERBALIST:
        vitality += random.randint(class_bonus_low, class_bonus_high)

    elif viking_class == VikingClass.SCOUT:
        agility += random.randint(class_bonus_low, class_bonus_high)

    elif viking_class == VikingClass.SAILOR:
        seamanship += random.randint(class_bonus_low, class_bonus_high)

    viking = Viking(
        name=pick_name(viking_class),
        age=age,
        birth_month=birth_month,
        birth_week=birth_week,
        might=min(100, might),
        skill=min(100, skill),
        cunning=min(100, cunning),
        leadership=min(100, leadership),
        courage=min(100, courage),
        vitality=min(100, vitality),
        agility=min(100, agility),
        loyalty=min(100, loyalty),
        seamanship=min(100, seamanship),
        favored_god=favored_god,
        viking_class=viking_class,
        role=role,
        silver_wage=random.randint(1, 3),
    )
    
    viking.traits.extend(roll_starting_traits(shrine_level))
    
    apply_god_bonus(viking)

    viking.stat_potential = roll_stat_potential_for_viking(viking)
    record_original_stats(viking)
    viking.record_stat_history()

    return viking
    
def roll_starting_traits(shrine_level: int = 0) -> list:
    import random
    trait_chances = {
        0: 0.15,
        1: 0.20,
        2: 0.25,
        3: 0.30,
        4: 0.35,
    }

    chance = trait_chances.get(shrine_level, 0.35)

    traits = []

    if random.random() <= chance:
        trait = roll_random_trait()
        if trait:
            traits.append(trait)

        if shrine_level >= 2:
            if random.random() <= chance:
                trait = roll_random_trait(
                    existing_traits=[t.name for t in traits]
                )

                if trait:
                    traits.append(trait)

        if shrine_level >= 4:
            if len(traits) >= 2:
                if random.random() <= chance:
                    trait = roll_random_trait(
                        existing_traits=[t.name for t in traits]
                    )

                    if trait:
                        traits.append(trait)

    return traits    
    
def generate_starting_crew_viking(
    role: CrewRole = CrewRole.RAIDER,
    viking_class: VikingClass | None = None,
) -> Viking:
    viking_class = viking_class or random_starting_class()
    birth_month, birth_week = random_birth_date()

    favored_god = random.choice(list(FavoredGod))

    viking = Viking(
        name=pick_name(viking_class),
        age=random.randint(16, 40),
        birth_month=birth_month,
        birth_week=birth_week,
        might=random.randint(25, 68),
        skill=random.randint(25, 68),
        cunning=random.randint(25, 68),
        leadership=random.randint(25, 68),
        courage=random.randint(25, 68),
        vitality=random.randint(25, 68),
        agility=random.randint(25, 68),
        loyalty=random.randint(55, 80),
        seamanship=random.randint(25, 68),
        favored_god=favored_god,
        viking_class=viking_class,
        role=role,
        silver_wage=random.randint(1, 3),
    )

    viking.traits.extend(roll_starting_traits(0))

    apply_god_bonus(viking)
    viking.stat_potential = roll_stat_potential_for_viking(viking)
    record_original_stats(viking)

    return viking    

def generate_starting_roster(
    player_name: str,
    player_favored_god: FavoredGod,
) -> dict[str, Viking]:
    vikings = {}

    player_jarl = create_player_jarl(player_name, player_favored_god)
    vikings[player_jarl.viking_id] = player_jarl

    starting_crew_size = 7

    for _ in range(starting_crew_size):
        viking = generate_starting_crew_viking()
        vikings[viking.viking_id] = viking

    viking.record_stat_history()

    return vikings

def create_starting_ship(
    vikings: dict[str, Viking],
    ship_name: str = "Sea Wolf",
) -> Ship:
    ship = Ship(name=ship_name)

    for viking_id in vikings:
        ship.add_crew_member(viking_id)

    return ship


def print_roster(vikings: dict[str, Viking], inventory: dict | None = None) -> None:
    inventory = inventory or {}

    def item_bonus(viking: Viking, stat_name: str) -> int:
        total = 0

        equipped_ids = [
            viking.equipment.armor,
            viking.equipment.helm,
            viking.equipment.primary_weapon,
            getattr(viking.equipment, "secondary_weapon", None),
            viking.equipment.shield,
        ]

        for item_id in equipped_ids:
            if not item_id:
                continue

            item = inventory.get(item_id)
            if not item:
                continue

            total += getattr(item, f"{stat_name}_bonus", 0)

        return total

    def stat_text(viking: Viking, stat_name: str) -> str:
        base = getattr(viking, stat_name)
        item = item_bonus(viking, stat_name)
        trait = viking.get_trait_bonus(stat_name)
        total = base + item + trait

        bonus = item + trait

        if bonus == 0:
            return str(base)

        return f"{total}({bonus:+})"

    print("\nCREW ROSTER")
    print("-" * 160)

    for viking in vikings.values():
        if viking.status.value in {"Dead", "Retired"}:
            continue

        player_marker = "*" if viking.is_player else " "

        injury_text = ""
        if viking.injury_weeks_remaining > 0:
            injury_text = f" | Injured {viking.injury_weeks_remaining}w"

        trait_text = ""
        if viking.traits:
            trait_text = " | Traits: " + ", ".join(
                trait.name for trait in viking.traits
            )

        print(
            f"{player_marker} {display_name(viking):22} "
            f"{viking.status.value:9} "
            f"{viking.role.value:10} "
            f"{viking.viking_class.value:13} "
            f"[OVR {viking.overall_grade()} / POT {viking.potential_overall_grade()}] | "
            f"Age {viking.age:2} "
            f"(Born M{viking.birth_month} W{viking.birth_week}) | "
            f"MGT {stat_text(viking, 'might')} "
            f"SKL {stat_text(viking, 'skill')} "
            f"CUN {stat_text(viking, 'cunning')} "
            f"LDR {stat_text(viking, 'leadership')} "
            f"CRG {stat_text(viking, 'courage')} "
            f"VIT {stat_text(viking, 'vitality')} "
            f"AGI {stat_text(viking, 'agility')} "
            f"SEA {stat_text(viking, 'seamanship')} "
            f"LOY {stat_text(viking, 'loyalty')} | "
            f"REN {viking.renown} | "
            f"WAGE {0 if viking.is_player else 1 + (viking.renown // 5)} | "
            f"{god_bonus_text(viking)}"
            f"{injury_text}"
            f"{trait_text}"
        )