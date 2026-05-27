from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import random


class PsychSeverity(str, Enum):
    TEMPORARY = "Temporary"
    PERMANENT = "Permanent"


class PsychType(str, Enum):
    COMBAT = "Combat"
    SAILING = "Sailing"
    COLD = "Cold"
    DEATH = "Death"
    FAILURE = "Failure"


@dataclass
class PsychConditionTemplate:
    name: str
    psych_type: PsychType
    severity: PsychSeverity
    

    weeks_min: int = 0
    weeks_max: int = 0

    possible_titles: list[str] = field(default_factory=list)
    courage_mod: int = 0
    cunning_mod: int = 0
    leadership_mod: int = 0
    vitality_mod: int = 0
    seamanship_mod: int = 0


PSYCH_CONDITIONS = {
    PsychSeverity.TEMPORARY: [
        # FAILURE - negative
        PsychConditionTemplate("Doubtful", PsychType.FAILURE, PsychSeverity.TEMPORARY, 3, 8, leadership_mod=-4, courage_mod=-2),
        PsychConditionTemplate("Ashamed", PsychType.FAILURE, PsychSeverity.TEMPORARY, 3, 8, leadership_mod=-5),
        PsychConditionTemplate("Second-Guessing", PsychType.FAILURE, PsychSeverity.TEMPORARY, 2, 6, cunning_mod=-3, leadership_mod=-2),
        PsychConditionTemplate("Shaken Confidence", PsychType.FAILURE, PsychSeverity.TEMPORARY, 4, 8, courage_mod=-5),

        # FAILURE - positive
        PsychConditionTemplate("Hard Lesson", PsychType.FAILURE, PsychSeverity.TEMPORARY, 3, 6, cunning_mod=3),
        PsychConditionTemplate("Humbled", PsychType.FAILURE, PsychSeverity.TEMPORARY, 3, 6, leadership_mod=2, courage_mod=-1),

        # DEATH - negative
        PsychConditionTemplate("Night Terrors", PsychType.DEATH, PsychSeverity.TEMPORARY, 4, 10, courage_mod=-5, vitality_mod=-3),
        PsychConditionTemplate("Haunted Sleep", PsychType.DEATH, PsychSeverity.TEMPORARY, 4, 10, vitality_mod=-5),
        PsychConditionTemplate("Blood-Shaken", PsychType.DEATH, PsychSeverity.TEMPORARY, 3, 8, courage_mod=-6),
        PsychConditionTemplate("Grief-Heavy", PsychType.DEATH, PsychSeverity.TEMPORARY, 4, 10, leadership_mod=-4, vitality_mod=-2),

        # DEATH - positive
        PsychConditionTemplate("Death-Hardened", PsychType.DEATH, PsychSeverity.TEMPORARY, 3, 8, courage_mod=4),
        PsychConditionTemplate("Vow of Vengeance", PsychType.DEATH, PsychSeverity.TEMPORARY, 4, 8, courage_mod=5, cunning_mod=-2),

        # OTHER TYPES - placeholders for later
        PsychConditionTemplate("Shaken", PsychType.COMBAT, PsychSeverity.TEMPORARY, 2, 6, courage_mod=-4),
        PsychConditionTemplate("Storm-Shaken", PsychType.SAILING, PsychSeverity.TEMPORARY, 3, 8, seamanship_mod=-5, courage_mod=-3),
        PsychConditionTemplate("Winter Gloom", PsychType.COLD, PsychSeverity.TEMPORARY, 4, 8, vitality_mod=-4, leadership_mod=-3),
    ],

    PsychSeverity.PERMANENT: [
        # FAILURE - negative
        PsychConditionTemplate("Broken Faith", PsychType.FAILURE, PsychSeverity.PERMANENT, leadership_mod=-8, courage_mod=-4),
        PsychConditionTemplate("Craven Doubt", PsychType.FAILURE, PsychSeverity.PERMANENT, courage_mod=-8, possible_titles=["the Doubtful"]),
        PsychConditionTemplate("Failure-Marked", PsychType.FAILURE, PsychSeverity.PERMANENT, leadership_mod=-6, cunning_mod=-3),

        # FAILURE - positive
        PsychConditionTemplate("Tempered by Failure", PsychType.FAILURE, PsychSeverity.PERMANENT, cunning_mod=5, leadership_mod=2),
        PsychConditionTemplate("Never Again", PsychType.FAILURE, PsychSeverity.PERMANENT, courage_mod=4, leadership_mod=3, possible_titles=["the Determined"]),

        # DEATH - negative
        PsychConditionTemplate("Haunted", PsychType.DEATH, PsychSeverity.PERMANENT, courage_mod=-6, cunning_mod=-4, possible_titles=["the Haunted"]),
        PsychConditionTemplate("Death-Fear", PsychType.DEATH, PsychSeverity.PERMANENT, courage_mod=-10),
        PsychConditionTemplate("Dead-Eyed", PsychType.DEATH, PsychSeverity.PERMANENT, leadership_mod=-5, vitality_mod=-4, possible_titles=["Deadeye"]),

        # DEATH - positive
        PsychConditionTemplate("Death-Touched", PsychType.DEATH, PsychSeverity.PERMANENT, courage_mod=6, leadership_mod=3),
        PsychConditionTemplate("Grim Resolve", PsychType.DEATH, PsychSeverity.PERMANENT, courage_mod=5, vitality_mod=3, possible_titles=["the Grim"]),

        # OTHER TYPES - placeholders for later
        PsychConditionTemplate("Battle-Mad", PsychType.COMBAT, PsychSeverity.PERMANENT, courage_mod=8, cunning_mod=-6),
        PsychConditionTemplate("Sea-Fear", PsychType.SAILING, PsychSeverity.PERMANENT, seamanship_mod=-10, courage_mod=-4),
        PsychConditionTemplate("Winter-Touched", PsychType.COLD, PsychSeverity.PERMANENT, vitality_mod=-6, cunning_mod=-4),
    ],
}


def psych_stat_modifiers(condition: PsychConditionTemplate) -> dict[str, int]:
    return {
        stat: value
        for stat, value in {
            "courage": condition.courage_mod,
            "cunning": condition.cunning_mod,
            "leadership": condition.leadership_mod,
            "vitality": condition.vitality_mod,
            "seamanship": condition.seamanship_mod,
        }.items()
        if value != 0
    }


def roll_psych_condition(psych_type: PsychType, permanent_chance: int = 10) -> PsychConditionTemplate:
    severity = (
        PsychSeverity.PERMANENT
        if random.randint(1, 100) <= permanent_chance
        else PsychSeverity.TEMPORARY
    )

    options = [
        condition for condition in PSYCH_CONDITIONS[severity]
        if condition.psych_type == psych_type
    ]

    if not options:
        options = PSYCH_CONDITIONS[severity]

    return random.choice(options)


def apply_psych_condition(viking, condition: PsychConditionTemplate) -> str:
    weeks = 0

    if condition.severity == PsychSeverity.TEMPORARY:
        weeks = random.randint(condition.weeks_min, condition.weeks_max)

    viking.add_injury(
        injury_name=condition.name,
        weeks_remaining=weeks,
        stat_modifiers=psych_stat_modifiers(condition),
        recovery_started=True,
        can_deploy_while_injured=True,
    )

    if condition.severity == PsychSeverity.PERMANENT:
        for stat, mod in psych_stat_modifiers(condition).items():
            current = getattr(viking, stat)
            setattr(viking, stat, max(1, current + mod))

        viking.suffer_permanent_injury(condition.name)
        if condition.possible_titles:
            title = random.choice(condition.possible_titles)
            viking.pending_title = title

        return f"{viking.name} is changed forever: {condition.name}."

    return f"{viking.name} suffers a temporary condition: {condition.name} ({weeks} weeks)."