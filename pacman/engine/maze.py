"""Adapter around the external mazegenerator package."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import IntEnum

from mazegenerator import MazeGenerator

from .constants import (
    MIN_GENERATOR_DIM,
    WALL_EAST,
    WALL_NORTH,
    WALL_SOLID,
    WALL_SOUTH,
    WALL_WEST,
)
from .parse import LevelConfig


class MazeAdapterError(Exception):
    """Raised when maze generation or validation fails."""


class Direction(IntEnum):
    """Cardinal directions mapped to maze wall bitmask flags."""

    NORTH = WALL_NORTH
    EAST = WALL_EAST
    SOUTH = WALL_SOUTH
    WEST = WALL_WEST


DIRECTION_DELTAS: dict[Direction, tuple[int, int]] = {
    Direction.NORTH: (0, -1),
    Direction.EAST: (1, 0),
    Direction.SOUTH: (0, 1),
    Direction.WEST: (-1, 0),
}


@dataclass(frozen=True)
class MazeData:
    """Immutable validated maze grid produced by the adapter.

    Attributes:
        width: Number of columns in the maze.
        height: Number of rows in the maze.
        seed: Seed passed to the generator (0 means random).
        grid: 2D tuple indexed as ``grid[y][x]`` with wall bitmasks.
    """

    width: int
    height: int
    seed: int
    grid: tuple[tuple[int, ...], ...]

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if ``(x, y)`` lies inside the maze grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_solid(self, x: int, y: int) -> bool:
        """Return True if cell ``(x, y)`` is solid ('42' block) or outside."""
        if not self.in_bounds(x, y):
            return True
        return self.grid[y][x] == WALL_SOLID

    def has_wall(self, x: int, y: int, direction: Direction) -> bool:
        """Return True if ``(x, y)`` has a wall in ``direction``."""
        if not self.in_bounds(x, y):
            return True
        return bool(self.grid[y][x] & int(direction))

    def can_move(self, x: int, y: int, direction: Direction) -> bool:
        """Return True if movement from ``(x, y)`` in ``direction`` is open."""
        if self.has_wall(x, y, direction):
            return False
        dx, dy = DIRECTION_DELTAS[direction]
        nx, ny = x + dx, y + dy
        return self.in_bounds(nx, ny) and not self.is_solid(nx, ny)

    def corridor_cells(self) -> tuple[tuple[int, int], ...]:
        """Return all walkable ``(x, y)`` coordinates (non-solid cells)."""
        return tuple(
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if self.grid[y][x] != WALL_SOLID
        )


def _validate_grid(
    raw_maze: object,
    width: int,
    height: int,
) -> tuple[tuple[int, ...], ...]:
    """Validate shape and bitmask values of a raw maze matrix."""
    if not isinstance(raw_maze, list) or len(raw_maze) != height:
        raise MazeAdapterError(
            f"Generator returned invalid maze height (expected {height})."
        )

    rows: list[tuple[int, ...]] = []
    has_walkable = False

    for y, raw_row in enumerate(raw_maze):
        if not isinstance(raw_row, list) or len(raw_row) != width:
            raise MazeAdapterError(
                f"Generator returned invalid row width at y={y} "
                f"(expected {width})."
            )

        clean_row: list[int] = []
        for x, cell in enumerate(raw_row):
            if (
                isinstance(cell, bool)
                or not isinstance(cell, int)
                or cell < 0
                or cell > WALL_SOLID
            ):
                raise MazeAdapterError(
                    f"Invalid cell bitmask at ({x}, {y}): {cell!r}."
                )
            if cell != WALL_SOLID:
                has_walkable = True
            clean_row.append(cell)

        rows.append(tuple(clean_row))

    if not has_walkable:
        raise MazeAdapterError("Generated maze contains no walkable cells.")

    return tuple(rows)


def generate_maze(
    width: int,
    height: int,
    seed: int = 0,
    generator_factory: Callable[..., object] | None = None,
) -> MazeData:
    """Generate a Pac-Man-compatible maze using the external package.

    Args:
        width: Maze width in cells (must be >= 2).
        height: Maze height in cells (must be >= 2).
        seed: Positive integer for deterministic mazes, or 0 for random.
        generator_factory: Optional callable overriding MazeGenerator (tests).

    Returns:
        Validated immutable MazeData instance.

    Raises:
        MazeAdapterError: If dimensions are invalid or the generator fails.
    """
    if width < MIN_GENERATOR_DIM or height < MIN_GENERATOR_DIM:
        raise MazeAdapterError(
            f"Maze dimensions ({width}x{height}) must be at least "
            f"{MIN_GENERATOR_DIM}x{MIN_GENERATOR_DIM}."
        )

    effective_seed = max(0, seed)
    factory: Callable[..., object] = (
        generator_factory if generator_factory is not None else MazeGenerator
    )

    try:
        generator = factory(
            size=(width, height),
            perfect=False,
            seed=effective_seed,
        )
        raw_maze: object = getattr(generator, "maze", None)
    except Exception as exc:
        raise MazeAdapterError(f"Maze generator failed: {exc}") from exc

    grid = _validate_grid(raw_maze, width, height)
    return MazeData(
        width=width,
        height=height,
        seed=effective_seed,
        grid=grid,
    )


def generate_level_maze(
    level_config: LevelConfig,
    level_index: int,
    base_seed: int,
    generator_factory: Callable[..., object] | None = None,
) -> MazeData:
    """Generate the maze for a specific level index.

    Level 0 uses ``base_seed`` deterministically; subsequent levels use
    random generation (``seed=0``), as required by the specification.

    Args:
        level_config: Dimensions for the requested level.
        level_index: Zero-based level index.
        base_seed: Configured seed for level 1.
        generator_factory: Optional callable overriding MazeGenerator (tests).

    Returns:
        Validated immutable MazeData for the requested level.

    Raises:
        MazeAdapterError: If ``level_index`` is negative or generation fails.
    """
    if level_index < 0:
        raise MazeAdapterError(
            f"Invalid level_index {level_index}: must be >= 0."
        )

    level_seed = base_seed if level_index == 0 and base_seed > 0 else 0
    return generate_maze(
        width=level_config.width,
        height=level_config.height,
        seed=level_seed,
        generator_factory=generator_factory,
    )
