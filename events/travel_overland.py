from __future__ import annotations

import random

from injury import apply_event_injury_risk, InjuryType
from .helpers import *
from .scandinavia import event_rival_jarl_scouts

# ====================================
# Travel - Overland
# ===================================

def event_bad_mountain_pass(result, ship, vikings):
    record_tested_stats(result, "vitality", "cunning", "agility")

    roll = average_top_crew_stat(vikings, "survival_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Survival Score {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew finds a safe way through a rough mountain pass.")
        return True

    result.final_duration_weeks += 1
    result.log.append("The pass turns cruel and slow (+1 week).")

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Bad Mountain Pass",
        injury_danger=4,
        injury_types=[InjuryType.FALLING, InjuryType.COLD, InjuryType.GENERIC],
        chance=35,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_forest_path_vanishes(result, ship, vikings):
    record_tested_stats(result, "cunning", "skill")

    roll = average_top_crew_stat(vikings, "scouting_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Scouting Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew finds the old forest path again before dusk.")
        return True

    result.final_duration_weeks += 1
    result.log.append("The forest path vanishes under moss and deadfall (+1 week).")

    if random.randint(1, 100) <= 30:
        result.log.append("Strange tracks lead away from the lost path.")
        return event_omen_beast_tracks(result, ship, vikings)

    return False


def event_wary_farmstead_dogs(result, ship, vikings):
    record_tested_stats(result, "leadership", "cunning")

    roll = average_top_crew_stat(vikings, "social_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Social Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        food = random.randint(5, 12)
        result.food_gained += food
        result.log.append(f"A wary farmstead is calmed and offers food (+{food} food).")
        return True

    result.log.append("Dogs bark, doors bar shut, and the farmstead raises alarm.")

    if random.randint(1, 100) <= 35:
        return event_rival_jarl_scouts(result, ship, vikings)

    result.difficulty_modifier += 1
    return False

def event_farmstead_shelter(result, ship, vikings):
    record_tested_stats(result, "leadership", "cunning")

    roll = average_top_crew_stat(vikings, "social_score")
    target, target_mod = fuzzy_target(50)

    result.log.append(
        f"[Roll] Average Social Score {roll} vs Target {target} "
        f"(Base 50, Mod {target_mod:+})."
    )

    if roll >= target:
        food = random.randint(6, 14)
        result.food_gained += food
        result.log.append(f"A farmstead offers shelter and provisions (+{food} food).")
        return True

    result.log.append("A wary farmstead bars its doors. The crew presses on hungry.")
    result.food_gained -= random.randint(2, 5)
    return False


def event_omen_beast_tracks(result, ship, vikings):
    record_tested_stats(result, "cunning", "skill")

    roll = average_top_crew_stat(vikings, "scouting_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Scouting Score {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        food = random.randint(10, 22)
        result.food_gained += food
        result.crew_strength_modifier += 3
        result.log.append(
            f"The crew follows strange tracks to worthy game "
            f"(+{food} food, +3 final crew strength)."
        )
        return True

    result.log.append("The omen tracks lead the crew into cold, empty country.")
    result.final_duration_weeks += 1

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Lost Following Omen Tracks",
        injury_danger=3,
        injury_types=[InjuryType.HUNTING, InjuryType.COLD, InjuryType.GENERIC],
        chance=30,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False