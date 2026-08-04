"""Core maths for 4x4 Lights Out over GF(2).

A board is a 16-bit vector, row-major, bit 0 = top-left. Clicking cell i adds
MASKS[i] mod 2, so click order is irrelevant and clicking twice is a no-op.
"""

from collections import Counter, deque

SIZE = 4
CELLS = SIZE * SIZE


def _build_masks():
    masks = []
    for r in range(SIZE):
        for c in range(SIZE):
            mask = 1 << (r * SIZE + c)
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < SIZE and 0 <= nc < SIZE:
                    mask |= 1 << (nr * SIZE + nc)
            masks.append(mask)
    return tuple(masks)


MASKS = _build_masks()


def click(state, i):
    """Board after clicking cell i."""
    return state ^ MASKS[i]


def apply(state, click_set):
    """Board after clicking every cell whose bit is set in click_set."""
    for i in range(CELLS):
        if click_set >> i & 1:
            state ^= MASKS[i]
    return state


# --- GF(2) linear algebra -------------------------------------------------
#
# A is the CELLS x CELLS click matrix: column i is MASKS[i]. We reduce the
# augmented system [A | I] once at import time. Each reduced row carries a
# `track` mask recording which original rows were combined into it, so the
# right-hand side for any board s is just popcount(track & s) mod 2.


def _reduce():
    rows = []
    for j in range(CELLS):
        coeffs = 0
        for i in range(CELLS):
            if MASKS[i] >> j & 1:
                coeffs |= 1 << i
        rows.append(coeffs | (1 << (CELLS + j)))

    pivots = {}
    r = 0
    for col in range(CELLS):
        piv = next((k for k in range(r, CELLS) if rows[k] >> col & 1), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for k in range(CELLS):
            if k != r and rows[k] >> col & 1:
                rows[k] ^= rows[r]
        pivots[col] = r
        r += 1
    return rows, pivots, r


_ROWS, _PIVOTS, _RANK = _reduce()
_COEFFS = [row & 0xFFFF for row in _ROWS]
_TRACK = [row >> CELLS for row in _ROWS]
# Rows below the rank have no coefficients left; they are the consistency
# conditions a board must satisfy to be solvable at all.
_CONDITIONS = tuple(_TRACK[k] for k in range(_RANK, CELLS))


def _build_nullspace():
    free = [c for c in range(CELLS) if c not in _PIVOTS]
    basis = []
    for f in free:
        vector = 1 << f
        for col, r in _PIVOTS.items():
            if _COEFFS[r] >> f & 1:
                vector |= 1 << col
        basis.append(vector)

    vectors = [0]
    for vector in basis:
        vectors += [v ^ vector for v in vectors]
    return tuple(sorted(vectors))


NULLSPACE = _build_nullspace()


def rank():
    """Rank of the click matrix over GF(2)."""
    return _RANK


def is_solvable(state):
    """True if some click set clears this board."""
    return all((track & state).bit_count() % 2 == 0 for track in _CONDITIONS)


def solve(state):
    """A click set clearing the board, or None if the board is unsolvable."""
    if not is_solvable(state):
        return None
    click_set = 0
    for col, r in _PIVOTS.items():
        if (_TRACK[r] & state).bit_count() % 2:
            click_set |= 1 << col
    return click_set


# --- shortest solutions and the state graph -------------------------------


def min_click_set(state):
    """The smallest click set clearing the board, or None if unsolvable.

    Every solution is a particular solution xored with a quiet pattern, so the
    16 cosets are the entire search space.
    """
    particular = solve(state)
    if particular is None:
        return None
    return min((particular ^ quiet for quiet in NULLSPACE), key=int.bit_count)


def min_clicks(state):
    """How many clicks the board is from solved, or None if unsolvable."""
    best = min_click_set(state)
    return None if best is None else best.bit_count()


def reachable(start):
    """Every board reachable from `start` by clicking, via BFS over 16 edges."""
    seen = {start}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        for i in range(CELLS):
            nxt = state ^ MASKS[i]
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def distribution(start=0x0000):
    """Counts of minimum solution length across the reachable state space."""
    return dict(sorted(Counter(min_clicks(s) for s in reachable(start)).items()))
