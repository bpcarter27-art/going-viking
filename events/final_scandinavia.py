from __future__ import annotations

import random

from injury import apply_event_injury_risk, InjuryType
from .helpers import *
from .combat import event_minor_raid

# =====================================
# Final Events - Scandinavia
# =====================================

def event_final_feud_champion(result, ship, vikings):
    result.log.append("The feud reaches its bloody answer: one champion must break the other side's will.")

    if random.randint(1, 100) <= 25:
        silver = random.randint(10, 25)
        result.log.append(f"The rival clan offers {silver} silver in blood payment instead of battle.")

        if random.randint(1, 100) <= 50:
            result.silver_gained += silver
            result.renown_gained += 1
            result.log.append("The blood price is accepted. The feud ends without further killing.")
            return True

        result.log.append("The blood price is rejected. Steel decides the matter.")

    champion = pick_random_viking(vikings)
    if not champion:
        return False

    record_individual_tested_stats(result, champion, "might", "courage")

    roll = champion.combat_score() + random.randint(-20, 20)
    target, target_mod = fuzzy_target(65)

    result.log.append(
        f"[Final Roll] {champion.name} Feud Champion {roll} vs Target {target} "
        f"(Base 65, Mod {target_mod:+})."
    )

    if roll >= target:
        champion.renown += 2
        result.crew_strength_modifier += 5
        result.log.append(f"{champion.name} wins the feud's final challenge (+2 personal renown, +5 final crew strength).")

        if random.randint(1, 100) <= 35:
            result.log.append("The defeated clan refuses the judgment and attacks in desperation.")
            return event_minor_raid(result, ship, vikings)

        return True

    apply_event_injury_risk(
        result=result,
        vikings=[champion],
        event_name="Feud Champion Defeated",
        injury_danger=7,
        injury_types=[InjuryType.COMBAT],
        chance=90,
        max_injuries=1,
        fatal_allowed=True,
    )
    return False


def event_final_thing_judgment(result, ship, vikings):
    result.log.append("The Thing falls silent. A judgment must be accepted, or blood will answer law.")

    if random.randint(1, 100) <= 35:
        result.log.append("Two witnesses accuse each other of false oath before the assembly.")
        return resolve_dispute_duel(
            result,
            vikings,
            reason="disputed testimony before the Thing",
        )

    record_tested_stats(result, "leadership", "courage")

    roll = average_top_crew_stat(vikings, "command_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Final Roll] Average Command Score {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        result.renown_gained += 2
        result.log.append("The judgment holds. The crew earns lasting respect (+2 renown).")

        if random.randint(1, 100) <= 20:
            silver = random.randint(5, 15)
            result.silver_gained += silver
            result.renown_gained += 1
            result.log.append(
                f"A nearby jarl is impressed by the crew's conduct "
                f"(+{silver} silver, +1 renown)."
            )

        return True

    result.difficulty_modifier += 1
    result.log.append("The assembly fractures into threats and sworn grudges. Difficulty increases by 1.")

    if random.randint(1, 100) <= 40:
        result.log.append("The failed judgment sparks an immediate challenge.")
        return resolve_dispute_duel(
            result,
            vikings,
            reason="a failed judgment before the Thing",
        )

    return False


def event_final_white_elk(result, ship, vikings):
    result.log.append("At last, the white elk appears between black pines and falling snow.")

    hunter = pick_random_viking(vikings)
    if not hunter:
        return False

    record_individual_tested_stats(result, hunter, "skill", "cunning")

    roll = ((hunter.skill + hunter.cunning) // 2) + random.randint(-20, 20)
    target, target_mod = fuzzy_target(65)

    result.log.append(
        f"[Final Roll] {hunter.name} Sacred Hunt {roll} vs Target {target} "
        f"(Base 65, Mod {target_mod:+})."
    )

    if roll >= target:
        food = random.randint(18, 32)
        result.food_gained += food
        result.renown_gained += 1
        hunter.renown += 1
        result.log.append(f"The omen beast falls cleanly (+{food} food, +1 renown, +1 personal renown).")

        if random.randint(1, 100) <= 20:
            result.crew_strength_modifier += 8
            result.log.append("The beast bears strange markings sacred to the gods (+8 final crew strength).")

        return True

    result.log.append("The omen beast vanishes deeper into the forest. Some insist it should be followed.")

    if random.randint(1, 100) <= 40:
        result.final_duration_weeks += 1

        if random.randint(1, 100) <= 50:
            food = random.randint(8, 18)
            result.food_gained += food
            result.log.append(f"The hunters discover hidden game trails and return with food (+{food} food).")
            return True

        result.log.append("The crew becomes lost among frozen woods.")

        apply_event_injury_risk(
            result=result,
            vikings=vikings,
            event_name="Lost In Sacred Woods",
            injury_danger=5,
            injury_types=[InjuryType.COLD, InjuryType.HUNTING],
            chance=40,
            max_injuries=1,
            fatal_allowed=False,
        )

    return False


def event_final_outlaw_standoff(result, ship, vikings):
    result.log.append("The outlaw is cornered at last, with steel in hand and nowhere left to run.")

    if random.randint(1, 100) <= 25:
        silver = random.randint(10, 30)
        result.log.append(f"The outlaw offers hidden silver in exchange for safe passage ({silver} silver).")

        if random.randint(1, 100) <= 50:
            result.silver_gained += silver
            result.log.append(f"The bargain is accepted (+{silver} silver).")
            return True

        result.log.append("The crew rejects the offer and closes in.")

    record_tested_stats(result, "might", "skill", "courage", "agility")

    roll = average_top_crew_stat(vikings, "skirmish_score")
    target, target_mod = fuzzy_target(60)

    result.log.append(
        f"[Final Roll] Average Skirmish Score {roll} vs Target {target} "
        f"(Base 60, Mod {target_mod:+})."
    )

    if roll >= target:
        silver = random.randint(10, 22)
        result.silver_gained += silver
        result.renown_gained += 2
        result.log.append(f"The outlaw is taken and justice is done (+{silver} silver, +2 renown).")

        if random.randint(1, 100) <= 15:
            result.renown_gained += 1
            result.log.append(
                "The outlaw yields secret names of other criminals before judgment "
                "(+1 renown)."
            )

        return True

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Outlaw's Last Stand",
        injury_danger=6,
        injury_types=[InjuryType.COMBAT, InjuryType.ARROW],
        chance=70,
        max_injuries=1,
        fatal_allowed=True,
    )
    return False
    return False


def event_final_funeral_pyre_omen(result, ship, vikings):
    result.log.append("The funeral pyre is lit. The smoke bends strangely, and every warrior watches the sky.")

    if random.randint(1, 100) <= 30:
        result.crew_strength_modifier += 5
        result.log.append("The dead warrior's kin swear friendship with the crew (+5 final crew strength).")

    record_tested_stats(result, "courage", "leadership")

    roll = average_crew_stat(vikings, "morale_score")
    target, target_mod = fuzzy_target(55)

    result.log.append(
        f"[Final Roll] Average Morale Score {roll} vs Target {target} "
        f"(Base 55, Mod {target_mod:+})."
    )

    if roll >= target:
        result.renown_gained += 2
        for viking in vikings:
            if viking.is_available() and not viking.is_player:
                viking.loyalty = min(100, viking.loyalty + 1)
        result.log.append("The dead are honored well. The crew returns steadier than before (+1 renown, +1 loyalty).")
        return True

    result.log.append("The pyre gutters in bad wind. The crew returns uneasy.")
    result.difficulty_modifier += 1

    if random.randint(1, 100) <= 25:
        result.log.append("The pyre collapses strangely, and whispers spread among the crew.")
        result.difficulty_modifier += 1

    return False