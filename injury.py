from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import random

from models import Viking, Job, JobType, VikingClass
from psych import roll_psych_condition, apply_psych_condition, PsychType


class InjurySeverity(str, Enum):
    SUPERFICIAL = "Superficial"
    MINOR = "Minor"
    MAJOR = "Major"
    PERMANENT = "Permanent"
    FATAL = "Fatal"


class InjuryType(str, Enum):
    GENERIC = "Generic"
    COMBAT = "Combat"
    SAILING = "Sailing"
    FIRE = "Fire"
    CRUSHING = "Crushing"
    COLD = "Cold"
    HUNTING = "Hunting"
    FALLING = "Falling"
    SICKNESS = "Sickness"
    ARROW = "Arrow"

SEVERITY_DOWNGRADE = {
    InjurySeverity.FATAL: InjurySeverity.PERMANENT,
    InjurySeverity.PERMANENT: InjurySeverity.MAJOR,
    InjurySeverity.MAJOR: InjurySeverity.MINOR,
    InjurySeverity.MINOR: InjurySeverity.SUPERFICIAL,
}


def maybe_reduce_severity_with_herbalists(
    result,
    vikings: list[Viking],
    injured_viking: Viking,
    severity: InjurySeverity,
) -> InjurySeverity:
    if severity == InjurySeverity.SUPERFICIAL:
        return severity

    herbalists = [
        viking for viking in vikings
        if viking.is_available()
        and viking.viking_class == VikingClass.HERBALIST
        and viking.viking_id != injured_viking.viking_id
    ]

    if not herbalists:
        return severity

    chance = 10 + ((len(herbalists) - 1) * 2)
    chance = clamp(chance, 5, 20)

    roll = random.randint(1, 100)

    if roll > chance:
        result.log.append(
            f"[Herbalist Aid] Roll {roll} vs {chance}%. "
            f"No severity reduction."
        )
        return severity

    reduced = SEVERITY_DOWNGRADE.get(severity, severity)

    result.log.append(
        f"[Herbalist Aid] Roll {roll} vs {chance}%. "
        f"{injured_viking.name}'s injury severity is reduced: "
        f"{severity.value} -> {reduced.value}."
    )

    return reduced

@dataclass
class InjuryTemplate:
    name: str
    injury_type: InjuryType
    severity: InjurySeverity

    recovery_weeks_min: int = 0
    recovery_weeks_max: int = 0

    permanent: bool = False
    fatal: bool = False
    can_deploy_while_injured: bool = True

    might_mod: int = 0
    skill_mod: int = 0
    cunning_mod: int = 0
    leadership_mod: int = 0
    courage_mod: int = 0
    vitality_mod: int = 0
    agility_mod: int = 0
    seamanship_mod: int = 0

    possible_titles: list[str] = field(default_factory=list)


INJURY_TABLES: dict[InjuryType, dict[InjurySeverity, list[InjuryTemplate]]] = {
    InjuryType.GENERIC: {
        InjurySeverity.SUPERFICIAL: [
            InjuryTemplate("Black Eye", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-2),
            InjuryTemplate("Scratched Cheek", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
            InjuryTemplate("Split Lip", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
            InjuryTemplate("Bloody Nose", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Bruised Jaw", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-2),
            InjuryTemplate("Swollen Cheek", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Cut Brow", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Loose Tooth", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
            InjuryTemplate("Bruised Knuckles", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Scraped Shin", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, agility_mod=-1),
            InjuryTemplate("Swollen Eye", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-2),
            InjuryTemplate("Bitten Tongue", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
            InjuryTemplate("Bruised Forearm", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, might_mod=-1),
            InjuryTemplate("Scraped Shoulder", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, might_mod=-1),
            InjuryTemplate("Aching Back", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Split Fingernail", InjuryType.GENERIC, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
        ],
        InjurySeverity.MINOR: [
            InjuryTemplate("Bruised Ribs", InjuryType.GENERIC, InjurySeverity.MINOR, 3, 6, vitality_mod=-5),
            InjuryTemplate("Sprained Wrist", InjuryType.GENERIC, InjurySeverity.MINOR, 3, 6, skill_mod=-5),
            InjuryTemplate("Twisted Knee", InjuryType.GENERIC, InjurySeverity.MINOR, 3, 7, agility_mod=-6),
            InjuryTemplate("Cut Forearm", InjuryType.GENERIC, InjurySeverity.MINOR, 2, 5, skill_mod=-4),
            InjuryTemplate("Badly Bruised Shoulder", InjuryType.GENERIC, InjurySeverity.MINOR, 3, 6, might_mod=-5),
            InjuryTemplate("Jammed Finger", InjuryType.GENERIC, InjurySeverity.MINOR, 2, 5, skill_mod=-4),
            InjuryTemplate("Pulled Back", InjuryType.GENERIC, InjurySeverity.MINOR, 4, 8, might_mod=-5, agility_mod=-3),
            InjuryTemplate("Deep Bruising", InjuryType.GENERIC, InjurySeverity.MINOR, 3, 6, vitality_mod=-5),
            InjuryTemplate("Wrenched Knee", InjuryType.GENERIC, InjurySeverity.MINOR, 3, 7, agility_mod=-6),
            InjuryTemplate("Strained Neck", InjuryType.GENERIC, InjurySeverity.MINOR, 3, 6, vitality_mod=-4),
            InjuryTemplate("Gashed Palm", InjuryType.GENERIC, InjurySeverity.MINOR, 2, 5, skill_mod=-5),
            InjuryTemplate("Bruised Hip", InjuryType.GENERIC, InjurySeverity.MINOR, 3, 6, agility_mod=-4),
            InjuryTemplate("Sore Shoulder", InjuryType.GENERIC, InjurySeverity.MINOR, 3, 6, might_mod=-5),
            InjuryTemplate("Deep Cut", InjuryType.GENERIC, InjurySeverity.MINOR, 3, 6, vitality_mod=-5),
            InjuryTemplate("Twisted Elbow", InjuryType.GENERIC, InjurySeverity.MINOR, 3, 7, skill_mod=-5),
            InjuryTemplate("Battered Ribs", InjuryType.GENERIC, InjurySeverity.MINOR, 4, 8, vitality_mod=-6),
        ],
        InjurySeverity.MAJOR: [
            InjuryTemplate("Broken Arm", InjuryType.GENERIC, InjurySeverity.MAJOR, 12, 24, might_mod=-24, skill_mod=-16, can_deploy_while_injured=False),
            InjuryTemplate("Broken Leg", InjuryType.GENERIC, InjurySeverity.MAJOR, 18, 32, agility_mod=-36, can_deploy_while_injured=False),
            InjuryTemplate("Badly Cracked Ribs", InjuryType.GENERIC, InjurySeverity.MAJOR, 10, 18, vitality_mod=-18),
            InjuryTemplate("Torn Shoulder", InjuryType.GENERIC, InjurySeverity.MAJOR, 12, 24, might_mod=-22, skill_mod=-14, can_deploy_while_injured=False),
            InjuryTemplate("Deep Side Wound", InjuryType.GENERIC, InjurySeverity.MAJOR, 10, 18, vitality_mod=-18),
            InjuryTemplate("Dislocated Shoulder", InjuryType.GENERIC, InjurySeverity.MAJOR, 10, 18, might_mod=-16, skill_mod=-10),
            InjuryTemplate("Split Open Scalp", InjuryType.GENERIC, InjurySeverity.MAJOR, 8, 16, vitality_mod=-14, skill_mod=-4),
            InjuryTemplate("Ruptured Tendon", InjuryType.GENERIC, InjurySeverity.MAJOR, 16, 28, agility_mod=-24, can_deploy_while_injured=False),
            InjuryTemplate("Collapsed Lung", InjuryType.GENERIC, InjurySeverity.MAJOR, 16, 30, vitality_mod=-28, can_deploy_while_injured=False),
            InjuryTemplate("Shattered Elbow", InjuryType.GENERIC, InjurySeverity.MAJOR, 14, 26, might_mod=-18, skill_mod=-16, can_deploy_while_injured=False),
        ],
        InjurySeverity.PERMANENT: [
            InjuryTemplate("Scarred Face", InjuryType.GENERIC, InjurySeverity.PERMANENT, 8, 14, permanent=True, leadership_mod=-1, possible_titles=["the Scarred"]),
            InjuryTemplate("Missing Fingers", InjuryType.GENERIC, InjurySeverity.PERMANENT, 16, 28, permanent=True, skill_mod=-10, possible_titles=["Half-Hand"]),
            InjuryTemplate("Broken Nose", InjuryType.GENERIC, InjurySeverity.PERMANENT, 6, 12, permanent=True, leadership_mod=-2, possible_titles=["Crooked-Nose"]),
            InjuryTemplate("Stiff Shoulder", InjuryType.GENERIC, InjurySeverity.PERMANENT, 12, 22, permanent=True, might_mod=-7, skill_mod=-5),
            InjuryTemplate("Old Limp", InjuryType.GENERIC, InjurySeverity.PERMANENT, 14, 26, permanent=True, agility_mod=-8, possible_titles=["the Limping"]),
            InjuryTemplate("Crooked Spine", InjuryType.GENERIC, InjurySeverity.PERMANENT, 20, 36, permanent=True, might_mod=-10, agility_mod=-10, possible_titles=["Bent-Back"], can_deploy_while_injured=False),
            InjuryTemplate("Missing Ear", InjuryType.GENERIC, InjurySeverity.PERMANENT, 8, 14, permanent=True, leadership_mod=-1, possible_titles=["Half-Ear"]),
            InjuryTemplate("Clouded Eye", InjuryType.GENERIC, InjurySeverity.PERMANENT, 16, 28, permanent=True, skill_mod=-8, possible_titles=["Cloud-Eye"]),
            InjuryTemplate("Permanent Lameness", InjuryType.GENERIC, InjurySeverity.PERMANENT, 18, 32, permanent=True, agility_mod=-14, possible_titles=["the Lame"], can_deploy_while_injured=False),
            InjuryTemplate("Crushed Chest", InjuryType.GENERIC, InjurySeverity.PERMANENT, 20, 36, permanent=True, vitality_mod=-12, can_deploy_while_injured=False),
        ],
        InjurySeverity.FATAL: [
            InjuryTemplate("Killed by Misfortune", InjuryType.GENERIC, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Died from Hidden Wounds", InjuryType.GENERIC, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Never Rose Again", InjuryType.GENERIC, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Collapsed After the Struggle", InjuryType.GENERIC, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Taken by Fate", InjuryType.GENERIC, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Bled Out from Wounds", InjuryType.GENERIC, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Died During the Night", InjuryType.GENERIC, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Never Recovered from the Injury", InjuryType.GENERIC, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Body Failed After the Expedition", InjuryType.GENERIC, InjurySeverity.FATAL, fatal=True),
        ],
    },

    InjuryType.COMBAT: {
        InjurySeverity.SUPERFICIAL: [
            InjuryTemplate("Shield Bruise", InjuryType.COMBAT, InjurySeverity.SUPERFICIAL, 1, 2, might_mod=-1),
            InjuryTemplate("Knife Nick", InjuryType.COMBAT, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Helmet Dent", InjuryType.COMBAT, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Shield-Splinter Cut", InjuryType.COMBAT, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Glancing Sword Cut", InjuryType.COMBAT, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-2),
            InjuryTemplate("Bruised Shield Arm", InjuryType.COMBAT, InjurySeverity.SUPERFICIAL, 1, 2, might_mod=-2),
            InjuryTemplate("Nicked Ear", InjuryType.COMBAT, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
            InjuryTemplate("Shield-Rim Bruise", InjuryType.COMBAT, InjurySeverity.SUPERFICIAL, 1, 2, might_mod=-1),
            InjuryTemplate("Sword-Scraped Knuckles", InjuryType.COMBAT, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Spear Shaft Bruise", InjuryType.COMBAT, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Cut Chin", InjuryType.COMBAT, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
            InjuryTemplate("Bruised Forearm", InjuryType.COMBAT, InjurySeverity.SUPERFICIAL, 1, 2, might_mod=-1),
        ],
        InjurySeverity.MINOR: [
            InjuryTemplate("Broken Finger", InjuryType.COMBAT, InjurySeverity.MINOR, 3, 7, skill_mod=-6),
            InjuryTemplate("Sword Cut", InjuryType.COMBAT, InjurySeverity.MINOR, 3, 6, vitality_mod=-5),
            InjuryTemplate("Shield Arm Strain", InjuryType.COMBAT, InjurySeverity.MINOR, 3, 6, might_mod=-5),
            InjuryTemplate("Spear Graze", InjuryType.COMBAT, InjurySeverity.MINOR, 2, 5, vitality_mod=-4),
            InjuryTemplate("Axe-Nicked Shoulder", InjuryType.COMBAT, InjurySeverity.MINOR, 4, 8, might_mod=-6),
            InjuryTemplate("Twisted in the Shield Wall", InjuryType.COMBAT, InjurySeverity.MINOR, 3, 6, agility_mod=-5),
            InjuryTemplate("Knife Cut Across Palm", InjuryType.COMBAT, InjurySeverity.MINOR, 3, 6, skill_mod=-5),
            InjuryTemplate("Spear-Butt Bruise", InjuryType.COMBAT, InjurySeverity.MINOR, 3, 6, vitality_mod=-5),
            InjuryTemplate("Axe-Split Brow", InjuryType.COMBAT, InjurySeverity.MINOR, 3, 6, skill_mod=-4),
            InjuryTemplate("Shield-Wrenched Wrist", InjuryType.COMBAT, InjurySeverity.MINOR, 3, 7, skill_mod=-6),
            InjuryTemplate("Kicked Knee", InjuryType.COMBAT, InjurySeverity.MINOR, 3, 6, agility_mod=-5),
            InjuryTemplate("Blade Cut Thigh", InjuryType.COMBAT, InjurySeverity.MINOR, 4, 8, agility_mod=-6),
        ],
        InjurySeverity.MAJOR: [
            InjuryTemplate("Spear Through Thigh", InjuryType.COMBAT, InjurySeverity.MAJOR, 12, 22, agility_mod=-24, might_mod=-10, can_deploy_while_injured=False),
            InjuryTemplate("Deep Axe Wound", InjuryType.COMBAT, InjurySeverity.MAJOR, 10, 18, vitality_mod=-20, courage_mod=-6, can_deploy_while_injured=False),
            InjuryTemplate("Sword Through Shoulder", InjuryType.COMBAT, InjurySeverity.MAJOR, 12, 24, might_mod=-20, skill_mod=-12, can_deploy_while_injured=False),
            InjuryTemplate("Shield Boss to the Face", InjuryType.COMBAT, InjurySeverity.MAJOR, 10, 18, vitality_mod=-14, skill_mod=-8),
            InjuryTemplate("Split Shield Arm", InjuryType.COMBAT, InjurySeverity.MAJOR, 10, 20, might_mod=-18, skill_mod=-8, can_deploy_while_injured=False),
            InjuryTemplate("Broken Jaw", InjuryType.COMBAT, InjurySeverity.MAJOR, 10, 18, leadership_mod=-8, vitality_mod=-12),
            InjuryTemplate("Shield Arm Broken", InjuryType.COMBAT, InjurySeverity.MAJOR, 14, 26, might_mod=-22, skill_mod=-8, can_deploy_while_injured=False),
            InjuryTemplate("Gut Wound", InjuryType.COMBAT, InjurySeverity.MAJOR, 16, 32, vitality_mod=-30, can_deploy_while_injured=False),
            InjuryTemplate("Deep Spear Wound", InjuryType.COMBAT, InjurySeverity.MAJOR, 12, 24, vitality_mod=-22, can_deploy_while_injured=False),
            InjuryTemplate("Axe-Cleft Shoulder", InjuryType.COMBAT, InjurySeverity.MAJOR, 14, 26, might_mod=-22, skill_mod=-10, can_deploy_while_injured=False),
        ],
        InjurySeverity.PERMANENT: [
            InjuryTemplate("Lost Eye", InjuryType.COMBAT, InjurySeverity.PERMANENT, 16, 28, permanent=True, skill_mod=-12, possible_titles=["One-Eye"], can_deploy_while_injured=False),
            InjuryTemplate("Maimed Hand", InjuryType.COMBAT, InjurySeverity.PERMANENT, 18, 32, permanent=True, skill_mod=-18, might_mod=-6, possible_titles=["Half-Hand"], can_deploy_while_injured=False),
            InjuryTemplate("Hacked Ear", InjuryType.COMBAT, InjurySeverity.PERMANENT, 8, 14, permanent=True, leadership_mod=-1, possible_titles=["Half-Ear"]),
            InjuryTemplate("Sword-Scarred Face", InjuryType.COMBAT, InjurySeverity.PERMANENT, 14, 24, permanent=True, courage_mod=3, leadership_mod=-2, possible_titles=["Scar-Face"]),
            InjuryTemplate("Missing Teeth", InjuryType.COMBAT, InjurySeverity.PERMANENT, 10, 18, permanent=True, leadership_mod=-3, possible_titles=["Broken-Jaw"]),
            InjuryTemplate("Severed Tendons", InjuryType.COMBAT, InjurySeverity.PERMANENT, 20, 36, permanent=True, agility_mod=-16, can_deploy_while_injured=False),
            InjuryTemplate("One-Handed", InjuryType.COMBAT, InjurySeverity.PERMANENT, 24, 40, permanent=True, might_mod=-14, skill_mod=-20, possible_titles=["One-Hand"], can_deploy_while_injured=True),
            InjuryTemplate("Battle-Madness", InjuryType.COMBAT, InjurySeverity.PERMANENT, 12, 24, permanent=True, courage_mod=8, cunning_mod=-8, possible_titles=["Battle-Mad"]),
            InjuryTemplate("Hamstrung by Blade", InjuryType.COMBAT, InjurySeverity.PERMANENT, 16, 30, permanent=True, agility_mod=-32, can_deploy_while_injured=False),
        ],
        InjurySeverity.FATAL: [
            InjuryTemplate("Slain in the Shield Wall", InjuryType.COMBAT, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Cut Down in Close Fighting", InjuryType.COMBAT, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Spear Through the Chest", InjuryType.COMBAT, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Split from Shoulder to Chest", InjuryType.COMBAT, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Trampled in Battle", InjuryType.COMBAT, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Beheaded in Combat", InjuryType.COMBAT, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Dragged Down by Enemies", InjuryType.COMBAT, InjurySeverity.FATAL, fatal=True),
        ],
    },

    InjuryType.SAILING: {
        InjurySeverity.SUPERFICIAL: [
            InjuryTemplate("Rope Burn", InjuryType.SAILING, InjurySeverity.SUPERFICIAL, 1, 2, seamanship_mod=-1),
            InjuryTemplate("Salt-Cracked Hands", InjuryType.SAILING, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Oar Blisters", InjuryType.SAILING, InjurySeverity.SUPERFICIAL, 1, 2, might_mod=-1),
            InjuryTemplate("Bruised by the Gunwale", InjuryType.SAILING, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Salt-Stung Cuts", InjuryType.SAILING, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Splintered Oar Cut", InjuryType.SAILING, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Wet Deck Bruise", InjuryType.SAILING, InjurySeverity.SUPERFICIAL, 1, 2, agility_mod=-1),
            InjuryTemplate("Raw Rowing Hands", InjuryType.SAILING, InjurySeverity.SUPERFICIAL, 1, 2, might_mod=-1),
            InjuryTemplate("Salt Rash", InjuryType.SAILING, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Rope-Snapped Wrist", InjuryType.SAILING, InjurySeverity.SUPERFICIAL, 1, 2, seamanship_mod=-1),
        ],
        InjurySeverity.MINOR: [
            InjuryTemplate("Rowing Strain", InjuryType.SAILING, InjurySeverity.MINOR, 3, 6, might_mod=-6),
            InjuryTemplate("Twisted on Wet Deck", InjuryType.SAILING, InjurySeverity.MINOR, 3, 6, agility_mod=-5),
            InjuryTemplate("Strained Back from Rowing", InjuryType.SAILING, InjurySeverity.MINOR, 4, 8, might_mod=-6, agility_mod=-3),
            InjuryTemplate("Cracked Shin on Deck", InjuryType.SAILING, InjurySeverity.MINOR, 3, 6, agility_mod=-5),
            InjuryTemplate("Sprained Wrist on the Oar", InjuryType.SAILING, InjurySeverity.MINOR, 3, 6, seamanship_mod=-5, skill_mod=-3),
            InjuryTemplate("Oarlock Pinched Hand", InjuryType.SAILING, InjurySeverity.MINOR, 3, 6, skill_mod=-5),
            InjuryTemplate("Slipped at the Stern", InjuryType.SAILING, InjurySeverity.MINOR, 3, 6, agility_mod=-5),
            InjuryTemplate("Rope-Wrenched Shoulder", InjuryType.SAILING, InjurySeverity.MINOR, 4, 8, might_mod=-6),
            InjuryTemplate("Deck-Smashed Knee", InjuryType.SAILING, InjurySeverity.MINOR, 3, 7, agility_mod=-6),
            InjuryTemplate("Back Strain at the Oar", InjuryType.SAILING, InjurySeverity.MINOR, 4, 8, might_mod=-5, seamanship_mod=-3),
        ],
        InjurySeverity.MAJOR: [
            InjuryTemplate("Badly Crushed by Loose Cargo", InjuryType.SAILING, InjurySeverity.MAJOR, 10, 18, vitality_mod=-18, can_deploy_while_injured=False),
            InjuryTemplate("Thrown Against the Mast", InjuryType.SAILING, InjurySeverity.MAJOR, 10, 18, vitality_mod=-18, agility_mod=-10),
            InjuryTemplate("Crushed Beneath an Oar", InjuryType.SAILING, InjurySeverity.MAJOR, 12, 22, might_mod=-18, vitality_mod=-14, can_deploy_while_injured=False),
            InjuryTemplate("Bones Broken by Heavy Seas", InjuryType.SAILING, InjurySeverity.MAJOR, 14, 26, vitality_mod=-22, can_deploy_while_injured=False),
            InjuryTemplate("Thrown Across the Deck", InjuryType.SAILING, InjurySeverity.MAJOR, 10, 20, agility_mod=-14, vitality_mod=-12),
            InjuryTemplate("Ribs Broken by the Oar Bench", InjuryType.SAILING, InjurySeverity.MAJOR, 10, 18, vitality_mod=-18, can_deploy_while_injured=False),
            InjuryTemplate("Storm-Wrenched Back", InjuryType.SAILING, InjurySeverity.MAJOR, 12, 22, might_mod=-14, agility_mod=-12, can_deploy_while_injured=False),
            InjuryTemplate("Crushed Against the Gunwale", InjuryType.SAILING, InjurySeverity.MAJOR, 12, 24, vitality_mod=-24, can_deploy_while_injured=False),
        ],
        InjurySeverity.PERMANENT: [
            InjuryTemplate("Crushed Leg", InjuryType.SAILING, InjurySeverity.PERMANENT, 18, 32, permanent=True, agility_mod=-18, possible_titles=["the Limping"], can_deploy_while_injured=False),
            InjuryTemplate("Storm-Ruined Shoulder", InjuryType.SAILING, InjurySeverity.PERMANENT, 16, 28, permanent=True, might_mod=-10, seamanship_mod=-5, possible_titles=["Storm-Broken"]),
            InjuryTemplate("Salt-Ruined Eye", InjuryType.SAILING, InjurySeverity.PERMANENT, 16, 28, permanent=True, seamanship_mod=-8, possible_titles=["Salt-Eye"], can_deploy_while_injured=False),
            InjuryTemplate("Storm-Lamed Leg", InjuryType.SAILING, InjurySeverity.PERMANENT, 18, 32, permanent=True, agility_mod=-14, possible_titles=["Storm-Lamed"], can_deploy_while_injured=False),
            InjuryTemplate("Sea-Madness", InjuryType.SAILING, InjurySeverity.PERMANENT, 12, 24, permanent=True, courage_mod=-8, cunning_mod=-5, possible_titles=["Wave-Mad"]),
        ],
        InjurySeverity.FATAL: [
            InjuryTemplate("Drowned in Black Water", InjuryType.SAILING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Swept Overboard", InjuryType.SAILING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Lost Beneath the Waves", InjuryType.SAILING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Crushed Between Ships", InjuryType.SAILING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Frozen and Swept Overboard", InjuryType.SAILING, InjurySeverity.FATAL, fatal=True),
        ],
    },

    InjuryType.FIRE: {
        InjurySeverity.SUPERFICIAL: [
            InjuryTemplate("Singed Beard", InjuryType.FIRE, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
            InjuryTemplate("Smoke-Stung Eyes", InjuryType.FIRE, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-2),
            InjuryTemplate("Soot-Burned Skin", InjuryType.FIRE, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Scorched Hair", InjuryType.FIRE, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
            InjuryTemplate("Hot Ash Burns", InjuryType.FIRE, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-2),
            InjuryTemplate("Ash-Stung Throat", InjuryType.FIRE, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Cinder Burn", InjuryType.FIRE, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Singe-Marked Hands", InjuryType.FIRE, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Smoke-Watery Eyes", InjuryType.FIRE, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Burned Ear", InjuryType.FIRE, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
        ],
        InjurySeverity.MINOR: [
            InjuryTemplate("Burned Hand", InjuryType.FIRE, InjurySeverity.MINOR, 4, 8, skill_mod=-7),
            InjuryTemplate("Scorched Arm", InjuryType.FIRE, InjurySeverity.MINOR, 4, 8, vitality_mod=-5, skill_mod=-3),
            InjuryTemplate("Blistered Palm", InjuryType.FIRE, InjurySeverity.MINOR, 3, 6, skill_mod=-5),
            InjuryTemplate("Smoke-Sick", InjuryType.FIRE, InjurySeverity.MINOR, 3, 6, vitality_mod=-6),
            InjuryTemplate("Burned Forearm", InjuryType.FIRE, InjurySeverity.MINOR, 4, 8, skill_mod=-6, might_mod=-3),
            InjuryTemplate("Burned Fingers", InjuryType.FIRE, InjurySeverity.MINOR, 3, 6, skill_mod=-6),
            InjuryTemplate("Smoke Cough", InjuryType.FIRE, InjurySeverity.MINOR, 3, 7, vitality_mod=-6),
            InjuryTemplate("Scalded Wrist", InjuryType.FIRE, InjurySeverity.MINOR, 3, 6, skill_mod=-5),
            InjuryTemplate("Blistered Forearm", InjuryType.FIRE, InjurySeverity.MINOR, 4, 8, might_mod=-4, skill_mod=-4),
            InjuryTemplate("Ash-Choked Breath", InjuryType.FIRE, InjurySeverity.MINOR, 3, 6, vitality_mod=-5),
        ],
        InjurySeverity.MAJOR: [
            InjuryTemplate("Severe Burns", InjuryType.FIRE, InjurySeverity.MAJOR, 14, 26, vitality_mod=-24, courage_mod=-8, can_deploy_while_injured=False),
            InjuryTemplate("Smoke-Choked Lungs", InjuryType.FIRE, InjurySeverity.MAJOR, 12, 24, vitality_mod=-24, can_deploy_while_injured=False),
            InjuryTemplate("Flayed by Flame", InjuryType.FIRE, InjurySeverity.MAJOR, 16, 30, vitality_mod=-30, courage_mod=-6, can_deploy_while_injured=False),
            
            InjuryTemplate("Smoke-Blinded Eyes", InjuryType.FIRE, InjurySeverity.MAJOR, 10, 18, skill_mod=-12),
        ],
        InjurySeverity.PERMANENT: [
            InjuryTemplate("Burn-Scarred Face", InjuryType.FIRE, InjurySeverity.PERMANENT, 14, 24, permanent=True, leadership_mod=-3, courage_mod=3, possible_titles=["Flame-Kissed"]),
            InjuryTemplate("Charred Hand", InjuryType.FIRE, InjurySeverity.PERMANENT, 18, 32, permanent=True, skill_mod=-14, possible_titles=["Black-Hand"], can_deploy_while_injured=False),
            InjuryTemplate("Flame-Scarred Skin", InjuryType.FIRE, InjurySeverity.PERMANENT, 18, 32, permanent=True, leadership_mod=-4, courage_mod=3, possible_titles=["Burn-Face"], can_deploy_while_injured=False),
            InjuryTemplate("Charred Eye", InjuryType.FIRE, InjurySeverity.PERMANENT, 16, 28, permanent=True, skill_mod=-10, possible_titles=["Ash-Eye"]),
            InjuryTemplate("Smoke-Damaged Lungs", InjuryType.FIRE, InjurySeverity.PERMANENT, 20, 36, permanent=True, vitality_mod=-20, can_deploy_while_injured=False),
            InjuryTemplate("Burned Lungs", InjuryType.FIRE, InjurySeverity.PERMANENT, 14, 28, vitality_mod=-28, can_deploy_while_injured=False),
        ],
        InjurySeverity.FATAL: [
            InjuryTemplate("Burned in a Collapsed Hall", InjuryType.FIRE, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Choked by Smoke and Flame", InjuryType.FIRE, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Burned Alive", InjuryType.FIRE, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Collapsed with the Burning Roof", InjuryType.FIRE, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Consumed by Flame", InjuryType.FIRE, InjurySeverity.FATAL, fatal=True),
        ],
    },

    InjuryType.CRUSHING: {
        InjurySeverity.SUPERFICIAL: [
            InjuryTemplate("Bruised Shoulder", InjuryType.CRUSHING, InjurySeverity.SUPERFICIAL, 1, 2, might_mod=-1),
            InjuryTemplate("Pinned Fingers", InjuryType.CRUSHING, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-2),
            InjuryTemplate("Banged Knee", InjuryType.CRUSHING, InjurySeverity.SUPERFICIAL, 1, 2, agility_mod=-1),
            InjuryTemplate("Bruised Hand", InjuryType.CRUSHING, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Knocked Breathless", InjuryType.CRUSHING, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-2),
            InjuryTemplate("Stubbed Knee", InjuryType.CRUSHING, InjurySeverity.SUPERFICIAL, 1, 2, agility_mod=-1),
            InjuryTemplate("Jarred Shoulder", InjuryType.CRUSHING, InjurySeverity.SUPERFICIAL, 1, 2, might_mod=-1),
            InjuryTemplate("Flattened Fingernail", InjuryType.CRUSHING, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Bruised Ribs", InjuryType.CRUSHING, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Bumped Head", InjuryType.CRUSHING, InjurySeverity.SUPERFICIAL, 1, 2, cunning_mod=-1),
        ],
        InjurySeverity.MINOR: [
            InjuryTemplate("Crushed Toe", InjuryType.CRUSHING, InjurySeverity.MINOR, 3, 6, agility_mod=-5),
            InjuryTemplate("Smashed Thumb", InjuryType.CRUSHING, InjurySeverity.MINOR, 3, 6, skill_mod=-5),
            InjuryTemplate("Stubbed Foot", InjuryType.CRUSHING, InjurySeverity.MINOR, 2, 5, agility_mod=-3),
            InjuryTemplate("Pinched Hand", InjuryType.CRUSHING, InjurySeverity.MINOR, 2, 5, skill_mod=-4),
            InjuryTemplate("Heavy Bruising", InjuryType.CRUSHING, InjurySeverity.MINOR, 3, 6, vitality_mod=-5),
            InjuryTemplate("Squeezed Wrist", InjuryType.CRUSHING, InjurySeverity.MINOR, 3, 6, skill_mod=-5),
            InjuryTemplate("Cracked Knuckles", InjuryType.CRUSHING, InjurySeverity.MINOR, 3, 6, skill_mod=-5),
            InjuryTemplate("Bruised Sternum", InjuryType.CRUSHING, InjurySeverity.MINOR, 3, 7, vitality_mod=-6),
            InjuryTemplate("Jammed Shoulder", InjuryType.CRUSHING, InjurySeverity.MINOR, 4, 8, might_mod=-6),
            InjuryTemplate("Smashed Knee", InjuryType.CRUSHING, InjurySeverity.MINOR, 4, 8, agility_mod=-6),
        ],
        InjurySeverity.MAJOR: [
            InjuryTemplate("Broken Ribs", InjuryType.CRUSHING, InjurySeverity.MAJOR, 12, 22, vitality_mod=-22, can_deploy_while_injured=False),
            InjuryTemplate("Crushed Shoulder", InjuryType.CRUSHING, InjurySeverity.MAJOR, 12, 24, might_mod=-22, skill_mod=-12, can_deploy_while_injured=False),
            InjuryTemplate("Badly Bruised Hip", InjuryType.CRUSHING, InjurySeverity.MAJOR, 10, 18, agility_mod=-18, vitality_mod=-8, can_deploy_while_injured=False),
            InjuryTemplate("Smashed Forearm", InjuryType.CRUSHING, InjurySeverity.MAJOR, 12, 24, might_mod=-18, skill_mod=-16, can_deploy_while_injured=False),
            InjuryTemplate("Pinned Under Timber", InjuryType.CRUSHING, InjurySeverity.MAJOR, 14, 28, vitality_mod=-26, might_mod=-10, can_deploy_while_injured=False),
        ],
        InjurySeverity.PERMANENT: [
            InjuryTemplate("Crushed Foot", InjuryType.CRUSHING, InjurySeverity.PERMANENT, 18, 32, permanent=True, agility_mod=-18, possible_titles=["Iron-Foot"], can_deploy_while_injured=False),
            InjuryTemplate("Flattened Hand", InjuryType.CRUSHING, InjurySeverity.PERMANENT, 18, 32, permanent=True, skill_mod=-15, possible_titles=["Flat-Hand"], can_deploy_while_injured=False),
            InjuryTemplate("Ruined Hip", InjuryType.CRUSHING, InjurySeverity.PERMANENT, 20, 36, permanent=True, agility_mod=-18, vitality_mod=-4, possible_titles=["the Limping"], can_deploy_while_injured=False),
            InjuryTemplate("Caved-In Ribs", InjuryType.CRUSHING, InjurySeverity.PERMANENT, 20, 36, permanent=True, vitality_mod=-16, possible_titles=["Hollow-Chest"], can_deploy_while_injured=False),
            InjuryTemplate("Crushed Hand", InjuryType.CRUSHING, InjurySeverity.PERMANENT, 18, 32, permanent=True, skill_mod=-18, possible_titles=["Stone-Hand"], can_deploy_while_injured=False),
            InjuryTemplate("Crushed Hip", InjuryType.CRUSHING, InjurySeverity.PERMANENT, 16, 30, agility_mod=-28, vitality_mod=-8, possible_titles=["the Limping"], can_deploy_while_injured=False),
        ],
        InjurySeverity.FATAL: [
            InjuryTemplate("Crushed Beneath Timber", InjuryType.CRUSHING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Pinned Under Stone", InjuryType.CRUSHING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Chest Crushed Flat", InjuryType.CRUSHING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Buried Under Collapse", InjuryType.CRUSHING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Skull Crushed by Falling Debris", InjuryType.CRUSHING, InjurySeverity.FATAL, fatal=True),
        ],
    },

    InjuryType.COLD: {
        InjurySeverity.SUPERFICIAL: [
            InjuryTemplate("Frost-Nipped Cheeks", InjuryType.COLD, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Numb Fingers", InjuryType.COLD, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-2),
            InjuryTemplate("Chapped Hands", InjuryType.COLD, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Cold-Stung Ears", InjuryType.COLD, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
            InjuryTemplate("Shivering Fit", InjuryType.COLD, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-2),
            InjuryTemplate("Ice-Burned Lips", InjuryType.COLD, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
            InjuryTemplate("Stiff Neck from Cold", InjuryType.COLD, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Cold-Sore Hands", InjuryType.COLD, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Watery Eyes", InjuryType.COLD, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Frozen Beard Clumps", InjuryType.COLD, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
        ],
        InjurySeverity.MINOR: [
            InjuryTemplate("Mild Frostbite", InjuryType.COLD, InjurySeverity.MINOR, 3, 7, vitality_mod=-6),
            InjuryTemplate("Frozen Feet", InjuryType.COLD, InjurySeverity.MINOR, 4, 8, agility_mod=-7),
            InjuryTemplate("Numb Toes", InjuryType.COLD, InjurySeverity.MINOR, 3, 6, agility_mod=-4),
            InjuryTemplate("Winter Cough", InjuryType.COLD, InjurySeverity.MINOR, 3, 7, vitality_mod=-6),
            InjuryTemplate("Stiff Fingers", InjuryType.COLD, InjurySeverity.MINOR, 3, 6, skill_mod=-5),
            InjuryTemplate("Numb Hands", InjuryType.COLD, InjurySeverity.MINOR, 3, 6, skill_mod=-5),
            InjuryTemplate("Cold-Swollen Feet", InjuryType.COLD, InjurySeverity.MINOR, 4, 8, agility_mod=-6),
            InjuryTemplate("Hard Shivers", InjuryType.COLD, InjurySeverity.MINOR, 3, 6, vitality_mod=-5),
            InjuryTemplate("Cold-Stiff Back", InjuryType.COLD, InjurySeverity.MINOR, 4, 8, might_mod=-4, agility_mod=-3),
            InjuryTemplate("Frostbitten Ear", InjuryType.COLD, InjurySeverity.MINOR, 3, 6, leadership_mod=-3),
        ],
        InjurySeverity.MAJOR: [
            InjuryTemplate("Frozen Chest", InjuryType.COLD, InjurySeverity.MAJOR, 10, 20, vitality_mod=-22, can_deploy_while_injured=False),
            InjuryTemplate("Snow-Blindness", InjuryType.COLD, InjurySeverity.MAJOR, 8, 16, skill_mod=-10),
            InjuryTemplate("Half-Frozen Hands", InjuryType.COLD, InjurySeverity.MAJOR, 10, 20, skill_mod=-16, might_mod=-6, can_deploy_while_injured=False),
            InjuryTemplate("Winter Fever", InjuryType.COLD, InjurySeverity.MAJOR, 8, 16, vitality_mod=-20, might_mod=-6, can_deploy_while_injured=False),            
            InjuryTemplate("Winter Lung", InjuryType.COLD, InjurySeverity.MAJOR, 14, 28, vitality_mod=-28, can_deploy_while_injured=False),            
        ],
        InjurySeverity.PERMANENT: [
            InjuryTemplate("Blackened Fingers", InjuryType.COLD, InjurySeverity.PERMANENT, 16, 28, permanent=True, skill_mod=-12, possible_titles=["Frost-Bitten"], can_deploy_while_injured=False),
            InjuryTemplate("Cold-Stiffened Leg", InjuryType.COLD, InjurySeverity.PERMANENT, 16, 28, permanent=True, agility_mod=-12, possible_titles=["Ice-Leg"], can_deploy_while_injured=False),
            InjuryTemplate("Missing Toes", InjuryType.COLD, InjurySeverity.PERMANENT, 18, 32, permanent=True, agility_mod=-12, possible_titles=["Frost-Toes"], can_deploy_while_injured=False),
            InjuryTemplate("White-Fingered", InjuryType.COLD, InjurySeverity.PERMANENT, 16, 28, permanent=True, skill_mod=-10, possible_titles=["White-Hand"], can_deploy_while_injured=False),
            InjuryTemplate("Winter-Shaken", InjuryType.COLD, InjurySeverity.PERMANENT, 16, 30, permanent=True, vitality_mod=-10, possible_titles=["Winter-Shaken"], can_deploy_while_injured=False),
            InjuryTemplate("Deep Frostbite", InjuryType.COLD, InjurySeverity.PERMANENT, 12, 24, permanent=True, vitality_mod=-18, agility_mod=-16, possible_titles=["Ice-Born", "Frost-Bitten"], can_deploy_while_injured=False),
            InjuryTemplate("Half-Frozen Limbs", InjuryType.COLD, InjurySeverity.PERMANENT, 14, 28, permanent=True, agility_mod=-24, skill_mod=-8, can_deploy_while_injured=False),
            InjuryTemplate("Ice-Cracked Feet", InjuryType.COLD, InjurySeverity.PERMANENT, 12, 24, permanent=True, agility_mod=-22, possible_titles=["Cold-Foot"], can_deploy_while_injured=False),
        ],
        InjurySeverity.FATAL: [
            InjuryTemplate("Frozen in the Night", InjuryType.COLD, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Claimed by Winter", InjuryType.COLD, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Frozen Solid", InjuryType.COLD, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Buried by Snow", InjuryType.COLD, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Died of Exposure", InjuryType.COLD, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Slept Beneath the Snow", InjuryType.COLD, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Heart Stilled by Frost", InjuryType.COLD, InjurySeverity.FATAL, fatal=True),
        ],
    },

    InjuryType.HUNTING: {
        InjurySeverity.SUPERFICIAL: [
            InjuryTemplate("Thorn Scratches", InjuryType.HUNTING, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Animal Bite Scrape", InjuryType.HUNTING, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Branch-Slashed Face", InjuryType.HUNTING, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
            InjuryTemplate("Briar Cuts", InjuryType.HUNTING, InjurySeverity.SUPERFICIAL, 1, 2, agility_mod=-1),
            InjuryTemplate("Animal Claw Mark", InjuryType.HUNTING, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-2),
            InjuryTemplate("Scratched by Bramble", InjuryType.HUNTING, InjurySeverity.SUPERFICIAL, 1, 2, agility_mod=-1),
            InjuryTemplate("Clawed Forearm", InjuryType.HUNTING, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Bitten Calf", InjuryType.HUNTING, InjurySeverity.SUPERFICIAL, 1, 2, agility_mod=-1),
            InjuryTemplate("Thorn in Palm", InjuryType.HUNTING, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Bruised by Antlers", InjuryType.HUNTING, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
        ],
        InjurySeverity.MINOR: [
            InjuryTemplate("Twisted Ankle", InjuryType.HUNTING, InjurySeverity.MINOR, 3, 7, agility_mod=-6),
            InjuryTemplate("Boar Tusk Graze", InjuryType.HUNTING, InjurySeverity.MINOR, 4, 8, vitality_mod=-6),
            InjuryTemplate("Bitten Hand", InjuryType.HUNTING, InjurySeverity.MINOR, 3, 6, skill_mod=-5),
            InjuryTemplate("Hunter's Strain", InjuryType.HUNTING, InjurySeverity.MINOR, 3, 6, vitality_mod=-4),
            InjuryTemplate("Slipped on Wet Leaves", InjuryType.HUNTING, InjurySeverity.MINOR, 3, 6, agility_mod=-5),
            InjuryTemplate("Wolf Bite", InjuryType.HUNTING, InjurySeverity.MINOR, 4, 8, vitality_mod=-6),
            InjuryTemplate("Boar-Torn Calf", InjuryType.HUNTING, InjurySeverity.MINOR, 4, 8, agility_mod=-6),
            InjuryTemplate("Clawed Hand", InjuryType.HUNTING, InjurySeverity.MINOR, 3, 6, skill_mod=-5),
            InjuryTemplate("Antler Bruise", InjuryType.HUNTING, InjurySeverity.MINOR, 3, 7, vitality_mod=-5),
            InjuryTemplate("Bad Fall in Brush", InjuryType.HUNTING, InjurySeverity.MINOR, 3, 6, agility_mod=-5),
        ],
        InjurySeverity.MAJOR: [
            InjuryTemplate("Gored by Boar", InjuryType.HUNTING, InjurySeverity.MAJOR, 12, 24, vitality_mod=-22, agility_mod=-10, can_deploy_while_injured=False),
            InjuryTemplate("Mauled by Wolves", InjuryType.HUNTING, InjurySeverity.MAJOR, 12, 24, vitality_mod=-22, courage_mod=-8, can_deploy_while_injured=False),
            InjuryTemplate("Bear-Clawed Chest", InjuryType.HUNTING, InjurySeverity.MAJOR, 14, 28, vitality_mod=-26, courage_mod=-6, can_deploy_while_injured=False),
            InjuryTemplate("Antler-Cracked Ribs", InjuryType.HUNTING, InjurySeverity.MAJOR, 10, 20, vitality_mod=-18, agility_mod=-6),
            InjuryTemplate("Torn by Boar Tusks", InjuryType.HUNTING, InjurySeverity.MAJOR, 14, 26, vitality_mod=-24, can_deploy_while_injured=False),
        ],
        InjurySeverity.PERMANENT: [
            InjuryTemplate("Lame from the Hunt", InjuryType.HUNTING, InjurySeverity.PERMANENT, 18, 32, permanent=True, agility_mod=-14, possible_titles=["the Lame"], can_deploy_while_injured=False),
            InjuryTemplate("Wolf-Scarred", InjuryType.HUNTING, InjurySeverity.PERMANENT, 14, 26, permanent=True, courage_mod=3, leadership_mod=-2, possible_titles=["Wolf-Bitten"]),
            InjuryTemplate("Bear-Maimed", InjuryType.HUNTING, InjurySeverity.PERMANENT, 18, 32, permanent=True, vitality_mod=-10, courage_mod=3, possible_titles=["Bear-Kissed"], can_deploy_while_injured=False),
            InjuryTemplate("Boar-Torn Leg", InjuryType.HUNTING, InjurySeverity.PERMANENT, 18, 32, permanent=True, agility_mod=-14, possible_titles=["Boar-Torn"], can_deploy_while_injured=False),
            InjuryTemplate("Clawed Face", InjuryType.HUNTING, InjurySeverity.PERMANENT, 12, 22, permanent=True, leadership_mod=-3, courage_mod=2, possible_titles=["Claw-Face"]),
        ],
        InjurySeverity.FATAL: [
            InjuryTemplate("Killed by a Boar", InjuryType.HUNTING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Taken by Wolves", InjuryType.HUNTING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Mauled by a Bear", InjuryType.HUNTING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Gored Through the Belly", InjuryType.HUNTING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Lost in the Winter Woods", InjuryType.HUNTING, InjurySeverity.FATAL, fatal=True),
        ],
    },

    InjuryType.FALLING: {
        InjurySeverity.SUPERFICIAL: [
            InjuryTemplate("Scraped Palms", InjuryType.FALLING, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Bruised Hip", InjuryType.FALLING, InjurySeverity.SUPERFICIAL, 1, 2, agility_mod=-1),
            InjuryTemplate("Skinned Knee", InjuryType.FALLING, InjurySeverity.SUPERFICIAL, 1, 2, agility_mod=-1),
            InjuryTemplate("Scraped Elbow", InjuryType.FALLING, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Bruised Tailbone", InjuryType.FALLING, InjurySeverity.SUPERFICIAL, 1, 2, agility_mod=-2),
            InjuryTemplate("Scuffed Chin", InjuryType.FALLING, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
            InjuryTemplate("Bruised Shoulder", InjuryType.FALLING, InjurySeverity.SUPERFICIAL, 1, 2, might_mod=-1),
            InjuryTemplate("Twisted Landing", InjuryType.FALLING, InjurySeverity.SUPERFICIAL, 1, 2, agility_mod=-1),
            InjuryTemplate("Scraped Knuckles", InjuryType.FALLING, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Bumped Head", InjuryType.FALLING, InjurySeverity.SUPERFICIAL, 1, 2, cunning_mod=-1),
        ],
        InjurySeverity.MINOR: [
            InjuryTemplate("Sprained Ankle", InjuryType.FALLING, InjurySeverity.MINOR, 3, 7, agility_mod=-6),
            InjuryTemplate("Wrenched Shoulder", InjuryType.FALLING, InjurySeverity.MINOR, 4, 8, might_mod=-5, skill_mod=-3),
            InjuryTemplate("Rolled Ankle", InjuryType.FALLING, InjurySeverity.MINOR, 3, 6, agility_mod=-5),
            InjuryTemplate("Jarred Back", InjuryType.FALLING, InjurySeverity.MINOR, 4, 8, might_mod=-5, agility_mod=-3),
            InjuryTemplate("Hard Landing", InjuryType.FALLING, InjurySeverity.MINOR, 3, 6, vitality_mod=-5),
            InjuryTemplate("Bruised Ribs from Fall", InjuryType.FALLING, InjurySeverity.MINOR, 3, 7, vitality_mod=-6),
            InjuryTemplate("Twisted Hip", InjuryType.FALLING, InjurySeverity.MINOR, 4, 8, agility_mod=-6),
            InjuryTemplate("Sprained Wrist", InjuryType.FALLING, InjurySeverity.MINOR, 3, 6, skill_mod=-5),
            InjuryTemplate("Strained Shoulder", InjuryType.FALLING, InjurySeverity.MINOR, 4, 8, might_mod=-5),
            InjuryTemplate("Knocked Senseless", InjuryType.FALLING, InjurySeverity.MINOR, 3, 6, cunning_mod=-4),
        ],
        InjurySeverity.MAJOR: [
            InjuryTemplate("Broken Collarbone", InjuryType.FALLING, InjurySeverity.MAJOR, 10, 20, might_mod=-18, skill_mod=-12, can_deploy_while_injured=False),
            InjuryTemplate("Broken Ribs from a Fall", InjuryType.FALLING, InjurySeverity.MAJOR, 10, 20, vitality_mod=-18, can_deploy_while_injured=False),
            InjuryTemplate("Dislocated Hip", InjuryType.FALLING, InjurySeverity.MAJOR, 12, 24, agility_mod=-20, can_deploy_while_injured=False),
            InjuryTemplate("Cracked Skull", InjuryType.FALLING, InjurySeverity.MAJOR, 12, 24, vitality_mod=-18, cunning_mod=-8, can_deploy_while_injured=False),
            InjuryTemplate("Broken Wrist", InjuryType.FALLING, InjurySeverity.MAJOR, 10, 20, skill_mod=-18, might_mod=-8, can_deploy_while_injured=False),
            InjuryTemplate("Shattered Ankle", InjuryType.FALLING, InjurySeverity.MAJOR, 12, 24, agility_mod=-22, can_deploy_while_injured=False),
        ],
        InjurySeverity.PERMANENT: [
            InjuryTemplate("Crooked Back", InjuryType.FALLING, InjurySeverity.PERMANENT, 18, 32, permanent=True, might_mod=-10, agility_mod=-10, possible_titles=["Crooked-Back"], can_deploy_while_injured=False),
            InjuryTemplate("Ruined Knee", InjuryType.FALLING, InjurySeverity.PERMANENT, 20, 36, permanent=True, agility_mod=-16, possible_titles=["the Limping"], can_deploy_while_injured=False),
            InjuryTemplate("Badly Set Wrist", InjuryType.FALLING, InjurySeverity.PERMANENT, 14, 26, permanent=True, skill_mod=-10, possible_titles=["Crooked-Hand"]),
            InjuryTemplate("Old Head Wound", InjuryType.FALLING, InjurySeverity.PERMANENT, 16, 28, permanent=True, cunning_mod=-8, possible_titles=["Crack-Skull"]),
            InjuryTemplate("Shortened Leg", InjuryType.FALLING, InjurySeverity.PERMANENT, 20, 36, permanent=True, agility_mod=-14, possible_titles=["Short-Leg"], can_deploy_while_injured=False),
            InjuryTemplate("Broken Hip", InjuryType.FALLING, InjurySeverity.PERMANENT, 18, 34, permanent=True, agility_mod=-32, vitality_mod=-10, can_deploy_while_injured=False),
            InjuryTemplate("Shattered Knee", InjuryType.FALLING, InjurySeverity.PERMANENT, 18, 32, permanent=True, agility_mod=-34, can_deploy_while_injured=False),
        ],
        InjurySeverity.FATAL: [
            InjuryTemplate("Fell to Their Death", InjuryType.FALLING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Neck Broken in the Fall", InjuryType.FALLING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Skull Split on Stone", InjuryType.FALLING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Vanished Over the Cliff", InjuryType.FALLING, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Impaled After the Fall", InjuryType.FALLING, InjurySeverity.FATAL, fatal=True),
        ],
    },

    InjuryType.SICKNESS: {
        InjurySeverity.SUPERFICIAL: [
            InjuryTemplate("Sour Stomach", InjuryType.SICKNESS, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Camp Fever", InjuryType.SICKNESS, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-2),
            InjuryTemplate("Queasy Stomach", InjuryType.SICKNESS, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Light Cough", InjuryType.SICKNESS, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Sleepless Fever", InjuryType.SICKNESS, InjurySeverity.SUPERFICIAL, 1, 2, cunning_mod=-1),
            InjuryTemplate("Runny Nose", InjuryType.SICKNESS, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Dizzy Spell", InjuryType.SICKNESS, InjurySeverity.SUPERFICIAL, 1, 2, cunning_mod=-1),
            InjuryTemplate("Sore Throat", InjuryType.SICKNESS, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
            InjuryTemplate("Weak Appetite", InjuryType.SICKNESS, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Sweating Fit", InjuryType.SICKNESS, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-2),
        ],
        InjurySeverity.MINOR: [
            InjuryTemplate("Bad Fever", InjuryType.SICKNESS, InjurySeverity.MINOR, 3, 7, vitality_mod=-6),
            InjuryTemplate("Gut Sickness", InjuryType.SICKNESS, InjurySeverity.MINOR, 3, 7, vitality_mod=-6),
            InjuryTemplate("Chills and Sweats", InjuryType.SICKNESS, InjurySeverity.MINOR, 3, 6, vitality_mod=-5),
            InjuryTemplate("Foul Gut", InjuryType.SICKNESS, InjurySeverity.MINOR, 3, 6, vitality_mod=-5),
            InjuryTemplate("Weakness After Fever", InjuryType.SICKNESS, InjurySeverity.MINOR, 4, 8, might_mod=-4, vitality_mod=-5),
            InjuryTemplate("Fever Shakes", InjuryType.SICKNESS, InjurySeverity.MINOR, 3, 7, vitality_mod=-6),
            InjuryTemplate("Sickbed Weakness", InjuryType.SICKNESS, InjurySeverity.MINOR, 4, 8, might_mod=-5, vitality_mod=-4),
            InjuryTemplate("Clouded Thoughts", InjuryType.SICKNESS, InjurySeverity.MINOR, 3, 6, cunning_mod=-5),
            InjuryTemplate("Racking Cough", InjuryType.SICKNESS, InjurySeverity.MINOR, 3, 7, vitality_mod=-6),
            InjuryTemplate("Unsteady Hands", InjuryType.SICKNESS, InjurySeverity.MINOR, 3, 6, skill_mod=-5),
        ],
        InjurySeverity.MAJOR: [
            InjuryTemplate("Wasting Fever", InjuryType.SICKNESS, InjurySeverity.MAJOR, 10, 20, vitality_mod=-26, might_mod=-10, can_deploy_while_injured=False),
            InjuryTemplate("Rotten Wound Fever", InjuryType.SICKNESS, InjurySeverity.MAJOR, 10, 22, vitality_mod=-28, can_deploy_while_injured=False),
            InjuryTemplate("Blood Fever", InjuryType.SICKNESS, InjurySeverity.MAJOR, 12, 24, vitality_mod=-30, courage_mod=-6, can_deploy_while_injured=False),
            InjuryTemplate("Shaking Fever", InjuryType.SICKNESS, InjurySeverity.MAJOR, 10, 20, vitality_mod=-22, skill_mod=-10, can_deploy_while_injured=False),
            InjuryTemplate("Lung Sickness", InjuryType.SICKNESS, InjurySeverity.MAJOR, 12, 24, vitality_mod=-28, can_deploy_while_injured=False),
        ],
        InjurySeverity.PERMANENT: [
            InjuryTemplate("Lingering Weakness", InjuryType.SICKNESS, InjurySeverity.PERMANENT, 16, 28, permanent=True, vitality_mod=-12, possible_titles=["the Pale"], can_deploy_while_injured=False),
            InjuryTemplate("Tremors", InjuryType.SICKNESS, InjurySeverity.PERMANENT, 14, 24, permanent=True, skill_mod=-10, possible_titles=["Shaking-Hand"]),
            InjuryTemplate("Fever-Clouded Mind", InjuryType.SICKNESS, InjurySeverity.PERMANENT, 16, 28, permanent=True, cunning_mod=-8, possible_titles=["Fever-Touched"]),
            InjuryTemplate("Sickly Lungs", InjuryType.SICKNESS, InjurySeverity.PERMANENT, 18, 32, permanent=True, vitality_mod=-14, possible_titles=["Thin-Breath"], can_deploy_while_injured=False),
            InjuryTemplate("Withered Frame", InjuryType.SICKNESS, InjurySeverity.PERMANENT, 18, 32, permanent=True, might_mod=-10, vitality_mod=-8, possible_titles=["the Withered"], can_deploy_while_injured=False),
        ],
        InjurySeverity.FATAL: [
            InjuryTemplate("Taken by Fever", InjuryType.SICKNESS, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Died in the Sick Tent", InjuryType.SICKNESS, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Body Wasted Away", InjuryType.SICKNESS, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Choked on Fevered Breath", InjuryType.SICKNESS, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Never Woke from Fever Dreams", InjuryType.SICKNESS, InjurySeverity.FATAL, fatal=True),
        ],
    },

    InjuryType.ARROW: {
        InjurySeverity.SUPERFICIAL: [
            InjuryTemplate("Arrow Nick", InjuryType.ARROW, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Splinter Cut", InjuryType.ARROW, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Arrow-Fletching Cut", InjuryType.ARROW, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Arrow Scrape", InjuryType.ARROW, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Splintered Shaft Cut", InjuryType.ARROW, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Fletching Rash", InjuryType.ARROW, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Arrow-Split Sleeve Cut", InjuryType.ARROW, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Bowshot Bruise", InjuryType.ARROW, InjurySeverity.SUPERFICIAL, 1, 2, vitality_mod=-1),
            InjuryTemplate("Shaft-Splintered Palm", InjuryType.ARROW, InjurySeverity.SUPERFICIAL, 1, 2, skill_mod=-1),
            InjuryTemplate("Arrow-Scraped Ear", InjuryType.ARROW, InjurySeverity.SUPERFICIAL, 1, 2, leadership_mod=-1),
        ],
        InjurySeverity.MINOR: [
            InjuryTemplate("Arrow Graze", InjuryType.ARROW, InjurySeverity.MINOR, 2, 6, vitality_mod=-4),
            InjuryTemplate("Arrow in the Arm", InjuryType.ARROW, InjurySeverity.MINOR, 3, 7, skill_mod=-6),
            InjuryTemplate("Arrow in the Shoulder", InjuryType.ARROW, InjurySeverity.MINOR, 4, 8, might_mod=-6, skill_mod=-3),
            InjuryTemplate("Arrow in the Calf", InjuryType.ARROW, InjurySeverity.MINOR, 3, 7, agility_mod=-6),
            InjuryTemplate("Barbed Arrow Wound", InjuryType.ARROW, InjurySeverity.MINOR, 4, 8, vitality_mod=-7),
            InjuryTemplate("Arrow in the Forearm", InjuryType.ARROW, InjurySeverity.MINOR, 3, 7, skill_mod=-6),
            InjuryTemplate("Arrow in the Hip", InjuryType.ARROW, InjurySeverity.MINOR, 4, 8, agility_mod=-6),
            InjuryTemplate("Arrow in the Side", InjuryType.ARROW, InjurySeverity.MINOR, 4, 8, vitality_mod=-7),
            InjuryTemplate("Shallow Arrow Wound", InjuryType.ARROW, InjurySeverity.MINOR, 3, 6, vitality_mod=-5),
            InjuryTemplate("Arrow-Torn Hand", InjuryType.ARROW, InjurySeverity.MINOR, 4, 8, skill_mod=-7),
        ],
        InjurySeverity.MAJOR: [
            InjuryTemplate("Arrow Through the Thigh", InjuryType.ARROW, InjurySeverity.MAJOR, 12, 24, agility_mod=-24, vitality_mod=-8, can_deploy_while_injured=False),
            InjuryTemplate("Arrow Under the Ribs", InjuryType.ARROW, InjurySeverity.MAJOR, 12, 24, vitality_mod=-26, can_deploy_while_injured=False),
            InjuryTemplate("Arrow Through the Shoulder", InjuryType.ARROW, InjurySeverity.MAJOR, 12, 24, might_mod=-18, skill_mod=-10, can_deploy_while_injured=False),
            InjuryTemplate("Barbed Arrow in the Side", InjuryType.ARROW, InjurySeverity.MAJOR, 14, 28, vitality_mod=-28, can_deploy_while_injured=False),
            InjuryTemplate("Arrow Through the Hand", InjuryType.ARROW, InjurySeverity.MAJOR, 10, 20, skill_mod=-24, can_deploy_while_injured=False),
        ],
        InjurySeverity.PERMANENT: [
            InjuryTemplate("Lost Eye to an Arrow", InjuryType.ARROW, InjurySeverity.PERMANENT, 16, 28, permanent=True, skill_mod=-12, possible_titles=["One-Eye"], can_deploy_while_injured=False),
            InjuryTemplate("Arrow-Lamed Leg", InjuryType.ARROW, InjurySeverity.PERMANENT, 18, 32, permanent=True, agility_mod=-16, possible_titles=["Arrow-Lamed"], can_deploy_while_injured=False),
            InjuryTemplate("Arrow-Blinded Eye", InjuryType.ARROW, InjurySeverity.PERMANENT, 16, 28, permanent=True, skill_mod=-12, possible_titles=["One-Eye"], can_deploy_while_injured=False),
            InjuryTemplate("Arrow-Stiffened Scar Tissue", InjuryType.ARROW, InjurySeverity.PERMANENT, 14, 26, permanent=True, agility_mod=-10, possible_titles=["Arrow-Scarred"]),
            InjuryTemplate("Arrow-Ruined Shoulder", InjuryType.ARROW, InjurySeverity.PERMANENT, 18, 32, permanent=True, might_mod=-12, skill_mod=-6, possible_titles=["Arrow-Scarred"], can_deploy_while_injured=False),
        ],
        InjurySeverity.FATAL: [
            InjuryTemplate("Arrow Through the Throat", InjuryType.ARROW, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Arrow Through the Heart", InjuryType.ARROW, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Pinned Through the Neck", InjuryType.ARROW, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Arrow Through the Lung", InjuryType.ARROW, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Shot Through the Eye", InjuryType.ARROW, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Feathered Through the Spine", InjuryType.ARROW, InjurySeverity.FATAL, fatal=True),
            InjuryTemplate("Arrow Buried in the Skull", InjuryType.ARROW, InjurySeverity.FATAL, fatal=True),
        ],
    },
}


JOB_INJURY_TYPES: dict[JobType, list[InjuryType]] = {
    JobType.COASTAL_RAID: [InjuryType.COMBAT, InjuryType.FIRE, InjuryType.GENERIC],
    JobType.RIVER_RAID: [InjuryType.COMBAT, InjuryType.SAILING, InjuryType.GENERIC],
    JobType.MONASTERY_RAID: [InjuryType.COMBAT, InjuryType.FIRE, InjuryType.CRUSHING],
    JobType.TRIBUTE_COLLECTION: [InjuryType.COMBAT, InjuryType.GENERIC],
    JobType.TRADE_VOYAGE: [InjuryType.SAILING, InjuryType.GENERIC],
    JobType.SCOUT_COASTLINE: [InjuryType.SAILING, InjuryType.FALLING, InjuryType.GENERIC],

    JobType.LIVESTOCK_RAID: [InjuryType.COMBAT, InjuryType.CRUSHING, InjuryType.GENERIC],
    JobType.THRALL_RAID: [InjuryType.COMBAT, InjuryType.GENERIC],
    JobType.TIMBER_EXPEDITION: [InjuryType.CRUSHING, InjuryType.FALLING, InjuryType.GENERIC],
    JobType.SALVAGE_EXPEDITION: [InjuryType.SAILING, InjuryType.CRUSHING, InjuryType.GENERIC],
    JobType.FISHING_EXPEDITION: [InjuryType.SAILING, InjuryType.COLD, InjuryType.GENERIC],

    JobType.WINTER_HUNT: [InjuryType.HUNTING, InjuryType.COLD, InjuryType.GENERIC],
    JobType.TIMBER_WORK: [InjuryType.CRUSHING, InjuryType.COLD, InjuryType.GENERIC],
    JobType.GUARD_DUTY: [InjuryType.COMBAT, InjuryType.COLD, InjuryType.GENERIC],
    JobType.LOCAL_TRADE: [InjuryType.COLD, InjuryType.SAILING, InjuryType.GENERIC],
}


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def injury_chance_for_viking(job: Job, success: bool) -> int:
    danger = clamp(job.danger, 1, 10)

    success_chance_by_danger = {
        1: 1,
        2: 2,
        3: 3,
        4: 5,
        5: 7,
        6: 10,
        7: 13,
        8: 17,
        9: 21,
        10: 25,
    }

    failure_chance_by_danger = {
        1: 3,
        2: 5,
        3: 8,
        4: 11,
        5: 15,
        6: 19,
        7: 23,
        8: 26,
        9: 28,
        10: 30,
    }

    if success:
        return success_chance_by_danger[danger]

    return failure_chance_by_danger[danger]


def roll_injury_count(job: Job, success: bool, available_count: int) -> int:
    if available_count <= 0:
        return 0

    weights = [80, 17, 3]

    if job.danger >= 5:
        weights = [65, 25, 8, 2]

    if job.danger >= 8:
        weights = [50, 28, 14, 6, 2]

    if not success:
        weights = [45, 30, 15, 7, 3]

    possible_counts = list(range(1, len(weights) + 1))
    count = random.choices(possible_counts, weights=weights, k=1)[0]

    return min(count, available_count)


def choose_injury_type(job: Job) -> InjuryType:
    injury_types = JOB_INJURY_TYPES.get(job.job_type, [InjuryType.GENERIC])

    # Weight first listed type slightly higher because it is the job's main context.
    weights = [3] + [2 for _ in injury_types[1:]]

    return random.choices(injury_types, weights=weights, k=1)[0]


def roll_severity(job: Job, success: bool, injury_type: InjuryType) -> InjurySeverity:
    roll = random.randint(1, 1000)

    fatal_allowed = injury_type not in {
        InjuryType.GENERIC,
    }

    # Low-risk food/work jobs should almost never kill in this first version.
    if job.job_type in {
        JobType.FISHING_EXPEDITION,
        JobType.LOCAL_TRADE,
        JobType.TIMBER_WORK,
    } and job.danger <= 2:
        fatal_allowed = False

    if success:
        superficial_max = 520
        minor_max = 880
        major_max = 975
        permanent_max = 998

        danger_shift = max(0, job.danger - 3) * 24
        fatal_bonus = max(0, job.danger - 5) * 2

        superficial_max -= danger_shift
        minor_max -= danger_shift // 2
        major_max -= danger_shift // 4
        permanent_max -= fatal_bonus

    else:
        superficial_max = 300
        minor_max = 700
        major_max = 930
        permanent_max = 990

        danger_shift = max(0, job.danger - 3) * 40
        major_push = max(0, job.danger - 5) * 28
        fatal_bonus = max(0, job.danger - 5) * 3

        superficial_max -= danger_shift
        minor_max -= danger_shift + major_push
        major_max -= danger_shift // 3
        permanent_max -= fatal_bonus

    if roll <= superficial_max:
        return InjurySeverity.SUPERFICIAL

    if roll <= minor_max:
        return InjurySeverity.MINOR

    if roll <= major_max:
        return InjurySeverity.MAJOR

    if roll <= permanent_max or not fatal_allowed:
        return InjurySeverity.PERMANENT

    return InjurySeverity.FATAL


def get_templates(injury_type: InjuryType, severity: InjurySeverity) -> list[InjuryTemplate]:
    by_type = INJURY_TABLES.get(injury_type, {})
    templates = by_type.get(severity, [])

    if templates:
        return templates

    return INJURY_TABLES[InjuryType.GENERIC][severity]

def apply_stat_modifiers(viking: Viking, injury: InjuryTemplate) -> None:
    for stat_name, modifier in {
        "might": injury.might_mod,
        "skill": injury.skill_mod,
        "cunning": injury.cunning_mod,
        "leadership": injury.leadership_mod,
        "courage": injury.courage_mod,
        "vitality": injury.vitality_mod,
        "agility": injury.agility_mod,
        "seamanship": injury.seamanship_mod,
    }.items():
        if modifier == 0:
            continue

        current = getattr(viking, stat_name)
        setattr(viking, stat_name, clamp(current + modifier, 1, 100))
        
def viking_has_earned_title(viking: Viking) -> bool:
    return any(trait == "Earned Title" for trait in viking.traits)


def base_name_without_title(name: str) -> str:
    parts = name.split()

    if not parts:
        return name

    # Preserve "Jarl Bryce" style names unless a third word exists.
    if parts[0] == "Jarl":
        if len(parts) <= 2:
            return name

        return " ".join(parts[:2])

    # Generated names are usually:
    # "Thoren"
    # "Thoren Oakenshield"
    # "Thoren the Red"
    if len(parts) >= 3 and parts[1] == "the":
        return parts[0]

    if len(parts) >= 2:
        return parts[0]

    return name


def format_title_name(base_name: str, title: str) -> str:
    if title.startswith("the "):
        return f"{base_name} {title}"

    return f"{base_name} {title}"


TITLE_EFFECTS = {
   # "Arrow-Lamed": {"renown": 6, "courage": 5},
    "Arrow-Scarred": {"renown": 6, "courage": 5},
    "Ash-Eye": {"renown": 6, "leadership": 5},
    "Battle-Mad": {"courage": 8, "cunning": -4, "renown": 7},
    "Bear-Kissed": {"renown": 6, "vitality": 7},
    "Bent-Back": {"renown": 5, "courage": 5},
    "Black-Hand": {"renown": 6, "courage": 5},
    "Boar-Torn": {"renown": 6, "courage": 5},
  #  "Broken-Jaw": {"renown": 5, "courage": 5},
    "Burn-Face": {"renown": 6, "courage": 5},
    "Claw-Face": {"renown": 5, "courage": 5},
    "Cloud-Eye": {"renown": 5, "leadership": 5},
    "Crack-Skull": {"renown": 5, "courage": 5},
    "Crooked-Hand": {"renown": 4},
    "Crooked-Nose": {"renown": 4},
  #  "Fever-Touched": {"renown": 5, "cunning": 5},
    "Flame-Kissed": {"courage": 7, "renown": 7},
    # "Flat-Hand": {"renown": 5},
    "Frost-Bitten": {"courage": 5, "renown": 5},
   # "Frost-Toes": {"renown": 5},
   # "Half-Ear": {"renown": 4},
    "Half-Hand": {"renown": 5},
    "Hollow-Chest": {"renown": 5, "courage": 5},
    "Ice-Leg": {"renown": 5, "courage": 4},
    "Iron-Foot": {"renown": 6, "courage": 5},
    "One-Eye": {"leadership": 7, "renown": 8},
    "One-Hand": {"renown": 7, "leadership": 6},
    "Salt-Eye": {"renown": 6, "leadership": 5},
    "Scar-Face": {"courage": 5, "renown": 6},
   # "Shaking-Hand": {"renown": 4},
  #  "Short-Leg": {"renown": 4},
    "Storm-Broken": {"courage": 5, "renown": 6},
  # "Storm-Lamed": {"renown": 6, "courage": 5},
    "Stone-Hand": {"renown": 5},
  #  "the Lame": {"renown": 5, "courage": 5},
  #  "the Limping": {"renown": 5, "courage": 4},
    "the Pale": {"renown": 4, "cunning": 5},
    "the Scarred": {"renown": 5},
    "the Withered": {"renown": 4, "cunning": 4},
  #  "Thin-Breath": {"renown": 4},
    "Wave-Mad": {"renown": 6, "courage": 6, "cunning": -4},
  #  "White-Hand": {"renown": 5},
    "Winter-Shaken": {"renown": 5, "courage": 5},
    "Wolf-Bitten": {"courage": 6, "renown": 6},
}


def maybe_award_injury_title(result, viking: Viking, injury: InjuryTemplate) -> str | None:
    if not injury.possible_titles:
        return None

    if viking_has_earned_title(viking):
        return None

    if random.random() > 0.60:
        return None

    return random.choice(injury.possible_titles)


def apply_title_effects(result, viking: Viking, title: str) -> None:
    effects = TITLE_EFFECTS.get(title, {})

    for stat_name, bonus in effects.items():
        if stat_name == "renown":
            viking.renown += bonus
            continue

        current = getattr(viking, stat_name)
        setattr(viking, stat_name, clamp(current + bonus, 1, 100))

    if effects:
        result.log.append(f"{viking.name}'s title changes their standing: {effects}.")   


def injury_stat_modifiers(injury: InjuryTemplate) -> dict[str, int]:
    modifiers = {}

    for stat_name, modifier in {
        "might": injury.might_mod,
        "skill": injury.skill_mod,
        "cunning": injury.cunning_mod,
        "leadership": injury.leadership_mod,
        "courage": injury.courage_mod,
        "vitality": injury.vitality_mod,
        "agility": injury.agility_mod,
        "seamanship": injury.seamanship_mod,
    }.items():
        if modifier != 0:
            modifiers[stat_name] = modifier

    return modifiers

def record_injury_for_saga(
    result,
    viking: Viking,
    injury: InjuryTemplate,
    job,
    weeks: int = 0,
    converted_from_fatal: bool = False,
) -> None:
    if not hasattr(result, "injury_records"):
        result.injury_records = []

    result.injury_records.append(
        {
            "viking_id": viking.viking_id,
            "viking_name": viking.name,
            "injury_name": injury.name,
            "injury_type": injury.injury_type.value,
            "severity": injury.severity.value,
            "weeks": weeks,
            "fatal": injury.fatal,
            "permanent": injury.permanent or injury.severity == InjurySeverity.PERMANENT,
            "converted_from_fatal": converted_from_fatal,
            "job_name": getattr(job, "name", "an expedition"),
            "job_id": getattr(job, "job_id", None),
        }
    )

def apply_injury_to_viking(
    result,
    viking: Viking,
    injury: InjuryTemplate,
    job: Job,
    witnesses: list[Viking] | None = None,
) -> None:
    # ==================================================
    # BRANCH 1: FATAL INJURY
    # ==================================================
    if injury.fatal:
        # ----------------------------------------------
        # BRANCH 1A: Fatal injury hits the player/Jarl
        # ----------------------------------------------
        if viking.is_player:
            fallback_templates = get_templates(
                injury.injury_type,
                InjurySeverity.PERMANENT,
            )
            fallback = random.choice(fallback_templates)

            viking.suffer_permanent_injury(fallback.name)

            weeks = random.randint(
                fallback.recovery_weeks_min,
                fallback.recovery_weeks_max,
            )

            pending_title = maybe_award_injury_title(result, viking, fallback)

            viking.add_injury(
                injury_name=fallback.name,
                weeks_remaining=weeks,
                stat_modifiers={},
                recovery_started=False,
                can_deploy_while_injured=fallback.can_deploy_while_injured,
                pending_title=pending_title,
            )

            apply_stat_modifiers(viking, fallback)
            
            record_injury_for_saga(
                result=result,
                viking=viking,
                injury=fallback,
                job=job,
                weeks=weeks,
                converted_from_fatal=True,
            )

            result.permanent_injuries.append(viking.name)
            result.log.append(
                f"{viking.name} should have died during {job.name}, "
                f"but fate refuses it. Permanent injury: {fallback.name} "
                f"({weeks} weeks recovery)."
            )
            return

        # ----------------------------------------------
        # BRANCH 1B: Fatal injury hits normal viking
        # ----------------------------------------------
        viking.status = type(viking.status).DEAD
        result.deaths.append(viking.name)
        result.log.append(f"{viking.name} is killed: {injury.name}.")
        record_injury_for_saga(
            result=result,
            viking=viking,
            injury=injury,
            job=job,
            weeks=0,
        )

        # Witnessing a crewmate die can scar the survivors.
        for witness in witnesses or []:
            if witness.viking_id == viking.viking_id:
                continue

            if witness.is_player:
                continue

            if not witness.is_available():
                continue

            if random.randint(1, 100) <= 15:
                condition = roll_psych_condition(
                    PsychType.DEATH,
                    permanent_chance=5,
                )
                result.log.append(apply_psych_condition(witness, condition))

        return

    # ==================================================
    # BRANCH 2: PERMANENT INJURY
    # ==================================================
    if injury.permanent or injury.severity == InjurySeverity.PERMANENT:
        viking.suffer_permanent_injury(injury.name)

        weeks = random.randint(
            injury.recovery_weeks_min,
            injury.recovery_weeks_max,
        )

        pending_title = maybe_award_injury_title(result, viking, injury)

        viking.add_injury(
            injury_name=injury.name,
            weeks_remaining=weeks,
            stat_modifiers={},
            recovery_started=False,
            can_deploy_while_injured=injury.can_deploy_while_injured,
            pending_title=pending_title,
        )

        apply_stat_modifiers(viking, injury)
        
        record_injury_for_saga(
            result=result,
            viking=viking,
            injury=injury,
            job=job,
            weeks=weeks,
        )

        result.permanent_injuries.append(viking.name)
        result.log.append(
            f"{viking.name} suffers a permanent injury: {injury.name} "
            f"({weeks} weeks recovery)."
        )
        return

    # ==================================================
    # BRANCH 3: TEMPORARY INJURY
    # ==================================================
    weeks = 0

    if injury.recovery_weeks_max > 0:
        weeks = random.randint(
            injury.recovery_weeks_min,
            injury.recovery_weeks_max,
        )

    viking.add_injury(
        injury_name=injury.name,
        weeks_remaining=weeks,
        stat_modifiers=injury_stat_modifiers(injury),
        recovery_started=False,
        can_deploy_while_injured=injury.can_deploy_while_injured,
    )

    if injury.severity == InjurySeverity.MAJOR:
        viking.status = type(viking.status).WOUNDED

    result.injuries.append(viking.name)
    
    record_injury_for_saga(
        result=result,
        viking=viking,
        injury=injury,
        job=job,
        weeks=weeks,
    )

    if weeks > 0:
        result.log.append(
            f"{viking.name} suffers {injury.severity.value.lower()} injury: "
            f"{injury.name} ({weeks} weeks recovery)."
        )
    else:
        result.log.append(
            f"{viking.name} suffers {injury.severity.value.lower()} injury: "
            f"{injury.name}."
        )


@dataclass
class EventInjuryContext:
    name: str
    danger: int
    job_type: JobType | None = None


def roll_event_severity(
    danger: int,
    injury_type: InjuryType,
    fatal_allowed: bool = False,
) -> InjurySeverity:
    roll = random.randint(1, 1000)

    danger = clamp(danger, 1, 10)

    superficial_max = 500
    minor_max = 875
    major_max = 980
    permanent_max = 999

    danger_shift = max(0, danger - 3) * 18
    fatal_bonus = max(0, danger - 6) * 2 if fatal_allowed else 0

    superficial_max -= danger_shift
    minor_max -= danger_shift // 2
    major_max -= danger_shift // 4
    permanent_max -= fatal_bonus

    if roll <= superficial_max:
        return InjurySeverity.SUPERFICIAL

    if roll <= minor_max:
        return InjurySeverity.MINOR

    if roll <= major_max:
        return InjurySeverity.MAJOR

    if roll <= permanent_max or not fatal_allowed:
        return InjurySeverity.PERMANENT

    return InjurySeverity.FATAL


def apply_event_injury_risk(
    result,
    vikings: list[Viking],
    event_name: str,
    injury_danger: int,
    injury_types: list[InjuryType],
    chance: int,
    max_injuries: int = 1,
    fatal_allowed: bool = False,
) -> None:
    available = [
        viking for viking in vikings
        if viking.is_available()
    ]

    if not available:
        return

    base_chance = chance
    chance_variation = random.randint(-5, 5)
    adjusted_chance = clamp(base_chance + chance_variation, 1, 95)

    max_injuries = max(1, min(max_injuries, len(available)))

    roll = random.randint(1, 100)

    result.log.append(
        f"[Event Injury Roll] {roll} vs {adjusted_chance}% "
        f"({event_name}, Danger {injury_danger}, "
        f"Base {base_chance}%, Variation {chance_variation:+})."
    )

    if roll > adjusted_chance:
        return

    injury_count = 1

    if max_injuries > 1:
        if random.random() < 0.20:
            injury_count = max_injuries

    injury_count = min(injury_count, len(available))

    injured_vikings = random.sample(
        available,
        k=injury_count,
    )

    for viking in injured_vikings:
        injury_type = random.choice(injury_types)

        severity = roll_event_severity(
            danger=injury_danger,
            injury_type=injury_type,
            fatal_allowed=fatal_allowed,
        )

        severity = maybe_reduce_severity_with_herbalists(
            result=result,
            vikings=vikings,
            injured_viking=viking,
            severity=severity,
        )

        injury = random.choice(get_templates(injury_type, severity))

        context = EventInjuryContext(
            name=event_name,
            danger=injury_danger,
        )

        result.log.append(
            f"[Event Injury Detail] {viking.name}: "
            f"{injury_type.value} / {severity.value}."
        )

        apply_injury_to_viking(result, viking, injury, context, witnesses=vikings)

def apply_job_injury_risk(result, vikings: list[Viking], job: Job) -> None:
    available = [
        viking for viking in vikings
        if viking.is_available()
    ]

    if not available:
        return

    chance = injury_chance_for_viking(job, result.success)

    result.log.append(
        f"[Injury Risk] {chance}% per crew member "
        f"(Danger {job.danger}, {'Success' if result.success else 'Failure'})."
    )

    injured_vikings = []

    for viking in available:
        roll = random.randint(1, 100)

        if roll <= chance:
            injured_vikings.append((viking, roll))

    if not injured_vikings:
        result.log.append("No crew members are injured.")
        return

    result.log.append(f"Injury event: {len(injured_vikings)} crew member(s) affected.")

    for viking, roll in injured_vikings:
        injury_type = choose_injury_type(job)
        severity = roll_severity(job, result.success, injury_type)

        severity = maybe_reduce_severity_with_herbalists(
            result=result,
            vikings=vikings,
            injured_viking=viking,
            severity=severity,
        )

        injury = random.choice(get_templates(injury_type, severity))

        result.log.append(
            f"[Injury Detail] {viking.name}: roll {roll} vs {chance}%, "
            f"{injury_type.value} / {severity.value}."
        )

        apply_injury_to_viking(result, viking, injury, job, witnesses=vikings)