# How it works

A playable Lights Out puzzle that lives entirely in a GitHub repository as
static markdown. No JavaScript, no server, no GitHub Pages.

## The trick

There is no JavaScript here, and there cannot be — GitHub strips `<script>`,
`<style>`, `<form>`, `<iframe>` and every event handler out of rendered
markdown. The only interactive thing left in a README is a link.

So the game is played by *navigation*. Every board you could possibly reach from
today's start position has been pre-computed and written to its own markdown
file, and each tile is a link to the file representing the board after that
click. The game engine is the file graph itself.

Clicking is addition modulo 2, so order never matters and clicking twice undoes
itself — which is what keeps the state space down to a tractable 4,096 boards
instead of the full 65,536.

## The maths

A 4×4 board is a 16-bit vector over GF(2), row-major, bit 0 = top-left. The
click matrix `A` has column *i* set at cell *i* and its orthogonal neighbours.
It has **rank 12** and **nullity 4**, so its null space holds 16 "quiet
patterns" — click sets that change nothing at all.

Two consequences fall out of that:

- Only **1 in 16** of the 65,536 possible boards can be solved. The daily start
  board is built by applying clicks to a dark board, never by randomising 16
  bits, so it is always solvable.
- The shortest solution comes from solving `A·x = s` by Gaussian elimination for
  any particular `x₀`, then taking the smallest `x₀ ⊕ n` across all 16 quiet
  patterns.

The observed distribution of minimum solution lengths across all 4,096 solvable
boards:

| clicks | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| boards | 1 | 16 | 120 | 560 | 1387 | 1440 | 540 | 32 |

The hardest board on a 4×4 grid needs just **7** clicks. Puzzles are drawn from
the 5–7 band, which is 2,012 of the 4,096 states.

## The shape of the repository

`main` holds the profile, the generator and the archive. An orphan branch called
`daily` holds nothing but today's state graph, force-pushed each morning so
history never accumulates — 4,096 files a day committed normally would be
several GB of permanent history within a year.

State files are sharded by their first hex digit, `s/c/c732.md`, keeping each
directory to about 256 entries. A flat directory of 4,096 files is slow in the
GitHub UI and paginates at 1,000.

Only two images exist for the entire game — `on.svg` and `off.svg`. Rendering a
board image per state would be the obvious approach and the wrong one: two fixed
files keep the repository small *and* sidestep GitHub's Camo image cache
entirely, because a stale cache of a file that never changes is always correct.

## What it deliberately does not do

No move counter, no streaks, no scores, no leaderboards, no shareable result
grid. State lives entirely in the URL and visitors cannot be identified, so
anything resembling a per-player statistic would be a fabrication rather than a
measurement. Task-list checkboxes are clickable only in issues and pull
requests, never in a rendered README, so they are no use either.

## Building it yourself

```bash
python tools/generate.py --date 2026-08-04   # write the state graph
python tools/verify.py   --date 2026-08-04   # check it before publishing
python -m unittest discover -s tools -t tools
```

`verify.py` is the gate: it re-derives the reachable set, checks every link
resolves, checks every page's tiles match the bits of its own filename, and
checks each tile links to `s ⊕ mask[i]`. A broken push means a dead puzzle on
the profile until tomorrow, so nothing is published unless it passes.

See [maintenance.md](maintenance.md) for running it.
