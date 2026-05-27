from __future__ import annotations

import random

from injury import apply_event_injury_risk, InjuryType
from .helpers import *

# ==========================================
# Travel - Coastal
# =========================================

def event_rough_seas(result, ship, vikings):
    record_tested_stats(result, "seamanship")
    roll = average_top_crew_stat(vikings, "seamanship")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Seamanship {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("Your crew handles rough seas well.")
        return True

    dmg = random.randint(5, 15)
    ship.damage(dmg)
    result.ship_damage += dmg
    result.log.append(f"Rough seas damage your ship (-{dmg} hull).")
    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Rough Seas",
        injury_danger=4,
        injury_types=[InjuryType.SAILING, InjuryType.GENERIC],
        chance=30,
        max_injuries=1,
        fatal_allowed=False,
    )
    return False


def event_hidden_reef(result, ship, vikings):
    record_tested_stats(result, "seamanship", "cunning", "skill")
    roll = average_top_crew_stat(vikings, "navigation_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Navigation Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("Sharp eyes and steady hands guide the ship past hidden reefs.")
        return True

    dmg = random.randint(8, 18)
    ship.damage(dmg)
    result.ship_damage += dmg
    result.log.append(f"The ship strikes hidden rocks (-{dmg} hull).")
    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Hidden Reef",
        injury_danger=5,
        injury_types=[InjuryType.SAILING, InjuryType.CRUSHING],
        chance=35,
        max_injuries=1,
        fatal_allowed=False,
    )    
    return False
    
def event_lost_in_fog(result, ship, vikings):
    record_tested_stats(result, "cunning", "skill")
    roll = average_top_crew_stat(vikings, "scouting_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Scouting Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew navigates through thick fog.")
        return True

    food_loss = random.randint(2, 5)

    result.final_duration_weeks += 1
    result.food_gained -= food_loss

    result.log.append(
        f"The ship loses time in heavy fog (+1 week, -{food_loss} food)."
    )

    return False

def event_ship_handling_drill(result, ship, vikings):
    record_tested_stats(result, "seamanship")
    roll = average_top_crew_stat(vikings, "seamanship")
    target, target_mod = fuzzy_target(50)

    result.log.append(
        f"[Roll] Average Seamanship {roll} vs Target {target} "
        f"(Base 50, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew handles the ship cleanly through difficult water.")
        return True

    dmg = random.randint(4, 10)
    ship.damage(dmg)
    result.ship_damage += dmg
    result.log.append(f"Poor ship handling causes damage (-{dmg} hull).")
    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Poor Ship Handling",
        injury_danger=3,
        injury_types=[InjuryType.SAILING, InjuryType.GENERIC],
        chance=25,
        max_injuries=1,
        fatal_allowed=False,
    )
    return False    


# ====================================================
# SEAMANSHIP EVENTS
# ====================================================

def event_hard_rowing(result, ship, vikings):
    record_tested_stats(result, "seamanship", "vitality")

    roll = average_top_crew_stat(vikings, "seamanship")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Seamanship {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.final_duration_weeks = max(1, result.final_duration_weeks - 1)
        result.log.append("Hard rowing cuts time from the journey (-1 week).")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Hard Rowing",
        injury_danger=3,
        injury_types=[InjuryType.SAILING, InjuryType.GENERIC],
        chance=35,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_beach_landing(result, ship, vikings):
    record_tested_stats(result, "seamanship", "agility")

    roll = average_top_crew_stat(vikings, "seamanship")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Seamanship {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew makes a clean beach landing before defenders can gather.")
        result.difficulty_modifier -= 1
        return True

    dmg = random.randint(5, 12)
    ship.damage(dmg)
    result.ship_damage += dmg
    result.log.append(f"A poor landing damages the ship (-{dmg} hull).")
    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Bad Beach Landing",
        injury_danger=4,
        injury_types=[InjuryType.SAILING, InjuryType.FALLING],
        chance=30,
        max_injuries=1,
        fatal_allowed=False,
    )
    return False


def event_thread_the_skerries(result, ship, vikings):
    record_tested_stats(result, "seamanship", "cunning", "skill")

    roll = average_top_crew_stat(vikings, "navigation_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Navigation {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        silver = random.randint(5, 12)
        result.silver_gained += silver
        result.log.append(f"The crew threads dangerous skerries and finds hidden cargo (+{silver} silver).")
        return True

    dmg = random.randint(8, 16)
    ship.damage(dmg)
    result.ship_damage += dmg
    result.log.append(f"The ship scrapes hidden stone in the skerries (-{dmg} hull).")
    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Skerries Collision",
        injury_danger=5,
        injury_types=[InjuryType.SAILING, InjuryType.CRUSHING],
        chance=35,
        max_injuries=1,
        fatal_allowed=False,
    )    
    return False


def event_reef_escape(result, ship, vikings):
    record_tested_stats(result, "seamanship", "cunning", "skill")

    roll = average_top_crew_stat(vikings, "navigation_score")
    target, target_mod = fuzzy_target(65)

    result.log.append(
        f"[Roll] Average Navigation {roll} vs Target {target} "
        f"(Base 65, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew escapes a reef line by oar and instinct.")
        return True

    dmg = random.randint(10, 20)
    ship.damage(dmg)
    result.ship_damage += dmg
    result.log.append(f"The ship tears along the reef (-{dmg} hull).")
    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Reef Escape",
        injury_danger=6,
        injury_types=[InjuryType.SAILING, InjuryType.CRUSHING],
        chance=40,
        max_injuries=1,
        fatal_allowed=True,
    )    
    return False    