"""Procedural map generation for the dungeon crawl."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

TILE_FLOOR = "."
TILE_WALL = "#"
TILE_DOOR = "+"
TILE_PLAYER = "@"
TILE_MONSTER = "M"
TILE_ITEM = "!"


@dataclass
class Room:
    x: int
    y: int
    width: int
    height: int

    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    def intersects(self, other: "Room") -> bool:
        return not (
            self.x + self.width < other.x
            or other.x + other.width < self.x
            or self.y + self.height < other.y
            or other.y + other.height < self.y
        )


@dataclass
class DungeonMap:
    width: int
    height: int
    tiles: List[List[str]] = field(init=False)
    rooms: List[Room] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.tiles = [[TILE_WALL for _ in range(self.width)] for _ in range(self.height)]

    def carve_room(self, room: Room) -> None:
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                self.tiles[y][x] = TILE_FLOOR

    def carve_hallway(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        x1, y1 = start
        x2, y2 = end
        if random.choice([True, False]):
            self._carve_horizontal(x1, x2, y1)
            self._carve_vertical(y1, y2, x2)
        else:
            self._carve_vertical(y1, y2, x1)
            self._carve_horizontal(x1, x2, y2)

    def _carve_horizontal(self, x1: int, x2: int, y: int) -> None:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[y][x] = TILE_FLOOR

    def _carve_vertical(self, y1: int, y2: int, x: int) -> None:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[y][x] = TILE_FLOOR

    def place_feature(self, symbol: str, position: Tuple[int, int]) -> None:
        x, y = position
        self.tiles[y][x] = symbol

    def available_positions(self) -> List[Tuple[int, int]]:
        return [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if self.tiles[y][x] == TILE_FLOOR
        ]

    def render(self, overlays: Dict[Tuple[int, int], str] | None = None) -> str:
        overlays = overlays or {}
        lines = []
        for y, row in enumerate(self.tiles):
            rendered_row = []
            for x, tile in enumerate(row):
                rendered_row.append(overlays.get((x, y), tile))
            lines.append("".join(rendered_row))
        return "\n".join(lines)


def generate_dungeon(width: int = 40, height: int = 20, room_attempts: int = 12) -> DungeonMap:
    dungeon = DungeonMap(width=width, height=height)
    for _ in range(room_attempts):
        w, h = random.randint(4, 8), random.randint(3, 6)
        x = random.randint(1, width - w - 1)
        y = random.randint(1, height - h - 1)
        room = Room(x=x, y=y, width=w, height=h)
        if any(room.intersects(other) for other in dungeon.rooms):
            continue
        dungeon.carve_room(room)
        if dungeon.rooms:
            prev_center = dungeon.rooms[-1].center()
            dungeon.carve_hallway(prev_center, room.center())
        dungeon.rooms.append(room)

    for room in dungeon.rooms:
        cx, cy = room.center()
        dungeon.place_feature(TILE_DOOR, (cx, room.y))
        dungeon.place_feature(TILE_DOOR, (cx, room.y + room.height - 1))

    return dungeon
