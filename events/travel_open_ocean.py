from __future__ import annotations

import random

from injury import apply_event_injury_risk, InjuryType
from .helpers import *

# =================================
# Travel - Open Ocean
# =================================

def event_open_ocean_storm(result, ship, vikings):
    record_tested_stats(result, "seamanship", "courage")

    roll = average_top_crew_stat(vikings, "navigation_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Navigation {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew rides out a hard ocean storm.")
        return True

    dmg = random.randint(8, 18)

    ship.damage(dmg)
    result.ship_damage += dmg

    result.log.append(
        f"Waves crash across the longship in the open sea (-{dmg} hull)."
    )

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Open Ocean Storm",
        injury_danger=5,
        injury_types=[InjuryType.SAILING, InjuryType.COLD],
        chance=40,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_seabirds_seen(result, ship, vikings):
    record_tested_stats(result, "cunning", "skill")

    roll = average_top_crew_stat(vikings, "scouting_score")
    target, target_mod = fuzzy_target(45)

    result.log.append(
        f"[Roll] Average Scouting {roll} vs Target {target} "
        f"(Base 45, Mod {target_mod:+})."
    )

    if roll >= target:
        result.final_duration_weeks = max(1, result.final_duration_weeks - 1)

        result.log.append(
            "Seabirds reveal nearby land and shorten the voyage (-1 week)."
        )

        return True

    result.log.append("The birds vanish again into empty sky.")
    return False


def event_ocean_calm(result, ship, vikings):
    result.crew_strength_modifier += 5
    result.log.append(
        "A rare calm settles over the open ocean. The crew recovers its strength (+5 final crew strength)."
    )

    for viking in vikings:
        if viking.is_available() and not viking.is_player:
            viking.loyalty = min(100, viking.loyalty + 1)

    return True


def event_oarsmen_collapse(result, ship, vikings):
    record_tested_stats(result, "vitality", "might", "courage")

    roll = average_crew_stat(vikings, "endurance_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Endurance {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The oarsmen endure brutal rowing shifts.")
        return True

    result.final_duration_weeks += 1

    result.log.append(
        "Several exhausted oarsmen collapse at their benches (+1 week)."
    )

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Collapsed Oarsmen",
        injury_danger=4,
        injury_types=[InjuryType.SAILING, InjuryType.GENERIC],
        chance=35,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_distant_whale_song(result, ship, vikings):
    result.log.append(
        "Strange whale-song echoes across the sea through the night."
    )

    if random.randint(1, 100) <= 50:
        result.crew_strength_modifier += 5
        result.log.append("The crew takes it as a favorable omen (+5 final crew strength).")
        return True

    result.difficulty_modifier += 1
    result.log.append("The sound unsettles the crew (-1 morale, difficulty +1).")
    return False
    
def event_storm_front(result, ship, vikings):
    record_tested_stats(result, "seamanship", "cunning", "skill")
    roll = average_top_crew_stat(vikings, "navigation_score")
    target, target_mod = fuzzy_target(65)

    result.log.append(
        f"[Roll] Average Navigation Score {roll} vs Target {target} "
        f"(Base 65, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew outruns a dangerous storm front.")
        return True

    dmg = random.randint(10, 22)
    ship.damage(dmg)
    result.ship_damage += dmg
    result.log.append(f"A storm batters the ship (-{dmg} hull).")
    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Storm Front",
        injury_danger=6,
        injury_types=[InjuryType.SAILING, InjuryType.COLD],
        chance=45,
        max_injuries=1,
        fatal_allowed=True,
    )    
    return False    