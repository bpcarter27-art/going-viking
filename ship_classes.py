from models import ShipClass, CrewRole

KARVI = ShipClass(
    name="Karvi",
    min_crew=6,
    max_crew=12,
    required_roles={
        CrewRole.CAPTAIN: 1,
    },
    base_hull=80,
    cargo_capacity=20,
    range=5,
    speed=7,
    seaworthiness=5,
    stealth=7,
)

SNEKKJA = ShipClass(
    name="Snekkja",
    min_crew=10,
    max_crew=18,
    required_roles={
        CrewRole.CAPTAIN: 1,
        #CrewRole.NAVIGATOR: 1,
    },
    base_hull=120,
    cargo_capacity=40,
    range=7,
    speed=6,
    seaworthiness=6,
    stealth=5,
)

DRAKKAR = ShipClass(
    name="Drakkar",
    min_crew=14,
    max_crew=28,
    required_roles={
        CrewRole.CAPTAIN: 1,
        #CrewRole.NAVIGATOR: 1,
        #CrewRole.CARPENTER: 1,
    },
    base_hull=180,
    cargo_capacity=70,
    range=10,
    speed=5,
    seaworthiness=7,
    stealth=3,
)

ALL_SHIP_CLASSES = {
    "Karvi": KARVI,
    "Snekkja": SNEKKJA,
    "Drakkar": DRAKKAR,
}