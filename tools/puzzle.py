"""Deterministic daily puzzle selection (spec §4).

The start board is chosen from the states reachable from all-off, so it is
solvable by construction -- never by randomising 16 bits, which would be
unsolvable 15 times out of 16.
"""

import datetime as dt
import hashlib
from dataclasses import dataclass
from functools import lru_cache

import lightsout as lo

# Chosen from the observed distribution of minimum solution lengths: the
# hardest possible 4x4 board is 7 clicks, so this band is the top half of the
# reachable space (2,012 of 4,096 states).
BAND = (5, 7)

# Seeds collide often enough that consecutive days can land on the same board.
# Step past anything used in the preceding month.
REPEAT_WINDOW = 30

# Boards that look like a generator bug even though they are perfectly valid.
TRIVIAL = frozenset(
    {
        0x0000,  # all off
        0xFFFF,  # all on
        0x000F, 0x00F0, 0x0F00, 0xF000,  # single rows
        0x1111, 0x2222, 0x4444, 0x8888,  # single columns
        0x9009,  # four corners
        0x5A5A, 0xA5A5,  # checkerboards
        0xF99F,  # border ring
        0x0660,  # centre block
        0x8421, 0x1248,  # diagonals
        0x00FF, 0xFF00, 0x3333, 0xCCCC,  # halves
    }
)


@dataclass(frozen=True)
class Puzzle:
    date: object
    start: int
    min_clicks: int
    solution: int

    @property
    def state_id(self):
        return f"{self.start:04x}"


def seed_for(date):
    """A stable 64-bit seed for a calendar date."""
    digest = hashlib.sha256(date.isoformat().encode()).hexdigest()
    return int(digest[:16], 16)


def is_trivial(state):
    """True for boards whose symmetry makes them look broken."""
    return state in TRIVIAL


@lru_cache(maxsize=1)
def candidates():
    """Every non-trivial board in the difficulty band, in a stable order."""
    low, high = BAND
    return tuple(
        sorted(
            s
            for s in lo.reachable(0x0000)
            if low <= lo.min_clicks(s) <= high and not is_trivial(s)
        )
    )


def _unadjusted(date, pool):
    """The raw seed pick, before repeat avoidance."""
    return pool[seed_for(date) % len(pool)]


def for_date(date):
    """The puzzle for a given day.

    Repeat avoidance compares against the *unadjusted* picks of preceding days
    so the lookback stays one level deep instead of recursing to the epoch.
    """
    pool = candidates()
    recent = {
        _unadjusted(date - dt.timedelta(days=k), pool)
        for k in range(1, REPEAT_WINDOW + 1)
    }
    index = seed_for(date) % len(pool)
    while pool[index] in recent:
        index = (index + 1) % len(pool)

    start = pool[index]
    solution = lo.min_click_set(start)
    return Puzzle(date=date, start=start, min_clicks=solution.bit_count(), solution=solution)
