from __future__ import annotations

import random

from injury import apply_event_injury_risk, InjuryType
from models import CrewRole
from .helpers import *
from .combat import event_ambush


# ====================================================
# GENERIC EVENTS
# ====================================================

def event_favorable_winds(result, ship, vikings):
    result.log.append("Favorable winds speed your journey.")
    return True


def event_food_spoilage(result, ship, vikings):
    loss = random.randint(3, 8)
    result.food_gained -= loss
    result.log.append(f"Food spoils during the journey (-{loss} food).")
    return False


def event_find_supplies(result, ship, vikings):
    food = random.randint(5, 12)
    record_tested_stats(result, "cunning")
    roll = average_crew_stat(vikings, "cunning")
    target, target_mod = fuzzy_target(50)

    result.log.append(
        f"[Roll] Average Cunning {roll} vs Target {target} "
        f"(Base 50, Mod {target_mod:+})."
)
    if roll >= target:
        food += random.randint(3, 8)
        result.food_gained += food
        result.log.append(f"You acquire supplies (+{food} food).")
        return True

    result.food_gained += food
    result.log.append(f"You find meager supplies (+{food} food).")
    return False


def event_easy_loot(result, ship, vikings):
    silver = random.randint(5, 15)
    result.silver_gained += silver
    result.log.append(f"You find easy loot (+{silver} silver).")
    return True


def event_social_tension(result, ship, vikings):
    record_tested_stats(result, "courage", "leadership")
    roll = average_crew_stat(vikings, "morale_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Morale Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew holds together despite rising tension.")
        return True

    viking = pick_random_viking(vikings)
    if viking and not viking.is_player:
        viking.loyalty = max(1, viking.loyalty - 1)
        result.log.append(
            f"{viking.name} grumbles about shares, glory, and bad omens (-1 loyalty)."
        )
    elif viking:
        result.log.append(f"{viking.name} grumbles about shares, glory, and bad omens.")

    return False


def event_lucky_omen(result, ship, vikings):
    result.crew_strength_modifier += 5
    result.log.append("A lucky omen lifts the crew's spirits (+5 final crew strength).")
    return True


def event_bad_omens(result, ship, vikings):
    result.difficulty_modifier += 1
    result.log.append("Bad omens unsettle the crew. Expedition difficulty increases by 1.")
    return False


def event_hidden_cache(result, ship, vikings):
    silver = random.randint(8, 18)
    food = random.randint(2, 6)
    result.silver_gained += silver
    result.food_gained += food
    result.log.append(f"The crew finds a hidden cache (+{silver} silver, +{food} food).")
    return True


def event_local_guide(result, ship, vikings):
    record_tested_stats(result, "leadership", "cunning")
    roll = average_top_crew_stat(vikings, "social_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Social Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("A local guide reveals a safer path.")

        if random.randint(1, 100) <= 25:
            food = random.randint(4, 10)
            result.food_gained += food
            result.log.append(f"The guide also points out hidden stores nearby (+{food} food).")

        return True

    result.log.append("A supposed guide leads the crew astray.")

    if random.randint(1, 100) <= 35:
        result.log.append("The false guide vanishes before dawn, leaving the crew exposed.")
        return event_ambush(result, ship, vikings)

    result.final_duration_weeks += 1
    result.log.append("The crew loses time finding the right road again (+1 week).")
    return False


def event_sickness(result, ship, vikings):
    result.log.append("Sickness spreads through camp.")

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Camp Sickness",
        injury_danger=3,
        injury_types=[InjuryType.SICKNESS],
        chance=45,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False
    
def event_exhausted_oarsmen(result, ship, vikings):
    record_tested_stats(result, "vitality", "courage", "might")
    roll = average_top_crew_stat(vikings, "endurance_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Endurance Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew rows through exhaustion without losing pace.")
        return True

    result.final_duration_weeks += 1
    result.log.append("Exhausted oarsmen slow the expedition (+1 week).")

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Exhausted Oarsmen",
        injury_danger=3,
        injury_types=[InjuryType.SAILING, InjuryType.GENERIC],
        chance=25,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_cold_camp_resolve(result, ship, vikings):
    record_tested_stats(result, "vitality", "cunning", "seamanship")
    roll = average_top_crew_stat(vikings, "survival_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Survival Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew makes a safe cold-weather camp.")
        return True

    result.log.append("The crew makes a poor cold-weather camp.")

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Cold Camp",
        injury_danger=4,
        injury_types=[InjuryType.COLD, InjuryType.SICKNESS, InjuryType.GENERIC],
        chance=40,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_crew_fear_spreads(result, ship, vikings):
    record_tested_stats(result, "courage", "leadership")
    roll = average_crew_stat(vikings, "morale_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Morale Score {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew masters its fear before panic spreads.")
        return True

    result.difficulty_modifier += 1

    viking = pick_random_viking(vikings)
    if viking and not viking.is_player:
        viking.loyalty = max(1, viking.loyalty - 1)
        result.log.append(
            f"Fear spreads through the crew. Expedition difficulty increases by 1. "
            f"{viking.name}'s loyalty wavers (-1 loyalty)."
        )
    else:
        result.log.append("Fear spreads through the crew. Expedition difficulty increases by 1.")

    return False


def event_captain_sets_pace(result, ship, vikings):
    captain = next(
        (
            viking for viking in vikings
            if viking.is_available()
            and viking.role == CrewRole.CAPTAIN
        ),
        None,
    )

    if not captain:
        result.log.append("No captain sets the pace for the expedition.")
        return False

    record_individual_tested_stats(result, captain, "leadership", "courage")

    roll = ((captain.leadership + captain.courage) // 2) + random.randint(-20, 20)
    target, target_mod = fuzzy_target(70)

    result.log.append(
        f"[Roll] {captain.name} Captain's Pace {roll} vs Target {target}. "
        f"(Base 70, Mod {target_mod:+})."
    )

    if roll >= target:
        result.final_duration_weeks = max(1, result.final_duration_weeks - 1)
        result.log.append(f"{captain.name} drives the crew onward with steady command (-1 week).")
        return True

    result.log.append(f"{captain.name} cannot keep the crew moving efficiently.")
    return False    
    
# ====================================================
# LEADERSHIP EVENTS
# ====================================================    

def event_rally_the_crew(result, ship, vikings):
    record_tested_stats(result, "leadership", "courage")

    roll = average_top_crew_stat(vikings, "command_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Command Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.crew_strength_modifier += 5
        result.difficulty_modifier -= 1
        result.log.append("Strong voices rally the crew. Expedition difficulty decreases by 1, +5 final crew strength.")
        return True

    result.log.append("No one takes command when the crew needs direction.")
    return False


def event_settle_shares_dispute(result, ship, vikings):
    record_tested_stats(result, "leadership", "courage")

    roll = average_top_crew_stat(vikings, "command_score")
    target, target_mod = fuzzy_target(50)

    result.log.append(
        f"[Roll] Average Command Score {roll} vs Target {target} "
        f"(Base 50, Mod {target_mod:+})."
    )

    if roll >= target:
        for viking in vikings:
            if viking.is_available():
                viking.loyalty = min(100, viking.loyalty + 1)

        result.log.append("A dispute over shares is settled fairly. Crew loyalty improves.")
        return True

    angry = pick_random_viking(vikings)
    if angry and not angry.is_player:
        angry.loyalty = max(1, angry.loyalty - 2)
        result.log.append(f"{angry.name} feels cheated over the division of shares (-2 loyalty).")
    elif angry:
        result.log.append(f"{angry.name} feels cheated over the division of shares.")

    if random.randint(1, 100) <= 20:
        resolve_dispute_duel(
            result=result,
            vikings=vikings,
            reason="the division of shares",
        )

    return False


def event_negotiate_safe_passage(result, ship, vikings):
    record_tested_stats(result, "leadership", "cunning")

    roll = average_top_crew_stat(vikings, "social_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Social {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        silver = random.randint(6, 16)
        result.silver_gained += silver
        result.log.append(f"The crew negotiates safe passage and gains favor (+{silver} silver).")
        return True

    result.difficulty_modifier += 1
    result.log.append("Negotiations sour. Expedition difficulty increases by 1.")
    return False


def event_orderly_retreat(result, ship, vikings):
    record_tested_stats(result, "leadership", "courage")

    roll = average_top_crew_stat(vikings, "command_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Command {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew withdraws in good order before losses mount.")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Disordered Retreat",
        injury_danger=5,
        injury_types=[InjuryType.COMBAT, InjuryType.GENERIC],
        chance=45,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False
    
# ====================================================
# LOYALTY EVENTS
# ====================================================    
    
def event_loyalty_under_strain(result, ship, vikings):
    roll = average_crew_stat(vikings, "loyalty")
    target, target_mod = fuzzy_target(50)

    result.log.append(
        f"[Roll] Average Loyalty {roll} vs Target {target} "
        f"(Base 50, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew remains loyal despite hardship.")
        return True

    viking = pick_random_viking(vikings)
    if viking:
        if not viking.is_player:
            loss = random.randint(2, 3)
            viking.loyalty = max(1, viking.loyalty - loss)
            result.log.append(f"{viking.name}'s loyalty wavers after hardship (-{loss} loyalty).")

    return False


def event_refuse_to_abandon_wounded(result, ship, vikings):
    roll = average_crew_stat(vikings, "loyalty")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Loyalty {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    wounded = [
        viking for viking in vikings
        if viking.is_available()
        and viking.injury_weeks_remaining > 0
    ]

    if roll >= target:
        result.log.append("The crew refuses to abandon the wounded.")
        for viking in vikings:
            if viking.is_available():
                viking.loyalty = min(100, viking.loyalty + 1)
        return True

    if wounded:
        patient = random.choice(wounded)
        patient.injury_weeks_remaining += 1
        result.log.append(f"{patient.name} is carried poorly and needs another week to recover.")

    return False