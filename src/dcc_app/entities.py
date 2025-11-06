"""Entity and combat definitions for the DCC game."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from . import data
from .utils import clamp, roll_dice


@dataclass
class Stats:
    strength: int = 10
    agility: int = 10
    stamina: int = 10
    personality: int = 10
    intelligence: int = 10
    luck: int = 10

    def modifier(self, value: int) -> int:
        return (value - 10) // 2

    @property
    def strength_mod(self) -> int:
        return self.modifier(self.strength)

    @property
    def agility_mod(self) -> int:
        return self.modifier(self.agility)

    @property
    def stamina_mod(self) -> int:
        return self.modifier(self.stamina)

    @property
    def personality_mod(self) -> int:
        return self.modifier(self.personality)

    @property
    def intelligence_mod(self) -> int:
        return self.modifier(self.intelligence)

    @property
    def luck_mod(self) -> int:
        return self.modifier(self.luck)


@dataclass
class Item:
    key: str
    name: str
    description: str
    bonus: int = 0


@dataclass
class Actor:
    name: str
    hit_points: int
    armor_class: int
    stats: Stats = field(default_factory=Stats)
    inventory: List[Item] = field(default_factory=list)
    attack_bonus: int = 0
    damage: str = "1d4"

    def is_alive(self) -> bool:
        return self.hit_points > 0

    def take_damage(self, amount: int) -> None:
        self.hit_points = clamp(self.hit_points - amount, 0, self.hit_points)

    def heal(self, amount: int) -> None:
        self.hit_points += amount

    def attack_roll(self) -> int:
        return roll_dice("1d20") + self.attack_bonus + self.stats.strength_mod

    def roll_damage(self) -> int:
        return roll_dice(self.damage) + self.stats.strength_mod

    def armor_class_total(self) -> int:
        return self.armor_class + self.stats.agility_mod


@dataclass
class PlayerCharacter(Actor):
    level: int = 1
    experience: int = 0
    spell_slots: Dict[str, int] = field(default_factory=lambda: {"mystic_bolt": 2, "healing_word": 1})

    def gain_experience(self, amount: int) -> None:
        self.experience += amount
        while self.experience >= self._xp_to_next_level():
            self.experience -= self._xp_to_next_level()
            self.level += 1
            self.hit_points += roll_dice("1d8") + self.stats.stamina_mod

    def _xp_to_next_level(self) -> int:
        return 100 + (self.level - 1) * 50

    def cast_spell(self, spell_name: str, target: Actor) -> str:
        if self.spell_slots.get(spell_name, 0) <= 0:
            return f"No {spell_name} slots left!"

        self.spell_slots[spell_name] -= 1
        if spell_name == "mystic_bolt":
            attack = roll_dice("1d20") + self.stats.intelligence_mod + self.level
            if attack >= target.armor_class_total():
                dmg = roll_dice("2d6") + self.level
                target.take_damage(max(1, dmg))
                return f"Mystic bolt hits {target.name} for {dmg} damage!"
            return f"Mystic bolt fizzles against {target.name}."
        if spell_name == "healing_word":
            heal = roll_dice("1d6") + self.stats.personality_mod
            target.heal(max(1, heal))
            return f"Healing word restores {heal} hit points to {target.name}."
        return f"Unknown spell: {spell_name}"


@dataclass
class Monster(Actor):
    template_key: str = ""

    @classmethod
    def from_template(cls, key: str) -> "Monster":
        template = data.MONSTER_LIBRARY[key]
        return cls(
            name=template.name,
            hit_points=template.hit_points,
            armor_class=template.armor_class,
            attack_bonus=template.attack_bonus,
            damage=template.damage,
            template_key=key,
        )

    def describe(self) -> str:
        template = data.MONSTER_LIBRARY[self.template_key]
        return template.description


def create_item(key: str) -> Item:
    template = data.ITEM_LIBRARY[key]
    return Item(key=key, name=template.name, description=template.description, bonus=template.bonus)
