## Hi there 👋

<!-- LIGHTS:START -->
### Lights Out · 2026-08-04

Click a tile to toggle it and its neighbours. Turn every light off. A new puzzle daily.

|  |  |  |  |
|:-:|:-:|:-:|:-:|
| [<img src="./img/off.svg" width="64" alt="off">](https://github.com/hhzks/hhzks/blob/daily/s/c/c721.md) | [<img src="./img/on.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/c/c715.md) | [<img src="./img/off.svg" width="64" alt="off">](https://github.com/hhzks/hhzks/blob/daily/s/c/c77c.md) | [<img src="./img/off.svg" width="64" alt="off">](https://github.com/hhzks/hhzks/blob/daily/s/c/c7be.md) |
| [<img src="./img/on.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/c/c603.md) | [<img src="./img/on.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/c/c540.md) | [<img src="./img/off.svg" width="64" alt="off">](https://github.com/hhzks/hhzks/blob/daily/s/c/c3d6.md) | [<img src="./img/off.svg" width="64" alt="off">](https://github.com/hhzks/hhzks/blob/daily/s/c/cffa.md) |
| [<img src="./img/on.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/d/d422.md) | [<img src="./img/on.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/e/e012.md) | [<img src="./img/on.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/8/8972.md) | [<img src="./img/off.svg" width="64" alt="off">](https://github.com/hhzks/hhzks/blob/daily/s/4/4bb2.md) |
| [<img src="./img/off.svg" width="64" alt="off">](https://github.com/hhzks/hhzks/blob/daily/s/f/f632.md) | [<img src="./img/off.svg" width="64" alt="off">](https://github.com/hhzks/hhzks/blob/daily/s/b/b532.md) | [<img src="./img/on.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/2/2332.md) | [<img src="./img/on.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/0/0f32.md) |
<!-- LIGHTS:END -->

## Lights Out

Every tile you click toggles itself and its orthogonal neighbours. Get the whole
board dark. A new puzzle appears daily.

There is no JavaScript here, and there cannot be — GitHub strips `<script>`,
`<style>`, `<form>` and every event handler out of rendered markdown. The only
interactive thing left in a README is a link.

So the game is played by *navigation*. Every board you could possibly reach from
today's start position has been pre-computed and written to its own markdown
file, and each tile is a link to the file representing the board after that
click. Clicking is addition modulo 2, so order never matters and clicking twice
undoes itself — which is what keeps the state space down to a tractable 4,096
boards instead of the full 65,536.

<details><summary>The details, if you like this sort of thing</summary>

A 4×4 board is a 16-bit vector over GF(2). The click matrix `A` has rank 12 and
nullity 4, so its null space holds 16 "quiet patterns" — click sets that change
nothing at all. Two consequences fall out of that:

- Only **1 in 16** of the 65,536 possible boards can be solved. Today's start
  board is built by applying clicks to a dark board, never by randomising bits,
  so it is always solvable.
- The shortest solution is found by solving `A·x = s` for any particular `x₀`,
  then taking the smallest `x₀ ⊕ n` across all 16 quiet patterns. The hardest
  board on a 4×4 grid needs just **7** clicks.

The whole game is 4,096 files of about 2 KB, sharded across 16 directories, on
an orphan branch that gets force-pushed daily so history never accumulates.
Only two images exist for the entire game — `on.svg` and `off.svg` — which keeps
the repository small and sidesteps GitHub's image cache entirely, since a stale
cache of a file that never changes is always correct.

No move counter, no streaks, no score. State lives entirely in the URL and
visitors cannot be identified, so anything resembling a per-player statistic
would be a fabrication.

</details>

📁 [Past puzzles and their solutions](archive/)

<details><summary>Maintenance</summary>

GitHub disables scheduled workflows after **60 days of repository inactivity**,
and commits pushed by `GITHUB_TOKEN` may not reset that clock. Check monthly
that the daily run is still firing, or push a manual commit now and then.

The schedule is also only a request — Actions cron is queued at low priority and
routinely drifts by minutes to hours, which is why nothing here promises a
specific time of day.

</details>
