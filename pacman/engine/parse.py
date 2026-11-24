import json
import logging
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .constants import (
    DEFAULT_HIGHSCORE_FILENAME,
    DEFAULT_LEVEL_HEIGHT,
    DEFAULT_LEVEL_MAX_TIME,
    DEFAULT_LEVEL_WIDTH,
    DEFAULT_LIVES,
    DEFAULT_PACGUM,
    DEFAULT_POINTS_PER_GHOST,
    DEFAULT_POINTS_PER_PACGUM,
    DEFAULT_POINTS_PER_SUPER_PACGUM,
    DEFAULT_SEED,
    MAX_LEVEL_HEIGHT,
    MAX_LEVEL_TIME,
    MAX_LEVEL_WIDTH,
    MAX_LIVES,
    MAX_PACGUM,
    MAX_POINTS,
    MAX_SEED,
    MIN_LEVEL_HEIGHT,
    MIN_LEVEL_TIME,
    MIN_LEVEL_WIDTH,
    MIN_LEVELS,
    MIN_LIVES,
    MIN_PACGUM,
    MIN_POINTS,
    MIN_SEED,
)

_LOGGER = logging.getLogger(__name__)


class ConfigError(Exception):
    """Raised when the configuration file cannot be opened or parsed."""


@dataclass(frozen=True)
class LevelConfig:
    """
    Configuration for game level
    Attributes:
        width: maze width in cells
        heigth: maze height in cells
    """
    width: int = DEFAULT_LEVEL_WIDTH
    height: int = DEFAULT_LEVEL_HEIGHT


@dataclass(frozen=True)
class GameConfig:
    """
    Imutable validated configuration for the entire game

    Attributes:
        highscore_filename: Path or filename used to store highscores.
        levels: Sequence of validated level configurations (at least 10).
        lives: Starting number of player lives.
        pacgum: Target pacgum count or density parameter from config.
        points_per_pacgum: Score awarded per regular pacgum.
        points_per_super_pacgum: Score awarded per super-pacgum.
        points_per_ghost: Score awarded per eaten ghost.
        seed: Deterministic seed used for the first level.
        level_max_time: Time limit per level in seconds.
    """

    highscore_filename: str
    levels: tuple[LevelConfig, ...]
    lives: int
    pacgum: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    seed: int
    level_max_time: int


def parse_config_args(argv: Sequence[str]) -> Path:
    """Parse configs for args, returns and raises."""
    if len(argv) != 1:
        raise ConfigError(
            "Invalid arguments. Usage: python3 pac-man.py <config.json>"
        )
    path = Path(argv[0])
    if path.suffix.lower() != ".json":
        raise ConfigError(
            f"Invalid configuration file '{path}': expected a .json file."
        )
    return path


def strip_json_comments(raw_text: str) -> str:
    """
    Remove ``#``, ``//``, and ``/* ... */`` comments outside of json strings.
    """
    output: list[str] = []
    in_string = False
    escaped = False
    idx = 0
    length = len(raw_text)

    while idx < length:
        ch = raw_text[idx]
        if in_string:
            output.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            idx += 1
            continue

        if ch == '"':
            in_string = True
            output.append(ch)
            idx += 1
            continue

        if ch == "#" or (
            ch == "/" and idx + 1 < length and raw_text[idx + 1] == "/"
        ):
            while idx < length and raw_text[idx] != "\n":
                idx += 1
            continue

        if ch == "/" and idx + 1 < length and raw_text[idx + 1] == "*":
            idx += 2
            closed = False
            while idx < length:
                if (
                    raw_text[idx] == "*"
                    and idx + 1 < length
                    and raw_text[idx + 1] == "/"
                ):
                    idx += 2
                    closed = True
                    output.append(" ")
                    break
                if raw_text[idx] == "\n":
                    output.append("\n")
                idx += 1
            if not closed:
                raise ConfigError(
                    "Unterminated block comment in configuration file."
                )
            continue

        output.append(ch)
        idx += 1

    return "".join(output)


def _parse_int(
    data: dict[str, object],
    key: str,
    default: int,
    min_val: int,
    max_val: int,
    logger: logging.Logger,
) -> int:
    """Extract, validate, and clamp an integer field from a config dict."""
    if key not in data:
        logger.warning("Missing key '%s'; using default %d.", key, default)
        return default

    raw_val = data[key]
    if isinstance(raw_val, bool) or not isinstance(raw_val, int):
        logger.warning(
            "Invalid value for '%s' (expected int); using default %d.",
            key,
            default,
        )
        return default

    if raw_val < min_val:
        logger.warning(
            "Value %d for '%s' below minimum %d; clamping to %d.",
            raw_val,
            key,
            min_val,
            min_val,
        )
        return min_val

    if raw_val > max_val:
        logger.warning(
            "Value %d for '%s' above maximum %d; clamping to %d.",
            raw_val,
            key,
            max_val,
            max_val,
        )
        return max_val

    return raw_val


def _parse_nonempty_str(
    data: dict[str, object],
    key: str,
    default: str,
    logger: logging.Logger,
) -> str:
    """Extract and validate a non-empty string from a config dict."""
    if key not in data:
        logger.warning("Missing key '%s'; using default '%s'.", key, default)
        return default

    raw_val = data[key]
    if not isinstance(raw_val, str) or not raw_val.strip():
        logger.warning(
            "Invalid value for '%s' (expected non-empty string); "
            "using default '%s'.",
            key,
            default,
        )
        return default

    return raw_val.strip()


def _parse_levels(
    data: dict[str, object],
    logger: logging.Logger,
) -> tuple[LevelConfig, ...]:
    """Parse and validate level definitions, ensuring at least 10 levels."""
    levels: list[LevelConfig] = []
    raw_levels = data.get("level")

    if raw_levels is None:
        logger.warning(
            "Missing key 'level'; generating %d default levels.",
            MIN_LEVELS,
        )
    elif not isinstance(raw_levels, list) or len(raw_levels) == 0:
        logger.warning(
            "Invalid or empty 'level' list; generating %d default levels.",
            MIN_LEVELS,
        )
    else:
        for idx, entry in enumerate(raw_levels):
            if not isinstance(entry, dict):
                logger.warning(
                    "Invalid entry at level[%d]; using default dimensions.",
                    idx,
                )
                levels.append(LevelConfig())
                continue

            entry_dict: dict[str, object] = {
                key: value
                for key, value in entry.items()
                if isinstance(key, str)
            }
            width = _parse_int(
                entry_dict,
                "width",
                DEFAULT_LEVEL_WIDTH,
                MIN_LEVEL_WIDTH,
                MAX_LEVEL_WIDTH,
                logger,
            )
            height = _parse_int(
                entry_dict,
                "height",
                DEFAULT_LEVEL_HEIGHT,
                MIN_LEVEL_HEIGHT,
                MAX_LEVEL_HEIGHT,
                logger,
            )
            levels.append(LevelConfig(width=width, height=height))

    if len(levels) < MIN_LEVELS:
        template = levels[-1] if levels else LevelConfig()
        if levels:
            logger.warning(
                "Only %d level(s) defined; padding to %d levels.",
                len(levels),
                MIN_LEVELS,
            )
        while len(levels) < MIN_LEVELS:
            levels.append(template)

    return tuple(levels)


def load_config(
    config_path: str | Path,
    logger: logging.Logger | None = None,
) -> GameConfig:
    """Load, sanitize, and validate a Pac-Man JSON configuration file.

    Unknown keys are ignored. Missing or out-of-range fields are logged and
    clamped to safe defaults.

    Args:
        config_path: Path to the ``.json`` configuration file.
        logger: Optional logger instance for warnings.

    Returns:
        Validated immutable GameConfig instance.

    Raises:
        ConfigError: If the file is missing, unreadable, not ``.json``,
            contains invalid JSON syntax, or its root is not a JSON object.
    """
    log = logger if logger is not None else _LOGGER
    path = Path(config_path)

    if path.suffix.lower() != ".json":
        raise ConfigError(
            f"Invalid configuration file '{path}': expected a .json file."
        )
    if not path.exists():
        raise ConfigError(f"Configuration file not found: '{path}'.")
    if not path.is_file():
        raise ConfigError(f"Configuration path is not a file: '{path}'.")

    try:
        raw_text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ConfigError(
            f"Failed to read configuration file '{path}': {exc}"
        ) from exc

    cleaned_text = strip_json_comments(raw_text)

    try:
        parsed: object = json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"Invalid JSON syntax in '{path}' "
            f"(line {exc.lineno}, column {exc.colno}): {exc.msg}."
        ) from exc

    if not isinstance(parsed, dict):
        raise ConfigError(
            f"Invalid configuration in '{path}': root must be a JSON object."
        )

    data: dict[str, object] = {
        key: value for key, value in parsed.items() if isinstance(key, str)
    }

    return GameConfig(
        highscore_filename=_parse_nonempty_str(
            data, "highscore_filename", DEFAULT_HIGHSCORE_FILENAME, log
        ),
        levels=_parse_levels(data, log),
        lives=_parse_int(
            data, "lives", DEFAULT_LIVES, MIN_LIVES, MAX_LIVES, log
        ),
        pacgum=_parse_int(
            data, "pacgum", DEFAULT_PACGUM, MIN_PACGUM, MAX_PACGUM, log
        ),
        points_per_pacgum=_parse_int(
            data,
            "points_per_pacgum",
            DEFAULT_POINTS_PER_PACGUM,
            MIN_POINTS,
            MAX_POINTS,
            log,
        ),
        points_per_super_pacgum=_parse_int(
            data,
            "points_per_super_pacgum",
            DEFAULT_POINTS_PER_SUPER_PACGUM,
            MIN_POINTS,
            MAX_POINTS,
            log,
        ),
        points_per_ghost=_parse_int(
            data,
            "points_per_ghost",
            DEFAULT_POINTS_PER_GHOST,
            MIN_POINTS,
            MAX_POINTS,
            log,
        ),
        seed=_parse_int(
            data, "seed", DEFAULT_SEED, MIN_SEED, MAX_SEED, log
        ),
        level_max_time=_parse_int(
            data,
            "level_max_time",
            DEFAULT_LEVEL_MAX_TIME,
            MIN_LEVEL_TIME,
            MAX_LEVEL_TIME,
            log,
        ),
    )
