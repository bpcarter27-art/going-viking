from __future__ import annotations

import random

from injury import apply_event_injury_risk, InjuryType
from .helpers import *


# ====================================================
# RESOURCE EVENTS
# ====================================================

def event_drive_livestock_home(result, ship, vikings):
    record_tested_stats(result, "leadership", "courage")
    roll = average_top_crew_stat(vikings, "command_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Command Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        food = random.randint(10, 24)
        result.food_gained += food
        result.log.append(f"The crew drives captured livestock home (+{food} food).")
        return True

    result.log.append("Panicked livestock scatter before they can be driven home.")
    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Scattered Livestock",
        injury_danger=3,
        injury_types=[InjuryType.CRUSHING, InjuryType.GENERIC],
        chance=25,
        max_injuries=1,
        fatal_allowed=False,
    )
    return False


def event_capture_thralls(result, ship, vikings):
    record_tested_stats(result, "might", "skill", "courage", "agility")
    roll = average_top_crew_stat(vikings, "raiding_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Raiding Score {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        thralls = random.randint(1, 3)
        result.thralls_gained += thralls
        result.log.append(f"The crew captures laborers (+{thralls} thralls).")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Capture Raid",
        injury_danger=5,
        injury_types=[InjuryType.COMBAT, InjuryType.ARROW],
        chance=55,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False


def event_haul_ship_timber(result, ship, vikings):
    record_tested_stats(result, "vitality", "courage", "might")
    roll = average_top_crew_stat(vikings, "endurance_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Endurance Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        timber = random.randint(4, 10)
        result.ship_timber_gained += timber
        result.log.append(f"The crew hauls quality ship timber home (+{timber} ship timber).")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Hauling Ship Timber",
        injury_danger=4,
        injury_types=[InjuryType.CRUSHING, InjuryType.GENERIC],
        chance=45,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_salvage_wreckage(result, ship, vikings):
    record_tested_stats(result, "cunning", "skill")
    roll = average_top_crew_stat(vikings, "scouting_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Scouting Score {roll} vs Target {target} "
        f"(Base 50, Mod {target_mod:+})."
    )

    if roll >= target:
        branch_roll = random.randint(1, 100)

        if branch_roll <= 20:
            result.log.append("The wreck still holds iron fittings worth prying loose.")
            return event_salvage_iron_fittings(result, ship, vikings)

        if branch_roll <= 40:
            food = random.randint(4, 10)
            silver = random.randint(4, 12)
            result.food_gained += food
            result.silver_gained += silver
            result.log.append(
                f"The crew finds sealed cargo among the wreckage "
                f"(+{food} food, +{silver} silver)."
            )
            return True

        timber = random.randint(3, 8)
        silver = random.randint(4, 12)
        result.ship_timber_gained += timber
        result.silver_gained += silver
        result.log.append(
            f"The crew salvages wreckage (+{timber} ship timber, +{silver} silver)."
        )
        return True

    result.log.append("The wreckage is picked clean or too rotten to use.")

    if random.randint(1, 100) <= 30:
        result.log.append("While searching deeper, the crew slips among broken beams.")
        apply_event_injury_risk(
            result=result,
            vikings=vikings,
            event_name="Bad Salvage",
            injury_danger=3,
            injury_types=[InjuryType.SAILING, InjuryType.CRUSHING, InjuryType.GENERIC],
            chance=35,
            max_injuries=1,
            fatal_allowed=False,
        )

    return False
    
def event_salvage_iron_fittings(result, ship, vikings):
    record_tested_stats(result, "skill", "cunning")

    roll = average_top_crew_stat(vikings, "scouting_score")
    target, target_mod = fuzzy_target(50)

    result.log.append(
        f"[Roll] Average Scouting {roll} vs Target {target} "
        f"(Base 50, Mod {target_mod:+})."
    )

    if roll >= target:
        metal = random.randint(1, 3)
        timber = random.randint(2, 6)

        result.fine_metal_gained += metal
        result.ship_timber_gained += timber

        result.log.append(
            f"The crew strips usable iron and timber from wreckage "
            f"(+{metal} fine metal, +{timber} ship timber)."
        )

        return True

    result.log.append("The wreck is too rotten to salvage.")
    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Rotten Wreck Salvage",
        injury_danger=3,
        injury_types=[InjuryType.CRUSHING, InjuryType.SAILING],
        chance=25,
        max_injuries=1,
        fatal_allowed=False,
    )
    return False    
    


def event_good_fishing_waters(result, ship, vikings):
    record_tested_stats(result, "seamanship")
    roll = average_top_crew_stat(vikings, "seamanship")
    target, target_mod = fuzzy_target(45)

    result.log.append(
        f"[Roll] Average Seamanship {roll} vs Target {target} "
        f"(Base 45, Mod {target_mod:+})."
    )

    if roll >= target:
        food = random.randint(12, 26)
        result.food_gained += food
        result.log.append(f"The crew finds good fishing waters (+{food} food).")
        return True

    result.log.append("The nets come up thin.")
    return False
    
def event_find_bog_iron(result, ship, vikings):
    record_tested_stats(result, "cunning", "vitality")

    roll = average_top_crew_stat(vikings, "survival_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Survival Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        metal = random.randint(1, 3)
        result.fine_metal_gained += metal
        result.log.append(f"The crew finds workable bog iron (+{metal} fine metal).")
        return True

    result.log.append("The bog gives up mud, leeches, and little else.")

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Bog Iron Search",
        injury_danger=3,
        injury_types=[InjuryType.SICKNESS, InjuryType.GENERIC],
        chance=25,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_strip_broken_weapons(result, ship, vikings):
    record_tested_stats(result, "skill", "cunning")

    roll = average_top_crew_stat(vikings, "scouting_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Scouting Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        metal = random.randint(1, 2)
        result.fine_metal_gained += metal
        result.log.append(f"The crew strips useful iron from broken weapons (+{metal} fine metal).")
        return True

    result.log.append("The broken weapons are too rusted to be worth hauling.")
    return False


def event_smiths_abandoned_cache(result, ship, vikings):
    record_tested_stats(result, "cunning", "skill")

    roll = average_top_crew_stat(vikings, "scouting_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Scouting Score {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        metal = random.randint(2, 4)
        silver = random.randint(4, 10)
        result.fine_metal_gained += metal
        result.silver_gained += silver
        result.log.append(
            f"The crew uncovers an abandoned smith's cache "
            f"(+{metal} fine metal, +{silver} silver)."
        )
        return True

    result.log.append("The supposed smith's cache has already been emptied.")
    return False


def event_pry_loose_iron_bands(result, ship, vikings):
    record_tested_stats(result, "might", "skill")

    roll = average_top_crew_stat(vikings, "endurance_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Endurance Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        metal = random.randint(1, 3)
        result.fine_metal_gained += metal
        result.log.append(f"The crew pries loose valuable iron bands (+{metal} fine metal).")
        return True

    result.log.append("The iron bands will not come free cleanly.")

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Prying Iron Bands",
        injury_danger=4,
        injury_types=[InjuryType.CRUSHING, InjuryType.GENERIC],
        chance=35,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False