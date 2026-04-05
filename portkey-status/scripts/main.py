#!/usr/bin/env python3
"""portkey-status CLI

Usage:
  uv run python main.py [check [filter]]   Test all models (optionally filtered)
  uv run python main.py credits            List virtual key budget limits
"""

import sys


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"

    if cmd == "check":
        import healthcheck
        healthcheck.run(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "credits":
        import credits
        credits.run()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
