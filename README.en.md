<div align="center">

<a href="https://kai987.github.io/IELTS-word-atlas/"><img src="docs/assets/cover-v2.jpg" alt="词光 · Word Atlas — an illustrated world of words" width="100%"></a>

# Word Atlas · 词光

**See the word. Hear it. Make it yours.**

7,298 IELTS words · Original illustrations · UK & US audio · Spaced repetition

[**Try this fork ↗**](https://kai987.github.io/IELTS-word-atlas/)　 /　 [Original 48-second film](docs/assets/launch.mp4)　 /　 [Get the dataset](data/)　 /　 [日本語](README.md)　 /　 [简体中文](README.zh-CN.md)　 /　 English

[![Code: MIT](https://img.shields.io/badge/Code-MIT-17283B?style=flat-square)](LICENSE)
[![Dataset: CC BY 4.0](https://img.shields.io/badge/Dataset-CC_BY_4.0-AD5038?style=flat-square)](CONTENT_LICENSE.md)
[![Follow on X](https://img.shields.io/badge/X-@yangleiocx3-17283B?style=flat-square&logo=x&logoColor=white)](https://x.com/yangleiocx3)

<br>

<a href="https://0xlei.tech/words/"><img src="https://0xlei.tech/words/beta/banner.png" alt="Word Atlas iOS beta — scan with WeChat to join the beta group" width="100%"></a>

**Upstream project announcement: the Word Atlas iOS app is in development.** This invitation belongs to the original project, separately from this Japanese-localized fork. Scan the code with WeChat to join the beta group. If the code has expired, open the [website](https://0xlei.tech/words/) and tap 「内测」 in the top bar to add the author on WeChat.

</div>

---

Word Atlas is an illustrated IELTS vocabulary app. This fork supports Japanese and Simplified Chinese in the interface and all 7,298 entries. Without a saved choice, Chinese browser locales use Chinese; all other locales use Japanese. A manual language choice is remembered on the device. Connect words with scenes and pronunciation, practise active recall, and return to them with FSRS spaced repetition. No account required. Learning progress stays on your device.

> **Version scope:** This is a Japanese-localized fork of [designfuchen/word-atlas](https://github.com/designfuchen/word-atlas). Its [GitHub Pages site](https://kai987.github.io/IELTS-word-atlas/) is built from this repository. The original upstream website evolves separately and may have different features. The code and dataset here remain available under their respective MIT and CC BY 4.0 licenses.

[Preview](#preview) · [Learning loop](#learning-loop) · [Quick start](#quick-start) · [Open dataset](#open-dataset) · [Contributing](#contributing)

## Preview

### A vocabulary atlas you can listen to and practise with

<img src="docs/assets/atlas-desktop.jpg" alt="Open-source edition: desktop vocabulary atlas" width="100%">

<table>
<tr>
<td width="50%"><img src="docs/assets/today-mobile.jpg" alt="Daily study plan on mobile" width="100%"></td>
<td width="50%"><img src="docs/assets/word-mobile.jpg" alt="Illustrated word card with pronunciation and examples" width="100%"></td>
</tr>
<tr><td align="center">A plan for today</td><td align="center">A scene for every word</td></tr>
</table>

<sub>Actual screenshots of the repository edition. The header is a conceptual brand illustration.</sub>

### Watch your vocabulary take shape

<img src="docs/assets/galaxy.jpg" alt="Vocabulary galaxy showing learning progress across topics" width="100%">

Explore 19 topic groups, rotate and zoom the galaxy, and select a star to open its word card. Brightness reflects learning status. Built with WebGL2, with a fallback for unsupported devices.

<details>
<summary><b>Watch the 48-second introduction</b></summary>

<a href="docs/assets/launch.mp4"><img src="docs/assets/launch-preview.webp" alt="Watch the Word Atlas introduction" width="100%"></a>

[Play the full film with sound](docs/assets/launch.mp4)

</details>

## Learning loop

| Step | What you do |
| :--- | :--- |
| **See** | Explore an illustration, bilingual definitions, two original examples, collocations and usage notes. |
| **Hear** | Switch between UK and US pronunciation and listen to example sentences. A subset includes audio for the second example. |
| **Recall** | Practise meaning-to-word, illustrated cloze, listening recognition and spelling. |
| **Review** | Let FSRS schedule reviews based on your history. Only the first answer counts toward accuracy. |
| **Keep** | Track progress in the galaxy, practise typing separately, and export or restore your local progress. |

**Local first.** Visited entries and media can be cached for offline use. Export a progress backup before moving to another device.

Listen to a sample: **abandon** — [UK](public/atlas/audio/uk/abandon.mp3) · [US](public/atlas/audio/us/abandon.mp3) · [Example](public/atlas/audio/ex/abandon.mp3).

## Quick start

Requires **Node.js 20+** and npm. This repository includes the full image and audio collection, so the initial download can take time.

```bash
git clone --depth 1 https://github.com/kai987/IELTS-word-atlas.git
cd IELTS-word-atlas
npm ci
npm run dev
```

Open **http://localhost:5188**.

```bash
npm test             # Unit tests
npm run check:atlas  # Dataset and media validation
npm run check:japanese # Japanese overlay validation
npm run build        # Production build in dist/
```

For a subpath deployment: `ATLAS_BASE=/IELTS-word-atlas/ npm run build`. See the [deployment guide](docs/deployment.md).

**Stack:** React 19 · TypeScript · Vite · ts-fsrs · WebGL2

## Open dataset

Use the app as it is, or build your own learning tools, Anki decks and research projects.

| Resource | Repository edition | Download / documentation |
| :--- | :--- | :--- |
| Entries | **7,298**, CEFR A1–C2, 19 topics | [JSON](data/word-atlas.json) · [CSV](data/word-atlas.csv) |
| Examples | **14,596**, everyday and IELTS contexts, with Chinese and Japanese translations | [Schema](docs/dataset.md) |
| Illustrations | **7,298**, 512 px WebP plus thumbnails | [Images](public/atlas/img/) |
| Recordings | **22,905**, UK/US words and example sentences | [Audio](public/atlas/audio/) |

```python
import json
from pathlib import Path

words = json.loads(Path("data/word-atlas.json").read_text(encoding="utf-8"))
b2_environment = [w for w in words if w["cefr"] == "B2" and w["topic"] == "environment"]
```

Japanese source translations are in [`data/ja/entries/`](data/ja/entries/); the deployable overlay and search labels are in [`public/atlas/ja/`](public/atlas/ja/). The full JSON and CSV exports above contain the original English/Chinese corpus.

### Provenance and limitations

The original text and illustrations were generated for the upstream project using AI; English speech was synthesized with ElevenLabs. Automated structure and consistency checks have been performed, but **the entire collection has not been manually reviewed**. Definitions, examples, illustrations or pronunciation may contain errors. This is not an official IELTS list and does not promise score improvements.

The Japanese overlay translates bilingual meanings, examples and collocations primarily from English; Chinese-only tips and notes are translated from Chinese. It retains English learning material, IDs, entry order and source hashes. Confirmed corrections from independent semantic review have been applied; see [Japanese localization](docs/japanese.md). This review does not certify the corpus as professionally proofread or error-free. The Japanese welcome recording uses AivisSpeech (morioki).

[Generation pipeline](docs/pipeline.md) · [Learning model](docs/learning-model.md) · [Scripts](scripts/atlas/)

## Contributing

Please include the **word ID, reproduction steps and expected result** when reporting a problem. For vocabulary corrections, reliable dictionary references are welcome.

- [Report an issue in this fork](https://github.com/kai987/IELTS-word-atlas/issues/new/choose)
- [Contribution guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

## License

| Scope | License |
| :--- | :--- |
| Application code | [MIT](LICENSE) |
| Vocabulary text, illustrations and word recordings | [CC BY 4.0](CONTENT_LICENSE.md); credit “Word Atlas contributors（词光）” |
| Dependencies and fonts | Their respective licenses |

---

Original project by [@designfuchen](https://github.com/designfuchen); Japanese localization in [this fork](https://github.com/kai987/IELTS-word-atlas). Follow the upstream project on [X · @yangleiocx3](https://x.com/yangleiocx3).

If Word Atlas helps you, consider starring the repository or sharing it with another learner.
