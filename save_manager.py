from __future__ import annotations

import json
from pathlib import Path

from campaign import Campaign


SAVE_DIR = Path("saves")


def ensure_save_dir() -> None:
    SAVE_DIR.mkdir(exist_ok=True)

def save_filename_for_slot(slot: str) -> str:
    slot = slot.strip()

    if not slot.isdigit():
        slot = "1"

    slot_number = max(1, int(slot))
    return f"save_{slot_number}.json"

def save_campaign(campaign: Campaign, filename: str = "save_1.json") -> Path:
    ensure_save_dir()

    save_path = SAVE_DIR / filename

    with save_path.open("w", encoding="utf-8") as f:
        json.dump(campaign.to_dict(), f, indent=4)

    return save_path


def load_campaign(filename: str = "save_1.json") -> Campaign:
    save_path = SAVE_DIR / filename

    with save_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return Campaign.from_dict(data)


def save_exists(filename: str = "save_1.json") -> bool:
    return (SAVE_DIR / filename).exists()