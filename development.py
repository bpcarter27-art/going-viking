from __future__ import annotations

import random

from models import Viking, VikingClass
from roster import CORE_STATS, GOD_STAT_BONUSES


AGE_BIRTHDAY_POINTS = [
    (16, 18, 12, 24),
    (19, 22, 8, 18),
    (23, 25, 4, 10),
    (26, 27, 0, 8),
    (28, 30, -2, 4),
    (31, 32, -4, 3),
    (33, 34, -6, 0),
    (35, 36, -8, -3),
    (37, 39, -14, -8),
    (40, 44, -18, -12),
    (45, 200, -24, -12),
]

CLASS_GROWTH_STATS = {
    VikingClass.RAIDER: ["might"],
    VikingClass.ARCHER: ["skill"],
    VikingClass.TRICKSTER: ["cunning"],
    VikingClass.HERSIR: ["leadership"],
    VikingClass.SHIELDMAIDEN: ["courage"],
    VikingClass.HERBALIST: ["vitality"],
    VikingClass.SCOUT: ["agility"],
    VikingClass.SAILOR: ["seamanship"],
}

def favored_stat_for(viking: Viking) -> str | None:
    return GOD_STAT_BONUSES.get(viking.favored_god)


def weighted_growth_stats(viking: Viking, stats: list[str]) -> list[str]:
    weighted = list(stats)

    favored = favored_stat_for(viking)

    if favored in stats:
        weighted.append(favored)

    class_growth_stats = CLASS_GROWTH_STATS.get(viking.viking_class, [])

    for stat in class_growth_stats:
        if stat in stats:
            weighted.append(stat)

    return weighted


def ensure_stat_potential(viking: Viking) -> None:
    if not viking.stat_potential:
        viking.stat_potential = {
            stat: random.randint(getattr(viking, stat), 100)
            for stat in CORE_STATS
        }


def increase_stat_if_possible(viking: Viking, stat: str, amount: int = 1) -> bool:
    ensure_stat_potential(viking)

    current = getattr(viking, stat)
    cap = viking.stat_potential.get(stat, current)

    if current >= cap:
        return False

    setattr(viking, stat, min(cap, current + amount))
    return True


AGE_DECLINE_STAT_WEIGHTS = {
    "agility": 6,
    "might": 5,
    "skill": 4,
    "vitality": 4,
    "seamanship": 3,
    "cunning": 2,
    "loyalty": 2,
    "leadership": 1,
    "courage": 1,
}


def decrease_random_stat(viking: Viking) -> str | None:
    stats = list(AGE_DECLINE_STAT_WEIGHTS.keys())
    weights = list(AGE_DECLINE_STAT_WEIGHTS.values())

    stat = random.choices(stats, weights=weights, k=1)[0]
    current = getattr(viking, stat)

    if current <= 1:
        return None

    setattr(viking, stat, current - 1)
    return stat


def birthday_point_range(age: int) -> tuple[int, int]:
    for min_age, max_age, low, high in AGE_BIRTHDAY_POINTS:
        if min_age <= age <= max_age:
            return low, high

    return 0, 0


def apply_birthday_development(viking: Viking) -> list[str]:
    logs = []

    if viking.status.value in {"Dead", "Retired"}:
        return logs

    ensure_stat_potential(viking)

    low, high = birthday_point_range(viking.age)
    points = random.randint(low, high)

    if points > 0:
        stat_pool = weighted_growth_stats(viking, CORE_STATS)
        gained_stats = {}

        for _ in range(points):
            stat = random.choice(stat_pool)

            if increase_stat_if_possible(viking, stat):
                gained_stats[stat] = gained_stats.get(stat, 0) + 1

        if gained_stats:
            stat_text = ", ".join(
                f"+{amount} {stat}"
                for stat, amount in gained_stats.items()
            )

            logs.append(
                f"{viking.name} grows with age: {stat_text}."
            )

    elif points < 0:
        lost_stats = []

        for _ in range(abs(points)):
            stat = decrease_random_stat(viking)

            if stat:
                lost_stats.append(stat)

        if lost_stats:
            stat_counts = {}

            for stat in lost_stats:
                stat_counts[stat] = stat_counts.get(stat, 0) + 1

            stat_text = ", ".join(
                f"-{amount} {stat}"
                for stat, amount in stat_counts.items()
            )

            logs.append(
                f"{viking.name} declines with age: {stat_text}."
            )

    return logs

def post_job_growth_chance_for_age(age: int) -> float:
    if age <= 18:
        return 0.22

    if age <= 21:
        return 0.18

    if age <= 24:
        return 0.14

    if age <= 27:
        return 0.10

    # 28-31 plateau
    if age <= 31:
        return 0.05

    return 0.00
    
def expedition_length_growth_bonus(duration_weeks: int) -> float:
    if duration_weeks <= 1:
        return 0.0

    extra_weeks = duration_weeks - 1
    month_bonus = duration_weeks // 4

    return (extra_weeks + month_bonus) / 100    

def build_post_job_growth_weights(
    viking: Viking,
    crew_tested_stats: list[str],
    individual_tested_stats: dict[str, list[str]],
) -> dict[str, int]:
    ensure_stat_potential(viking)

    favored = favored_stat_for(viking)
    weights = {}

    for stat in CORE_STATS:
        current = getattr(viking, stat)
        cap = viking.stat_potential.get(stat, current)

        if current >= cap:
            weights[stat] = 0
        elif stat == favored:
            weights[stat] = 2
        else:
            weights[stat] = 1

    tested_stats = list(crew_tested_stats)
    tested_stats.extend(individual_tested_stats.get(viking.viking_id, []))

    for stat in tested_stats:
        if stat in weights and weights[stat] > 0:
            weights[stat] += 1

    return weights
    
def apply_post_job_growth(
    vikings: list[Viking],
    crew_tested_stats: list[str],
    individual_tested_stats: dict[str, list[str]],
    duration_weeks: int,
    chance_multiplier: float = 1.0,
) -> list[str]:

    logs = []

    for viking in vikings:
        if viking.status.value in {"Dead", "Retired"}:
            continue

        ensure_stat_potential(viking)

        base_growth = post_job_growth_chance_for_age(viking.age)
        length_bonus = expedition_length_growth_bonus(duration_weeks)

        growth_chance = (
            (base_growth + length_bonus)
            * chance_multiplier
        )

        if growth_chance <= 0:
            continue

        gained_stats = {}

        weights_by_stat = build_post_job_growth_weights(
            viking,
            crew_tested_stats,
            individual_tested_stats,
        )

        available_stats = [
            stat for stat, weight in weights_by_stat.items()
            if weight > 0
        ]

        if not available_stats:
            continue

        weights = [
            weights_by_stat[stat]
            for stat in available_stats
        ]

        for _ in CORE_STATS:
            if random.random() >= growth_chance:
                continue

            stat = random.choices(
                available_stats,
                weights=weights,
                k=1,
            )[0]

            if increase_stat_if_possible(viking, stat):
                gained_stats[stat] = gained_stats.get(stat, 0) + 1

                if getattr(viking, stat) >= viking.stat_potential.get(stat, getattr(viking, stat)):
                    weights_by_stat[stat] = 0

                    available_stats = [
                        s for s, weight in weights_by_stat.items()
                        if weight > 0
                    ]

                    if not available_stats:
                        break

                    weights = [
                        weights_by_stat[s]
                        for s in available_stats
                    ]

        if gained_stats:
            stat_text = ", ".join(
                f"+{amount} {stat}"
                for stat, amount in gained_stats.items()
            )

            logs.append(
                f"{viking.name} grows from experience: {stat_text}."
            )

    return logs    
    
def age_decline_points_for_job(age: int) -> int:
    if age < 32:
        return 0

    if age <= 34:
        return random.randint(1, 2)

    if age <= 37:
        return random.randint(2, 3)

    if age <= 40:
        return random.randint(3, 5)

    if age <= 43:
        return random.randint(4, 7)

    return random.randint(7, 11)    
    
def post_job_decline_chance_for_age(age: int) -> float:
    if age < 32:
        return 0.0

    if age <= 34:
        return 0.12

    if age <= 37:
        return 0.20

    if age <= 40:
        return 0.34

    if age <= 43:
        return 0.48

    return 0.65  
    
def apply_post_job_aging_wear(
    vikings: list[Viking],
    duration_weeks: int,
    job_success: bool,
) -> list[str]:
    logs = []

    for viking in vikings:
        if viking.status.value in {"Dead", "Retired"}:
            continue

        if viking.age < 32:
            continue

        base_decline = post_job_decline_chance_for_age(viking.age)
        length_bonus = expedition_length_growth_bonus(duration_weeks)

        chance = base_decline + length_bonus

        if job_success:
            chance *= 0.85

        if random.random() >= chance:
            continue

        points_lost = age_decline_points_for_job(viking.age)
        lost_stats = []

        for _ in range(points_lost):
            stat = decrease_random_stat(viking)

            if stat:
                lost_stats.append(stat)

        if lost_stats:
            stat_counts = {}

            for stat in lost_stats:
                stat_counts[stat] = stat_counts.get(stat, 0) + 1

            stat_text = ", ".join(
                f"-{amount} {stat}"
                for stat, amount in stat_counts.items()
            )

            logs.append(
                f"{viking.name} feels the strain of age after the expedition: "
                f"{stat_text}."
            )

    return logs  

def apply_post_job_loyalty_change(
    vikings: list[Viking],
    job_success: bool,
    event_failures: int,
    total_nodes: int,
) -> list[str]:
    logs = []

    if total_nodes <= 0:
        total_nodes = 1

    failure_pressure = event_failures / total_nodes

    for viking in vikings:
        if viking.status.value in {"Dead", "Retired"}:
            continue

        if viking.is_player:
            continue

        if job_success and failure_pressure <= 0.25:
            if random.random() < 0.25:
                viking.loyalty = min(100, viking.loyalty + 1)
                logs.append(f"{viking.name}'s loyalty grows after a clean success.")

        elif job_success and failure_pressure >= 0.60:
            if random.random() < 0.08:
                viking.loyalty = max(1, viking.loyalty - 1)
                logs.append(f"{viking.name} questions the cost of the expedition (-1 loyalty).")

        elif not job_success:
            if random.random() < 0.30:
                viking.loyalty = max(1, viking.loyalty - 1)
                logs.append(f"{viking.name} loses faith after failure (-1 loyalty).")

    return logs   
    
def retirement_chance_for_age(age: int, loyalty: int) -> int:
    if age < 34:
        return 0

    base_chances = {
        34: 5,
        35: 8,
        36: 10,
        37: 15,
        38: 20,
        39: 30,
        40: 40,
        41: 55,
        42: 75,
    }

    base = base_chances.get(age, 45)

    # Loyalty 50 = no modifier.
    # Every 10 loyalty above/below 50 adjusts chance by 2%.
    loyalty_modifier = ((50 - loyalty) // 10) * 2

    return max(0, min(95, base + loyalty_modifier))    