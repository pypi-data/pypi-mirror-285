"""
Redefine command line tool (enable python -m redefine syntax)
"""

import sys


def main() -> None:  # needed for console script
    if not __package__:
        # To be able to run 'python redefine-<version>.whl/wheel':
        from pathlib import Path

        path = Path(__file__).parent.parent.as_posix()
        sys.path[0:0] = [path]
    from . import _cmd

    sys.exit(_cmd.execute_from_cmd())


if __name__ == "__main__":
    main()
