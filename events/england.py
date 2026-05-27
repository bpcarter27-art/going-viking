from __future__ import annotations

import random

from injury import apply_event_injury_risk, InjuryType
from .helpers import *

# ===================================
# Events - England
# ===================================

def event_saxon_fyrd_musters(result, ship, vikings):
    record_tested_stats(result, "might", "skill", "courage", "agility")

    roll = average_top_crew_stat(vikings, "raiding_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Raiding {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew strikes before the Saxon fyrd can fully muster.")
        return True

    result.difficulty_modifier += 1
    result.log.append("The Saxon fyrd gathers faster than expected. Expedition difficulty increases by 1.")
    return False


def event_church_silver_cache(result, ship, vikings):
    record_tested_stats(result, "cunning", "skill")

    roll = average_top_crew_stat(vikings, "scouting_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Scouting {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        silver = random.randint(12, 28)
        metal = random.randint(1, 2)
        result.silver_gained += silver
        result.fine_metal_gained += metal
        result.log.append(f"The crew finds hidden church silver (+{silver} silver, +{metal} fine metal).")
        return True

    result.log.append("The church silver has already been hidden or carried away.")
    return False


def event_northumbrian_warband(result, ship, vikings):
    record_tested_stats(result, "might", "skill", "courage", "agility")

    roll = average_top_crew_stat(vikings, "raiding_score")
    target, target_mod = fuzzy_target(65)

    result.log.append(
        f"[Roll] Average Raiding {roll} vs Target {target} "
        f"(Base 65, Mod {target_mod:+})."
    )

    if roll >= target:
        hero = random.choice([v for v in vikings if v.is_available()])
        hero.renown += 1
        result.log.append(
            f"The crew defeats a hard Northumbrian warband. "
            f"{hero.name}'s courage is remembered (+1 personal renown)."
        )
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Northumbrian Warband",
        injury_danger=8,
        injury_types=[InjuryType.COMBAT, InjuryType.ARROW],
        chance=85,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False


def event_lindisfarne_pilgrim_rumors(result, ship, vikings):
    record_tested_stats(result, "leadership", "cunning")

    roll = average_top_crew_stat(vikings, "social_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Social {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        silver = random.randint(8, 20)
        result.silver_gained += silver
        result.log.append(f"Pilgrim rumors lead the crew toward hidden valuables (+{silver} silver).")
        return True

    result.log.append("Pilgrim rumors lead only to empty roads and wasted time.")
    result.final_duration_weeks += 1
    return False   

def event_loot_church_bells(result, ship, vikings):
    record_tested_stats(result, "might", "skill", "courage")

    roll = average_top_crew_stat(vikings, "raiding_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Raiding {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        metal = random.randint(1, 3)
        silver = random.randint(8, 18)

        result.fine_metal_gained += metal
        result.silver_gained += silver

        result.log.append(
            f"The crew hacks down bronze church bells "
            f"(+{metal} fine metal, +{silver} silver)."
        )

        return True

    result.log.append("The bells are too heavy to haul away safely.")
    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Falling Church Bells",
        injury_danger=5,
        injury_types=[InjuryType.CRUSHING, InjuryType.FALLING, InjuryType.FIRE],
        chance=45,
        max_injuries=1,
        fatal_allowed=False,
    )    
    return False    