"""Markdown rendering for the state graph, README block and archive.

GitHub strips scripts, styles, forms and event handlers from rendered markdown,
so the only interactivity available is following a link. Every tile is a linked
image pointing at the state that results from clicking it.
"""

import datetime as dt

import lightsout as lo

START_MARKER = "<!-- LIGHTS:START -->"
END_MARKER = "<!-- LIGHTS:END -->"

# The play pages state the goal; the profile README is kept deliberately terse.
RULES = "Click a tile to toggle it and its neighbours. Turn every light off."
README_RULES = "Click a tile to toggle it and its neighbours."

# The profile README carries no `## Lights Out` heading, so there is no
# `#lights-out` anchor to point at. Link the explanation itself instead.
ABOUT_PATH = "docs/how-it-works.md"

TILE_WIDTH = 64
ARCHIVE_TILE_WIDTH = 28


def state_id(state):
    """Canonical 4-lowercase-hex-digit name for a board."""
    return f"{state:04x}"


def state_path(state):
    """Sharded path, keeping each directory to ~256 files."""
    name = state_id(state)
    return f"s/{name[0]}/{name}.md"


def relative_link(from_state, to_state):
    """Link between two state files, both of which live one level inside `s/`."""
    name = state_id(to_state)
    return f"../{name[0]}/{name}.md"


def _tile(state, i, src_prefix, width, link_for):
    lit = "on" if state >> i & 1 else "off"
    img = f'<img src="{src_prefix}/img/{lit}.svg" width="{width}" alt="{lit}">'
    if link_for is None:
        return img
    return f"[{img}]({link_for(i)})"


def board_table(state, link_for=None, src_prefix="../..", width=TILE_WIDTH):
    """The 4x4 board as a markdown table.

    The header row is empty but must declare four cells, otherwise GitHub will
    not treat the delimiter row as a table.
    """
    lines = ["|  |  |  |  |", "|:-:|:-:|:-:|:-:|"]
    for r in range(4):
        cells = [_tile(state, r * 4 + c, src_prefix, width, link_for) for c in range(4)]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _archive_month(date):
    return f"{date:%Y-%m}"


def archive_path(date):
    return f"archive/{_archive_month(date)}.md"


def _coords(click_set):
    return [
        f"r{i // 4 + 1}c{i % 4 + 1}" for i in range(lo.CELLS) if click_set >> i & 1
    ]


def state_page(puzzle, state, repo):
    """One page per reachable board. The solved board gets a different body."""
    profile = f"https://github.com/{repo}"
    about = f"{profile}/blob/main/{ABOUT_PATH}"
    yesterday = puzzle.date - dt.timedelta(days=1)
    archive_url = f"{profile}/blob/main/{archive_path(yesterday)}"

    if state == 0x0000:
        board = board_table(state, link_for=None)
        return (
            f"# Lights Out · {puzzle.date}\n\n"
            f"## Solved 🎉\n\n"
            f"{board}\n\n"
            f"Every light is off. Today's board could be cleared in "
            f"**{puzzle.min_clicks} clicks** — how did you do?\n\n"
            f"[Play again]({relative_link(state, puzzle.start)}) · "
            f"[How it works]({about}) · "
            f"[Past puzzles]({archive_url})\n"
        )

    board = board_table(state, link_for=lambda i: relative_link(state, state ^ lo.MASKS[i]))
    remaining = lo.min_clicks(state)
    return (
        f"# Lights Out · {puzzle.date}\n\n"
        f"{RULES}\n\n"
        f"{board}\n\n"
        f"[↻ Reset]({relative_link(state, puzzle.start)}) · "
        f"[About]({about}) · "
        f"[Yesterday's solution]({archive_url})\n\n"
        f"<details><summary>Hint</summary>\n\n"
        f"{remaining} clicks from solved.\n\n"
        f"</details>\n"
    )


def readme_block(puzzle, repo):
    """The board as it appears on `main`.

    Relative links cannot cross branches, so every tile link is absolute. The
    images are relative because `img/` exists on `main` too.
    """
    def link_for(i):
        target = puzzle.start ^ lo.MASKS[i]
        return f"https://github.com/{repo}/blob/daily/{state_path(target)}"

    board = board_table(puzzle.start, link_for=link_for, src_prefix=".")
    return (
        f"{START_MARKER}\n"
        f"### Lights Out · {puzzle.date}\n\n"
        f"{README_RULES}\n"
        f"{board}\n"
        f"{END_MARKER}\n"
    )


def splice_readme(readme, block):
    """Replace only the region between the markers."""
    start = readme.find(START_MARKER)
    end = readme.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise ValueError(
            f"README is missing the {START_MARKER} / {END_MARKER} markers"
        )
    return readme[:start] + block.rstrip("\n") + readme[end + len(END_MARKER):]


def archive_entry(puzzle):
    """Yesterday's puzzle, board and solution, for the monthly archive."""
    board = board_table(
        puzzle.start, link_for=None, src_prefix="..", width=ARCHIVE_TILE_WIDTH
    )
    clicks = ", ".join(f"`{coord}`" for coord in _coords(puzzle.solution))
    return (
        f"## {puzzle.date}\n\n"
        f"{board}\n\n"
        f"Minimum solution: **{puzzle.min_clicks} clicks**\n\n"
        f"<details><summary>Solution</summary>\n\n"
        f"Click {clicks} — in any order, since clicks commute.\n\n"
        f"</details>\n"
    )
