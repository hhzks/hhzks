A playable Lights Out puzzle that lives entirely in a GitHub repository as
static markdown.

## How it works

There is no JavaScript here, and there cannot be (GitHub strips `<script>`,
`<style>`, `<form>`, `<iframe>` and every event handler out of rendered
markdown). The only interactive thing left in a README is a link.

Hence, the game is played by *navigation*. Every board you could possibly reach from
the day's start position is been pre-computed and written to its own markdown
file, and each tile is a link to the file representing the board after that
click. The game engine is the file graph itself.

Clicking is addition modulo 2, so order never matters and clicking twice undoes
itself which is what keeps the state space down to a tractable **4,096** boards
(instead of the full **65,536**).

## The maths

A 4×4 board is a 16-bit vector over $\mathbb{F}_2$, row-major, bit 0 = top-left. The
click matrix `A` has column *i* set at cell *i* and its orthogonal neighbours.
It has **rank 12** and **nullity 4**, so its null space holds 16 "quiet
patterns" (click sets that change nothing at all).

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

The hardest board on a 4×4 grid requires just **7** clicks. Puzzles are drawn from
the 5–7 band, which is 2,012 of the 4,096 states.

## Repository structure

`main` holds the profile, the generator and the archive. An orphan branch called
`daily` holds nothing but today's state graph, force-pushed each morning so
history never accumulates, since 4,096 files a day committed normally would be
several GB of permanent history within a year.

State files are sharded by their first hex digit, `s/c/c732.md`, keeping each
directory to about 256 entries. A flat directory of 4,096 files is slow in the
GitHub UI and paginates at 1,000.

Three images exist for the entire game: `on.svg`, `off.svg`, and `init.svg`. 
You can probably guess what `on.svg` and `off.svg` are, and `init.svg` is
just a special *animated* version of `on.svg` used for the start position, mainly
to grab the players attention.

## Limitations

No move counter, no streaks, no scores, no leaderboards, no shareable result
grid; state lives entirely in the URL and visitors cannot be identified. 
Task-list checkboxes are clickable only in issues and pull requests, never in a rendered README, 
so they are no use either. I don't know if there is a way to add state without making this project
needlessly complex.

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
