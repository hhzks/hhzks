"""Generate a day's Lights Out state graph, README board and archive entry.

    python tools/generate.py                      # today, into build/daily
    python tools/generate.py --date 2026-08-04    # any day, reproducibly

Writes ~4,096 tiny markdown files -- one per reachable board -- plus the two
tile images. The state graph is meant for the orphan `daily` branch; the README
and archive belong to `main`.
"""

import argparse
import datetime as dt
import os
import re
import shutil
import sys
from pathlib import Path

import lightsout as lo
import puzzle
import render

EXPECTED_STATES = 4096
RELATIVE_LINK = re.compile(r"\]\((\.\./[^)]+)\)")


class GeneratorError(Exception):
    """Something is wrong with the build. Fail loudly rather than publish."""


def check_graph(states):
    """Spec §3: the reachable set must be exactly 4,096 states including 0x0000."""
    if len(states) != EXPECTED_STATES:
        raise GeneratorError(
            f"reachable set has {len(states)} states, expected {EXPECTED_STATES}"
        )
    if 0x0000 not in states:
        raise GeneratorError("solved board 0x0000 is not reachable from the start")


def relative_targets(text):
    """Every relative link target in a rendered page."""
    return RELATIVE_LINK.findall(text)


def write_state_graph(day, repo, out, root):
    """Write one page per reachable board, sharded by first hex digit."""
    out, root = Path(out), Path(root)
    states = lo.reachable(day.start)
    check_graph(states)

    # A previous day's graph would otherwise linger as unreachable dead files.
    if (out / "s").exists():
        shutil.rmtree(out / "s")

    for state in states:
        path = out / render.state_path(state)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render.state_page(day, state, repo), encoding="utf-8")

    images = out / "img"
    images.mkdir(parents=True, exist_ok=True)
    for name in ("on.svg", "off.svg"):
        shutil.copyfile(root / "img" / name, images / name)

    return len(states)


def write_readme(day, repo, root):
    """Rewrite only the region between the markers."""
    path = Path(root) / "README.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(render.splice_readme(text, render.readme_block(day, repo)), encoding="utf-8")


def append_archive(day, root):
    """Append a puzzle to its monthly archive. Returns False if already there."""
    path = Path(root) / render.archive_path(day.date)
    path.parent.mkdir(parents=True, exist_ok=True)

    heading = f"## {day.date}"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if heading in existing:
        return False

    if not existing:
        existing = f"# Lights Out · {day.date:%B %Y}\n\nPast puzzles and their solutions.\n"
    path.write_text(f"{existing.rstrip()}\n\n{render.archive_entry(day)}", encoding="utf-8")
    return True


def main(argv=None, env=None):
    env = os.environ if env is None else env
    parser = argparse.ArgumentParser(description="Generate a daily Lights Out puzzle.")
    parser.add_argument("--date", type=dt.date.fromisoformat, default=None,
                        help="puzzle date (default: today, UTC)")
    parser.add_argument("--out", default="build/daily",
                        help="where to write the state graph")
    parser.add_argument("--root", default=".", help="checkout of `main`")
    args = parser.parse_args(argv)

    repo = env.get("GITHUB_REPOSITORY")
    if not repo:
        raise GeneratorError("GITHUB_REPOSITORY is not set; refusing to guess OWNER/REPO")

    date = args.date or dt.datetime.now(dt.timezone.utc).date()
    today = puzzle.for_date(date)

    count = write_state_graph(today, repo, args.out, args.root)
    write_readme(today, repo, args.root)
    # Yesterday's puzzle only -- today's solution stays unpublished until tomorrow.
    append_archive(puzzle.for_date(date - dt.timedelta(days=1)), args.root)

    print(
        f"{date}: start {today.state_id}, {today.min_clicks} clicks minimum, "
        f"{count} states -> {args.out}"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GeneratorError as exc:
        sys.exit(f"generate: {exc}")
