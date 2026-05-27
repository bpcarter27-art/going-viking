from .helpers import *

from .pools import (
    COMBAT_EVENTS,
    GENERIC_EVENTS,
    JOB_TYPE_EVENTS,
    JOB_FINAL_EVENTS,
    TRAVEL_TYPE_EVENTS,
    DANGER_EVENTS,
    get_location_events,
)

from models import VikingClass, CrewRole, FavoredGod

from .specialists import (
    event_raider_breach,
    event_sailor_reads_water,
    event_archer_clear_shot,
    event_trickster_false_tracks,
    event_hersir_gives_orders,
    event_shieldmaiden_rally,
    event_herbalist_mends_wounds,
    event_scout_finds_path,

    event_loki_trick,
    event_thor_strength,
    event_odin_omen,
    event_njord_favorable_seas,
    event_tyr_oath,
    event_heimdall_watchfulness,
    event_frigg_protection,
    event_baldr_blessing,
    event_freyja_mercy,
    event_skadi_huntsman,
)

from .generic import event_captain_sets_pace


def event_is_eligible(event, vikings):

    available = [
        viking for viking in vikings
        if viking.is_available()
    ]

    if not available:
        return False

    required_classes = {
        event_raider_breach: VikingClass.RAIDER,
        event_sailor_reads_water: VikingClass.SAILOR,
        event_archer_clear_shot: VikingClass.ARCHER,
        event_trickster_false_tracks: VikingClass.TRICKSTER,
        event_hersir_gives_orders: VikingClass.HERSIR,
        event_shieldmaiden_rally: VikingClass.SHIELDMAIDEN,
        event_herbalist_mends_wounds: VikingClass.HERBALIST,
        event_scout_finds_path: VikingClass.SCOUT,
    }

    required_gods = {
        event_loki_trick: FavoredGod.LOKI,
        event_thor_strength: FavoredGod.THOR,
        event_odin_omen: FavoredGod.ODIN,
        event_njord_favorable_seas: FavoredGod.NJORD,
        event_tyr_oath: FavoredGod.TYR,
        event_heimdall_watchfulness: FavoredGod.HEIMDALL,
        event_frigg_protection: FavoredGod.FRIGG,
        event_baldr_blessing: FavoredGod.BALDR,
        event_freyja_mercy: FavoredGod.FREYJA,
        event_skadi_huntsman: FavoredGod.SKADI,
    }

    required_class = required_classes.get(event)

    if required_class:
        return any(
            viking.viking_class == required_class
            for viking in available
        )

    required_god = required_gods.get(event)

    if required_god:
        return any(
            viking.favored_god == required_god
            for viking in available
        )

    if event == event_captain_sets_pace:
        return any(
            viking.role == CrewRole.CAPTAIN
            for viking in available
        )

    return True