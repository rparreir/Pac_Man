"""Entry point."""
import logging
import sys

from pacman.engine import ConfigError, load_config, parse_config_args


def main() -> None:
    """Main with parsing CLI arguments and load configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )
    logger = logging.getLogger(__name__)

    try:
        config_path = parse_config_args(sys.argv[1:])
        config = load_config(config_path)
        logger.info(
            "Configuration loaded: %d level, %d lives, seed=%d.",
            len(config.levels),
            config.lives,
            config.seed
        )
        # TODO(#17) inicializar o GameEngine e a UI com 'config'.
        sys.exit(0)
    except ConfigError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except (KeyboardInterrupt):
        print("Program Interrupted", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

# TODO: rever docstring quando o parser estiver ligado e o jogo tiver a rodar
