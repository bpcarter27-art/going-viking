import random
from models import Viking, JobType, VikingClass, CrewRole, FavoredGod, TravelType
from injury import apply_event_injury_risk, InjuryType

CURRENT_EXPEDITION_RESULT = None


"""
# Crew-wide event checks
roll = average_crew_stat(vikings, "raiding_score")
target = 55

# Raw rating checks
roll = average_crew_stat(vikings, "cunning")
target = 50

# Individual checks
roll = ((viking.might + viking.skill) // 2) + random.randint(-20, 20)
target = 60
"""

def set_current_expedition_result(result) -> None:
    global CURRENT_EXPEDITION_RESULT
    CURRENT_EXPEDITION_RESULT = result


def clear_current_expedition_result() -> None:
    global CURRENT_EXPEDITION_RESULT
    CURRENT_EXPEDITION_RESULT = None


def current_derived_score_modifier() -> int:
    if CURRENT_EXPEDITION_RESULT is None:
        return 0

    return getattr(CURRENT_EXPEDITION_RESULT, "derived_score_modifier", 0)

def roll_crew_stat(vikings: list[Viking], attr: str) -> int:
    total = 0

    for viking in vikings:
        if not viking.is_available():
            continue

        value = getattr(viking, attr)

        if callable(value):
            value = value()

        total += value

    return total
    
def average_crew_stat(vikings: list[Viking], attr: str) -> int:
    values = []

    for viking in vikings:
        if not viking.is_available():
            continue

        value = getattr(viking, attr)

        if callable(value):
            value = value()

        values.append(value)

    if not values:
        return 0

    return (sum(values) // len(values)) + current_derived_score_modifier()

def average_top_crew_stat(vikings: list[Viking], attr: str, top_fraction: float = 0.5) -> int:
    values = []

    for viking in vikings:
        if not viking.is_available():
            continue

        value = getattr(viking, attr)

        if callable(value):
            value = value()

        values.append(value)

    if not values:
        return 0

    values.sort(reverse=True)

    count = max(1, round(len(values) * top_fraction))
    top_values = values[:count]

    return (sum(top_values) // len(top_values)) + current_derived_score_modifier()   
    
def fuzzy_target(base_target: int) -> tuple[int, int]:
    modifier = random.randint(-15, 15)
    return base_target + modifier, modifier    

def record_tested_stats(result, *stats: str) -> None:
    for stat in stats:
        if stat not in result.tested_stats:
            result.tested_stats.append(stat)
                      
def record_individual_tested_stats(result, viking: Viking, *stats: str) -> None:
    if not viking:
        return

    current = result.individual_tested_stats.setdefault(viking.viking_id, [])

    for stat in stats:
        if stat not in current:
            current.append(stat)

def pick_random_viking(vikings: list[Viking]) -> Viking | None:
    available = [v for v in vikings if v.is_available()]
    if not available:
        return None
    return random.choice(available)
    
def pick_viking_by_class(vikings: list[Viking], viking_class: VikingClass) -> Viking | None:
    candidates = [
        viking for viking in vikings
        if viking.is_available()
        and viking.viking_class == viking_class
    ]
    return random.choice(candidates) if candidates else None


def pick_viking_by_role(vikings: list[Viking], role: CrewRole) -> Viking | None:
    candidates = [
        viking for viking in vikings
        if viking.is_available()
        and viking.role == role
    ]
    return random.choice(candidates) if candidates else None


def pick_viking_by_god(vikings: list[Viking], favored_god: FavoredGod) -> Viking | None:
    candidates = [
        viking for viking in vikings
        if viking.is_available()
        and viking.favored_god == favored_god
    ]
    return random.choice(candidates) if candidates else None
    



def injure_viking(result, viking: Viking, wound_name: str, severity: str = "minor") -> None:
    viking.add_injury(wound_name)

    if severity == "major":
        viking.injury_weeks_remaining = random.randint(4, 12)
        viking.status = type(viking.status).WOUNDED
        result.log.append(
            f"{viking.name} suffers a major injury "
            f"({viking.injury_weeks_remaining} weeks recovery)."
        )

    elif severity == "minor":
        viking.injury_weeks_remaining = random.randint(1, 3)
        result.log.append(
            f"{viking.name} suffers a minor injury "
            f"({viking.injury_weeks_remaining} weeks recovery)."
        )

    else:
        result.log.append(f"{viking.name} is wounded: {wound_name}.")

    result.injuries.append(viking.name)


def kill_or_permanently_injure_viking(result, viking: Viking, cause: str) -> None:
    if viking.is_player:
        injury = random.choice(PERMANENT_INJURIES)
        viking.suffer_permanent_injury(injury)
        result.permanent_injuries.append(viking.name)
        result.log.append(
            f"{viking.name} survives {cause}, but suffers a permanent injury: {injury}."
        )
    else:
        viking.status = type(viking.status).DEAD
        result.deaths.append(viking.name)
        result.log.append(f"{viking.name} is killed during {cause}.")

# ====================================================
# RARE EVENT BRANCHES
# ====================================================

def resolve_dispute_duel(result, vikings, reason: str = "a bitter dispute") -> bool:
    candidates = [
        viking for viking in vikings
        if viking.is_available()
        and not viking.is_player
    ]

    if len(candidates) < 2:
        return False

    challenger, defender = random.sample(candidates, 2)

    challenger_roll = challenger.combat_score() + random.randint(-20, 20)
    defender_roll = defender.combat_score() + random.randint(-20, 20)

    result.log.append(
        f"{challenger.name} challenges {defender.name} to a duel over {reason}."
    )
    result.log.append(
        f"[Duel Roll] {challenger.name} {challenger_roll} vs "
        f"{defender.name} {defender_roll}."
    )

    if challenger_roll >= defender_roll:
        winner = challenger
        loser = defender
    else:
        winner = defender
        loser = challenger

    winner.renown += 1

    result.log.append(
        f"{winner.name} wins the duel and gains renown "
        f"(+1 personal renown)."
    )

    apply_event_injury_risk(
        result=result,
        vikings=[loser],
        event_name="Dispute Duel Loser",
        injury_danger=5,
        injury_types=[InjuryType.COMBAT, InjuryType.GENERIC],
        chance=75,
        max_injuries=1,
        fatal_allowed=False,
    )

    apply_event_injury_risk(
        result=result,
        vikings=[winner],
        event_name="Dispute Duel Winner",
        injury_danger=3,
        injury_types=[InjuryType.COMBAT, InjuryType.GENERIC],
        chance=20,
        max_injuries=1,
        fatal_allowed=False,
    )

    return True    