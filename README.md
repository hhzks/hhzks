<!-- LIGHTS:START -->
### Lights Out · 2026-11-13

Click a tile to toggle it and its neighbours.
|  |  |  |  |
|:-:|:-:|:-:|:-:|
| [<img src="./img/init.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/8/89fe.md) | [<img src="./img/off.svg" width="64" alt="off">](https://github.com/hhzks/hhzks/blob/daily/s/8/89ca.md) | [<img src="./img/init.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/8/89a3.md) | [<img src="./img/init.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/8/8961.md) |
| [<img src="./img/off.svg" width="64" alt="off">](https://github.com/hhzks/hhzks/blob/daily/s/8/88dc.md) | [<img src="./img/init.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/8/8b9f.md) | [<img src="./img/init.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/8/8d09.md) | [<img src="./img/init.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/8/8125.md) |
| [<img src="./img/init.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/9/9afd.md) | [<img src="./img/off.svg" width="64" alt="off">](https://github.com/hhzks/hhzks/blob/daily/s/a/aecd.md) | [<img src="./img/off.svg" width="64" alt="off">](https://github.com/hhzks/hhzks/blob/daily/s/c/c7ad.md) | [<img src="./img/init.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/0/056d.md) |
| [<img src="./img/off.svg" width="64" alt="off">](https://github.com/hhzks/hhzks/blob/daily/s/b/b8ed.md) | [<img src="./img/off.svg" width="64" alt="off">](https://github.com/hhzks/hhzks/blob/daily/s/f/fbed.md) | [<img src="./img/off.svg" width="64" alt="off">](https://github.com/hhzks/hhzks/blob/daily/s/6/6ded.md) | [<img src="./img/init.svg" width="64" alt="on">](https://github.com/hhzks/hhzks/blob/daily/s/4/41ed.md) |
<!-- LIGHTS:END -->

[Past puzzles](archive/) · [View source](src/)

## Projects

### [Audio Engine](https://github.com/hhzks/rt-audio)

**Low-latency realtime audio passthrough with an effects chain, written in C++26 with a Rust terminal UI.**

<img src="https://img.shields.io/badge/C%2B%2B-26-00599C?style=flat-square&logo=cplusplus&logoColor=white" alt="C++ 26"> <img src="https://img.shields.io/badge/Rust-TUI-000000?style=flat-square&logo=rust&logoColor=white" alt="Rust TUI"> <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-555555?style=flat-square&logo=linux&logoColor=white" alt="platform Windows | Linux"> <a href="https://github.com/hhzks/rt-audio/releases/latest"><img src="https://img.shields.io/github/v/release/hhzks/rt-audio?style=flat-square" alt="Latest release"></a>

<a href="https://github.com/hhzks/rt-audio"><img src="https://github.com/user-attachments/assets/4cd0c155-bca4-4342-8fca-0cc456c0135c" width="720" alt="rt_rig, the rt-audio terminal UI"></a>

- **Four audio backends:** WASAPI (shared and exclusive), ALSA, ASIO and a null device for testing
- **Live terminal rig:** level meters, the effect chain, bypass, and callback timing against the block deadline
- **Built-in latency check:** measures the round-trip latency through your own microphone and headphones
- **Recovers by itself:** if a device disconnects, it opens it again when it comes back

<br>

### [PDF Bookmarker](https://github.com/hhzks/pdf-bookmarker)

**Adds a clickable chapter and section outline to PDFs that have none.** [Try it in the browser →](https://pdf-bookmarker.vercel.app/)

<img src="https://img.shields.io/badge/Python-CLI-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python CLI"> <img src="https://img.shields.io/badge/model-~5%20MB%20heading%20classifier-F7931E?style=flat-square&logo=scikitlearn&logoColor=white" alt="model ~5 MB heading classifier"> <img src="https://img.shields.io/badge/LLM-Claude%20%7C%20Gemini%20%7C%20local-D97757?style=flat-square&logo=anthropic&logoColor=white" alt="LLM Claude | Gemini | local">

- **Reads the typography** of every page (font size, weight, position), and OCRs scanned PDFs first
- **Trained heading model** finds headings and their depth on CPU in milliseconds, with no API key
- **LLM check only when needed:** the LLM runs on only 38% of documents, and its outline is merged with the model's

| on 76 held-out documents | title F1 | level accuracy |
|---|:-:|:-:|
| font rules only | 0.62 | 0.82 |
| heading model | 0.80 | **0.89** |
| heading model + LLM when needed | **0.82** | **0.89** |

<br>

### [Sleep Insight App](https://github.com/hhzks/sleep-insight-app)

**A sleep tracker with Fitbit sync and AI insights from a self-hosted model.** [Open the app →](https://sleepinsight.pages.dev)

<img src="https://img.shields.io/badge/Django-REST-092E20?style=flat-square&logo=django&logoColor=white" alt="Django REST"> <img src="https://img.shields.io/badge/React-TypeScript-3178C6?style=flat-square&logo=react&logoColor=white" alt="React TypeScript"> <img src="https://img.shields.io/badge/Celery-Redis-37814A?style=flat-square&logo=celery&logoColor=white" alt="Celery Redis"> <img src="https://img.shields.io/badge/Ollama-self--hosted-000000?style=flat-square&logo=ollama&logoColor=white" alt="Ollama self-hosted">

<a href="https://github.com/hhzks/sleep-insight-app"><img src="https://raw.githubusercontent.com/hhzks/sleep-insight-app/main/assets/screenshots/dashboard.png" width="720" alt="sleep-insight-app dashboard"></a>

- **Fitbit OAuth sync** every night on a background worker, with a per-user opt-out
- **AI insights** from a self-hosted Ollama model, with a rule-based fallback when the model is not available
- **Dashboard, trends and sleep goals,** with Firebase sign-in (email or Google)
