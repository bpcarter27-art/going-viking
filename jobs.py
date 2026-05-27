from __future__ import annotations

import random

from models import Job, JobType, Season, TravelType
from locations import JobLocation


GLOBAL_EQUIPMENT_REWARDS = [
    "Iron Axe",
    "Iron Sword",
    "Iron Spear",
    "Iron Knife",
    "Ash Bow",
    "Leather Armor",
    "Leather Helm",
    "Reinforced Wooden Shield",
]

JOB_TEMPLATES = {
    # Scandinavian Jobs
    JobType.BLOOD_FEUD: {
        "names": [
            "Join a Blood Feud in {location}",
            "Avenge a Slain Kinsman near {location}",
            "Burn a Rival Hall in {location}",
            "Settle a Feud along {location}",
        ],
        "duration": (2, 4),
        "difficulty": (2, 4),
        "danger": (3, 6),
        "silver": (8, 24),
        "food": (0, 6),
        "thralls": (0, 1),
        "ship_timber": (0, 0),
        "fine_metal": (0, 2),
        "renown": (3, 6),
        "min_crew": (5, 7),
        "travel_type": lambda location: random.choice(
            [TravelType.OVERLAND, location.travel_type]
        ),        
        "description": "A local feud between rival kin-groups threatens to spill into open bloodshed.",
    },

    JobType.THING_GUARD: {
        "names": [
            "Guard the Thing at {location}",
            "Keep Order at the Assembly of {location}",
            "Protect a Jarl's Gathering near {location}",
        ],
        "duration": (1, 2),
        "difficulty": (1, 3),
        "danger": (1, 4),
        "silver": (10, 22),
        "food": (0, 5),
        "thralls": (0, 0),
        "ship_timber": (0, 0),
        "fine_metal": (0, 1),
        "renown": (1, 4),
        "min_crew": (4, 6),
        "description": "A public assembly needs steady hands, sharp eyes, and warriors willing to enforce peace.",
    },

    JobType.SACRED_HUNT: {
        "names": [
            "Hunt the White Elk of {location}",
            "Track an Omen Beast near {location}",
            "Join the Sacred Hunt in {location}",
        ],
        "duration": (2, 3),
        "difficulty": (2, 4),
        "danger": (2, 5),
        "silver": (0, 10),
        "food": (16, 34),
        "thralls": (0, 0),
        "ship_timber": (0, 0),
        "fine_metal": (0, 0),
        "renown": (2, 5),
        "min_crew": (4, 8),
        "travel_type": TravelType.OVERLAND,
        "description": "A hunt wrapped in omens, old vows, and whispers of the gods.",
    },

    JobType.SETTLER_ESCORT: {
        "names": [
            "Escort Settlers along {location}",
            "Guard a Farmstead Caravan near {location}",
            "Carry Families through {location}",
        ],
        "duration": (2, 4),
        "difficulty": (1, 2),
        "danger": (1, 4),
        "silver": (10, 24),
        "food": (2, 10),
        "thralls": (0, 0),
        "ship_timber": (0, 4),
        "fine_metal": (0, 1),
        "renown": (1, 3),
        "min_crew": (4, 6),
        "travel_type": lambda location: random.choice(
            [TravelType.OVERLAND, location.travel_type]
        ),        
        "description": "Families, livestock, and household goods must be moved safely through unsettled country.",
    },

    JobType.OATH_COLLECTION: {
        "names": [
            "Collect Oaths along {location}",
            "Demand Allegiance near {location}",
            "Enforce a Jarl's Claim in {location}",
        ],
        "duration": (2, 3),
        "difficulty": (1, 4),
        "danger": (2, 4),
        "silver": (12, 28),
        "food": (2, 8),
        "thralls": (0, 0),
        "ship_timber": (0, 0),
        "fine_metal": (0, 2),
        "renown": (2, 4),
        "min_crew": (4, 6),
        "description": "Local households must be reminded whose protection, law, and wrath they live under.",
    },

    JobType.OUTLAW_HUNT: {
        "names": [
            "Hunt an Outlaw near {location}",
            "Track a Murderer through {location}",
            "Bring an Oathbreaker to Justice",
        ],
        "duration": (2, 4),
        "difficulty": (2, 4),
        "danger": (2, 5),
        "silver": (8, 20),
        "food": (4, 12),
        "thralls": (0, 1),
        "ship_timber": (0, 0),
        "fine_metal": (0, 2),
        "renown": (2, 5),
        "min_crew": (4, 8),
        "travel_type": lambda location: random.choice(
            [TravelType.OVERLAND, location.travel_type]
        ),        
        "description": "An outlaw has fled into the wilds, and justice follows with spear, hound, and oath.",
    },

    JobType.FUNERAL_VOYAGE: {
        "names": [
            "Escort a Fallen Jarl across {location}",
            "Carry a Chieftain's Ashes through {location}",
            "Guard a Funeral Voyage near {location}",
        ],
        "duration": (1, 3),
        "difficulty": (2, 3),
        "danger": (1, 4),
        "silver": (4, 14),
        "food": (0, 6),
        "thralls": (0, 0),
        "ship_timber": (0, 2),
        "fine_metal": (0, 1),
        "renown": (2, 5),
        "min_crew": (4, 6),
        "travel_type": lambda location: random.choice(
            [TravelType.COASTAL, TravelType.OVERLAND, location.travel_type]
        ),
        "description": "A dead leader must be carried with honor, and the living must survive the omens that follow.",
    },

    JobType.MONASTERY_RAID: {
        "names": [
            "Raid the Monastery at {location}",
            "Plunder the Abbey near {location}",
            "Strike a Rich Monastery in {location}",
            "Burn the Bells of {location}",
            "Take Church Silver from {location}",
        ],
        "duration": (3, 5),
        "difficulty": (3, 6),
        "danger": (3, 6),
        "silver": (30, 70),
        "food": (4, 12),
        "thralls": (0, 3),
        "ship_timber": (0, 0),
        "fine_metal": (1, 5),
        "renown": (4, 8),
        "min_crew": (8, 14),
        "description": (
            "Monasteries hold silver, relics, wine, books, bells, and little mercy "
            "for raiders caught too deep inland."
        ),
    },
    JobType.SCOUT_COASTLINE: {
        "names": [
            "Scout the {location}",
            "Chart Hidden Coves near {location}",
            "Watch for Enemy Sails near {location}",
        ],
        "duration": (2, 3),
        "difficulty": (1, 2),
        "danger": (1, 2),
        "silver": (6, 14),
        "food": (3, 8),
        "renown": (1, 2),
        "thralls": (0, 0),
        "ship_timber": (0, 0),
        "fine_metal": (0, 0),
        "min_crew": (4, 6),
        "description": "Scout the coastline for threats, safe landings, and future targets.",
    },
    JobType.TRIBUTE_COLLECTION: {
        "names": [
            "Collect Tribute from {location}",
            "Demand Oaths along {location}",
            "Shake Down a Coastal Settlement in {location}",
        ],
        "duration": (2, 3),
        "difficulty": (1, 3),
        "danger": (1, 3),
        "silver": (14, 28),
        "food": (4, 10),
        "renown": (2, 3),
        "thralls": (0, 0),
        "ship_timber": (0, 0),
        "fine_metal": (1, 4),
        "min_crew": (5, 8),
        "description": "Remind a settlement that tribute is cheaper than fire.",
    },
    JobType.COASTAL_RAID: {
        "names": [
            "Raid the {location}",
            "Strike a Shore Village in {location}",
            "Burn a Watch Post near {location}",
        ],
        "duration": (3, 4),
        "difficulty": (3, 5),
        "danger": (2, 4),
        "silver": (14, 30),
        "food": (6, 14),
        "renown": (3, 5),
        "thralls": (0, 2),
        "ship_timber": (0, 0),
        "fine_metal": (0, 0),
        "min_crew": (6, 10),
        "travel_type": TravelType.COASTAL,
        "description": "A direct raid against a coastal target.",
    },
    JobType.RIVER_RAID: {
        "names": [
            "Raid Upriver in {location}",
            "Push into the Riverlands of {location}",
            "Strike a River Shrine in {location}",
        ],
        "duration": (4, 6),
        "difficulty": (3, 5),
        "danger": (3, 5),
        "silver": (30, 60),
        "food": (6, 16),
        "renown": (4, 7),
        "thralls": (0, 2),
        "ship_timber": (0, 0),
        "fine_metal": (0, 0),
        "min_crew": (8, 12),
        "travel_type": TravelType.RIVER,
        "description": "Push inland by river before local defenders can gather.",
    },
    JobType.TRADE_VOYAGE: {
        "names": [
            "Trade in {location}",
            "Carry Goods to {location}",
            "Escort Merchants through {location}",
        ],
        "duration": (3, 5),
        "difficulty": (1, 3),
        "danger": (1, 3),
        "silver": (18, 38),
        "food": (0, 6),
        "renown": (1, 3),
        "thralls": (0, 0),
        "ship_timber": (0, 6), 
        "fine_metal": (0, 3),
        "min_crew": (5, 8),
        "travel_type": lambda location: random.choice(
            [TravelType.RIVER, location.travel_type]
        ),
        "description": "A safer voyage, though trade routes still attract thieves.",
    },

# ==================================================
# WINTER JOBS
# ==================================================

    JobType.WINTER_HUNT: {
        "names": [
            "Hunt the Winter Woods near {location}",
            "Track Elk through {location}",
            "Bring Meat Home from {location}",
        ],
        "allowed_seasons": [Season.WINTER],        
        "duration": (1, 2),
        "difficulty": (1, 2),
        "danger": (1, 3),
        "silver": (4, 10),
        "food": (8, 18),
        "renown": (0, 1),
        "thralls": (0, 0),
        "ship_timber": (0, 0),
        "fine_metal": (0, 0),
        "min_crew": (4, 8),
        "travel_type": TravelType.OVERLAND,
        "description": "A winter hunt to keep the village fed, though the cold can kill as surely as steel.",
    },

    JobType.TIMBER_WORK: {
        "names": [
            "Cut Winter Timber near {location}",
            "Haul Ship Timber from {location}",
            "Work the Frozen Pines of {location}",
        ],
        "allowed_seasons": [Season.WINTER],        
        "duration": (1, 2),
        "difficulty": (1, 2),
        "danger": (1, 2),
        "silver": (8, 16),
        "food": (0, 4),
        "renown": (0, 1),
        "thralls": (0, 0),
        "ship_timber": (5, 10),
        "fine_metal": (0, 0),
        "min_crew": (4, 8),
        "travel_type": TravelType.OVERLAND,
        "description": "Hard winter labor hauling timber for halls, ships, and repairs.",
    },

    JobType.GUARD_DUTY: {
        "names": [
            "Guard a Winter Storehouse in {location}",
            "Stand Watch for a Local Jarl",
            "Protect Traders Snowed In near {location}",
        ],
        "allowed_seasons": [Season.WINTER],        
        "duration": (1, 2),
        "difficulty": (1, 3),
        "danger": (1, 3),
        "silver": (10, 20),
        "food": (0, 4),
        "renown": (0, 2),
        "thralls": (0, 0),
        "ship_timber": (0, 0),
        "fine_metal": (0, 0),
        "min_crew": (5, 9),
        "travel_type": TravelType.OVERLAND,        
        "description": "Low glory work, but someone must guard silver, grain, and trade goods.",
    },

    JobType.LOCAL_TRADE: {
        "names": [
            "Carry Winter Goods through {location}",
            "Trade Preserved Goods near {location}",
            "Move Supplies between Frozen Settlements",
        ],
        "allowed_seasons": [Season.WINTER],        
        "duration": (1, 2),
        "difficulty": (1, 2),
        "danger": (1, 3),
        "silver": (8, 18),
        "food": (2, 8),
        "renown": (0, 1),
        "thralls": (0, 0),
        "ship_timber": (0, 6),
        "fine_metal": (0, 3),
        "min_crew": (4, 7),
        "travel_type": TravelType.OVERLAND,        
        "description": "A modest winter trade run for silver, food, and favors.",
    },

# =============================================
# NEW JOBS
# =============================================

    JobType.LIVESTOCK_RAID: {
        "names": [
            "Seize Livestock in {location}",
            "Drive Cattle from {location}",
            "Raid Sheepfolds near {location}",
        ],
        "duration": (2, 4),
        "difficulty": (1, 3),
        "danger": (1, 3),
        "silver": (4, 14),
        "food": (18, 36),
        "thralls": (0, 2),
        "ship_timber": (0, 0),
        "fine_metal": (0, 0),
        "renown": (1, 3),
        "min_crew": (4, 6),
        "travel_type": lambda location: random.choice(
            [TravelType.OVERLAND, location.travel_type]
        ),        
        "description": "Steal livestock and drive them home before defenders gather.",
    },

    JobType.THRALL_RAID: {
        "names": [
            "Capture Thralls in {location}",
            "Raid for Laborers near {location}",
            "Take Prisoners from {location}",
        ],
        "duration": (3, 5),
        "difficulty": (2, 4),
        "danger": (3, 5),
        "silver": (6, 18),
        "food": (4, 10),
        "thralls": (2, 6),
        "ship_timber": (0, 0),
        "fine_metal": (0, 0),
        "renown": (2, 5),
        "min_crew": (7, 10),
        "description": "A dangerous raid meant to bring back captives for labor.",
    },

    JobType.TIMBER_EXPEDITION: {
        "names": [
            "Cut Ship Timber near {location}",
            "Haul Keel Timber from {location}",
            "Fell Tall Pines in {location}",
        ],
        "duration": (2, 4),
        "difficulty": (1, 2),
        "danger": (1, 3),
        "silver": (0, 8),
        "food": (0, 6),
        "thralls": (0, 1),
        "ship_timber": (8, 20),
        "fine_metal": (0, 0),
        "renown": (0, 2),
        "min_crew": (4, 6),
        "travel_type": TravelType.OVERLAND,
        "description": "Cut and haul quality timber for shipbuilding and repairs.",
    },

    JobType.SALVAGE_EXPEDITION: {
        "names": [
            "Salvage a Wreck near {location}",
            "Recover Timber from Broken Ships",
            "Search Drift Wrecks along {location}",
        ],
        "duration": (2, 4),
        "difficulty": (1, 3),
        "danger": (1, 4),
        "silver": (4, 16),
        "food": (0, 6),
        "thralls": (0, 0),
        "ship_timber": (6, 18),
        "fine_metal": (0, 2),
        "renown": (0, 2),
        "min_crew": (4, 8),
        "travel_type": lambda location: random.choice(
            [TravelType.COASTAL, location.travel_type]
        ),
        "description": "Recover usable ship timber, cargo, and tools from wreckage.",
    },

    JobType.FISHING_EXPEDITION: {
        "names": [
            "Fish the Waters near {location}",
            "Fill the Smokehouses from {location}",
            "Cast Nets off {location}",
        ],
        "duration": (1, 2),
        "difficulty": (1, 2),
        "danger": (1, 2),
        "silver": (0, 6),
        "food": (18, 34),
        "thralls": (0, 0),
        "ship_timber": (0, 0),
        "fine_metal": (0, 0),
        "renown": (0, 1),
        "min_crew": (3, 6),
        "description": "A low-risk food expedition to fill village stores.",
    },
}

LOCATION_JOB_FLAVOR = {
    "Norway": {
        "employers": [
            "Local Jarl",
            "Rival Hersir",
            "Fishing Elder",
            "Timber Master",
            "Farmstead Headman",
            "Thing Speaker",
            "Widowed Bondi",
            "Shipwright's Kin",
            "Old Shield-Brother",
            "Goði of a Fjord Shrine",
            None,
        ],
        "items": [],
    },

    "Denmark": {
        "employers": [
            "Danish Jarl",
            "Cattle Lord",
            "Market Elder",
            "Ambitious Hersir",
            "Harbor Trader",
            "Mead Hall Steward",
            "Disgraced Thane",
            "Ferry Master",
            "Farmstead Alliance",
            "Thor's Boastful Witness",
            None,
        ],
        "items": [],
    },

    "Swedish Coast": {
        "employers": [
            "Amber Trader",
            "Burial Mound Keeper",
            "Forest Chieftain",
            "Baltic Merchant",
            "Rune-Carver",
            "Silent Fisherman",
            "Ship-Burial Watcher",
            "Eastern Silver Broker",
            "Oath-Bound Guide",
            "Völva's Messenger",
            None,
        ],
        "items": [],
    },

    "Rus' Riverlands": {
        "employers": [
            "Rus' Trader",
            "River Prince",
            "Varangian Contact",
            "Fur Merchant",
            "Portage Guide",
            "Eastern Boatman",
            "Silver Weigher",
            "Timber Camp Boss",
            "Slavic Headman",
            "River Toll-Keeper",
            None,
        ],
        "items": [],
    },

    "Baltic Coast": {
        "employers": [
            "Baltic Trader",
            "Coastal Chieftain",
            "Amber Broker",
            "Wary Fisher Elder",
            "Hidden Post Keeper",
            "Rival Crew Captain",
            "Salt Merchant",
            "Forest Guide",
            "Foreign Silver Dealer",
            "Watchful Harbor Master",
            None,
        ],
        "items": [],
    },

    "Lindisfarne": {
        "employers": [
            "Whispering Scout",
            "Runaway Thrall",
            "Foreign Informant",
            "Greedy Sailor",
            "Raven-Omened Stranger",
            None,
        ],
        "items": [],
    },

    "Northumbria": {
        "employers": [
            "Northumbrian Exile",
            "Rival King",
            "Captured Scout",
            "Monastery Informant",
            "Disgraced Thegn",
            "Border Reeve",
            "Anglo-Saxon Rival",
            "Frightened Monk",
            "Church Silver Fence",
            "Broken Mercenary",
            None,
        ],
        "items": [],
    },

    "East Anglia": {
        "employers": [
            "Exiled Thegn",
            "Monastery Informant",
            "Anglo-Saxon Rival",
            "Fenland Guide",
            "Coastal Priest",
            "Market Reeve",
            "Runaway Serf",
            "Silver-Hoard Keeper",
            "Harbor Smuggler",
            "Local Claimant",
            None,
        ],
        "items": [],
    },
}


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))




def generate_job_for_location(location: JobLocation, job_type: JobType) -> Job:
    template = JOB_TEMPLATES[job_type]
    flavor = LOCATION_JOB_FLAVOR.get(
        location.name,
        {
            "employers": [None],
            "items": [],
        },
    )

    difficulty_mod = location.difficulty_mod
    danger_mod = location.danger_mod
    duration_mod = location.duration_mod
    silver_mod = location.silver_mod
        
    duration = random.randint(*template["duration"]) + duration_mod
    difficulty = random.randint(*template["difficulty"]) + difficulty_mod
    danger = random.randint(*template["danger"]) + danger_mod


    guaranteed_silver = random.randint(*template["silver"])
    guaranteed_food = random.randint(*template["food"])
    reward_renown = random.randint(*template["renown"])
    required_min_crew = random.randint(*template["min_crew"])
    
    reward_thralls = random.randint(*template.get("thralls", (0, 0)))
    reward_ship_timber = random.randint(*template.get("ship_timber", (0, 0)))
    reward_fine_metal = random.randint(*template.get("fine_metal", (0, 0)))
    
    guaranteed_item_rewards = []

    if difficulty >= 5:
        guaranteed_item_rewards.append(random.choice(location.common_items))

    if difficulty >= 8 and location.common_items:
        guaranteed_item_rewards.append(random.choice(location.common_items))    
    
    difficulty_bonus = max(0, difficulty - 4)
    danger_bonus = max(0, danger - 3)
    
    duration_bonus = max(0, duration - template["duration"][0])

    guaranteed_silver += silver_mod

    if duration >= 5:
        reward_renown += 1    

    guaranteed_silver += duration_bonus * random.randint(1, 3)
    guaranteed_silver += (difficulty_bonus * random.randint(2, 4))
    guaranteed_silver += (danger_bonus * random.randint(1, 2))

    reward_renown += max(0, difficulty_bonus // 2)    

    name_template = random.choice(template["names"])

    return Job(
        name=name_template.format(location=location.name),
        job_type=job_type,
        location_name=location.name,        
        allowed_seasons=template.get("allowed_seasons", [Season.SPRING, Season.SUMMER]),
        duration_weeks=duration,
        required_range=location.required_range,
        required_min_crew=required_min_crew,
        difficulty=clamp(difficulty, 1, 10),
        danger=clamp(danger, 1, 10),
        travel_type=(
            template["travel_type"](location)
            if callable(template.get("travel_type"))
            else template.get("travel_type", location.travel_type)
        ),        
        guaranteed_silver=guaranteed_silver,
        guaranteed_food=guaranteed_food,
        reward_renown=reward_renown,
        random_silver_min=0,
        random_silver_max=max(4, guaranteed_silver // 2),
        random_food_min=0,
        random_food_max=max(3, guaranteed_food // 2),
        guaranteed_item_rewards=guaranteed_item_rewards,
        reward_thralls=reward_thralls,
        reward_ship_timber=reward_ship_timber,
        reward_fine_metal=reward_fine_metal,        
        possible_item_rewards=(
            list(GLOBAL_EQUIPMENT_REWARDS)
            + list(location.common_items)
            + list(location.rare_items)
            + list(location.legendary_items)
        ),
        employer=random.choice(flavor["employers"]),
        description=template["description"],
    )


def generate_jobs_for_location(
    location: JobLocation,
    month: int,
    week_of_month: int,
    ship,
    count: int = 3,
) -> list[Job]:
    from models import get_season_for_month

    current_season = get_season_for_month(month)

    possible_types = [
        job_type for job_type in location.job_types
        if job_type in JOB_TEMPLATES
    ]

    jobs: list[Job] = []
    attempts = 0
    max_attempts = count * 12

    while len(jobs) < count and attempts < max_attempts:
        attempts += 1

        if not possible_types:
            break

        job_type = random.choice(possible_types)
        job = generate_job_for_location(location, job_type)

        if (
            job.is_available_in_season(current_season)
            and job.time_can_fit(month, week_of_month)
            and job.ship_can_take_job(ship)
        ):
            jobs.append(job)

    return jobs