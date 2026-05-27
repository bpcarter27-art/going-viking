from __future__ import annotations

import random

from injury import apply_event_injury_risk, InjuryType
from .helpers import *


# ====================================================
# COMBAT EVENTS
# ====================================================

def event_ambush(result, ship, vikings):
    record_tested_stats(result, "might", "skill", "courage", "agility")
    roll = average_top_crew_stat(vikings, "raiding_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Raiding Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("You repel an ambush.")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Ambush",
        injury_danger=6,
        injury_types=[InjuryType.COMBAT, InjuryType.ARROW],
        chance=65,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False


def event_shield_wall(result, ship, vikings):
    record_tested_stats(result, "might", "skill", "courage", "agility")
    roll = average_top_crew_stat(vikings, "raiding_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Raiding {roll} vs Target {target} "
        f"(Base 65, Mod {target_mod:+})."
    )

    if roll >= target:

        silver = random.randint(8, 20)
        result.silver_gained += silver
        result.log.append(f"Your shield wall breaks the enemy line (+{silver} silver).")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Shield Wall Clash",
        injury_danger=6,
        injury_types=[InjuryType.COMBAT, InjuryType.ARROW],
        chance=60,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False


def event_duel(result, ship, vikings):
    viking = pick_random_viking(vikings)
    if not viking:
        return True
        
    record_individual_tested_stats(result, viking, "might", "skill")
    roll = ((viking.might + viking.skill) // 2) + random.randint(-20, 20)
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] {viking.name} Duel {roll} vs Target {target}. "
        f"(Base 60, Mod {target_mod:+})."
        )

    if roll >= target:
        result.log.append(f"{viking.name} wins a duel and earns renown.")
        result.renown_gained += 1
        viking.renown += 1
        return True

    apply_event_injury_risk(
        result=result,
        vikings=[viking],
        event_name="Duel",
        injury_danger=6,
        injury_types=[InjuryType.COMBAT],
        chance=80,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False


def event_minor_raid(result, ship, vikings):
    record_tested_stats(result, "might", "skill", "courage", "agility")
    roll = average_top_crew_stat(vikings, "raiding_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Raiding Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:

        silver = random.randint(10, 25)
        result.silver_gained += silver
        result.log.append(f"A successful raid yields {silver} silver.")
        return True

    result.log.append("The raid meets resistance and yields little.")

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Minor Raid Resistance",
        injury_danger=4,
        injury_types=[InjuryType.COMBAT, InjuryType.ARROW, InjuryType.GENERIC],
        chance=35,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_burning_hall(result, ship, vikings):
    record_tested_stats(result, "might", "skill", "courage", "agility")
    roll = average_top_crew_stat(vikings, "raiding_score")
    target, target_mod = fuzzy_target(65)

    result.log.append(
        f"[Roll] Average Raiding Score {roll} vs Target {target} "
        f"(Base 65, Mod {target_mod:+})."
    )

    if roll >= target:

        silver = random.randint(12, 28)
        result.silver_gained += silver
        result.log.append(f"The crew storms a burning hall (+{silver} silver).")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Burning Hall",
        injury_danger=7,
        injury_types=[InjuryType.FIRE, InjuryType.COMBAT, InjuryType.CRUSHING, InjuryType.ARROW],
        chance=75,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False


def event_archer_volley(result, ship, vikings): # Start here dummy
    record_tested_stats(result, "agility", "vitality")
    roll = average_crew_stat(vikings, "evasion_score")
    target, target_mod = fuzzy_target(50)

    result.log.append(
        f"[Roll] Average Evasion Score {roll} vs Target {target} "
        f"(Base 50, Mod {target_mod:+})."
    )

    if roll >= target:

        result.log.append("The crew pushes through a volley of arrows.")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Archer Volley",
        injury_danger=5,
        injury_types=[InjuryType.ARROW],
        chance=55,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False


def event_chieftain_guard(result, ship, vikings):
    record_tested_stats(result, "might", "skill", "courage", "agility")
    roll = average_top_crew_stat(vikings, "raiding_score")
    target, target_mod = fuzzy_target(65)

    result.log.append(
        f"[Roll] Average Raiding {roll} vs Target {target} "
        f"(Base 70, Mod {target_mod:+})."
    )

    if roll >= target:

        hero = random.choice([v for v in vikings if v.is_available()])
        hero.renown += 2
        result.log.append(
            f"The crew defeats a chieftain's guard. "
            f"{hero.name}'s deeds stand out (+2 personal renown)."
        )
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Chieftain's Guard",
        injury_danger=7,
        injury_types=[InjuryType.COMBAT, InjuryType.ARROW],
        chance=75,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False


def event_weapons_cache(result, ship, vikings):
    record_tested_stats(result, "cunning", "skill")

    roll = average_top_crew_stat(vikings, "scouting_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Scouting {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        metal = random.randint(1, 2)

        result.fine_metal_gained += metal

        result.log.append(
            f"The crew uncovers a hidden weapons cache "
            f"(+{metal} fine metal)."
        )

        return True

    result.log.append("The supposed cache turns out empty.")
    return False 

# ====================================================
# DANGER EVENTS
# ====================================================

def event_serious_casualty(result, ship, vikings):
    viking = pick_random_viking(vikings)
    if not viking:
        return False

    record_individual_tested_stats(result, viking, "vitality", "courage")
    roll = ((viking.vitality + viking.courage) // 2) + random.randint(-20, 20)
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] {viking.name} Survival {roll} vs Target {target}. "
        f"(Base 55, Mod {target_mod:+})"
        )

    if roll >= target:
        apply_event_injury_risk(
            result=result,
            vikings=[viking],
            event_name="Serious Casualty",
            injury_danger=8,
            injury_types=[InjuryType.COMBAT, InjuryType.CRUSHING, InjuryType.GENERIC],
            chance=100,
            max_injuries=1,
            fatal_allowed=False,
        )
    else:
        apply_event_injury_risk(
            result=result,
            vikings=[viking],
            event_name="Deadly Casualty",
            injury_danger=9,
            injury_types=[InjuryType.COMBAT, InjuryType.CRUSHING],
            chance=100,
            max_injuries=1,
            fatal_allowed=True,
        )

    return False


def event_deadly_trap(result, ship, vikings):
    record_tested_stats(result, "agility", "skill", "cunning")
    roll = average_top_crew_stat(vikings, "skirmish_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Skirmish Score {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:

        result.log.append("The crew spots a deadly trap before it is sprung.")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Deadly Trap",
        injury_danger=8,
        injury_types=[InjuryType.COMBAT, InjuryType.CRUSHING],
        chance=90,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False
    
def event_falling_masonry(result, ship, vikings):
    record_tested_stats(result, "agility", "vitality")
    roll = average_top_crew_stat(vikings, "evasion_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Evasion {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew avoids falling masonry during the raid.")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Falling Masonry",
        injury_danger=7,
        injury_types=[InjuryType.CRUSHING, InjuryType.FALLING],
        chance=80,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False  

def event_spear_trap(result, ship, vikings):
    record_tested_stats(result, "agility", "vitality")
    roll = average_top_crew_stat(vikings, "evasion_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Evasion {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew narrowly avoids a hidden spear trap.")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Spear Trap",
        injury_danger=8,
        injury_types=[InjuryType.COMBAT],
        chance=85,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False  

def event_arrow_storm(result, ship, vikings):
    record_tested_stats(result, "agility", "vitality")
    roll = average_crew_stat(vikings, "evasion_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Evasion {roll} vs Target {target} "
        f"(Base 65, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew weaves through a deadly storm of arrows.")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Arrow Storm",
        injury_danger=7,
        injury_types=[InjuryType.ARROW],
        chance=75,
        max_injuries=2,
        fatal_allowed=True,
    )

    return False  

def event_leap_between_rooftops(result, ship, vikings):
    viking = pick_random_viking(vikings)

    if not viking:
        return True

    record_individual_tested_stats(result, viking, "agility")

    roll = viking.agility + random.randint(-20, 20)
    target, target_mod = fuzzy_target(65)

    result.log.append(
        f"[Roll] {viking.name} Rooftop Leap {roll} vs Target {target}. "
        f"(Base 65, Mod {target_mod:+})."
    )

    if roll >= target:
        silver = random.randint(8, 18)
        result.silver_gained += silver

        result.log.append(
            f"{viking.name} leaps between rooftops and secures valuable loot "
            f"(+{silver} silver)."
        )

        return True

    apply_event_injury_risk(
        result=result,
        vikings=[viking],
        event_name="Rooftop Leap",
        injury_danger=7,
        injury_types=[InjuryType.FALLING, InjuryType.GENERIC],
        chance=100,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False    

# ====================================================
# FIRE EVENTS
# ====================================================

def event_pitch_fire_attack(result, ship, vikings):
    record_tested_stats(result, "agility", "seamanship", "courage")

    roll = average_top_crew_stat(vikings, "evasion_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Evasion Score {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append(
            "The crew avoids flaming pitch and pushes through the attack."
        )
        return True

    dmg = random.randint(6, 14)
    ship.damage(dmg)
    result.ship_damage += dmg

    result.log.append(
        f"Flaming pitch splashes across the ship (-{dmg} hull)."
    )

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Pitch Fire Attack",
        injury_danger=6,
        injury_types=[
            InjuryType.FIRE,
            InjuryType.SAILING,
            InjuryType.COMBAT,
        ],
        chance=65,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False
    
def event_smoke_choked_raid(result, ship, vikings):
    record_tested_stats(result, "vitality", "courage", "agility")

    roll = average_crew_stat(vikings, "survival_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Survival Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        silver = random.randint(6, 14)

        result.silver_gained += silver

        result.log.append(
            f"The crew fights through smoke and confusion "
            f"(+{silver} silver)."
        )

        return True

    result.log.append(
        "Smoke and collapsing beams scatter the raiders."
    )

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Smoke-Choked Raid",
        injury_danger=5,
        injury_types=[
            InjuryType.FIRE,
            InjuryType.CRUSHING,
            InjuryType.GENERIC,
        ],
        chance=55,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False