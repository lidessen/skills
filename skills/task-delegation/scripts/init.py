#!/usr/bin/env python3
"""Create an editable task delegation policy without replacing an existing one."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "policy.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="Policy file to create")
    parser.add_argument("--dry-run", action="store_true", help="Check without writing")
    args = parser.parse_args(argv)
    output = args.output.expanduser()

    try:
        content = TEMPLATE.read_text(encoding="utf-8")
    except OSError as error:
        print(f"Cannot read policy template: {error}", file=sys.stderr)
        return 1

    if output.exists() or output.is_symlink():
        print(f"Policy already exists; left unchanged: {output}", file=sys.stderr)
        return 1
    if not output.parent.is_dir():
        print(f"Parent directory does not exist: {output.parent}", file=sys.stderr)
        return 1
    if args.dry_run:
        print(f"Would create policy: {output}")
        return 0

    try:
        with output.open("x", encoding="utf-8") as policy:
            policy.write(content)
    except FileExistsError:
        print(f"Policy already exists; left unchanged: {output}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Cannot create policy: {error}", file=sys.stderr)
        return 1

    print(f"Created policy: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
