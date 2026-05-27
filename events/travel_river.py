from __future__ import annotations

import random

from injury import apply_event_injury_risk, InjuryType
from .helpers import *
from .travel_frozen import event_timber_accident

# =====================================
# Travel - River
# ====================================

def event_shallow_river_drag(result, ship, vikings):
    record_tested_stats(result, "might", "vitality", "seamanship")

    roll = average_top_crew_stat(vikings, "endurance_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Endurance Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew drags the ship through shallow water without losing much time.")
        return True

    result.final_duration_weeks += 1
    dmg = random.randint(2, 6)
    ship.damage(dmg)
    result.ship_damage += dmg
    result.log.append(f"The ship scrapes through shallows (+1 week, -{dmg} hull).")
    return False


def event_riverbank_archers(result, ship, vikings):
    record_tested_stats(result, "agility", "courage", "seamanship")

    roll = average_top_crew_stat(vikings, "evasion_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Evasion Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew rows hard past hidden riverbank archers.")
        return True

    result.log.append("Arrows hiss from the riverbank.")

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Riverbank Archers",
        injury_danger=5,
        injury_types=[InjuryType.ARROW, InjuryType.SAILING],
        chance=55,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_muddy_portage(result, ship, vikings):
    record_tested_stats(result, "might", "vitality", "leadership")

    roll = average_top_crew_stat(vikings, "endurance_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Endurance Score {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew hauls the ship across a muddy portage.")
        return True

    result.final_duration_weeks += 1
    result.log.append("Mud, sweat, and snapped ropes slow the portage (+1 week).")

    if random.randint(1, 100) <= 35:
        return event_timber_accident(result, ship, vikings)

    return False

def event_river_current(result, ship, vikings):
    record_tested_stats(result, "seamanship")
    roll = average_top_crew_stat(vikings, "seamanship")
    target, target_mod = fuzzy_target(50)

    result.log.append(
        f"[Roll] Average Seamanship {roll} vs Target {target} "
        f"(Base 50, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew uses the river current to make swift progress.")
        return True

    dmg = random.randint(4, 10)
    ship.damage(dmg)
    result.ship_damage += dmg
    result.log.append(f"Treacherous river currents damage the ship (-{dmg} hull).")
    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="River Current",
        injury_danger=3,
        injury_types=[InjuryType.SAILING, InjuryType.FALLING],
        chance=25,
        max_injuries=1,
        fatal_allowed=False,
    )
    return False
    
def event_river_prince_toll(result, ship, vikings):
    record_tested_stats(result, "leadership", "courage")

    roll = average_top_crew_stat(vikings, "command_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Command {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew talks its way past a river prince's tollmen.")
        return True

    toll = random.randint(8, 18)
    result.silver_gained -= toll
    result.log.append(f"A river prince's tollmen force payment (-{toll} silver).")
    return False    