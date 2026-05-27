from __future__ import annotations

import random

from injury import apply_event_injury_risk, InjuryType
from models import VikingClass, FavoredGod

from .helpers import *

# ===================================
# Class Events
# ===================================

def event_archer_clear_shot(result, ship, vikings):
    viking = pick_viking_by_class(vikings, VikingClass.ARCHER)
    if not viking:
        return True
        
    record_individual_tested_stats(result, viking, "skill")
    roll = viking.skill + random.randint(-20, 20)
    target, target_mod = fuzzy_target(60)
    
    result.log.append(
        f"[Roll] {viking.name} Archery Shot {roll} vs Target {target}. "
        f"(Base 60, Mod {target_mod:+})."
    )
    
    if roll >= target:
        silver = random.randint(6, 14)
        viking.renown += 1
        result.silver_gained += silver
        result.log.append(
            f"{viking.name} lands a perfect shot and earns renown (+1 personal renown)."
        )
        return True

    apply_event_injury_risk(
        result=result,
        vikings=[viking],
        event_name="Archer's Clear Shot",
        injury_danger=3,
        injury_types=[InjuryType.ARROW, InjuryType.GENERIC],
        chance=30,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_shieldmaiden_rally(result, ship, vikings):
    viking = pick_viking_by_class(vikings, VikingClass.SHIELDMAIDEN)
    if not viking:
        return True

    result.crew_strength_modifier += 5
    viking.renown += 1
    result.log.append(f"{viking.name} rallies the crew with fearless resolve (+1 perosnal renown, 5 final crew strength).")
    return True
    
def event_herbalist_mends_wounds(result, ship, vikings):
    viking = pick_viking_by_class(vikings, VikingClass.HERBALIST)
    if not viking:
        return True

    wounded = [
        crewman for crewman in vikings
        if crewman.injury_weeks_remaining > 0
        and crewman.status.value != "Dead"
    ]

    if not wounded:
        result.log.append(f"{viking.name} gathers herbs and prevents sickness from spreading.")
        return True

    patient = random.choice(wounded)
    patient.injury_weeks_remaining = max(0, patient.injury_weeks_remaining - 1)
    result.log.append(f"{viking.name} treats {patient.name}'s wounds (-1 recovery week).")
    return True

def event_raider_breach(result, ship, vikings):
    viking = pick_viking_by_class(vikings, VikingClass.RAIDER)
    if not viking:
        return True

    record_individual_tested_stats(result, viking, "might")

    roll = viking.might + random.randint(-20, 20)
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] {viking.name} Raider Breach {roll} vs Target {target}. "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        silver = random.randint(6, 14)
        viking.renown += 1
        result.silver_gained += silver
        result.log.append(
            f"{viking.name} smashes through the enemy line and earns renown (+1 personal renown)."
        )
        return True

    apply_event_injury_risk(
        result=result,
        vikings=[viking],
        event_name="Raider Breach",
        injury_danger=5,
        injury_types=[InjuryType.COMBAT],
        chance=60,
        max_injuries=1,
        fatal_allowed=True,
    )

    return False


def event_sailor_reads_water(result, ship, vikings):
    viking = pick_viking_by_class(vikings, VikingClass.SAILOR)
    if not viking:
        return True

    record_individual_tested_stats(result, viking, "seamanship")

    roll = viking.seamanship + random.randint(-20, 20)
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] {viking.name} Reads Water {roll} vs Target {target}. "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.final_duration_weeks = max(1, result.final_duration_weeks - 1)
        result.log.append(f"{viking.name} finds cleaner water and saves time (-1 week).")
        return True

    dmg = random.randint(3, 8)
    ship.damage(dmg)
    result.ship_damage += dmg
    result.log.append(f"{viking.name} misreads the water and the ship takes damage (-{dmg} hull).")
    apply_event_injury_risk(
        result=result,
        vikings=[viking],
        event_name="Misread Water",
        injury_danger=3,
        injury_types=[InjuryType.SAILING, InjuryType.FALLING],
        chance=25,
        max_injuries=1,
        fatal_allowed=False,
    )
    return False


def event_trickster_false_tracks(result, ship, vikings):
    viking = pick_viking_by_class(vikings, VikingClass.TRICKSTER)
    if not viking:
        return True

    record_individual_tested_stats(result, viking, "cunning")

    roll = viking.cunning + random.randint(-20, 20)
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] {viking.name} False Tracks {roll} vs Target {target}. "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.difficulty_modifier -= 1
        result.log.append(f"{viking.name} lays false tracks and confuses pursuers (-1 difficulty).")
        return True

    result.log.append(f"{viking.name}'s trick fools no one.")
    return False


def event_hersir_gives_orders(result, ship, vikings):
    viking = pick_viking_by_class(vikings, VikingClass.HERSIR)
    if not viking:
        return True

    record_individual_tested_stats(result, viking, "leadership", "courage")

    roll = ((viking.leadership + viking.courage) // 2) + random.randint(-20, 20)
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] {viking.name} Gives Orders {roll} vs Target {target}. "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        viking.renown += 1
        result.difficulty_modifier -= 1
        result.log.append(
            f"{viking.name}'s command steadies the crew (+1 personal renown, difficulty -1)."
        )
        return True

    result.log.append(f"{viking.name}'s orders are lost in the chaos.")
    return False


def event_scout_finds_path(result, ship, vikings):
    viking = pick_viking_by_class(vikings, VikingClass.SCOUT)
    if not viking:
        return True

    record_individual_tested_stats(result, viking, "agility", "cunning")

    roll = ((viking.agility + viking.cunning) // 2) + random.randint(-20, 20)
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] {viking.name} Finds Path {roll} vs Target {target}. "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.difficulty_modifier -= 1
        result.log.append(
            f"{viking.name} discovers a safer route. The expedition's burden eases."
        )
        return True

    result.final_duration_weeks += 1
    result.log.append(f"{viking.name} loses the trail (+1 week).")
    return False

# ====================================================
# VIKING RENOWN EVENTS
# ====================================================


def event_single_viking_boast(result, ship, vikings):
    viking = pick_random_viking(vikings)
    if not viking:
        return True
    
    record_individual_tested_stats(result, viking, "leadership", "courage")
    roll = ((viking.leadership + viking.courage) // 2) + random.randint(-20, 20)
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] {viking.name} Boast {roll} vs Target {target}. "
        f"(Base 60, Mod {target_mod:+})."
        )

    if roll >= target:
        viking.renown += 1
        result.log.append(f"{viking.name}'s boast spreads through the crew (+1 personal renown).")
        return True

    result.log.append(f"{viking.name}'s boast is met with laughter.")
    return False


def event_single_viking_clever_solution(result, ship, vikings):
    viking = pick_random_viking(vikings)
    if not viking:
        return True

    record_individual_tested_stats(result, viking, "cunning", "skill")
    roll = ((viking.cunning + viking.skill) // 2) + random.randint(-20, 20)
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] {viking.name} Clever Solution {roll} vs Target {target}. "
        f"(Base 60, Mod {target_mod:+})."
        )

    if roll >= target:
        viking.renown += 1
        result.log.append(f"{viking.name} solves a problem with quick wit (+1 personal renown).")
        return True

    result.log.append(f"{viking.name}'s plan fails to impress anyone.")
    return False


def event_single_viking_brave_deed(result, ship, vikings):
    viking = pick_random_viking(vikings)
    if not viking:
        return True

    record_individual_tested_stats(result, viking, "might", "courage")
    roll = ((viking.might + viking.courage) // 2) + random.randint(-20, 20)
    target, target_mod = fuzzy_target(65)

    result.log.append(
        f"[Roll] {viking.name} Brave Deed {roll} vs Target {target}. "
        f"(Base 65, Mod {target_mod:+})."
        )

    if roll >= target:
        viking.renown += 2
        result.log.append(f"{viking.name} performs a deed worth singing about (+2 personal renown).")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=[viking],
        event_name="Reckless Brave Deed",
        injury_danger=5,
        injury_types=[InjuryType.COMBAT, InjuryType.FALLING, InjuryType.GENERIC],
        chance=65,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False

# ====================================================
# FAVORED GOD EVENTS
# ====================================================

def event_loki_trick(result, ship, vikings):
    viking = pick_viking_by_god(vikings, FavoredGod.LOKI)
    if not viking:
        return True

    if random.random() < 0.60:
        silver = random.randint(8, 20)
        result.silver_gained += silver
        result.log.append(f"{viking.name}, favored by Loki, turns deceit into profit (+{silver} silver).")
        return True

    result.difficulty_modifier += 1
    result.log.append(f"{viking.name}'s trickery backfires. Difficulty increases by 1.")
    return False


def event_thor_strength(result, ship, vikings):
    viking = pick_viking_by_god(vikings, FavoredGod.THOR)
    if not viking:
        return True

    result.log.append(f"{viking.name} invokes Thor and leads the crew through brutal labor.")
    result.difficulty_modifier -= 1
    return True


def event_odin_omen(result, ship, vikings):
    viking = pick_viking_by_god(vikings, FavoredGod.ODIN)
    if not viking:
        return True

    viking.renown += 1
    result.log.append(f"{viking.name} reads a grim omen of Odin and earns notice (+1 personal renown).")
    return True


def event_freyja_mercy(result, ship, vikings):
    viking = pick_viking_by_god(vikings, FavoredGod.FREYJA)
    if not viking:
        return True

    result.crew_strength_modifier += 5
    result.log.append(f"{viking.name} offers thanks to Freyja, calming fear and grief among the crew (+5 final crew strength).")
    return True
    
def event_njord_favorable_seas(result, ship, vikings):
    viking = pick_viking_by_god(vikings, FavoredGod.NJORD)

    if not viking:
        return True

    result.final_duration_weeks = max(1, result.final_duration_weeks - 1)

    result.log.append(
        f"{viking.name} offers prayer to Njord. Favorable seas shorten the voyage by 1 week."
    )

    return True    
    
def event_tyr_oath(result, ship, vikings):
    viking = pick_viking_by_god(vikings, FavoredGod.TYR)

    if not viking:
        return True

    viking.renown += 1

    for crewman in vikings:
        if crewman.is_available() and not crewman.is_player:
            crewman.loyalty = min(100, crewman.loyalty + 1)

    result.log.append(
        f"{viking.name} swears an oath in Tyr's name. "
        f"The crew's loyalty strengthens, and {viking.name} earns renown."
    )

    return True

def event_heimdall_watchfulness(result, ship, vikings):
    viking = pick_viking_by_god(vikings, FavoredGod.HEIMDALL)

    if not viking:
        return True

    result.difficulty_modifier -= 1

    result.log.append(
        f"{viking.name}'s sharp senses reveal danger before it strikes "
        f"(-1 expedition difficulty)."
    )

    return True 

def event_frigg_protection(result, ship, vikings):
    viking = pick_viking_by_god(vikings, FavoredGod.FRIGG)

    if not viking:
        return True

    wounded = [
        crewman for crewman in vikings
        if crewman.injury_weeks_remaining > 0
    ]

    if wounded:
        patient = random.choice(wounded)

        patient.injury_weeks_remaining = max(
            0,
            patient.injury_weeks_remaining - 2
        )

        result.log.append(
            f"{viking.name} invokes Frigg's protection over the wounded."
        )

    else:
        result.log.append(
            f"{viking.name} offers blessings to Frigg for the crew's safety."
        )

    return True    
    
def event_baldr_blessing(result, ship, vikings):
    viking = pick_viking_by_god(vikings, FavoredGod.BALDR)

    if not viking:
        return True

    gain = random.randint(1, 2)

    viking.renown += gain
    

    result.log.append(
        f"{viking.name}'s grace and charisma inspire the crew "
        f"(+{gain} renown)."
    )

    return True

def event_skadi_huntsman(result, ship, vikings):
    viking = pick_viking_by_god(vikings, FavoredGod.SKADI)

    if not viking:
        return True

    record_individual_tested_stats(result, viking, "agility", "skill")

    roll = ((viking.agility + viking.skill) // 2) + random.randint(-20, 20)
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] {viking.name} Hunt {roll} vs Target {target}. "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        food = random.randint(8, 18)
        result.food_gained += food

        result.log.append(
            f"{viking.name} hunts successfully under Skadi's guidance "
            f"(+{food} food)."
        )

        return True

    result.log.append(
        f"{viking.name}'s hunt fails in the cold wilderness."
    )

    apply_event_injury_risk(
        result=result,
        vikings=[viking],
        event_name="Skadi's Hunt",
        injury_danger=5,
        injury_types=[InjuryType.HUNTING, InjuryType.COLD],
        chance=45,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False      