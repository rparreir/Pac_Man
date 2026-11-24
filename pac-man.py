"""Entry point."""
import sys


def main() -> None:
    """Main."""
    try:
        arg_len = len(sys.argv)
        if arg_len != 2:
            print("Usage: python3 pac-man.py <config.json>", file=sys.stderr)
            sys.exit(1)
        else:
            # entry point
            print("Correct amount of args")
            sys.exit(0)

    except (KeyboardInterrupt):
        print("Program Interrupted", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

# TODO: rever docstring quando o parser estiver ligado e o jogo tiver a rodar
