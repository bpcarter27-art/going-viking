from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from models import JobType, TravelType


class LocationRegion(str, Enum):
    SCANDINAVIA = "Scandinavia"
    RUS = "Rus'"
    BRITAIN = "Britain"
    IRELAND = "Ireland"
    FRANKIA = "Frankia"


@dataclass
class JobLocation:
    name: str
    region: LocationRegion
    required_range: int
    job_types: list[JobType]
    travel_type: TravelType = TravelType.COASTAL
    
    difficulty_mod: int = 0
    danger_mod: int = 0
    duration_mod: int = 0
    silver_mod: int = 0

    common_items: list[str] = field(default_factory=list)
    rare_items: list[str] = field(default_factory=list)
    legendary_items: list[str] = field(default_factory=list)

    description: str = ""

LOCATIONS = [

    # ==================================================
    # INTRO — HIGH SEAT
    # ==================================================

    JobLocation(
        name="The High Seat",
        region=LocationRegion.SCANDINAVIA,
        required_range=1,
        travel_type=TravelType.OVERLAND,
        job_types=[
            JobType.TRIAL_BY_COMBAT,
        ],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="The hall where judgment is given, blood is answered, and power changes hands.",
    ),

    # ==================================================
    # RANGE 1 — HOMELAND
    # ==================================================

    JobLocation(
        name="Norway",
        region=LocationRegion.SCANDINAVIA,
        required_range=1,
        travel_type=TravelType.COASTAL,
        difficulty_mod=-1,
        danger_mod=-1,
        job_types=[
        # SPRING/SUMMER JOBS
            JobType.SCOUT_COASTLINE,
            JobType.TRIBUTE_COLLECTION,
            JobType.COASTAL_RAID,
            JobType.LIVESTOCK_RAID,
            JobType.TIMBER_EXPEDITION,
            JobType.FISHING_EXPEDITION,
            JobType.SALVAGE_EXPEDITION,
            
            JobType.BLOOD_FEUD,
            JobType.THING_GUARD,
            JobType.SACRED_HUNT,
            JobType.SETTLER_ESCORT,
            JobType.OATH_COLLECTION,
            JobType.OUTLAW_HUNT,
            JobType.FUNERAL_VOYAGE,
        # WINTER JOBS
            JobType.WINTER_HUNT,
            JobType.TIMBER_WORK,
            JobType.GUARD_DUTY,
            JobType.LOCAL_TRADE,        
        ],
        common_items=[
            "Nordic Axe",
            "Nordic Spear",
            "Nordic Knife",
            "Nordic Shield",
        ],
        rare_items=[
            "Nordic Sword",
            "Nordic Bow",
            "Nordic Armor",
            "Nordic Helm",
            "Carved Amber Icon",
        ],
        legendary_items=[
            "Silver Chalice",
            "Jeweled Carafe",
        ],
        description="The rugged fjords and isolated settlements of Norway, home to rival jarls, timber camps, and hard seafarers.",
    ),
    JobLocation(
        name="Denmark",
        region=LocationRegion.SCANDINAVIA,
        required_range=1,
        travel_type=TravelType.COASTAL,
        difficulty_mod=-1,
        danger_mod=-1,
        duration_mod=0,
        silver_mod=6,
            job_types=[
            JobType.SCOUT_COASTLINE,
            JobType.TRIBUTE_COLLECTION,
            JobType.COASTAL_RAID,
            JobType.LIVESTOCK_RAID,
            JobType.TRADE_VOYAGE,
            JobType.FISHING_EXPEDITION,
            JobType.SALVAGE_EXPEDITION,

            JobType.BLOOD_FEUD,
            JobType.THING_GUARD,
            JobType.OATH_COLLECTION,
            JobType.SETTLER_ESCORT,

            JobType.WINTER_HUNT,
            JobType.GUARD_DUTY,
            JobType.LOCAL_TRADE,
        ],
        common_items=[
            "Dane Axe",
            "Dane Spear",
            "Dane Knife",
            "Dane Shield",
        ],
        rare_items=[
            "Dane Sword",
            "Dane Bow",
            "Dane Armor",
            "Dane Helm",
            "Silver Arm Ring",
        ],
        legendary_items=[
            "Golden Torque",
            "Runed War Banner",
        ],
        description="Rich farmland, crowded halls, and ambitious jarls across the Danish coast.",
    ),
    JobLocation(
        name="Swedish Coast",
        region=LocationRegion.SCANDINAVIA,
        required_range=1,
        travel_type=TravelType.OPEN_OCEAN,
        difficulty_mod=0,
        danger_mod=-1,
        duration_mod=0,
        silver_mod=8,       
        job_types=[
            JobType.SCOUT_COASTLINE,
            JobType.TRADE_VOYAGE,
            JobType.COASTAL_RAID,
            JobType.SALVAGE_EXPEDITION,
            JobType.FISHING_EXPEDITION,

            JobType.THING_GUARD,
            JobType.SETTLER_ESCORT,
            JobType.OUTLAW_HUNT,

            JobType.WINTER_HUNT,
            JobType.LOCAL_TRADE,
        ],
        common_items=[
            "Gotlandish Axe",
            "Gotlandish Spear",
            "Gotlandish Knife",
            "Gotlandish Shield",
        ],
        rare_items=[
            "Gotlandish Sword",
            "Baltic Bow",
            "Merchant Mail",
            "Amber Necklace",
        ],
        legendary_items=[
            "Jeweled Compass",
            "Eastern Silver Hoard",
        ],
        description="The forested eastern shores of Scandinavia, home to traders, burial mounds, and strange old rites.",
    ),
    
    

    # ==================================================
    # RANGE 2 — NEAR SEAS / EASTERN ROUTES
    # ==================================================

    JobLocation(
        name="Rus' Riverlands",
        region=LocationRegion.RUS,
        required_range=2,
        travel_type=TravelType.RIVER,
        job_types=[
        # SPRING/SUMMER JOBS
            JobType.RIVER_RAID,
           # JobType.COASTAL_RAID,
            JobType.TRADE_VOYAGE,
            JobType.LIVESTOCK_RAID,
            JobType.THRALL_RAID,
            JobType.TIMBER_EXPEDITION,
            JobType.SALVAGE_EXPEDITION,
        # WINTER JOBS
            JobType.WINTER_HUNT,
            JobType.GUARD_DUTY,
            JobType.LOCAL_TRADE,        
        ],
        common_items=[
            "Rus' Axe",
            "Rus' Spear",
            "Rus' Knife",
            "Rus' Shield",
        ],
        rare_items=[
            "Rus' Sword",
            "Rus' Bow",
            "Rus' Armor",
            "Rus' Helm",
            "Bolt of Eastern Silk",
        ],
        legendary_items=[
            "Jeweled Carafe",
        ],
        description="River trade routes and wealthy settlements deep inland.",
    ),

    JobLocation(
        name="Baltic Coast",
        region=LocationRegion.RUS,
        required_range=2,
        travel_type=TravelType.OPEN_OCEAN,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="Cold waters, trading posts, rival crews, and coastal tribes.",
    ),

    # ==================================================
    # RANGE 3 — NORTHUMBRIA INTRO
    # ==================================================

    JobLocation(
        name="Lindisfarne",
        region=LocationRegion.BRITAIN,
        required_range=3,
        travel_type=TravelType.OPEN_OCEAN,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="A holy island monastery whose bells and treasures call across the sea.",
    ),

    JobLocation(
        name="Northumbria",
        region=LocationRegion.BRITAIN,
        required_range=3,
        travel_type=TravelType.OPEN_OCEAN,
        job_types=[
            JobType.COASTAL_RAID,
            JobType.MONASTERY_RAID,
            JobType.FEUD_ATTACK,
            JobType.RESCUE_CAPTIVE,
        ],
        common_items=[
            "Northumbrian Axe",
            "Northumbrian Spear",
            "Northumbrian Knife",
            "Northumbrian Shield",
        ],
        rare_items=[
            "Northumbrian Sword",
            "Northumbrian Bow",
            "Northumbrian Armor",
            "Northumbrian Helm",
            "Anglo Silver Cross",
        ],
        legendary_items=[
            "Gilded Book Cover",
            "Monastery Reliquary",
        ],
        description="A dangerous northern kingdom with famous monasteries and hard-fighting defenders.",
    ),

    # ==================================================
    # RANGE 4 — EAST ANGLIA
    # ==================================================

    JobLocation(
        name="East Anglia",
        region=LocationRegion.BRITAIN,
        required_range=4,
        travel_type=TravelType.OPEN_OCEAN,
        job_types=[
            JobType.COASTAL_RAID,
            JobType.MONASTERY_RAID,
            JobType.TRIBUTE_COLLECTION,
            JobType.TRADE_VOYAGE,
        ],
        common_items=[
            "East Anglian Axe",
            "East Anglian Spear",
            "East Anglian Knife",
            "East Anglian Shield",
        ],
        rare_items=[
            "East Anglian Sword",
            "East Anglian Bow",
            "East Anglian Armor",
            "East Anglian Helm",
            "Anglo Silver Cross",
        ],
        legendary_items=[
            "Gilded Book Cover",
            "Monastery Reliquary",
        ],
        description="Rich coastal settlements and vulnerable monasteries across eastern Britain.",
    ),

    # ==================================================
    # RANGE 5 — ANGLO-SAXON KINGDOMS
    # ==================================================

    JobLocation(
        name="Mercia",
        region=LocationRegion.BRITAIN,
        required_range=5,
        travel_type=TravelType.OPEN_OCEAN,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="A powerful inland kingdom of fortified towns, roads, and rival claimants.",
    ),

    JobLocation(
        name="Wessex",
        region=LocationRegion.BRITAIN,
        required_range=5,
        travel_type=TravelType.OPEN_OCEAN,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="A resilient southern kingdom where raiders meet organized resistance.",
    ),

    JobLocation(
        name="The Danelaw",
        region=LocationRegion.BRITAIN,
        required_range=5,
        travel_type=TravelType.OPEN_OCEAN,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="Settled Norse lands in England, full of allies, rivals, markets, and old grudges.",
    ),

    # ==================================================
    # RANGE 6 — FRANCIA
    # ==================================================

    JobLocation(
        name="Frankish Coast",
        region=LocationRegion.FRANKIA,
        required_range=6,
        travel_type=TravelType.OPEN_OCEAN,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="Wealthy coastal lands guarded by watchmen, counts, and fortified churches.",
    ),

    JobLocation(
        name="Seine River",
        region=LocationRegion.FRANKIA,
        required_range=6,
        travel_type=TravelType.RIVER,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="A rich river road leading inland toward monasteries, towns, and Paris itself.",
    ),

    JobLocation(
        name="Paris",
        region=LocationRegion.FRANKIA,
        required_range=6,
        travel_type=TravelType.RIVER,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="A great Frankish prize, rich enough to draw the boldest crews in the north.",
    ),

    # ==================================================
    # RANGE 7 — IRELAND / SCOTLAND
    # ==================================================

    JobLocation(
        name="Ireland",
        region=LocationRegion.IRELAND,
        required_range=7,
        travel_type=TravelType.OPEN_OCEAN,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="Green kingdoms, cattle wealth, monastic treasures, mist, feuds, and hard bargains.",
    ),

    JobLocation(
        name="Dublin",
        region=LocationRegion.IRELAND,
        required_range=7,
        travel_type=TravelType.COASTAL,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="A Norse-Gael trading town where silver, slaves, ships, and politics meet.",
    ),

    JobLocation(
        name="Scotland",
        region=LocationRegion.BRITAIN,
        required_range=7,
        travel_type=TravelType.OPEN_OCEAN,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="Rugged northern lands of islands, raids, storms, clans, and hidden strongholds.",
    ),

    JobLocation(
        name="Orkney",
        region=LocationRegion.BRITAIN,
        required_range=7,
        travel_type=TravelType.OPEN_OCEAN,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="A northern island base between Norway, Scotland, and the western sea.",
    ),

    # ==================================================
    # RANGE 8 — ICELAND
    # ==================================================

    JobLocation(
        name="Iceland",
        region=LocationRegion.SCANDINAVIA,
        required_range=8,
        travel_type=TravelType.DEEP_SEA,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="A harsh island of fire, ice, law-speakers, settlers, and lonely farmsteads.",
    ),

    # ==================================================
    # RANGE 9 — GREENLAND
    # ==================================================

    JobLocation(
        name="Greenland",
        region=LocationRegion.SCANDINAVIA,
        required_range=9,
        travel_type=TravelType.FROZEN,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="A far western land of ice, hunger, hunting, isolation, and stubborn settlers.",
    ),

    # ==================================================
    # RANGE 10 — VINLAND
    # ==================================================

    JobLocation(
        name="Vinland",
        region=LocationRegion.SCANDINAVIA,
        required_range=10,
        travel_type=TravelType.OPEN_OCEAN,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="A strange western shore of timber, grapes, mystery, and impossible signs.",
    ),

    # ==================================================
    # POSTGAME — MYTHIC REALMS
    # ==================================================

    JobLocation(
        name="Jotunheim",
        region=LocationRegion.SCANDINAVIA,
        required_range=10,
        travel_type=TravelType.FROZEN,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="A mythic realm of giants, stone, frost, and ancient grudges.",
    ),

    JobLocation(
        name="Alfheim",
        region=LocationRegion.SCANDINAVIA,
        required_range=10,
        travel_type=TravelType.OPEN_OCEAN,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="A bright and perilous realm of elves, beauty, bargains, and hidden dangers.",
    ),

    JobLocation(
        name="Niflheim",
        region=LocationRegion.SCANDINAVIA,
        required_range=10,
        travel_type=TravelType.FROZEN,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="A frozen realm of mist, silence, deathly cold, and old fear.",
    ),

    JobLocation(
        name="Helheim",
        region=LocationRegion.SCANDINAVIA,
        required_range=10,
        travel_type=TravelType.DEEP_SEA,
        job_types=[],
        common_items=[],
        rare_items=[],
        legendary_items=[],
        description="The shadowed realm of Hel, where the dead keep old secrets.",
    ),
]





def get_locations_for_ship_range(ship_range: int) -> list[JobLocation]:
    return [
        location for location in LOCATIONS
        if location.required_range <= ship_range
    ]