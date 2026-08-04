"""Integrity checks for a generated puzzle (spec §9).

Runs before the push. A broken push means a dead puzzle on the profile until
tomorrow, so every check here is a build-failing condition.

    python tools/verify.py --date 2026-08-04
    python tools/verify.py --days 365          # a year, locally, without pushing
"""

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

import lightsout as lo
import puzzle
import render

EXPECTED_STATES = 4096
TILE = re.compile(r'<img src="[^"]*img/(on|off)\.svg"')
RELATIVE_LINK = re.compile(r"\]\((\.\./[^)]+)\)")
ABSOLUTE_LINK = re.compile(r"https://github\.com/([^/]+/[^/]+)/blob/daily/([^)\s]+)")


def check_state_space(day):
    """§9.1, §9.2 -- exactly 4,096 reachable states, including the solved board."""
    states = lo.reachable(day.start)
    errors = []
    if len(states) != EXPECTED_STATES:
        errors.append(f"reachable set has {len(states)} states, expected {EXPECTED_STATES}")
    if 0x0000 not in states:
        errors.append("solved board 0x0000 is not reachable from the start")
    return errors


def check_difficulty(day):
    """§9.8 -- the start board sits inside the configured band."""
    low, high = puzzle.BAND
    actual = lo.min_clicks(day.start)
    if actual is None:
        return [f"start board {day.state_id} is unsolvable"]
    if not low <= actual <= high:
        return [f"start board {day.state_id} needs {actual} clicks, outside band {low}-{high}"]
    return []


def check_files(day, out):
    """§9.3 -- exactly one file per reachable state, at its sharded path."""
    out = Path(out)
    expected = {render.state_path(s) for s in lo.reachable(day.start)}
    found = {p.relative_to(out).as_posix() for p in out.glob("s/*/*.md")}

    errors = [f"missing state file: {path}" for path in sorted(expected - found)]
    errors += [f"unexpected state file: {path}" for path in sorted(found - expected)]
    return errors


def _pages(out):
    for path in sorted(Path(out).glob("s/*/*.md")):
        yield path, path.read_text(encoding="utf-8")


def check_links(out):
    """§9.4 -- every relative link resolves to a file that exists."""
    out = Path(out)
    errors = []
    for path, text in _pages(out):
        for target in RELATIVE_LINK.findall(text):
            if not (path.parent / target).resolve().exists():
                errors.append(f"{path.name}: dangling link -> {target}")
    return errors


def check_tiles(out):
    """§9.5 -- 16 tile images per page, matching the bits of the state ID."""
    errors = []
    for path, text in _pages(out):
        tiles = TILE.findall(text)
        if len(tiles) != lo.CELLS:
            errors.append(f"{path.name}: has {len(tiles)} tile images, expected 16")
            continue
        state = int(path.stem, 16)
        for i, tile in enumerate(tiles):
            if tile != ("on" if state >> i & 1 else "off"):
                errors.append(f"{path.name}: tile pattern does not match state at cell {i}")
                break
    return errors


def check_click_targets(day, out):
    """§9.6 -- clicking cell i from state s must lead to s XOR mask[i]."""
    out = Path(out)
    errors = []
    for state in sorted(lo.reachable(day.start)):
        if state == 0x0000:
            continue  # the solved page deliberately has no tile links
        path = out / render.state_path(state)
        if not path.is_file():
            continue  # already reported by check_files; don't crash on it here
        text = path.read_text(encoding="utf-8")
        targets = RELATIVE_LINK.findall(text)[: lo.CELLS]
        if len(targets) != lo.CELLS:
            errors.append(f"{path.name}: has {len(targets)} tile links, expected 16")
            continue
        for i, target in enumerate(targets):
            expected = render.relative_link(state, state ^ lo.MASKS[i])
            if target != expected:
                errors.append(
                    f"{path.name}: cell {i} links to {target}, expected {expected}"
                )
    return errors


def check_readme(repo, root, out):
    """§9.7 -- both markers present, and every URL between them exists on `daily`."""
    text = (Path(root) / "README.md").read_text(encoding="utf-8")
    start = text.find(render.START_MARKER)
    end = text.find(render.END_MARKER)
    if start == -1 or end == -1 or end < start:
        return ["README is missing the LIGHTS:START / LIGHTS:END markers"]

    block = text[start:end]
    urls = ABSOLUTE_LINK.findall(block)
    if len(urls) != lo.CELLS:
        return [f"README block has {len(urls)} board links, expected 16"]

    errors = []
    for owner_repo, path in urls:
        if owner_repo != repo:
            errors.append(f"README links to {owner_repo}, expected {repo}")
        elif not (Path(out) / path).exists():
            errors.append(f"README links to {path}, which does not exist on daily")
    return errors


def verify(day, repo, out, root):
    """Every §9 criterion. An empty list means the build may be published."""
    return (
        check_state_space(day)
        + check_difficulty(day)
        + check_files(day, out)
        + check_links(out)
        + check_tiles(out)
        + check_click_targets(day, out)
        + check_readme(repo, root, out)
    )


def main(argv=None, env=None):
    env = os.environ if env is None else env
    parser = argparse.ArgumentParser(description="Verify a generated Lights Out puzzle.")
    parser.add_argument("--date", type=dt.date.fromisoformat, default=None)
    parser.add_argument("--out", default="build/daily")
    parser.add_argument("--root", default=".")
    parser.add_argument("--days", type=int, default=1,
                        help="also check puzzle selection for N days from --date")
    args = parser.parse_args(argv)

    repo = env.get("GITHUB_REPOSITORY")
    if not repo:
        print("verify: GITHUB_REPOSITORY is not set", file=sys.stderr)
        return 1

    date = args.date or dt.datetime.now(dt.timezone.utc).date()
    errors = verify(puzzle.for_date(date), repo, args.out, args.root)

    # Selection-only sweep: proves a year of puzzles is well formed without
    # writing a year of state graphs.
    for offset in range(1, args.days):
        day = puzzle.for_date(date + dt.timedelta(days=offset))
        errors += [f"{day.date}: {e}" for e in check_state_space(day) + check_difficulty(day)]

    if errors:
        print(f"verify: {len(errors)} problem(s) found", file=sys.stderr)
        for error in errors[:40]:
            print(f"  - {error}", file=sys.stderr)
        if len(errors) > 40:
            print(f"  ... and {len(errors) - 40} more", file=sys.stderr)
        return 1

    print(f"verify: {date} OK - 4096 states, links, tiles and README all consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
