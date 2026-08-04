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

There is no JavaScript here, and there cannot be GitHub strips `<script>`,
`<style>`, `<form>` and every event handler out of rendered markdown. The only
interactive thing left in a README is a link.

So the game is played by *navigation*. Every board you could possibly reach from
today's start position has been pre-computed and written to its own markdown
file, and each tile is a link to the file representing the board after that
click. Clicking is addition modulo 2, so order never matters and clicking twice
undoes itself — which is what keeps the state space down to a tractable 4,096
boards instead of the full 65,536.

📁 [Past puzzles and their solutions](archive/)
