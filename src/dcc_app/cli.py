"""Command line interface for the DCC game."""

from __future__ import annotations

from typing import Dict, Iterable, Tuple

from .campaign import run_ai_campaign
from .game import GameState

DIRECTIONS: Dict[str, Tuple[int, int]] = {
    "north": (0, -1),
    "south": (0, 1),
    "west": (-1, 0),
    "east": (1, 0),
}


def format_status(state: GameState) -> str:
    player = state.player
    stats = player.stats
    return (
        f"Name: {player.name} | HP: {player.hit_points} | AC: {player.armor_class_total()} | "
        f"Level: {player.level} (XP {player.experience})\n"
        f"Stats STR:{stats.strength} DEX:{stats.agility} STA:{stats.stamina} "
        f"PER:{stats.personality} INT:{stats.intelligence} LCK:{stats.luck}\n"
        f"Inventory: {', '.join(item.name for item in player.inventory) or 'Empty'}\n"
        f"Spells: {', '.join(f'{spell}({slots})' for spell, slots in player.spell_slots.items())}"
    )


def show_help() -> str:
    return (
        "Commands:\n"
        "  help - Show this message\n"
        "  map - Display the current dungeon map\n"
        "  move <north|south|east|west> - Move in a direction\n"
        "  attack <north|south|east|west> - Attack towards a direction\n"
        "  cast <spell> <direction?> - Cast a spell (direction required for offensive spells)\n"
        "  use - Use an item at your feet\n"
        "  rest - Recover a bit of health and spells\n"
        "  look - Inspect the current tile\n"
        "  status - Show hero information\n"
        "  log - Show recent log entries\n"
        "  ai - Let the built-in AI run the campaign"
    )


def run_cli(commands: Iterable[str] | None = None) -> None:
    state = GameState.new_game()
    print("Welcome to the Dungeon Crawl Classics (DCC) console experience! Type 'help' for commands.")
    if commands is None:
        command_iter = iter(lambda: input("> "), "")
    else:
        command_iter = iter(commands)
    for raw in command_iter:
        if commands is None:
            cmd = raw.strip()
        else:
            cmd = raw
            print(f"> {cmd}")
        if not cmd:
            continue
        parts = cmd.split()
        verb = parts[0].lower()
        if verb in {"quit", "exit"}:
            print("Farewell, adventurer.")
            break
        elif verb == "help":
            print(show_help())
        elif verb == "map":
            print(state.render_map())
        elif verb == "move":
            if len(parts) < 2 or parts[1].lower() not in DIRECTIONS:
                print("Specify a direction: north, south, east, or west.")
                continue
            dx, dy = DIRECTIONS[parts[1].lower()]
            print(state.move_player(dx, dy))
        elif verb == "attack":
            if len(parts) < 2 or parts[1].lower() not in DIRECTIONS:
                print("Specify a direction to attack.")
                continue
            dx, dy = DIRECTIONS[parts[1].lower()]
            target = (state.player_position[0] + dx, state.player_position[1] + dy)
            if target not in state.monsters:
                print("There is nothing to attack there.")
            else:
                print(state.attack(target))
        elif verb == "cast":
            if len(parts) < 2:
                print("Specify a spell name.")
                continue
            spell = parts[1].lower()
            target_pos = None
            if len(parts) >= 3 and parts[2].lower() in DIRECTIONS:
                dx, dy = DIRECTIONS[parts[2].lower()]
                target_pos = (state.player_position[0] + dx, state.player_position[1] + dy)
            print(state.cast_spell(spell, target_pos))
        elif verb == "use":
            print(state.use_item(state.player_position))
        elif verb == "rest":
            print(state.rest())
        elif verb == "look":
            print(state.check_tile())
        elif verb == "status":
            print(format_status(state))
        elif verb == "log":
            print("\n".join(state.log.recent()))
        elif verb == "ai":
            transcript = run_ai_campaign(state)
            print("\n".join(transcript))
            break
        else:
            print("Unknown command. Type 'help' for a list of commands.")
        if not state.player.is_alive():
            print("Your journey ends here.")
            break
