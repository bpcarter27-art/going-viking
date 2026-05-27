# ====================================================
# Imports
# ====================================================

from models import JobType, TravelType

from .generic import *
from .combat import *
from .resources import *
from .specialists import *

from .travel_coastal import *
from .travel_river import *
from .travel_overland import *
from .travel_open_ocean import *
from .travel_deep_sea import *
from .travel_frozen import *

from .scandinavia import *
from .england import *
from .final_scandinavia import *


# ====================================================
# Generic Node Pools
# ====================================================

TRAVEL_EVENTS = [
    event_favorable_winds,
    event_food_spoilage,
    event_find_supplies,
    event_exhausted_oarsmen,
    event_cold_camp_resolve,
    event_captain_sets_pace,
    event_sickness,
]

SOCIAL_EVENTS = [
    event_social_tension,
    event_lucky_omen,
    event_bad_omens,
    event_local_guide,
    event_crew_fear_spreads,
]

RESOURCE_DISCOVERY_EVENTS = [
    event_easy_loot,
    event_hidden_cache,
    event_find_bog_iron,
    event_strip_broken_weapons,
    event_salvage_wreckage,
    event_good_fishing_waters,
    event_smiths_abandoned_cache,
]

VIKING_SPECIFIC_EVENTS = [
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
    event_single_viking_boast,
    event_single_viking_clever_solution,
    event_single_viking_brave_deed,
]

LEADERSHIP_EVENTS = [
    event_rally_the_crew,
    event_settle_shares_dispute,
    event_negotiate_safe_passage,
    event_orderly_retreat,
]

LOYALTY_EVENTS = [
    event_loyalty_under_strain,
    event_refuse_to_abandon_wounded,
]

EARLY_NODE_EVENTS = (
    TRAVEL_EVENTS
    + SOCIAL_EVENTS
    + VIKING_SPECIFIC_EVENTS
)

MID_NODE_EVENTS = (
    TRAVEL_EVENTS
    + SOCIAL_EVENTS
    + RESOURCE_DISCOVERY_EVENTS
    + VIKING_SPECIFIC_EVENTS
    + LEADERSHIP_EVENTS
    + LOYALTY_EVENTS
)

GENERIC_EVENTS = list(dict.fromkeys(EARLY_NODE_EVENTS + MID_NODE_EVENTS))


# ====================================================
# Combat Pools
# ====================================================

COMBAT_CORE_EVENTS = [
    event_ambush,
    event_shield_wall,
    event_duel,
    event_minor_raid,
    event_archer_volley,
    event_chieftain_guard,
    event_orderly_retreat,
    event_capture_thralls,
]

COMBAT_DANGER_EVENTS = [
    event_arrow_storm,
    event_serious_casualty,
    event_deadly_trap,
    event_falling_masonry,
    event_spear_trap,
]

COMBAT_REWARD_EVENTS = [
    event_easy_loot,
    event_hidden_cache,
    event_weapons_cache,
    event_strip_broken_weapons,
]

FIRE_RAID_EVENTS = [
    event_burning_hall,
    event_smoke_choked_raid,
    event_pitch_fire_attack,
]

COMBAT_EVENTS = (
    COMBAT_CORE_EVENTS
    + COMBAT_REWARD_EVENTS
    + FIRE_RAID_EVENTS
)


# ====================================================
# Resource / Job Theme Pools
# ====================================================

LIVESTOCK_EVENTS = [
    event_drive_livestock_home,
    event_ambush,
    event_orderly_retreat,
    event_minor_raid,
]

THRALL_EVENTS = [
    event_capture_thralls,
    event_ambush,
    event_social_tension,
    event_orderly_retreat,
    event_minor_raid,
]

TIMBER_EVENTS = [
    event_haul_ship_timber,
    event_timber_accident,
    event_frozen_trail,
    event_pry_loose_iron_bands,
]

SALVAGE_EVENTS = [
    event_salvage_wreckage,
    event_salvage_iron_fittings,
    event_strip_broken_weapons,
    event_pry_loose_iron_bands,
    event_hidden_reef,
    event_rough_seas,
]

FISHING_EVENTS = [
    event_good_fishing_waters,
    event_rough_seas,
    event_cold_camp_resolve,
]

WINTER_EVENTS = [
    event_winter_hunt,
    event_frozen_trail,
    event_timber_accident,
    event_winter_bandits,
    event_ice_breaks,
    event_haul_ship_timber,
    event_salvage_wreckage,
]

FINE_METAL_EVENTS = [
    event_weapons_cache,
    event_salvage_iron_fittings,
    event_find_bog_iron,
    event_strip_broken_weapons,
    event_smiths_abandoned_cache,
    event_pry_loose_iron_bands,
]


# ====================================================
# Sea / Seamanship Pools
# ====================================================

SEAMANSHIP_EVENTS = [
    event_hard_rowing,
    event_beach_landing,
    event_thread_the_skerries,
    event_reef_escape,
]

SEA_HAZARD_EVENTS = [
    event_rough_seas,
    event_hidden_reef,
    event_storm_front,
    event_lost_in_fog,
    event_river_current,
    event_ship_handling_drill,
]

SEA_RESOURCE_EVENTS = [
    event_salvage_wreckage,
    event_salvage_iron_fittings,
    event_good_fishing_waters,
]

SEA_EVENTS = (
    SEA_HAZARD_EVENTS
    + SEAMANSHIP_EVENTS
    + SEA_RESOURCE_EVENTS
)


# ====================================================
# Travel Type Pools
# ====================================================

TRAVEL_TYPE_EVENTS = {
    TravelType.COASTAL: [
        event_hidden_reef,
        event_beach_landing,
        event_thread_the_skerries,
        event_good_fishing_waters,
        event_seal_rock_harvest,
        event_hidden_fjord_path,
        event_favorable_winds,
        event_ship_handling_drill,
    ],

    TravelType.RIVER: [
        event_river_current,
        event_shallow_river_drag,
        event_riverbank_archers,
        event_muddy_portage,
        event_river_prince_toll,
        event_local_guide,
        event_lost_in_fog,
        event_exhausted_oarsmen,
        event_find_supplies,
    ],

    TravelType.OVERLAND: [
        event_bad_mountain_pass,
        event_forest_path_vanishes,
        event_wary_farmstead_dogs,
        event_farmstead_shelter,
        event_frozen_trail,
        event_sickness,
        event_find_supplies,
        event_local_guide,
        event_cold_camp_resolve,
        event_loyalty_under_strain,
    ],

    TravelType.OPEN_OCEAN: [
        event_open_ocean_storm,
        event_seabirds_seen,
        event_ocean_calm,
        event_oarsmen_collapse,
        event_distant_whale_song,
        event_exhausted_oarsmen,
        event_food_spoilage,
        event_captain_sets_pace,
        event_lost_in_fog,
        event_rough_seas,
    ],

    TravelType.DEEP_SEA: [
        event_storm_front,
        event_rough_seas,
        event_lost_in_fog,
        event_food_spoilage,
        event_exhausted_oarsmen,
        event_crew_fear_spreads,
        event_bad_omens,
        event_cold_camp_resolve,
    ],

    TravelType.FROZEN: [
        event_ice_breaks,
        event_frozen_trail,
        event_cold_camp_resolve,
        event_storm_front,
        event_bad_omens,
        event_winter_hunt,
        event_sickness,
    ],
}


# ====================================================
# Scandinavia Pools
# ====================================================

SCANDINAVIA_LOCAL_EVENTS = [
    event_rival_jarl_scouts,
    event_seal_rock_harvest,
    event_hidden_fjord_path,
    event_farmstead_shelter,
    event_law_speaker_warning,
]

SCANDINAVIA_FEUD_EVENTS = [
    event_feud_challenge_at_dawn,
    event_old_grudge_resurfaces,
    event_oath_ring_dispute,
    event_rival_jarl_scouts,
    event_burning_hall,
    event_duel,
    event_orderly_retreat,
]

SCANDINAVIA_THING_EVENTS = [
    event_law_speaker_warning,
    event_oath_ring_dispute,
    event_old_grudge_resurfaces,
    event_settle_shares_dispute,
    event_duel,
    event_social_tension,
    event_tyr_oath,
]

SCANDINAVIA_HUNT_EVENTS = [
    event_omen_beast_tracks,
    event_winter_hunt,
    event_skadi_huntsman,
    event_farmstead_shelter,
    event_frozen_trail,
    event_lucky_omen,
    event_bad_omens,
]

SCANDINAVIA_ESCORT_EVENTS = [
    event_hidden_fjord_path,
    event_farmstead_shelter,
    event_rival_jarl_scouts,
    event_winter_bandits,
    event_local_guide,
    event_loyalty_under_strain,
]

SCANDINAVIA_OUTLAW_EVENTS = [
    event_outlaw_hidden_camp,
    event_scout_finds_path,
    event_ambush,
    event_deadly_trap,
    event_winter_bandits,
    event_duel,
]

SCANDINAVIA_FUNERAL_EVENTS = [
    event_funeral_omens,
    event_grave_goods_temptation,
    event_lucky_omen,
    event_bad_omens,
    event_refuse_to_abandon_wounded,
    event_social_tension,
]


# ====================================================
# High Danger Pool
# ====================================================

DANGER_EVENTS = [
    event_serious_casualty,
    event_deadly_trap,
    event_falling_masonry,
    event_spear_trap,
    event_arrow_storm,
    event_leap_between_rooftops,
]


# ====================================================
# Location Pools
# ====================================================

LOCATION_EVENTS = {
    "Norway": [
        event_rival_jarl_scouts,
        event_seal_rock_harvest,
        event_hidden_fjord_path,
        event_norway_fjord_echoes,
        event_norway_hard_farmstead,
    ],

    "Denmark": [
        event_law_speaker_warning,
        event_oath_ring_dispute,
        event_denmark_mead_hall_boast,
        event_denmark_cattle_drift,
    ],

    "Swedish Coast": [
        event_funeral_omens,
        event_grave_goods_temptation,
        event_swedish_burial_runes,
        event_swedish_amber_merchant,
    ],

    "Rus' Riverlands": [
        event_rus_market_bargain,
        event_river_prince_toll,
        event_river_current,
        event_weapons_cache,
    ],

    "East Anglia": [
        event_saxon_fyrd_musters,
        event_church_silver_cache,
        event_loot_church_bells,
        event_archer_volley,
        event_smoke_choked_raid,
    ],

    "Northumbria": [
        event_northumbrian_warband,
        event_lindisfarne_pilgrim_rumors,
        event_loot_church_bells,
        event_arrow_storm,
        event_pitch_fire_attack,
    ],
}


def get_location_events(location_name: str) -> list:
    return list(LOCATION_EVENTS.get(location_name, []))


# ====================================================
# Job Type Pools
# ====================================================

JOB_TYPE_EVENTS = {
    # ----------------------------
    # Scandinavia
    # ----------------------------

    JobType.BLOOD_FEUD: (
        SCANDINAVIA_FEUD_EVENTS
        + LOYALTY_EVENTS
    ),

    JobType.THING_GUARD: (
        SCANDINAVIA_THING_EVENTS
        + LEADERSHIP_EVENTS
        + LOYALTY_EVENTS
    ),

    JobType.SACRED_HUNT: (
        SCANDINAVIA_HUNT_EVENTS
        + [
            event_cold_camp_resolve,
            event_find_supplies,
        ]
    ),

    JobType.SETTLER_ESCORT: (
        SCANDINAVIA_ESCORT_EVENTS
        + TRAVEL_EVENTS
        + [
            event_orderly_retreat,
        ]
    ),

    JobType.OATH_COLLECTION: (
        SCANDINAVIA_THING_EVENTS
        + LEADERSHIP_EVENTS
        + [
            event_negotiate_safe_passage,
        ]
    ),

    JobType.OUTLAW_HUNT: (
        SCANDINAVIA_OUTLAW_EVENTS
        + [
            event_orderly_retreat,
            event_weapons_cache,
        ]
    ),

    JobType.FUNERAL_VOYAGE: (
        SCANDINAVIA_FUNERAL_EVENTS
        + TRAVEL_EVENTS
        + LOYALTY_EVENTS
    ),

    # ----------------------------
    # Story / Region Unlocks
    # ----------------------------

    JobType.LINDISFARNE_RAID: (
        [
            event_lindisfarne_pilgrim_rumors,
            event_church_silver_cache,
            event_loot_church_bells,
            event_northumbrian_warband,
            event_saxon_fyrd_musters,
        ]
        + FIRE_RAID_EVENTS
        + COMBAT_REWARD_EVENTS
    ),

    # ----------------------------
    # Spring / Summer
    # ----------------------------

    JobType.COASTAL_RAID: (
        COMBAT_CORE_EVENTS
        + COMBAT_REWARD_EVENTS
    ),

    JobType.RIVER_RAID: (
        COMBAT_CORE_EVENTS
        + SEA_EVENTS
        + COMBAT_REWARD_EVENTS
    ),

    JobType.MONASTERY_RAID: (
        COMBAT_CORE_EVENTS
        + FIRE_RAID_EVENTS
        + COMBAT_REWARD_EVENTS
        + [
            event_church_silver_cache,
            event_loot_church_bells,
        ]
    ),

    JobType.ESCORT_VOYAGE: (
        SEA_EVENTS
        + [
            event_ambush,
            event_archer_volley,
            event_orderly_retreat,
        ]
    ),

    JobType.TRIBUTE_COLLECTION: (
        SOCIAL_EVENTS
        + LEADERSHIP_EVENTS
        + [
            event_easy_loot,
            event_local_guide,
        ]
    ),

    JobType.JOIN_JARL_WARBAND: (
        COMBAT_CORE_EVENTS
        + COMBAT_DANGER_EVENTS
        + COMBAT_REWARD_EVENTS
    ),

    JobType.SCOUT_COASTLINE: (
        SEA_HAZARD_EVENTS
        + SEAMANSHIP_EVENTS
        + [
            event_find_supplies,
            event_local_guide,
            event_rival_jarl_scouts,
        ]
    ),

    JobType.FEUD_ATTACK: (
        COMBAT_CORE_EVENTS
        + COMBAT_DANGER_EVENTS
    ),

    JobType.RESCUE_CAPTIVE: (
        COMBAT_CORE_EVENTS
        + COMBAT_DANGER_EVENTS
        + [
            event_social_tension,
            event_deadly_trap,
        ]
    ),

    JobType.TRADE_VOYAGE: (
        SEA_EVENTS
        + SOCIAL_EVENTS
        + [
            event_rus_market_bargain,
            event_river_prince_toll,
        ]
    ),

    JobType.LIVESTOCK_RAID: LIVESTOCK_EVENTS,

    JobType.THRALL_RAID: (
        THRALL_EVENTS
        + COMBAT_DANGER_EVENTS
    ),

    JobType.TIMBER_EXPEDITION: TIMBER_EVENTS,

    JobType.SALVAGE_EXPEDITION: SALVAGE_EVENTS,

    JobType.FISHING_EXPEDITION: FISHING_EVENTS,

    # ----------------------------
    # Winter
    # ----------------------------

    JobType.WINTER_HUNT: [
        event_winter_hunt,
        event_frozen_trail,
        event_ice_breaks,
        event_skadi_huntsman,
    ],

    JobType.TIMBER_WORK: [
        event_timber_accident,
        event_frozen_trail,
        event_haul_ship_timber,
        event_pry_loose_iron_bands,
    ],

    JobType.GUARD_DUTY: [
        event_winter_bandits,
        event_social_tension,
        event_frozen_trail,
        event_rival_jarl_scouts,
    ],

    JobType.LOCAL_TRADE: [
        event_frozen_trail,
        event_winter_bandits,
        event_local_guide,
        event_rus_market_bargain,
        event_river_prince_toll,
    ],
}


# ====================================================
# Final Node Pools
# ====================================================

JOB_FINAL_EVENTS = {
    JobType.BLOOD_FEUD: [
        event_final_feud_champion,
        event_burning_hall,
        event_feud_challenge_at_dawn,
    ],

    JobType.THING_GUARD: [
        event_final_thing_judgment,
        event_oath_ring_dispute,
    ],

    JobType.SACRED_HUNT: [
        event_final_white_elk,
        event_omen_beast_tracks,
    ],

    JobType.SETTLER_ESCORT: [
        event_farmstead_shelter,
        event_rival_jarl_scouts,
        event_orderly_retreat,
    ],

    JobType.OATH_COLLECTION: [
        event_oath_ring_dispute,
        event_final_thing_judgment,
    ],

    JobType.OUTLAW_HUNT: [
        event_final_outlaw_standoff,
        event_outlaw_hidden_camp,
    ],

    JobType.FUNERAL_VOYAGE: [
        event_final_funeral_pyre_omen,
        event_grave_goods_temptation,
    ],

    JobType.LIVESTOCK_RAID: [
        event_drive_livestock_home,
        event_minor_raid,
    ],

    JobType.TIMBER_EXPEDITION: [
        event_haul_ship_timber,
        event_timber_accident,
    ],

    JobType.SALVAGE_EXPEDITION: [
        event_salvage_wreckage,
        event_salvage_iron_fittings,
    ],

    JobType.FISHING_EXPEDITION: [
        event_good_fishing_waters,
        event_seal_rock_harvest,
    ],
}