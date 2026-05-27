from __future__ import annotations

import random

from injury import apply_event_injury_risk, InjuryType
from .helpers import *
from .generic import event_social_tension

# ===================================
# Events - Scandinavia
# ===================================


def event_rival_jarl_scouts(result, ship, vikings):
    record_tested_stats(result, "cunning", "skill")

    roll = average_top_crew_stat(vikings, "scouting_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Scouting {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("Scouts spot rival jarl-men before they can spring an ambush.")
        return True

    result.difficulty_modifier += 1
    result.log.append("Rival jarl-men shadow the crew. Expedition difficulty increases by 1.")
    return False


def event_seal_rock_harvest(result, ship, vikings):
    record_tested_stats(result, "seamanship", "agility")

    roll = average_top_crew_stat(vikings, "seamanship")
    target, target_mod = fuzzy_target(50)

    result.log.append(
        f"[Roll] Average Seamanship {roll} vs Target {target} "
        f"(Base 50, Mod {target_mod:+})."
    )

    if roll >= target:
        food = random.randint(8, 18)
        result.food_gained += food
        result.log.append(f"The crew harvests seal meat from slick coastal rocks (+{food} food).")
        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Seal Rock Harvest",
        injury_danger=4,
        injury_types=[InjuryType.FALLING, InjuryType.SAILING],
        chance=45,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False

def event_feud_challenge_at_dawn(result, ship, vikings):
    challenger = pick_random_viking(vikings)

    if not challenger:
        return True

    record_individual_tested_stats(result, challenger, "might", "courage")

    roll = ((challenger.might + challenger.courage) // 2) + random.randint(-20, 20)
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] {challenger.name} Dawn Challenge {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        challenger.renown += 1
        result.renown_gained += 1
        result.log.append(
            f"{challenger.name} answers a feud challenge at dawn and wins honor "
            f"(+1 personal renown, +1 renown)."
        )
        return True

    apply_event_injury_risk(
        result=result,
        vikings=[challenger],
        event_name="Feud Challenge at Dawn",
        injury_danger=5,
        injury_types=[InjuryType.COMBAT, InjuryType.GENERIC],
        chance=70,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_old_grudge_resurfaces(result, ship, vikings):
    record_tested_stats(result, "leadership", "courage")

    roll = average_top_crew_stat(vikings, "command_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Command Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("An old grudge is cooled before blades come out.")

        if random.randint(1, 100) <= 20:
            result.renown_gained += 1
            result.log.append("The restraint is admired by nearby households (+1 renown).")

        return True

    result.difficulty_modifier += 1
    result.log.append("An old grudge resurfaces. Expedition difficulty increases by 1.")

    branch_roll = random.randint(1, 100)

    if branch_roll <= 35:
        return resolve_dispute_duel(
            result=result,
            vikings=vikings,
            reason="an old family grudge",
        )

    if branch_roll <= 60:
        result.log.append("The quarrel spreads through the crew.")
        return event_social_tension(result, ship, vikings)

    result.log.append("The offended kinfolk shadow the crew from a distance.")
    return event_rival_jarl_scouts(result, ship, vikings)


def event_law_speaker_warning(result, ship, vikings):
    record_tested_stats(result, "leadership", "cunning")

    roll = average_top_crew_stat(vikings, "social_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Social Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        silver = random.randint(6, 14)
        result.silver_gained += silver
        result.log.append(
            f"A law-speaker's warning helps the crew avoid trouble and earn favor "
            f"(+{silver} silver)."
        )
        return True

    result.log.append("The law-speaker's warning is ignored, and local tempers worsen.")
    result.difficulty_modifier += 1
    return False


def event_oath_ring_dispute(result, ship, vikings):
    record_tested_stats(result, "leadership", "courage")

    roll = average_top_crew_stat(vikings, "command_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Roll] Average Command Score {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        for viking in vikings:
            if viking.is_available() and not viking.is_player:
                viking.loyalty = min(100, viking.loyalty + 2)

        result.log.append(
            "A disputed oath is settled before the oath ring. "
            "The crew gains renown and loyalty improves."
        )
        return True

    result.log.append("The oath dispute turns bitter. Loyalty wavers.")

    viking = pick_random_viking(vikings)
    if viking and not viking.is_player:
        viking.loyalty = max(1, viking.loyalty - 2)
        result.log.append(f"{viking.name} loses faith in the judgment (-2 loyalty).")

    return False


def event_hidden_fjord_path(result, ship, vikings):
    record_tested_stats(result, "seamanship", "cunning", "skill")

    roll = average_top_crew_stat(vikings, "navigation_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Navigation Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.final_duration_weeks = max(1, result.final_duration_weeks - 1)
        result.log.append("The crew finds a hidden fjord path and saves time (-1 week).")
        return True

    result.log.append("The fjord path twists into dead water and wastes time.")
    result.final_duration_weeks += 1
    return False

def event_outlaw_hidden_camp(result, ship, vikings):
    record_tested_stats(result, "cunning", "skill", "agility")

    roll = average_top_crew_stat(vikings, "scouting_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Scouting Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        silver = random.randint(8, 18)
        result.silver_gained += silver
        result.log.append(f"The crew finds an outlaw camp before dusk (+{silver} silver).")
        return True

    result.log.append("The outlaw camp is found too late, and the quarry is ready.")

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Outlaw Ambush",
        injury_danger=5,
        injury_types=[InjuryType.COMBAT, InjuryType.ARROW],
        chance=55,
        max_injuries=1,
        fatal_allowed=False,
    )

    return False


def event_funeral_omens(result, ship, vikings):
    record_tested_stats(result, "courage", "leadership")

    roll = average_crew_stat(vikings, "morale_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Morale Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.crew_strength_modifier += 5
        result.log.append("The funeral omens are accepted with courage (+5 final crew strength).")
        return True

    result.log.append("Dark funeral omens unsettle the crew.")
    result.difficulty_modifier += 1
    return False


def event_grave_goods_temptation(result, ship, vikings):
    record_tested_stats(result, "courage", "loyalty")

    roll = average_crew_stat(vikings, "loyalty")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Loyalty {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.log.append("The crew leaves the grave goods untouched and keeps its honor.")
        result.loyalty_gained += 1
        return True

    silver = random.randint(8, 18)
    result.silver_gained += silver
    result.log.append(
        f"Someone takes grave goods despite the taboo (+{silver} silver, but bad omens follow)."
    )
    result.difficulty_modifier += 1
    return False


def event_rus_market_bargain(result, ship, vikings):
    record_tested_stats(result, "leadership", "cunning")

    roll = average_top_crew_stat(vikings, "social_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Social {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        silver = random.randint(8, 18)
        metal = random.randint(1, 2)
        result.silver_gained += silver
        result.fine_metal_gained += metal
        result.log.append(f"The crew bargains well in a Rus' market (+{silver} silver, +{metal} fine metal).")
        return True

    result.log.append("The market traders cheat the crew with bad weights and false promises.")
    return False
    
# ===================================
# Norway-only Events
# ===================================

def event_norway_fjord_echoes(result, ship, vikings):
    record_tested_stats(result, "seamanship", "cunning")

    roll = average_top_crew_stat(vikings, "navigation_score")
    target, target_mod = fuzzy_target(52)

    result.log.append(
        f"[Roll] Average Navigation Score {roll} vs Target {target} "
        f"(Base 52, Mod {target_mod:+})."
    )

    if roll >= target:
        result.final_duration_weeks = max(1, result.final_duration_weeks - 1)
        result.log.append("The crew reads the fjord winds well and saves time (-1 week).")
        return True

    result.log.append("The fjord walls twist sound and weather alike. The crew loses time.")
    result.final_duration_weeks += 1
    return False


def event_norway_hard_farmstead(result, ship, vikings):
    record_tested_stats(result, "leadership", "courage")

    roll = average_top_crew_stat(vikings, "command_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Roll] Average Command Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        food = random.randint(6, 14)
        result.food_gained += food
        result.log.append(f"A stubborn farmstead bargains instead of fighting (+{food} food).")
        return True

    result.log.append("The farmstead refuses terms, and word spreads ahead of the crew.")
    result.difficulty_modifier += 1
    return False    
    
# ===================================
# Denmark-only Events
# ===================================

def event_denmark_mead_hall_boast(result, ship, vikings):
    record_tested_stats(result, "leadership", "courage")

    roll = average_top_crew_stat(vikings, "social_score")
    target, target_mod = fuzzy_target(54)

    result.log.append(
        f"[Roll] Average Social Score {roll} vs Target {target} "
        f"(Base 54, Mod {target_mod:+})."
    )

    if roll >= target:
        result.crew_strength_modifier += 10
        result.log.append("The crew wins the hall with boasts and laughter (+10 final crew strength).")
        return True

    result.log.append("The hall laughs at the wrong boast. Pride curdles into tension.")
    return event_social_tension(result, ship, vikings)


def event_denmark_cattle_drift(result, ship, vikings):
    record_tested_stats(result, "skill", "agility")

    roll = average_top_crew_stat(vikings, "survival_score")
    target, target_mod = fuzzy_target(53)

    result.log.append(
        f"[Roll] Average Survival Score {roll} vs Target {target} "
        f"(Base 53, Mod {target_mod:+})."
    )

    if roll >= target:
        food = random.randint(10, 20)
        result.food_gained += food
        result.log.append(f"The crew drives loose cattle from the marshland (+{food} food).")
        return True

    result.log.append("The cattle scatter through wet ground, wasting precious time.")
    result.final_duration_weeks += 1
    return False    

# ===================================
# Swedish Coast-only Events
# ===================================

def event_swedish_burial_runes(result, ship, vikings):
    record_tested_stats(result, "cunning", "courage")

    roll = average_top_crew_stat(vikings, "wisdom_score")
    target, target_mod = fuzzy_target(56)

    result.log.append(
        f"[Roll] Average Wisdom Score {roll} vs Target {target} "
        f"(Base 56, Mod {target_mod:+})."
    )

    if roll >= target:
        result.renown_gained += 1
        result.log.append("The crew interprets old burial runes and earns fearful respect (+1 renown).")
        return True

    result.log.append("The runes are misread, and the dead seem less quiet afterward.")
    result.difficulty_modifier += 1
    return False


def event_swedish_amber_merchant(result, ship, vikings):
    record_tested_stats(result, "leadership", "cunning")

    roll = average_top_crew_stat(vikings, "social_score")
    target, target_mod = fuzzy_target(53)

    result.log.append(
        f"[Roll] Average Social Score {roll} vs Target {target} "
        f"(Base 53, Mod {target_mod:+})."
    )

    if roll >= target:
        silver = random.randint(10, 22)
        result.silver_gained += silver
        result.log.append(f"An amber merchant pays well for safe passage (+{silver} silver).")
        return True

    result.log.append("The merchant vanishes before dawn, taking promised payment with him.")
    return False    