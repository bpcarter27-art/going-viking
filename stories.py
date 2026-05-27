from models import Job, JobType, Season, TravelType




DENMARK_RENOWN_REQUIRED = 8
SWEDISH_COAST_RENOWN_REQUIRED = 16
BALTIC_COAST_RENOWN_REQUIRED = 23
RUS_RENOWN_REQUIRED = 30
SUNSTONE_RENOWN_REQUIRED = 35

def create_intro_trial_by_combat_job(village_name: str) -> Job:
    return Job(
        name=f"Trial by Combat for {village_name}",
        job_type=JobType.TRIAL_BY_COMBAT,
        location_name="The High Seat",
        allowed_seasons=[Season.SPRING, Season.SUMMER, Season.WINTER],
        duration_weeks=0,
        required_range=1,
        required_min_crew=1,
        difficulty=1,
        danger=1,
        travel_type=TravelType.OVERLAND,
        guaranteed_silver=0,
        guaranteed_food=0,
        reward_renown=1,
        reward_thralls=0,
        reward_ship_timber=0,
        reward_fine_metal=0,
        random_silver_min=0,
        random_silver_max=0,
        random_food_min=0,
        random_food_max=0,
        guaranteed_item_rewards=[],
        possible_item_rewards=[],
        employer="The Old Jarl",
        description=(
            "The old Jarl has sentenced you to death. "
            "You invoke the ancient right of trial by combat. "
            "Win, and the hall will name you Jarl."
        ),
    )


def create_denmark_intro_job() -> Job:
    return Job(
        name="Thor's Stolen Hammer",
        job_type=JobType.OATH_COLLECTION,
        location_name="Denmark",
        allowed_seasons=[Season.SPRING, Season.SUMMER],
        duration_weeks=2,
        required_range=1,
        required_min_crew=3,
        difficulty=1,
        danger=1,
        travel_type=TravelType.COASTAL,
        guaranteed_silver=10,
        guaranteed_food=6,
        reward_renown=2,
        description=(
            "You hear of a land not far away, a place where mighty Thor is said "
            "to walk. In fact, word reaches your hall that Thor's hammer, Mjolnir, "
            "has been stolen, and he seeks bold warriors to help retrieve it. "
            "His plan, supposedly, is to disguise himself in women's clothing "
            "and infiltrate the thieves."
        ),
    )
    
def create_swedish_coast_intro_job() -> Job:
    return Job(
        name="The Sunless Burial",
        job_type=JobType.SALVAGE_EXPEDITION,
        location_name="Swedish Coast",
        allowed_seasons=[Season.SPRING, Season.SUMMER],
        duration_weeks=3,
        required_range=1,
        required_min_crew=4,
        difficulty=2,
        danger=2,
        travel_type=TravelType.OPEN_OCEAN,
        guaranteed_silver=12,
        guaranteed_food=0,
        reward_renown=2,
        reward_fine_metal=1,
        description=(
            "A fisherman arrives from the eastern sea carrying amber beads and "
            "a silver coin blackened with age. He speaks of an ancient ship burial "
            "exposed by a storm along the Swedish Coast. The locals refuse to touch "
            "it, claiming the dead there do not sleep beneath the sun."
        ),
    )

def create_baltic_coast_intro_job() -> Job:
    return Job(
        name="The Varangian Feast",
        job_type=JobType.TRADE_VOYAGE,
        location_name="Baltic Coast",
        allowed_seasons=[Season.SPRING, Season.SUMMER],
        duration_weeks=4,
        required_range=2,
        required_min_crew=5,
        difficulty=3,
        danger=3,
        travel_type=TravelType.OPEN_OCEAN,
        guaranteed_silver=18,
        guaranteed_food=4,
        reward_renown=3,
        reward_fine_metal=1,
        description=(
            "A band of eastern-traveling Norsemen arrive in your hall carrying "
            "Arab silver, strange furs, and stories of rivers that stretch beyond "
            "the edge of known maps. Their leader speaks of a great feast along "
            "the Baltic Coast where ambitious jarls, traders, and mercenaries gather "
            "to swear oaths and seek crews bold enough to sail east."
        ),
    )


def create_rus_intro_job() -> Job:
    return Job(
        name="The River Wolf",
        job_type=JobType.TRADE_VOYAGE,
        location_name="Rus' Riverlands",
        allowed_seasons=[Season.SPRING, Season.SUMMER],
        duration_weeks=5,
        required_range=2,
        required_min_crew=6,
        difficulty=3,
        danger=3,
        travel_type=TravelType.RIVER,
        guaranteed_silver=20,
        guaranteed_food=4,
        reward_renown=3,
        reward_fine_metal=2,
        description=(
            "Eastern traders speak of river roads stretching deep inland through "
            "the lands of the Rus'. Along those waters travels a massive Norse warrior "
            "called the River Wolf, a man said to have fought Slavs, steppe raiders, "
            "and river kings alike. Hoping to trade for silver and hear the truth of "
            "these stories, your crew sails east."
        ),
    )

def create_sunstone_navigation_job() -> Job:
    return Job(
        name="The Wanderer's Stone",
        job_type=JobType.TRADE_VOYAGE,
        location_name="Norway",
        allowed_seasons=[Season.WINTER],
        duration_weeks=2,
        required_range=2,
        required_min_crew=3,
        difficulty=1,
        danger=1,
        travel_type=TravelType.OVERLAND,

        guaranteed_silver=0,
        guaranteed_food=0,

        reward_renown=2,
        reward_fine_metal=0,

        description=(
            "A wanderer arrives at your hall during the dark of winter, "
            "speaking of distant seas and strange ways of finding one's path "
            "beneath cloud and storm. Most dismiss the old traveler as mad, "
            "but something in his words lingers in your thoughts. "
            "You set out to find him again before the snows pass."
        ),
    )   

def create_lindisfarne_raid_job() -> Job:
    return Job(
        name="Raid Lindisfarne Monastery",
        job_type=JobType.LINDISFARNE_RAID,
        location_name="Lindisfarne",
        allowed_seasons=[Season.SPRING, Season.SUMMER],
        duration_weeks=4,
        required_range=3,
        required_min_crew=8,
        difficulty=5,
        danger=2,
        travel_type=TravelType.OPEN_OCEAN,        
        guaranteed_silver=75,
        guaranteed_food=8,
        reward_renown=10,
        reward_thralls=2,
        reward_ship_timber=0,
        reward_fine_metal=4,
        random_silver_min=10,
        random_silver_max=35,
        random_food_min=0,
        random_food_max=8,
        guaranteed_item_rewards=["Anglo Silver Cross"],
        possible_item_rewards=[
            "Anglo Silver Cross",
            "Gilded Book Cover",
            "Monastery Reliquary",
            "Northumbrian Sword",
            "Northumbrian Helm",
        ],
        employer="Whispers from across the sea",
        description=(
            "A holy island monastery lies exposed off the Northumbrian coast. "
            "Its bells, books, silver, and frightened monks may mark the beginning "
            "of a new age of raiding."
        ),
    )

def create_ragnar_feast_job() -> Job:
    return Job(
        name="The Feast of Ragnar Lodbrok",
        job_type=JobType.COASTAL_RAID,
        location_name="Northumbria",

        allowed_seasons=[Season.SPRING, Season.SUMMER],

        duration_weeks=2,

        required_range=3,
        required_min_crew=6,

        difficulty=2,
        danger=1,

        travel_type=TravelType.OPEN_OCEAN,

        guaranteed_silver=20,
        guaranteed_food=6,

        reward_renown=4,
        reward_thralls=0,
        reward_ship_timber=0,
        reward_fine_metal=1,

        employer="Ragnar Lodbrok",

        description=(
            "Word of your raid upon Lindisfarne spreads quickly through the north. "
            "Before long, a messenger arrives bearing an invitation to feast beside "
            "the growing warband of a charismatic and ambitious jarl: Ragnar Lodbrok. "
            "The man speaks openly of England's wealth and the weakness of its kings."
        ),
    )


def create_aelle_silver_job() -> Job:
    return Job(
        name="The Price of Peace",
        job_type=JobType.COASTAL_RAID,
        location_name="Northumbria",

        allowed_seasons=[Season.SPRING, Season.SUMMER],

        duration_weeks=4,

        required_range=3,
        required_min_crew=8,

        difficulty=4,
        danger=3,

        travel_type=TravelType.OPEN_OCEAN,

        guaranteed_silver=60,
        guaranteed_food=8,

        reward_renown=8,
        reward_thralls=1,
        reward_ship_timber=0,
        reward_fine_metal=2,

        employer="Ragnar Lodbrok",

        description=(
            "Your crew sails beside Ragnar's growing fleet as yet another "
            "Northumbrian raid begins. Yet this time the English respond far "
            "faster than before. Riders gather inland, banners appear across "
            "the hills, and before long King Aelle himself arrives beneath a "
            "flag of truce bearing an offer of silver and safe passage in "
            "exchange for Ragnar's oath never to return."
        ),
    )

def create_east_anglia_intro_job() -> Job:
    return Job(
        name="The Sons' Whisper",
        job_type=JobType.TRADE_VOYAGE,
        location_name="East Anglia",
        allowed_seasons=[Season.SPRING, Season.SUMMER],
        duration_weeks=3,
        required_range=4,
        required_min_crew=8,
        difficulty=3,
        danger=3,
        travel_type=TravelType.OPEN_OCEAN,
        guaranteed_silver=35,
        guaranteed_food=6,
        reward_renown=5,
        reward_thralls=0,
        reward_ship_timber=0,
        reward_fine_metal=2,
        employer="A Messenger of Ragnar's Sons",
        description=(
            "Word reaches your hall that Ragnar's sons have begun looking beyond "
            "Northumbria. A quiet messenger speaks of East Anglia: rich shores, "
            "watchful kings, and men willing to bargain before the fires begin."
        ),
    )

def get_available_story_jobs(campaign) -> list[Job]:
    jobs: list[Job] = []

    if "intro_trial_completed" not in campaign.world_flags:
        return [
            create_intro_trial_by_combat_job(campaign.village.name)
        ]

    if (
        campaign.renown >= DENMARK_RENOWN_REQUIRED
        and "denmark_intro_completed" not in campaign.world_flags
    ):
        jobs.append(create_denmark_intro_job())

    if (
        campaign.renown >= SWEDISH_COAST_RENOWN_REQUIRED
        and "swedish_coast_intro_completed" not in campaign.world_flags
    ):
        jobs.append(create_swedish_coast_intro_job())
    if (
        campaign.renown >= BALTIC_COAST_RENOWN_REQUIRED
        and "baltic_coast_intro_completed" not in campaign.world_flags
    ):
        jobs.append(create_baltic_coast_intro_job())
    if (
        campaign.renown >= RUS_RENOWN_REQUIRED
        and "rus_intro_completed" not in campaign.world_flags
    ):
        jobs.append(create_rus_intro_job())         

    if (
        campaign.renown >= SUNSTONE_RENOWN_REQUIRED
        and campaign.ship.sail_level >= 1
        and "sunstone_navigation_completed" not in campaign.world_flags
    ):
        jobs.append(create_sunstone_navigation_job())

    if (
        campaign.ship.range >= 3
        and "lindisfarne_raided" not in campaign.world_flags
    ):
        jobs.append(create_lindisfarne_raid_job())

    if (
        "lindisfarne_raided" in campaign.world_flags
        and "met_ragnar" not in campaign.world_flags
    ):
        jobs.append(create_ragnar_feast_job())

    if (
        "met_ragnar" in campaign.world_flags
        and "aelle_paid_tribute" not in campaign.world_flags
    ):
        jobs.append(create_aelle_silver_job())

    if (
        "aelle_paid_tribute" in campaign.world_flags
        and campaign.ship.range >= 4
        and "east_anglia_intro_completed" not in campaign.world_flags
    ):
        jobs.append(create_east_anglia_intro_job())

    return jobs    
    
def location_is_unlocked(campaign, location_name: str) -> bool:
    if location_name == "The High Seat":
        return "intro_trial_completed" not in campaign.world_flags

    if location_name == "Norway":
        return "intro_trial_completed" in campaign.world_flags

    if location_name == "Denmark":
        return "denmark_intro_completed" in campaign.world_flags

    if location_name == "Swedish Coast":
        return "swedish_coast_intro_completed" in campaign.world_flags

    if location_name == "Baltic Coast":
        return "baltic_coast_intro_completed" in campaign.world_flags

    if location_name == "Rus' Riverlands":
        return "rus_intro_completed" in campaign.world_flags

    if location_name == "Lindisfarne":
        return (
            campaign.ship.range >= 3
            and "sunstone_navigation_completed" in campaign.world_flags
            and "lindisfarne_raided" not in campaign.world_flags
        )

    if location_name == "Northumbria":
        return "aelle_paid_tribute" in campaign.world_flags
        
    if location_name == "East Anglia":
        return "east_anglia_intro_completed" in campaign.world_flags        

    return True

def apply_story_completion(campaign, job: Job, success: bool) -> list[str]:
    logs: list[str] = []

    if not success:
        return logs

    if job.name == "Thor's Stolen Hammer":
        campaign.world_flags.add("denmark_intro_completed")
        logs.append(
            "It turns out the tale was somewhat embellished: a Danish farmer had "
            "his hammer stolen and invoked Thor's name more freely than truth allowed. "
            "Still, your crew handled the matter well. Denmark is now open to regular jobs."
        )

    elif job.name == "The Sunless Burial":
        campaign.world_flags.add("swedish_coast_intro_completed")
        logs.append(
            "The burial mound proves real: an ancient longship buried beneath stone and "
            "earth, filled with rusted weapons, old silver, and forgotten carvings. "
            "Whether the dead were truly restless or merely the victims of frightened "
            "stories, your crew returns wealthier and wiser. The Swedish Coast is now "
            "open to regular jobs."
        )
        
    elif job.name == "The Varangian Feast":
        campaign.world_flags.add("baltic_coast_intro_completed")
        logs.append(
            "The Baltic gathering proves larger than any market your crew has seen. "
            "Varangians, traders, raiders, and wandering warriors crowd the coast, "
            "speaking of eastern kingdoms rich in silver. The Baltic Coast is now "
            "open to regular jobs."
        )

    elif job.name == "The River Wolf":
        campaign.world_flags.add("rus_intro_completed")
        logs.append(
            "The eastern rivers prove dangerous, wealthy, and full of wandering Norsemen "
            "seeking fortune beyond the Baltic. Though the River Wolf vanishes before "
            "you learn his true name, tales of his deeds spread through your crew. "
            "The Rus' Riverlands are now open to regular jobs."
        )       

    elif job.name == "The Wanderer's Stone":
        from ship_upgrades import ShipPart

        campaign.world_flags.add("sunstone_navigation_completed")
        campaign.ship.set_part_level(ShipPart.NAVIGATION, 1)

        logs.append(
            "The wanderer's strange crystal reveals what your crew once thought "
            "impossible: even beneath cloud and sea-mist, the hidden sun may still "
            "be found. New western waters no longer seem beyond reach."
        )

    elif job.name == "The Feast of Ragnar Lodbrok":
        campaign.world_flags.add("met_ragnar")

        logs.append(
            "Ragnar proves sharp-eyed, restless, and far more ambitious than "
            "most jarls. Over drink and laughter he speaks openly of England's "
            "wealth and weak kings. Before the feast ends, he invites your "
            "crew to sail beside his."
        )

    elif job.name == "The Price of Peace":
        campaign.world_flags.add("aelle_paid_tribute")

        logs.append(
            "King Aelle pays dearly for peace, and Ragnar accepts with a smile "
            "that never reaches his eyes. As your ships depart Northumbria, "
            "Ragnar watches the shore quietly before saying:\n\n"
            "'A king willing to buy peace must possess wealth worth taking twice.'\n\n"
            "He turns to you with a glint in his eye.\n\n"
            "'We will sail together again, if the weavers of destiny allow it.'\n\n"
            "Northumbria is now open to regular jobs."
        )

    elif job.job_type == JobType.LINDISFARNE_RAID:
        campaign.world_flags.add("lindisfarne_raided")
        logs.append(
            "Word of Lindisfarne spreads across the sea. "
            "Powerful men begin to take notice of your crew."
        )

    elif job.name == "The Sons' Whisper":
        campaign.world_flags.add("east_anglia_intro_completed")

        logs.append(
            "The messenger's words prove true. East Anglia is wealthy, cautious, "
            "and already listening for the names of Ragnar's sons. East Anglia is "
            "now open to regular jobs."
        )

    return logs    
    