from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import uuid
import random


# ====================================================
# ITEM TYPES
# ====================================================

class ItemType(str, Enum):
    WEAPON = "Weapon"
    ARMOR = "Armor"
    HELM = "Helm"
    SHIELD = "Shield"

    RESOURCE = "Resource"
    TREASURE = "Treasure"
    ARTIFACT = "Artifact"
    TRADE_ITEM = "Trade Item"


# ====================================================
# EQUIPMENT SLOTS
# ====================================================

class EquipmentSlot(str, Enum):
    PRIMARY_WEAPON = "Primary Weapon"
    ARMOR = "Armor"
    HELM = "Helm"
    SHIELD = "Shield"

# ====================================================
# WEAPON CATEGORY
# ====================================================

class WeaponCategory(str, Enum):
    AXE = "Axe"
    SWORD = "Sword"
    SPEAR = "Spear"
    KNIFE = "Knife"
    HAMMER = "Hammer"
    BOW = "Bow"


# ====================================================
# WEAPON QUALITY
# ====================================================

class ItemQuality(str, Enum):
    CRUDE = "Crude"
    WORN = "Worn"
    COMMON = "Common"
    FINE = "Fine"
    SUPERIOR = "Superior"
    MASTERWORK = "Masterwork"
    SAGA_FORGED = "Saga-Forged"


QUALITY_MULTIPLIERS = {
    ItemQuality.CRUDE: (0.10, 0.25),
    ItemQuality.WORN: (0.33, 0.50),
    ItemQuality.COMMON: (0.66, 0.75),
    ItemQuality.FINE: (1.00, 1.00),
    ItemQuality.SUPERIOR: (1.33, 1.25),
    ItemQuality.MASTERWORK: (1.66, 1.50),
    ItemQuality.SAGA_FORGED: (1.90, 1.75),
}

# ====================================================
# ITEM MODEL
# ====================================================

def item_quality_from_save(value: str) -> ItemQuality:
    legacy_quality_map = {
        "Broken": ItemQuality.CRUDE,
        "Damaged": ItemQuality.WORN,
        "Worn": ItemQuality.COMMON,
        "Fine": ItemQuality.FINE,
        "New": ItemQuality.SUPERIOR,
        "Pristine": ItemQuality.MASTERWORK,
        "Flawless": ItemQuality.SAGA_FORGED,
    }

    if value in legacy_quality_map:
        return legacy_quality_map[value]

    return ItemQuality(value)

@dataclass
class Item:
    name: str
    item_type: ItemType

    value: int = 0
    rarity: str = "Common"
    
    quality: ItemQuality = ItemQuality.FINE

    slot: EquipmentSlot | None = None
    
    weapon_category: WeaponCategory | None = None

    might_bonus: int = 0
    skill_bonus: int = 0
    cunning_bonus: int = 0
    leadership_bonus: int = 0
    courage_bonus: int = 0
    vitality_bonus: int = 0
    loyalty_bonus: int = 0
    seamanship_bonus: int = 0

    description: str = ""

    item_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # ------------------------------------------------
    # Helpers
    # ------------------------------------------------

    def is_equippable(self) -> bool:
        return self.slot is not None

    # ------------------------------------------------
    # Save / Load
    # ------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "name": self.name,
            "item_type": self.item_type.value,
            "value": self.value,
            "quality": self.quality.value,
            "rarity": self.rarity,
            "slot": self.slot.value if self.slot else None,
            
            "weapon_category": self.weapon_category.value if self.weapon_category else None,

            "might_bonus": self.might_bonus,
            "skill_bonus": self.skill_bonus,
            "cunning_bonus": self.cunning_bonus,
            "leadership_bonus": self.leadership_bonus,
            "courage_bonus": self.courage_bonus,
            "vitality_bonus": self.vitality_bonus,
            "loyalty_bonus": self.loyalty_bonus,
            "seamanship_bonus": self.seamanship_bonus,

            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Item":
        return cls(
            item_id=data.get("item_id", str(uuid.uuid4())),
            name=data["name"],
            item_type=ItemType(data["item_type"]),
            value=data.get("value", 0),
            quality=item_quality_from_save(data.get("quality", ItemQuality.FINE.value)),            
            rarity=data.get("rarity", "Common"),

            slot=EquipmentSlot(data["slot"]) if data.get("slot") else None,
            
            weapon_category=WeaponCategory(data["weapon_category"]) if data.get("weapon_category") else None,

            might_bonus=data.get("might_bonus", 0),
            skill_bonus=data.get("skill_bonus", 0),
            cunning_bonus=data.get("cunning_bonus", 0),
            leadership_bonus=data.get("leadership_bonus", 0),
            courage_bonus=data.get("courage_bonus", 0),
            vitality_bonus=data.get("vitality_bonus", 0),
            loyalty_bonus=data.get("loyalty_bonus", 0),
            seamanship_bonus=data.get("seamanship_bonus", 0),

            description=data.get("description", ""),
        )
#=====================================================
# BASIC ITEMS
#=====================================================

def make_basic_item(
    name: str,
    item_type: ItemType,
    slot: EquipmentSlot,
    weapon_category: WeaponCategory | None = None,
) -> Item:
    return Item(
        name=name,
        item_type=item_type,
        slot=slot,
        weapon_category=weapon_category,
        value=1,
        rarity="Poor",
        description="Basic worn equipment.",
    )
    
BASIC_AXE = make_basic_item("Rusty Axe", ItemType.WEAPON, EquipmentSlot.PRIMARY_WEAPON, WeaponCategory.AXE)
BASIC_KNIFE = make_basic_item("Rusty Knife", ItemType.WEAPON, EquipmentSlot.PRIMARY_WEAPON, WeaponCategory.KNIFE)
BASIC_HAMMER = make_basic_item("Worn Hammer", ItemType.WEAPON, EquipmentSlot.PRIMARY_WEAPON, WeaponCategory.HAMMER)
BASIC_SPEAR = make_basic_item("Cracked Wooden Spear", ItemType.WEAPON, EquipmentSlot.PRIMARY_WEAPON, WeaponCategory.SPEAR)
BASIC_SWORD = make_basic_item("Rusty Sword", ItemType.WEAPON, EquipmentSlot.PRIMARY_WEAPON, WeaponCategory.SWORD)
BASIC_BOW = make_basic_item("Old Bow", ItemType.WEAPON, EquipmentSlot.PRIMARY_WEAPON, WeaponCategory.BOW)

BASIC_SHIELD = make_basic_item("Splintered Shield", ItemType.SHIELD, EquipmentSlot.SHIELD)
BASIC_ARMOR = make_basic_item("Padded Shirt", ItemType.ARMOR, EquipmentSlot.ARMOR)
BASIC_HELM = make_basic_item("Padded Hat", ItemType.HELM, EquipmentSlot.HELM)  
    
    
def copy_item(template: Item, quality: ItemQuality | None = None) -> Item:
    quality = quality or ItemQuality.FINE

    if template.item_type == ItemType.TRADE_ITEM:
        quality = ItemQuality.FINE

    value_mult, bonus_mult = QUALITY_MULTIPLIERS[quality]

    def scale_bonus(value: int) -> int:
        if value == 0:
            return 0
        return max(1, round(value * bonus_mult))

    item_name = template.name
    if quality != ItemQuality.FINE and template.is_equippable():
        item_name = f"{quality.value} {template.name}"

    return Item(
        name=item_name,
        item_type=template.item_type,
        value=max(1, round(template.value * value_mult)),
        rarity=template.rarity,
        slot=template.slot,
        weapon_category=template.weapon_category,
        might_bonus=scale_bonus(template.might_bonus),
        skill_bonus=scale_bonus(template.skill_bonus),
        cunning_bonus=scale_bonus(template.cunning_bonus),
        leadership_bonus=scale_bonus(template.leadership_bonus),
        courage_bonus=scale_bonus(template.courage_bonus),
        vitality_bonus=scale_bonus(template.vitality_bonus),
        loyalty_bonus=scale_bonus(template.loyalty_bonus),
        seamanship_bonus=scale_bonus(template.seamanship_bonus),
        description=template.description,
        quality=quality,
    )  

def roll_reward_quality() -> ItemQuality:
    return random.choices(
        population=[
            ItemQuality.CRUDE,
            ItemQuality.WORN,
            ItemQuality.COMMON,
            ItemQuality.FINE,
            ItemQuality.SUPERIOR,
            ItemQuality.MASTERWORK,
            ItemQuality.SAGA_FORGED,
        ],
        weights=[8, 18, 28, 30, 12, 3, 1],
        k=1,
    )[0]    

# ====================================================
# TRADER IRON TIER
# ====================================================

IRON_AXE = Item(
    name="Iron Axe",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.AXE,
    might_bonus=3,
    value=22,
    rarity="Common",
    description="A solid iron axe, better than a rusty blade.",
)

IRON_SWORD = Item(
    name="Iron Sword",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.SWORD,
    skill_bonus=3,
    value=28,
    rarity="Common",
    description="A plain but dependable iron sword.",
)

IRON_SPEAR = Item(
    name="Iron Spear",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.SPEAR,
    skill_bonus=3,
    value=24,
    rarity="Common",
    description="A sturdy iron-tipped spear.",
)

IRON_KNIFE = Item(
    name="Iron Knife",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.KNIFE,
    cunning_bonus=3,
    value=18,
    rarity="Common",
    description="A useful iron knife.",
)

ASH_BOW = Item(
    name="Ash Bow",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.BOW,
    skill_bonus=3,
    value=26,
    rarity="Common",
    description="A flexible ash bow.",
)

LEATHER_ARMOR = Item(
    name="Leather Armor",
    item_type=ItemType.ARMOR,
    slot=EquipmentSlot.ARMOR,
    vitality_bonus=3,
    value=26,
    rarity="Common",
    description="Simple leather armor.",
)

LEATHER_HELM = Item(
    name="Leather Helm",
    item_type=ItemType.HELM,
    slot=EquipmentSlot.HELM,
    vitality_bonus=3,
    value=18,
    rarity="Common",
    description="A reinforced leather helm.",
)

REINFORCED_WOODEN_SHIELD = Item(
    name="Reinforced Wooden Shield",
    item_type=ItemType.SHIELD,
    slot=EquipmentSlot.SHIELD,
    courage_bonus=3,
    value=22,
    rarity="Common",
    description="A sturdy shield with iron bands.",
)

# ====================================================
# REWARD ITEMS
# ====================================================


JEWELED_CARAFE = Item(
    name="Jeweled Carafe",
    item_type=ItemType.TRADE_ITEM,
    value=75,
    rarity="Uncommon",
    description="A delicate jeweled vessel worth a handsome price.",
)

CARVED_AMBER_ICON = Item(
    name="Carved Amber Icon",
    item_type=ItemType.TRADE_ITEM,
    value=55,
    rarity="Uncommon",
    description="A small amber icon prized by foreign traders.",
)

SILK_BOLT = Item(
    name="Bolt of Eastern Silk",
    item_type=ItemType.TRADE_ITEM,
    value=90,
    rarity="Rare",
    description="Fine silk from distant markets.",
)

SILVER_CHALICE = Item(
    name="Silver Chalice",
    item_type=ItemType.TRADE_ITEM,
    value=65,
    rarity="Uncommon",
    description="A valuable drinking vessel taken from a wealthy hall.",
)


# ====================================================
# LOCATION EQUIPMENT - NORWAY
# ====================================================

NORDIC_AXE = Item(
    name="Nordic Axe",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.AXE,
    might_bonus=5,
    value=45,
    rarity="Uncommon",
    description="A well-balanced axe from Norway.",
)

NORDIC_SWORD = Item(
    name="Nordic Sword",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.SWORD,
    skill_bonus=5,
    value=50,
    rarity="Uncommon",
    description="A sharp Nordic blade suited for close fighting.",
)

NORDIC_SPEAR = Item(
    name="Nordic Spear",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.SPEAR,
    skill_bonus=3,
    courage_bonus=3,
    value=46,
    rarity="Uncommon",
    description="A sturdy spear favored by coastal raiders.",
)

NORDIC_KNIFE = Item(
    name="Nordic Knife",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.KNIFE,
    cunning_bonus=5,
    value=38,
    rarity="Uncommon",
    description="A finely made knife useful in camp and combat.",
)

NORDIC_BOW = Item(
    name="Nordic Bow",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.BOW,
    skill_bonus=5,
    value=48,
    rarity="Uncommon",
    description="A reliable bow made from northern wood.",
)

NORDIC_ARMOR = Item(
    name="Nordic Armor",
    item_type=ItemType.ARMOR,
    slot=EquipmentSlot.ARMOR,
    vitality_bonus=5,
    value=52,
    rarity="Uncommon",
    description="Reinforced armor suitable for early raids.",
)

NORDIC_HELM = Item(
    name="Nordic Helm",
    item_type=ItemType.HELM,
    slot=EquipmentSlot.HELM,
    vitality_bonus=3,
    courage_bonus=3,
    value=42,
    rarity="Uncommon",
    description="A solid helm with a simple nasal guard.",
)

NORDIC_SHIELD = Item(
    name="Nordic Shield",
    item_type=ItemType.SHIELD,
    slot=EquipmentSlot.SHIELD,
    courage_bonus=5,
    value=44,
    rarity="Uncommon",
    description="A strong round shield painted in northern colors.",
)

# ====================================================
# LOCATION EQUIPMENT - DENMARK
# ====================================================

DANE_AXE = Item(
    name="Dane Axe",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.AXE,
    might_bonus=5,
    courage_bonus=2,
    value=46,
    rarity="Uncommon",
    description="A broad Danish axe built for shield wall fighting.",
)

DANE_SWORD = Item(
    name="Dane Sword",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.SWORD,
    skill_bonus=5,
    leadership_bonus=2,
    value=52,
    rarity="Uncommon",
    description="A well-made sword carried by ambitious Danish warriors.",
)

DANE_SPEAR = Item(
    name="Dane Spear",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.SPEAR,
    skill_bonus=4,
    courage_bonus=3,
    value=44,
    rarity="Uncommon",
    description="A long ash spear common among Danish raiders.",
)

DANE_KNIFE = Item(
    name="Dane Knife",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.KNIFE,
    cunning_bonus=5,
    value=40,
    rarity="Uncommon",
    description="A practical knife favored by sailors and traders.",
)

DANE_BOW = Item(
    name="Dane Bow",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.BOW,
    skill_bonus=5,
    value=48,
    rarity="Uncommon",
    description="A sturdy bow of Danish yew.",
)

DANE_ARMOR = Item(
    name="Dane Armor",
    item_type=ItemType.ARMOR,
    slot=EquipmentSlot.ARMOR,
    vitality_bonus=5,
    courage_bonus=2,
    value=54,
    rarity="Uncommon",
    description="Heavy layered armor worn by seasoned Danish fighters.",
)

DANE_HELM = Item(
    name="Dane Helm",
    item_type=ItemType.HELM,
    slot=EquipmentSlot.HELM,
    vitality_bonus=4,
    courage_bonus=2,
    value=44,
    rarity="Uncommon",
    description="A strong iron helm with reinforced cheek guards.",
)

DANE_SHIELD = Item(
    name="Dane Shield",
    item_type=ItemType.SHIELD,
    slot=EquipmentSlot.SHIELD,
    courage_bonus=5,
    leadership_bonus=2,
    value=46,
    rarity="Uncommon",
    description="A painted round shield carried by Danish warbands.",
)

SILVER_ARM_RING = Item(
    name="Silver Arm Ring",
    item_type=ItemType.TRADE_ITEM,
    value=70,
    rarity="Uncommon",
    description="A silver arm ring used as both wealth and oath-gift.",
)

GOLDEN_TORQUE = Item(
    name="Golden Torque",
    item_type=ItemType.TRADE_ITEM,
    value=120,
    rarity="Rare",
    description="A heavy golden neck ring worn by powerful nobles.",
)

RUNED_WAR_BANNER = Item(
    name="Runed War Banner",
    item_type=ItemType.TRADE_ITEM,
    value=145,
    rarity="Rare",
    description="A battle banner stitched with old runes and symbols.",
)

# ====================================================
# LOCATION EQUIPMENT - GOTLAND
# ====================================================

GOTLANDISH_AXE = Item(
    name="Gotlandish Axe",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.AXE,
    might_bonus=4,
    skill_bonus=3,
    value=46,
    rarity="Uncommon",
    description="A compact Baltic axe suited for shipboard fighting.",
)

GOTLANDISH_SWORD = Item(
    name="Gotlandish Sword",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.SWORD,
    skill_bonus=5,
    cunning_bonus=2,
    value=54,
    rarity="Uncommon",
    description="A finely traded blade from the markets of Gotland.",
)

GOTLANDISH_SPEAR = Item(
    name="Gotlandish Spear",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.SPEAR,
    skill_bonus=5,
    seamanship_bonus=2,
    value=48,
    rarity="Uncommon",
    description="A flexible spear favored by Baltic sailors and traders.",
)

GOTLANDISH_KNIFE = Item(
    name="Gotlandish Knife",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.KNIFE,
    cunning_bonus=5,
    seamanship_bonus=2,
    value=42,
    rarity="Uncommon",
    description="A narrow trading knife common in Baltic ports.",
)

BALTIC_BOW = Item(
    name="Baltic Bow",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.BOW,
    skill_bonus=5,
    cunning_bonus=2,
    value=50,
    rarity="Uncommon",
    description="A bow built from flexible Baltic wood.",
)

MERCHANT_MAIL = Item(
    name="Merchant Mail",
    item_type=ItemType.ARMOR,
    slot=EquipmentSlot.ARMOR,
    vitality_bonus=5,
    cunning_bonus=2,
    value=56,
    rarity="Uncommon",
    description="Chain armor commonly worn by wealthy Baltic merchants.",
)

GOTLANDISH_HELM = Item(
    name="Gotlandish Helm",
    item_type=ItemType.HELM,
    slot=EquipmentSlot.HELM,
    vitality_bonus=3,
    seamanship_bonus=3,
    value=44,
    rarity="Uncommon",
    description="A lightweight helm suited for long voyages.",
)

GOTLANDISH_SHIELD = Item(
    name="Gotlandish Shield",
    item_type=ItemType.SHIELD,
    slot=EquipmentSlot.SHIELD,
    courage_bonus=4,
    seamanship_bonus=3,
    value=46,
    rarity="Uncommon",
    description="A reinforced shield painted in Baltic colors.",
)

AMBER_NECKLACE = Item(
    name="Amber Necklace",
    item_type=ItemType.TRADE_ITEM,
    value=75,
    rarity="Uncommon",
    description="A polished amber necklace prized by foreign traders.",
)

JEWELED_COMPASS = Item(
    name="Jeweled Compass",
    item_type=ItemType.TRADE_ITEM,
    value=130,
    rarity="Rare",
    description="A rare navigational device decorated with silver and amber.",
)

EASTERN_SILVER_HOARD = Item(
    name="Eastern Silver Hoard",
    item_type=ItemType.TRADE_ITEM,
    value=150,
    rarity="Rare",
    description="A cache of foreign silver gathered through Baltic trade.",
)

# ====================================================
# LOCATION EQUIPMENT - RUS'
# ====================================================

RUS_AXE = Item(
    name="Rus' Axe",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.AXE,
    might_bonus=5,
    skill_bonus=5,
    value=48,
    rarity="Uncommon",
    description="A broad axe traded through the Rus' riverlands.",
)

RUS_SWORD = Item(
    name="Rus' Sword",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.SWORD,
    might_bonus=5,
    skill_bonus=5,
    value=54,
    rarity="Uncommon",
    description="A river-forged sword prized by traveling warriors.",
)

RUS_SPEAR = Item(
    name="Rus' Spear",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.SPEAR,
    skill_bonus=6,
    value=48,
    rarity="Uncommon",
    description="A long spear suited for river fighting.",
)

RUS_KNIFE = Item(
    name="Rus' Knife",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.KNIFE,
    cunning_bonus=5,
    skill_bonus=5,
    value=40,
    rarity="Uncommon",
    description="A curved knife from the eastern trade routes.",
)

RUS_BOW = Item(
    name="Rus' Bow",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.BOW,
    skill_bonus=5,
    cunning_bonus=5,
    value=50,
    rarity="Uncommon",
    description="A compact bow useful along rivers and forests.",
)

RUS_ARMOR = Item(
    name="Rus' Armor",
    item_type=ItemType.ARMOR,
    slot=EquipmentSlot.ARMOR,
    vitality_bonus=5,
    courage_bonus=5,
    value=56,
    rarity="Uncommon",
    description="Layered armor influenced by eastern styles.",
)

RUS_HELM = Item(
    name="Rus' Helm",
    item_type=ItemType.HELM,
    slot=EquipmentSlot.HELM,
    vitality_bonus=6,
    value=44,
    rarity="Uncommon",
    description="A sturdy helm common among river warriors.",
)

RUS_SHIELD = Item(
    name="Rus' Shield",
    item_type=ItemType.SHIELD,
    slot=EquipmentSlot.SHIELD,
    courage_bonus=5,
    vitality_bonus=5,
    value=46,
    rarity="Uncommon",
    description="A reinforced shield from the Rus' riverlands.",
)

# ====================================================
# LOCATION EQUIPMENT - EAST ANGLIA
# ====================================================

EAST_ANGLIAN_AXE = Item(
    name="East Anglian Axe",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.AXE,
    might_bonus=8,
    skill_bonus=5,
    value=58,
    rarity="Uncommon",
    description="A sturdy axe taken from the eastern shores of Britain.",
)

EAST_ANGLIAN_SWORD = Item(
    name="East Anglian Sword",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.SWORD,
    skill_bonus=8,
    courage_bonus=5,
    value=68,
    rarity="Uncommon",
    description="A fine sword from East Anglia.",
)

EAST_ANGLIAN_SPEAR = Item(
    name="East Anglian Spear",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.SPEAR,
    skill_bonus=9,
    value=56,
    rarity="Uncommon",
    description="A well-made spear from Britain.",
)

EAST_ANGLIAN_KNIFE = Item(
    name="East Anglian Knife",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.KNIFE,
    cunning_bonus=7,
    skill_bonus=6,
    value=52,
    rarity="Uncommon",
    description="A sharp knife useful for raiders and scouts.",
)

EAST_ANGLIAN_BOW = Item(
    name="East Anglian Bow",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.BOW,
    skill_bonus=7,
    cunning_bonus=5,
    value=62,
    rarity="Uncommon",
    description="A strong bow of British make.",
)

EAST_ANGLIAN_ARMOR = Item(
    name="East Anglian Armor",
    item_type=ItemType.ARMOR,
    slot=EquipmentSlot.ARMOR,
    vitality_bonus=7,
    courage_bonus=7,
    value=72,
    rarity="Uncommon",
    description="Armor seized from a wealthy settlement.",
)

EAST_ANGLIAN_HELM = Item(
    name="East Anglian Helm",
    item_type=ItemType.HELM,
    slot=EquipmentSlot.HELM,
    vitality_bonus=8,
    value=56,
    rarity="Uncommon",
    description="A reinforced helm from East Anglia.",
)

EAST_ANGLIAN_SHIELD = Item(
    name="East Anglian Shield",
    item_type=ItemType.SHIELD,
    slot=EquipmentSlot.SHIELD,
    courage_bonus=8,
    vitality_bonus=5,
    value=60,
    rarity="Uncommon",
    description="A broad shield used by local defenders.",
)


# ====================================================
# LOCATION EQUIPMENT - NORTHUMBRIA
# ====================================================

NORTHUMBRIAN_AXE = Item(
    name="Northumbrian Axe",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.AXE,
    might_bonus=8,
    courage_bonus=6,
    value=64,
    rarity="Uncommon",
    description="A heavy axe from the north of Britain.",
)

NORTHUMBRIAN_SWORD = Item(
    name="Northumbrian Sword",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.SWORD,
    skill_bonus=9,
    value=76,
    rarity="Rare",
    description="A prized sword from Northumbria.",
)

NORTHUMBRIAN_SPEAR = Item(
    name="Northumbrian Spear",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.SPEAR,
    skill_bonus=8,
    courage_bonus=5,
    value=66,
    rarity="Uncommon",
    description="A long spear suited for shield walls.",
)

NORTHUMBRIAN_KNIFE = Item(
    name="Northumbrian Knife",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.KNIFE,
    cunning_bonus=10,
    value=58,
    rarity="Uncommon",
    description="A finely honed knife from Northumbria.",
)

NORTHUMBRIAN_BOW = Item(
    name="Northumbrian Bow",
    item_type=ItemType.WEAPON,
    slot=EquipmentSlot.PRIMARY_WEAPON,
    weapon_category=WeaponCategory.BOW,
    skill_bonus=9,
    value=72,
    rarity="Rare",
    description="A powerful bow from northern Britain.",
)

NORTHUMBRIAN_ARMOR = Item(
    name="Northumbrian Armor",
    item_type=ItemType.ARMOR,
    slot=EquipmentSlot.ARMOR,
    vitality_bonus=10,
    value=82,
    rarity="Rare",
    description="Strong armor taken from a wealthy northern lord.",
)

NORTHUMBRIAN_HELM = Item(
    name="Northumbrian Helm",
    item_type=ItemType.HELM,
    slot=EquipmentSlot.HELM,
    vitality_bonus=8,
    courage_bonus=6,
    value=68,
    rarity="Uncommon",
    description="A sturdy helm marked by northern craft.",
)

NORTHUMBRIAN_SHIELD = Item(
    name="Northumbrian Shield",
    item_type=ItemType.SHIELD,
    slot=EquipmentSlot.SHIELD,
    courage_bonus=10,
    value=70,
    rarity="Rare",
    description="A battle-tested shield from Northumbria.",
)

GILDED_BOOK_COVER = Item(
    name="Gilded Book Cover",
    item_type=ItemType.TRADE_ITEM,
    value=110,
    rarity="Rare",
    description="A jeweled cover stripped from a holy book.",
)

MONASTERY_RELIQUARY = Item(
    name="Monastery Reliquary",
    item_type=ItemType.TRADE_ITEM,
    value=140,
    rarity="Rare",
    description="A sacred container worth a fortune to the right buyer.",
)

ANGLO_SILVER_CROSS = Item(
    name="Anglo Silver Cross",
    item_type=ItemType.TRADE_ITEM,
    value=95,
    rarity="Uncommon",
    description="A silver cross taken from a wealthy church.",
)


ITEM_TEMPLATES = {
    item.name: item
    for item in [
    # Trader Items
        IRON_AXE,
        IRON_SWORD,
        IRON_SPEAR,
        IRON_KNIFE,
        ASH_BOW,
        LEATHER_ARMOR,
        LEATHER_HELM,
        REINFORCED_WOODEN_SHIELD,

        JEWELED_CARAFE,
        CARVED_AMBER_ICON,
        SILK_BOLT,
        SILVER_CHALICE,

    # Norse items
        NORDIC_AXE,
        NORDIC_SWORD,
        NORDIC_SPEAR,
        NORDIC_KNIFE,
        NORDIC_BOW,
        NORDIC_ARMOR,
        NORDIC_HELM,
        NORDIC_SHIELD,

    # Denmark Items
        DANE_AXE,
        DANE_SWORD,
        DANE_SPEAR,
        DANE_KNIFE,
        DANE_BOW,
        DANE_ARMOR,
        DANE_HELM,
        DANE_SHIELD,

        SILVER_ARM_RING,
        GOLDEN_TORQUE,
        RUNED_WAR_BANNER,

    # Gotland items
        GOTLANDISH_AXE,
        GOTLANDISH_SWORD,
        GOTLANDISH_SPEAR,
        GOTLANDISH_KNIFE,
        BALTIC_BOW,
        MERCHANT_MAIL,
        GOTLANDISH_HELM,
        GOTLANDISH_SHIELD,

        AMBER_NECKLACE,
        JEWELED_COMPASS,
        EASTERN_SILVER_HOARD,        
        
    # Rus' items
        RUS_AXE,
        RUS_SWORD,
        RUS_SPEAR,
        RUS_KNIFE,
        RUS_BOW,
        RUS_ARMOR,
        RUS_HELM,
        RUS_SHIELD,
        
    # East Anglia items    
        EAST_ANGLIAN_AXE,
        EAST_ANGLIAN_SWORD,
        EAST_ANGLIAN_SPEAR,
        EAST_ANGLIAN_KNIFE,
        EAST_ANGLIAN_BOW,
        EAST_ANGLIAN_ARMOR,
        EAST_ANGLIAN_HELM,
        EAST_ANGLIAN_SHIELD,

    # Northumbrian items
        NORTHUMBRIAN_AXE,
        NORTHUMBRIAN_SWORD,
        NORTHUMBRIAN_SPEAR,
        NORTHUMBRIAN_KNIFE,
        NORTHUMBRIAN_BOW,
        NORTHUMBRIAN_ARMOR,
        NORTHUMBRIAN_HELM,
        NORTHUMBRIAN_SHIELD,

        GILDED_BOOK_COVER,
        MONASTERY_RELIQUARY,
        ANGLO_SILVER_CROSS,        
    ]
}

TRADER_STOCK = [
    IRON_AXE,
    IRON_SWORD,
    IRON_SPEAR,
    IRON_KNIFE,
    ASH_BOW,
    LEATHER_ARMOR,
    LEATHER_HELM,
    REINFORCED_WOODEN_SHIELD,
]


def create_item_by_name(name: str, quality: ItemQuality | None = None) -> Item | None:
    template = ITEM_TEMPLATES.get(name)

    if not template:
        return None

    return copy_item(template, quality)


