"""Static game data used by the DCC application."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class MonsterTemplate:
    """Reusable monster information."""

    name: str
    hit_points: int
    attack_bonus: int
    damage: str
    armor_class: int
    description: str


MONSTER_LIBRARY: Dict[str, MonsterTemplate] = {
    "goblin": MonsterTemplate(
        name="Goblin",
        hit_points=5,
        attack_bonus=1,
        damage="1d6",
        armor_class=11,
        description="A sneaky goblin with a jagged blade and an appetite for treasure.",
    ),
    "skeleton": MonsterTemplate(
        name="Skeleton",
        hit_points=8,
        attack_bonus=2,
        damage="1d8",
        armor_class=12,
        description="A rattling skeleton animated by dark sorcery.",
    ),
    "orc": MonsterTemplate(
        name="Orc",
        hit_points=10,
        attack_bonus=3,
        damage="1d10",
        armor_class=13,
        description="A brutal orc warrior hungry for battle.",
    ),
    "cultist": MonsterTemplate(
        name="Cultist",
        hit_points=7,
        attack_bonus=2,
        damage="1d6",
        armor_class=11,
        description="An unhinged cultist devoted to forgotten gods.",
    ),
    "ogre": MonsterTemplate(
        name="Ogre",
        hit_points=18,
        attack_bonus=4,
        damage="2d6",
        armor_class=12,
        description="A hulking ogre capable of crushing armor with a single blow.",
    ),
}


@dataclass(frozen=True)
class ItemTemplate:
    """Reusable item description."""

    name: str
    bonus: int
    description: str


ITEM_LIBRARY: Dict[str, ItemTemplate] = {
    "healing_potion": ItemTemplate(
        name="Healing Potion",
        bonus=8,
        description="A sparkling draught that restores a modest amount of vitality.",
    ),
    "mighty_axe": ItemTemplate(
        name="Mighty Axe",
        bonus=2,
        description="An axe of dwarven make that adds to the wielder's lethality.",
    ),
    "cloak_of_shadows": ItemTemplate(
        name="Cloak of Shadows",
        bonus=2,
        description="A shimmering cloak that makes the wearer harder to hit.",
    ),
    "ring_of_wisdom": ItemTemplate(
        name="Ring of Wisdom",
        bonus=1,
        description="A ring that sharpens the mind and empowers spellcasting.",
    ),
}


AI_CAMPAIGN_STORIES: List[str] = [
    "A star fell from the heavens, crashing into the mire. Cultists gather; you must reach the crater before they complete the ritual.",
    "Villagers vanish during the new moon. Beneath the old abbey, tunnels hide a sinister force enthroning a demon.",
    "A once gentle forest has twisted overnight. Fey spirits cry for help as a faerie queen is corrupted by an unknown artifact.",
    "Sea-raiders pillage the coast, emboldened by a relic stolen from a dragon turtle's nest. Recover the relic before it awakens.",
    "A plague of living shadows stalks the streets. Discover the mastermind weaving darkness through the city catacombs.",
]
