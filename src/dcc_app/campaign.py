"""Campaign generator and AI-driven exploration."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Iterable, List, Sequence

from . import data
from .game import GameState
from .maps import TILE_DOOR, TILE_FLOOR


@dataclass
class Quest:
    title: str
    goal_description: str
    completion_condition: Callable[[GameState], bool]


@dataclass
class Campaign:
    name: str
    synopsis: str
    quests: List[Quest]

    def next_quest(self, state: GameState) -> Quest | None:
        for quest in self.quests:
            if not quest.completion_condition(state):
                return quest
        return None


def _monster_cleared_condition(state: GameState) -> bool:
    return not state.monsters


def _find_item_condition(state: GameState) -> bool:
    return any(item.name == "Ring of Wisdom" for item in state.player.inventory)


def _reach_exit_condition(state: GameState) -> bool:
    px, py = state.player_position
    return state.dungeon.tiles[py][px] == TILE_DOOR


def generate_campaign(seed: int | None = None) -> Campaign:
    rng = random.Random(seed)
    synopsis = rng.choice(data.AI_CAMPAIGN_STORIES)
    quests = [
        Quest(
            title="Cleanse the Depths",
            goal_description="Eliminate every hostile creature that lurks here.",
            completion_condition=_monster_cleared_condition,
        ),
        Quest(
            title="Recover the Relic",
            goal_description="Find the Ring of Wisdom hidden within the complex.",
            completion_condition=_find_item_condition,
        ),
        Quest(
            title="Escape the Labyrinth",
            goal_description="Reach a door and escape back to the surface.",
            completion_condition=_reach_exit_condition,
        ),
    ]
    return Campaign(name="AI-Directed Expedition", synopsis=synopsis, quests=quests)


@dataclass
class CampaignAI:
    """Simple heuristic based agent for auto-playing a campaign."""

    prioritised_actions: Sequence[str] = ("attack", "cast", "move", "rest")

    def choose_action(self, state: GameState) -> str:
        quest = generate_campaign().next_quest(state)
        if quest and "Eliminate" in quest.goal_description and state.monsters:
            return "attack"
        if quest and "Find" in quest.goal_description and state.items:
            return "move"
        if state.player.hit_points < state.player.stats.stamina:
            return "rest"
        return random.choice(self.prioritised_actions)

    def perform_action(self, state: GameState) -> str:
        action = self.choose_action(state)
        if action == "attack":
            return self._attack_nearest(state)
        if action == "cast":
            return self._cast_bolt(state)
        if action == "move":
            return self._move_towards_goal(state)
        if action == "rest":
            return state.rest()
        return "The AI hesitates."

    def _attack_nearest(self, state: GameState) -> str:
        if not state.monsters:
            return "No monsters to attack."
        px, py = state.player_position
        target = min(state.monsters.keys(), key=lambda pos: abs(pos[0] - px) + abs(pos[1] - py))
        dx = target[0] - px
        dy = target[1] - py
        if abs(dx) + abs(dy) == 1:
            return state.attack(target)
        return self._move_towards(state, target)

    def _cast_bolt(self, state: GameState) -> str:
        for spell, slots in state.player.spell_slots.items():
            if spell == "mystic_bolt" and slots > 0 and state.monsters:
                px, py = state.player_position
                target = min(state.monsters.keys(), key=lambda pos: abs(pos[0] - px) + abs(pos[1] - py))
                return state.cast_spell(spell, target)
        return "No spells available."

    def _move_towards_goal(self, state: GameState) -> str:
        quest = generate_campaign().next_quest(state)
        if quest and quest.title == "Recover the Relic" and state.items:
            px, py = state.player_position
            target = min(state.items.keys(), key=lambda pos: abs(pos[0] - px) + abs(pos[1] - py))
            return self._move_towards(state, target)
        return self._explore(state)

    def _move_towards(self, state: GameState, target: tuple[int, int]) -> str:
        px, py = state.player_position
        dx = 0 if target[0] == px else (1 if target[0] > px else -1)
        dy = 0 if target[1] == py else (1 if target[1] > py else -1)
        if abs(dx) > abs(dy):
            first = (dx, 0)
            second = (0, dy)
        else:
            first = (0, dy)
            second = (dx, 0)
        for step in (first, second):
            if step != (0, 0):
                result = state.move_player(*step)
                if "cannot" not in result and "wall" not in result:
                    return result
        return "The AI cannot find a path."

    def _explore(self, state: GameState) -> str:
        px, py = state.player_position
        options = [
            (px + 1, py),
            (px - 1, py),
            (px, py + 1),
            (px, py - 1),
        ]
        random.shuffle(options)
        for nx, ny in options:
            if 0 <= nx < state.dungeon.width and 0 <= ny < state.dungeon.height:
                if state.dungeon.tiles[ny][nx] in {TILE_FLOOR, TILE_DOOR}:
                    return state.move_player(nx - px, ny - py)
        return "The AI waits."


def run_ai_campaign(state: GameState, max_turns: int = 200) -> List[str]:
    campaign = generate_campaign()
    ai = CampaignAI()
    transcript: List[str] = [f"Campaign: {campaign.name}", campaign.synopsis]
    for turn in range(max_turns):
        quest = campaign.next_quest(state)
        if quest is None:
            transcript.append("All campaign objectives completed!")
            break
        transcript.append(f"Turn {turn + 1}: Current quest - {quest.title}: {quest.goal_description}")
        transcript.extend(state.log.recent(1))
        transcript.append(ai.perform_action(state))
        if not state.player.is_alive():
            transcript.append("The AI party has fallen.")
            break
    return transcript
