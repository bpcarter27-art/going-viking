from __future__ import annotations

import random

from injury import apply_event_injury_risk, InjuryType
from .helpers import *

# ===============================
# Travel - Frozen
# ===============================

def event_winter_hunt(result, ship, vikings):
    record_tested_stats(result, "cunning", "skill")
    roll = average_top_crew_stat(vikings, "scouting_score")
    target, target_mod = fuzzy_target(50)

    result.log.append(
        f"[Roll] Average Scouting Score {roll} vs Target {target} "
        f"(Base 50, Mod {target_mod:+})."
    )

    if roll >= target:

        food = random.randint(8, 18)
        result.food_gained += food
        result.log.append(f"The hunters bring down good game (+{food} food).")
        return True

    result.log.append("The hunt fails. The woods are empty and cold.")

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Winter Hunt",
        injury_danger=4,
        injury_types=[InjuryType.HUNTING, InjuryType.COLD],
        chance=35,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_frozen_trail(result, ship, vikings):
    record_tested_stats(result, "vitality", "courage", "might")
    roll = average_crew_stat(vikings, "endurance_score")
    target, target_mod = fuzzy_target(50)

    result.log.append(
        f"[Roll] Average Endurance Score {roll} vs Target {target} "
        f"(Base 50, Mod {target_mod:+})."
    )

    if roll >= target:

        result.log.append("The crew endures the frozen trail.")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Frozen Trail",
        injury_danger=4,
        injury_types=[InjuryType.COLD, InjuryType.GENERIC],
        chance=45,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_timber_accident(result, ship, vikings):
    record_tested_stats(result, "agility", "skill", "cunning")
    roll = average_top_crew_stat(vikings, "skirmish_score")
    target, target_mod = fuzzy_target(50)

    result.log.append(
        f"[Roll] Average Skirmish Score {roll} vs Target {target} "
        f"(Base 50, Mod {target_mod:+})."
    )

    if roll >= target:

        silver = random.randint(6, 14)
        result.silver_gained += silver
        result.log.append(f"The timber work is finished cleanly (+{silver} silver).")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Timber Accident",
        injury_danger=5,
        injury_types=[InjuryType.CRUSHING, InjuryType.FALLING],
        chance=60,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_winter_bandits(result, ship, vikings):
    record_tested_stats(result, "might", "skill", "courage", "agility")
    roll = average_top_crew_stat(vikings, "raiding_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Raiding {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:

        silver = random.randint(8, 18)
        result.silver_gained += silver
        result.log.append(f"The crew drives off desperate bandits and claims their goods (+{silver} silver).")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Winter Bandits",
        injury_danger=5,
        injury_types=[InjuryType.COMBAT, InjuryType.ARROW, InjuryType.COLD],
        chance=55,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False


def event_ice_breaks(result, ship, vikings):
    record_tested_stats(result, "vitality", "cunning", "seamanship")
    roll = average_crew_stat(vikings, "survival_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Survival Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:

        result.log.append("Cracking ice is spotted in time.")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Breaking Ice",
        injury_danger=7,
        injury_types=[InjuryType.COLD, InjuryType.SAILING],
        chance=75,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False