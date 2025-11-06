"""Core game loop and mechanics."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from . import data
from .entities import Monster, PlayerCharacter, Stats, create_item
from .maps import (
    TILE_DOOR,
    TILE_FLOOR,
    TILE_ITEM,
    TILE_MONSTER,
    TILE_PLAYER,
    DungeonMap,
    generate_dungeon,
)
from .utils import roll_dice

Position = Tuple[int, int]


@dataclass
class EncounterLog:
    messages: List[str] = field(default_factory=list)

    def add(self, message: str) -> None:
        self.messages.append(message)

    def recent(self, limit: int = 10) -> List[str]:
        return self.messages[-limit:]


@dataclass
class GameState:
    dungeon: DungeonMap
    player: PlayerCharacter
    player_position: Position
    monsters: Dict[Position, Monster]
    items: Dict[Position, str]
    log: EncounterLog = field(default_factory=EncounterLog)
    explored: Dict[Position, bool] = field(default_factory=dict)

    @classmethod
    def new_game(cls, seed: int | None = None) -> "GameState":
        if seed is not None:
            random.seed(seed)
        dungeon = generate_dungeon()
        player_room = random.choice(dungeon.rooms)
        px, py = player_room.center()
        stats = Stats(
            strength=roll_dice("3d6"),
            agility=roll_dice("3d6"),
            stamina=roll_dice("3d6"),
            personality=roll_dice("3d6"),
            intelligence=roll_dice("3d6"),
            luck=roll_dice("3d6"),
        )
        player = PlayerCharacter(name="Adventurer", hit_points=roll_dice("1d8") + stats.stamina_mod + 8, armor_class=12, stats=stats)

        monsters: Dict[Position, Monster] = {}
        items: Dict[Position, str] = {}
        for room in dungeon.rooms[1:]:
            if random.random() < 0.7:
                key = random.choice(list(data.MONSTER_LIBRARY.keys()))
                monster = Monster.from_template(key)
                monsters[room.center()] = monster
        for pos in random.sample(dungeon.available_positions(), k=min(5, len(dungeon.available_positions()))):
            key = random.choice(list(data.ITEM_LIBRARY.keys()))
            items[pos] = key

        state = cls(
            dungeon=dungeon,
            player=player,
            player_position=(px, py),
            monsters=monsters,
            items=items,
        )
        state.log.add("You awaken in a strange dungeon, torch in hand.")
        return state

    def render_map(self) -> str:
        overlays: Dict[Position, str] = {}
        overlays[self.player_position] = TILE_PLAYER
        for pos in self.monsters:
            overlays[pos] = TILE_MONSTER
        for pos in self.items:
            overlays[pos] = TILE_ITEM
        return self.dungeon.render(overlays)

    def move_player(self, dx: int, dy: int) -> str:
        x, y = self.player_position
        nx, ny = x + dx, y + dy
        if not (0 <= nx < self.dungeon.width and 0 <= ny < self.dungeon.height):
            return "You cannot move there."
        tile = self.dungeon.tiles[ny][nx]
        if tile not in {TILE_FLOOR, TILE_DOOR}:
            return "A wall blocks your path."
        target = (nx, ny)
        if target in self.monsters:
            return self.attack(target)
        self.player_position = target
        self.explored[target] = True
        self.log.add(f"You move to {target}.")
        self.monster_turns()
        return "You move cautiously."

    def attack(self, position: Position) -> str:
        monster = self.monsters[position]
        attack_roll = self.player.attack_roll()
        if attack_roll >= monster.armor_class_total():
            damage = max(1, self.player.roll_damage())
            monster.take_damage(damage)
            if not monster.is_alive():
                del self.monsters[position]
                xp = roll_dice("2d8")
                self.player.gain_experience(xp)
                self.log.add(f"You slay {monster.name}! (+{xp} XP)")
                self.monster_turns()
                return f"You slay {monster.name}!"
            self.log.add(f"You hit {monster.name} for {damage} damage.")
            self.monster_turns()
            return f"You hit {monster.name}."
        self.log.add(f"Your attack misses {monster.name}.")
        self.monster_turns()
        return "You miss."

    def cast_spell(self, spell_name: str, target_position: Position | None = None) -> str:
        if spell_name not in self.player.spell_slots:
            return f"{spell_name} is not a spell you know."
        if spell_name == "healing_word":
            result = self.player.cast_spell(spell_name, self.player)
            self.log.add(result)
            self.monster_turns()
            return result
        if target_position is None or target_position not in self.monsters:
            return "No target for the spell."
        result = self.player.cast_spell(spell_name, self.monsters[target_position])
        if "hits" in result and target_position not in self.monsters:
            self.player.gain_experience(roll_dice("1d12"))
        self.log.add(result)
        self.monster_turns()
        return result

    def use_item(self, position: Position | None = None) -> str:
        if position and position in self.items:
            item_key = self.items.pop(position)
        else:
            item_key = next(iter(self.items.values()), None)
            if item_key:
                # remove arbitrary item from dict
                for pos, key in list(self.items.items()):
                    if key == item_key:
                        del self.items[pos]
                        break
        if not item_key:
            return "There is nothing to use."
        item = create_item(item_key)
        if item_key == "healing_potion":
            amount = roll_dice("2d4") + 2
            self.player.heal(amount)
            message = f"You drink a healing potion and recover {amount} hit points."
        elif item_key == "mighty_axe":
            self.player.damage = "1d10"
            message = "You wield the mighty axe. Your attacks hit harder!"
        elif item_key == "cloak_of_shadows":
            self.player.armor_class += item.bonus
            message = "You don the cloak of shadows, harder to strike now."
        elif item_key == "ring_of_wisdom":
            for spell in self.player.spell_slots:
                self.player.spell_slots[spell] += 1
            message = "Wisdom flows through you; spell slots refreshed." 
        else:
            message = f"You examine {item.name} but gain no benefit."
        self.player.inventory.append(item)
        self.log.add(message)
        self.monster_turns()
        return message

    def rest(self) -> str:
        heal = roll_dice("1d4") + self.player.stats.stamina_mod
        self.player.heal(max(1, heal))
        for spell in self.player.spell_slots:
            self.player.spell_slots[spell] = max(self.player.spell_slots[spell], 1)
        self.log.add("You take a moment to rest and recover.")
        self.monster_turns(resting=True)
        return "You rest briefly."

    def monster_turns(self, resting: bool = False) -> None:
        for position, monster in list(self.monsters.items()):
            if not monster.is_alive():
                continue
            px, py = self.player_position
            mx, my = position
            if abs(px - mx) + abs(py - my) == 1:
                attack_roll = monster.attack_roll()
                if attack_roll >= self.player.armor_class_total():
                    damage = max(1, monster.roll_damage())
                    self.player.take_damage(damage)
                    self.log.add(f"{monster.name} hits you for {damage} damage!")
                else:
                    self.log.add(f"{monster.name} misses you.")
                if not self.player.is_alive():
                    self.log.add("You collapse. The dungeon claims another soul.")
                    return
            else:
                if resting and random.random() < 0.5:
                    continue
                step = self._step_towards(position, self.player_position)
                if step and step not in self.monsters and self.dungeon.tiles[step[1]][step[0]] == TILE_FLOOR:
                    self.monsters[step] = self.monsters.pop(position)

    def _step_towards(self, start: Position, goal: Position) -> Position | None:
        sx, sy = start
        gx, gy = goal
        options: List[Position] = []
        if gx > sx:
            options.append((sx + 1, sy))
        elif gx < sx:
            options.append((sx - 1, sy))
        if gy > sy:
            options.append((sx, sy + 1))
        elif gy < sy:
            options.append((sx, sy - 1))
        random.shuffle(options)
        for option in options:
            x, y = option
            if 0 <= x < self.dungeon.width and 0 <= y < self.dungeon.height:
                if self.dungeon.tiles[y][x] in {TILE_FLOOR, TILE_DOOR}:
                    return option
        return None

    def check_tile(self) -> str:
        if self.player_position in self.items:
            item = data.ITEM_LIBRARY[self.items[self.player_position]].name
            return f"You see {item} here."
        if self.player_position in self.monsters:
            monster = self.monsters[self.player_position]
            return monster.describe()
        return "The chamber is quiet."
