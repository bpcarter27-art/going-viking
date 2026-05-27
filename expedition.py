from __future__ import annotations

from dataclasses import dataclass, field
import random

from models import Viking, Job, JobType, CrewRole, FavoredGod
from events import (
    COMBAT_EVENTS,
    GENERIC_EVENTS,
    JOB_TYPE_EVENTS,
    JOB_FINAL_EVENTS,
    TRAVEL_TYPE_EVENTS,
    DANGER_EVENTS,
    get_location_events,
    roll_crew_stat,
    pick_random_viking,
    injure_viking,
    kill_or_permanently_injure_viking,
    event_is_eligible,
    set_current_expedition_result,
    clear_current_expedition_result,
)
from items import create_item_by_name, roll_reward_quality
from injury import apply_job_injury_risk, apply_event_injury_risk, InjuryType


#====================================================
# RESULTS
#====================================================

@dataclass
class ExpeditionResult:
    success: bool
    log: list[str] = field(default_factory=list)

    silver_gained: int = 0
    food_gained: int = 0
    renown_gained: int = 0
    loyalty_gained: int = 0
    
    thralls_gained: int = 0
    ship_timber_gained: int = 0
    fine_metal_gained: int = 0

    injuries: list[str] = field(default_factory=list)
    deaths: list[str] = field(default_factory=list)
    permanent_injuries: list[str] = field(default_factory=list)
    
    tested_stats: list[str] = field(default_factory=list)
    individual_tested_stats: dict[str, list[str]] = field(default_factory=dict)

    ship_damage: int = 0
    items_gained: list[str] = field(default_factory=list)
    
    event_failures: int = 0
    total_nodes: int = 0
    
    final_duration_weeks: int = 0
    difficulty_modifier: int = 0
    crew_strength_modifier: int = 0
    derived_score_modifier: int = 0
    nodes_completed: int = 0


#====================================================
# HELPERS
#====================================================

MIN_SUCCESS_CHANCE = 5
MAX_SUCCESS_CHANCE = 95
EVEN_MATCH_SUCCESS_CHANCE = 60
AUTO_FAIL_MARGIN = -250
AUTO_SUCCESS_MARGIN = 250

def calculate_success_chance(
    crew_strength: int,
    target: int,
) -> int:
    difference = crew_strength - target

    # Extreme mismatch = automatic outcomes.
    if difference <= AUTO_FAIL_MARGIN:
        return MIN_SUCCESS_CHANCE

    if difference >= AUTO_SUCCESS_MARGIN:
        return MAX_SUCCESS_CHANCE

    # Every 5 points = 1% shift.
    chance = EVEN_MATCH_SUCCESS_CHANCE + round(difference / 5)

    return max(
        MIN_SUCCESS_CHANCE,
        min(MAX_SUCCESS_CHANCE, chance)
    )

def apply_final_node_success_bonus(
    success_chance: int,
    final_node_success: bool | None,
) -> tuple[int, int]:
    if final_node_success is True:
        bonus = 25 if success_chance < 50 else 10
        return min(MAX_SUCCESS_CHANCE, success_chance + bonus), bonus

    if final_node_success is False:
        penalty = -5
        return max(MIN_SUCCESS_CHANCE, success_chance + penalty), penalty

    return success_chance, 0

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
    
def calculate_crew_strength(vikings: list[Viking]) -> int:
    """
    Summed expedition strength.

    A solid early viking contributes roughly 45-65.
    A strong viking may contribute 70-85+.
    Larger crews are therefore meaningfully stronger.
    """
    total = 0

    for viking in vikings:
        if not viking.is_available():
            continue

        total += (
            viking.raiding_score()
            + viking.sailing_score()
            + viking.command_score()
            + viking.survival_score()
        ) // 4

    return total


def expected_strength_for_difficulty(job: Job) -> int:
    expected_average_score = 50

    expected_crew_by_difficulty = {
        1: 5,
        2: 6,
        3: 7,
        4: 8,
        5: 10,
        6: 12,
        7: 15,
        8: 18,
        9: 22,
        10: 26,
    }

    expected_crew = expected_crew_by_difficulty.get(
        max(1, min(10, job.difficulty)),
        26,
    )

    return round(expected_crew * expected_average_score)


def calculate_job_success_with_modifier(
    vikings: list[Viking],
    job: Job,
    difficulty_modifier: int,
    final_node_success: bool | None = None,
    crew_strength_modifier: int = 0,
) -> tuple[bool, int, int, int, int, int, int, int]:
    original_difficulty = job.difficulty
    job.difficulty = max(1, job.difficulty + difficulty_modifier)

    base_crew_strength = calculate_crew_strength(vikings)
    crew_strength = base_crew_strength + crew_strength_modifier

    base_target = expected_strength_for_difficulty(job)
    danger_penalty = job.danger * 10
    rng = random.randint(-40, 40)

    final_target = base_target + danger_penalty + rng

    base_success_chance = calculate_success_chance(
        crew_strength,
        final_target,
    )

    success_chance, final_node_modifier = apply_final_node_success_bonus(
        base_success_chance,
        final_node_success,
    )

    success_roll = random.randint(1, 100)
    success = success_roll <= success_chance

    job.difficulty = original_difficulty

    return (
        success,
        success_roll,
        success_chance,
        final_target,
        rng,
        crew_strength,
        crew_strength - final_target,
        final_node_modifier,
    )
    
def record_tested_stats(result: ExpeditionResult, *stats: str) -> None:
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

def award_crew_success_renown(result, vikings):
    if not result.success:
        return

    if result.renown_gained < 2:
        return

    for viking in vikings:
        if not viking.is_available():
            continue

        if viking.role == CrewRole.CAPTAIN:
            continue

        rolls = 2 if viking.favored_god == FavoredGod.BALDR else 1
        gained = 0

        for _ in range(rolls):
            if random.randint(1, 100) <= 16:
                gained += 1

        if gained > 0:
            viking.renown += gained
            result.log.append(
                f"{viking.display_name()}'s deeds are noticed by the crew "
                f"(+{gained} personal renown)."
            )

#====================================================
# MAIN RESOLUTION
#====================================================

SUB_NODE_TRIGGER_CHANCE = 0.20


def roll_node_count(job: Job) -> int:
    """
    Every expedition now has at least:
    - 1 travel node
    - 1 general/relevant node
    - 1 final node
    """
    if job.duration_weeks <= 2:
        return random.randint(3, 4)

    if job.duration_weeks <= 4:
        return random.randint(3, 6)

    return random.randint(5, 8)


def apply_sub_node_event(result: ExpeditionResult, job: Job) -> int:
    if random.random() > SUB_NODE_TRIGGER_CHANCE:
        quiet_events = [
            "[Sub-node] The crew rows through gray water without incident.",
            "[Sub-node] Cold rain follows the ship, but nothing worse comes of it.",
            "[Sub-node] The men mutter over thin meals and keep moving.",
            "[Sub-node] A long day passes under dull skies.",
        ]
        result.log.append(random.choice(quiet_events))
        return 0

    roll = random.randint(1, 100)

    if roll <= 20:
        messages = [
            "[Sub-node] Scouts report stronger resistance than expected. Difficulty increases by 1.",
            "[Sub-node] A local guide warns that warriors are gathering nearby. Difficulty increases by 1.",
            "[Sub-node] Bad tracks, wary locals, and hard weather complicate the job. Difficulty increases by 1.",
        ]
        result.difficulty_modifier += 1
        result.log.append(random.choice(messages))
        return 0

    if roll <= 40:
        messages = [
            "[Sub-node] A frightened local reveals a safer approach. Difficulty decreases by 1.",
            "[Sub-node] The crew finds an abandoned trail around the worst ground. Difficulty decreases by 1.",
            "[Sub-node] An old contact offers useful advice. Difficulty decreases by 1.",
        ]
        result.difficulty_modifier -= 1
        result.log.append(random.choice(messages))
        return 0

    if roll <= 60:
        messages = [
            "[Sub-node] Heavy weather pins the crew down. Duration increases by 1 week and 1 node.",
            "[Sub-node] A broken oar, spoiled rope, and bitter winds cost precious time. Duration increases by 1 week and 1 node.",
            "[Sub-node] The crew must detour around hostile ground. Duration increases by 1 week and 1 node.",
        ]
        result.final_duration_weeks += 1
        result.log.append(random.choice(messages))
        return 1

    if roll <= 80:
        if result.final_duration_weeks > 1:
            messages = [
                "[Sub-node] Favorable winds and hard rowing cut time from the journey. Duration decreases by 1 week and 1 node.",
                "[Sub-node] The crew finds a shortcut through familiar waters. Duration decreases by 1 week and 1 node.",
                "[Sub-node] A lucky break lets the crew make better time than expected. Duration decreases by 1 week and 1 node.",
            ]
            result.final_duration_weeks -= 1
            result.log.append(random.choice(messages))
            return -1

        result.log.append("[Sub-node] The crew makes good time, but the job cannot get any shorter.")
        return 0

    bad_events = [
        "[Sub-node] A bitter quarrel divides the crew before order is restored.",
        "[Sub-node] Wolves stalk the camp through the night.",
        "[Sub-node] A pack animal breaks loose with supplies before it is caught.",
        "[Sub-node] A strange omen leaves the crew uneasy.",
    ]
    result.log.append(random.choice(bad_events))

    if random.random() < 0.25:
        result.difficulty_modifier += 1
        result.log.append("[Sub-node] The unease lingers. Difficulty increases by 1.")

    return 0


def node_kind_for_index(node_index: int, target_nodes: int) -> str:
    """
    Node pacing:
    - First half of non-final nodes are travel.
    - Second half are general/job/location.
    - Last node is always final.
    """
    target_nodes = max(3, target_nodes)

    if node_index >= target_nodes:
        return "final"

    non_final_nodes = target_nodes - 1
    travel_nodes = max(1, round(non_final_nodes / 2))

    if node_index <= travel_nodes:
        return "travel"

    return "general"


def pick_node_event(job: Job, node_kind: str, used_events: set, vikings: list[Viking]):
    location_events = get_location_events(job.location_name)

    if node_kind == "travel":
        pool = list(TRAVEL_TYPE_EVENTS.get(job.travel_type, []))

        if not pool:
            pool = list(GENERIC_EVENTS)

    elif node_kind == "final":
        pool = list(JOB_FINAL_EVENTS.get(job.job_type, []))

        if not pool:
            pool = list(JOB_TYPE_EVENTS.get(job.job_type, COMBAT_EVENTS))

    else:
        pool = list(GENERIC_EVENTS)
        pool += location_events
        pool += list(JOB_TYPE_EVENTS.get(job.job_type, []))

        if job.danger >= 7:
            pool += DANGER_EVENTS

    available_pool = [
        event for event in pool
        if event.__name__ not in used_events
        and event_is_eligible(event, vikings)
    ]

    if not available_pool:
        available_pool = [
            event for event in pool
            if event_is_eligible(event, vikings)
        ]

    if not available_pool:
        available_pool = [
            event for event in GENERIC_EVENTS
            if event_is_eligible(event, vikings)
        ]

    return random.choice(available_pool)



def handle_shipwreck_if_needed(
    result: ExpeditionResult,
    ship,
    vikings: list[Viking],
    job: Job,
    node_index: int,
    target_nodes: int,
) -> bool:
    """
    Returns True if the ship is wrecked and the expedition should end immediately.
    """
    if ship.hull > 0:
        return False

    result.success = False

    elapsed_weeks = max(
        1,
        round(job.duration_weeks * (node_index / max(1, target_nodes))),
    )

    result.final_duration_weeks = min(
        result.final_duration_weeks,
        elapsed_weeks,
    )

    result.log.append(
        f"{ship.name}'s hull is broken open. "
        "The ship is wrecked, and the expedition ends immediately."
    )

    apply_event_injury_risk(
        result=result,
        vikings=vikings,
        event_name="Shipwreck",
        injury_danger=7,
        injury_types=[
            InjuryType.SAILING,
            InjuryType.COLD,
            InjuryType.CRUSHING,
            InjuryType.FALLING,
        ],
        chance=100,
        max_injuries=len(vikings),
        fatal_allowed=True,
    )

    result.log.append(
        "The survivors limp home with the wreckage, empty-handed."
    )

    result.silver_gained = 0
    result.food_gained = 0
    result.renown_gained = 0
    result.thralls_gained = 0
    result.ship_timber_gained = 0
    result.fine_metal_gained = 0

    return True

def resolve_expedition(campaign, job: Job) -> ExpeditionResult:
    ship = campaign.ship
    vikings = campaign.get_active_crew_list()

    result = ExpeditionResult(success=True)
    result.final_duration_weeks = job.duration_weeks
    
    set_current_expedition_result(result)

    base_node_count = roll_node_count(job)
    target_nodes = base_node_count
    
    used_events = set()

    result.log.append(f"Expedition begins: {job.name}.")
    result.log.append(
        f"Initial plan: {job.duration_weeks} weeks, {base_node_count} main nodes."
    )

    if job.name in {
        "The Feast of Ragnar Lodbrok",
        "The Price of Peace",
    }:
        result.crew_strength_modifier += 4000
        result.derived_score_modifier += 40
        result.log.append(
            "[Ragnar's Host] Your crew sails within Ragnar Lodbrok's greater warband "
            "(+4000 final crew strength, +40 event rolls)."
        )

    failures = 0
    node_index = 0
    final_node_success = None

    while node_index < target_nodes:
        node_index += 1

        node_delta = apply_sub_node_event(result, job)
        target_nodes = max(3, target_nodes + node_delta)

        node_kind = node_kind_for_index(node_index, target_nodes)
        event = pick_node_event(job, node_kind, used_events, vikings)
        used_events.add(event.__name__)

        event_name = event.__name__.replace("event_", "").replace("_", " ").title()

        if node_kind == "final":
            result.log.append(f"[Final Node] {job.job_type.value} climax: {event_name}.")
        elif node_kind == "travel":
            result.log.append(f"[Travel Node {node_index}] {job.travel_type.value}: {event_name}.")
        else:
            result.log.append(f"[Job Node {node_index}] {event_name}.")

        tested_before = len(result.tested_stats) + sum(
            len(stats) for stats in result.individual_tested_stats.values()
        )

        success = event(result, ship, vikings)

        tested_after = len(result.tested_stats) + sum(
            len(stats) for stats in result.individual_tested_stats.values()
        )

        event_tested_stats = tested_after > tested_before

        if node_kind == "final":
            final_node_success = success
        elif event_tested_stats:
            if success:
                result.crew_strength_modifier += 5
                result.log.append(
                    "[Momentum] Success lifts the crew's confidence "
                    "(+5 final crew strength)."
                )
            else:
                result.crew_strength_modifier -= 2
                result.log.append(
                    "[Momentum] The setback weighs on the crew "
                    "(-2 final crew strength)."
                )        

        if handle_shipwreck_if_needed(
            result=result,
            ship=ship,
            vikings=vikings,
            job=job,
            node_index=node_index,
            target_nodes=target_nodes,
        ):
            result.event_failures = failures + 1
            result.total_nodes = target_nodes
            result.nodes_completed = node_index

            for viking in vikings:
                viking.start_injury_recovery()

            result.log.append(
                f"Final expedition length: {result.final_duration_weeks} weeks."
            )

            clear_current_expedition_result()
            return result

        if not success:
            failures += 1
            
    if failures > max(1, target_nodes // 2):
        result.difficulty_modifier += 1
        result.log.append("Too many setbacks increase expedition difficulty by 1.")        

    (
        job_success,
        success_roll,
        success_chance,
        success_target,
        success_rng,
        crew_strength,
        difference,
        final_node_modifier,
    ) = calculate_job_success_with_modifier(
        vikings,
        job,
        result.difficulty_modifier,
        final_node_success,
        result.crew_strength_modifier,
    )

    result.success = job_success

    result.log.append(
        f"Final expedition check:"
        f"\nCrew Strength: {crew_strength}"
        f"\nCrew Strength Modifier: {result.crew_strength_modifier:+}"        
        f"\nTarget: {success_target}"
        f"\nDifference: {difference:+}"
        f"\nSuccess Chance: {success_chance}%"
        f"\nFinal Node Modifier: {final_node_modifier:+}%"
        f"\nRoll: {success_roll}"
        f"\n(Base {expected_strength_for_difficulty(job)} | "
        f"Danger +{job.danger * 10} | "
        f"RNG {success_rng:+} | "
        f"Difficulty Modifier {result.difficulty_modifier:+})"
    )

    result.silver_gained += job.guaranteed_silver
    result.food_gained += job.guaranteed_food
    result.renown_gained += job.reward_renown
    
    result.thralls_gained += job.reward_thralls
    result.ship_timber_gained += job.reward_ship_timber
    result.fine_metal_gained += job.reward_fine_metal

    result.silver_gained += random.randint(job.random_silver_min, job.random_silver_max)
    result.food_gained += random.randint(job.random_food_min, job.random_food_max)

    item_drop_chance = 0.10 + (job.difficulty * 0.025) + (job.danger * 0.015)
    item_drop_chance = min(0.45, item_drop_chance)

    if result.success and job.possible_item_rewards:
        from items import create_item_by_name

        item_slots = 3
        reward_names = []

        for item_name in job.guaranteed_item_rewards:
            if len(reward_names) >= item_slots:
                break
            reward_names.append(item_name)

        remaining_slots = item_slots - len(reward_names)

        item_drop_chance = 0.10 + (job.difficulty * 0.025) + (job.danger * 0.015)
        item_drop_chance = min(0.45, item_drop_chance)

        for _ in range(remaining_slots):
            if random.random() < item_drop_chance:
                reward_names.append(random.choice(job.possible_item_rewards))

        for item_name in reward_names:
            item = create_item_by_name(item_name, roll_reward_quality())

            if item:
                campaign.add_item(item)
                result.items_gained.append(item.name)
                result.log.append(f"You recover an item: {item.name}.")
            else:
                result.items_gained.append(item_name)
                result.log.append(f"You recover an item: {item_name}.")

    if not result.success:
        result.log.append("The expedition struggles and fails to achieve its goals.")

        result.silver_gained = max(0, result.silver_gained // 2)
        result.food_gained = max(0, result.food_gained // 2)
        
        result.thralls_gained = max(0, result.thralls_gained // 2)
        result.ship_timber_gained = max(0, result.ship_timber_gained // 2)

    else:
        result.log.append("Expedition complete: success.")

    award_crew_success_renown(result, vikings)
    if result.loyalty_gained > 0:
        for viking in vikings:
            if viking.is_available() and not viking.is_player:
                viking.loyalty = min(100, viking.loyalty + result.loyalty_gained)

        result.log.append(
            f"Crew loyalty improves by {result.loyalty_gained}."
        )    
    apply_job_injury_risk(result, vikings, job)
    for log in campaign.apply_herbalists_hut_recovery_bonus(vikings):
        result.log.append(log)
    

    # --------------------------------------------------
    # Injuries suffered during the expedition now begin
    # their recovery timers after the expedition ends.
    # --------------------------------------------------
    for viking in vikings:
        viking.start_injury_recovery()

    result.log.append(
        f"Final expedition length: {result.final_duration_weeks} weeks."
    )
    result.event_failures = failures
    result.total_nodes = target_nodes

    clear_current_expedition_result()
    return result