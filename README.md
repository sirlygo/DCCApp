# DCC Console Game

This project contains a self-contained Dungeon Crawl Classics inspired console game. It features:

- Procedurally generated dungeon maps with rooms, corridors, doors, monsters, and loot.
- Full player character sheet with spells, equipment, and advancement.
- Turn-based combat and rest mechanics faithful to classic dungeon crawling.
- A campaign generator capable of running AI-directed expeditions through the dungeon.

## Getting Started

1. Ensure you have Python 3.10 or newer installed.
2. Install dependencies (only the standard library is required).
3. Launch the game:

```bash
python -m dcc_app.main
```

You will be greeted with the command prompt for the game. Type `help` to see available commands.

## Gameplay Overview

- `map`: Renders the dungeon with your hero (`@`), monsters (`M`), doors (`+`), items (`!`), and terrain.
- `move <direction>`: Move north, south, east, or west. Bumping into a monster automatically attacks it.
- `attack <direction>`: Attack a monster in an adjacent tile.
- `cast <spell> <direction?>`: Cast spells such as `mystic_bolt` or `healing_word`.
- `use`: Use an item located on your tile (healing potions, magical gear, etc.).
- `rest`: Recover some hit points and spell slots while risking wandering monsters.
- `look`: Describe your current surroundings.
- `status`: Inspect your character sheet and spell slots.
- `ai`: Engage the built-in campaign AI that plays the game automatically.

## AI Campaigns

Selecting the `ai` command hands over control to an automated expedition script. The AI:

1. Generates a narrative hook and quest list for the run.
2. Chooses actions using heuristics (attacking, exploring, resting) based on current objectives.
3. Plays until all quests are completed, the hero falls, or the turn limit is reached.

The AI transcript is printed to the console, allowing you to observe the full campaign progression.

## Project Structure

- `src/dcc_app/data.py`: Static data for monsters, items, and story hooks.
- `src/dcc_app/entities.py`: Character, monster, and combat logic.
- `src/dcc_app/maps.py`: Procedural generation of dungeon maps.
- `src/dcc_app/game.py`: Core game state, actions, and encounter log.
- `src/dcc_app/campaign.py`: Campaign quest generation and AI autoplay.
- `src/dcc_app/cli.py`: Command-line interface for manual play and AI runs.
- `src/dcc_app/main.py`: Entry point when executed as a module.

Enjoy delving into the dungeon!
