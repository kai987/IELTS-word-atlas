# Japanese localization

On 2026-10-28, the 62 confirmed field corrections from the
[full-corpus source review](ja-full-semantic-review-results-2026-10-27.md) were applied
to 58 entries and assembled into the public overlay and search labels. The
[focused review of the remaining 47 fields](ja-uncertain-focused-review-2026-10-28.md)
then confirmed 15 additional errors, which have also been applied. The cumulative
77 corrected fields affect 73 entries (8 major and 69 minor). The other 28 optional
clarifications and 4 retained fields keep their existing text. The historical
reports record the translations before application; the `student` and `from`
reviewed-entry overrides were updated so that rebuilding preserves both fixes.
See the [application record](ja-focused-corrections-2026-10-28.md). These reviewed
corrections do not certify the entire corpus as free of undiscovered errors.

For source-grounded review of the existing final Japanese corpus, use the
[independent semantic review workflow](ja-semantic-review.md). It freezes the
actual public overlay after corrections and keeps model detection, reference
translation, proposed repairs and independent final decisions separate.

The interface supports Chinese (`zh`) and Japanese (`ja`). The language selector
uses `中` and `日`, and stores the choice locally. English headwords, example
sentences and English audio remain the learning material in both languages.

Without a saved selection, the initial language follows the browser's primary
preferred language (`navigator.languages[0]`): Chinese locales use Chinese; Japanese and all other locales use
Japanese. A valid manual selection takes precedence on later visits. The inline
startup script and the application resolve the language consistently, including
when browser storage is blocked. Latin text and digits follow the hosted Word
Atlas font scheme: Atkinson Hyperlegible Next for Latin text and the Noto Sans
SC Latin subset as the digits-only `WA Digits` face (`U+0030-0039`). Chinese text
uses Noto Sans SC. Japanese glyphs retain the existing
`"Hiragino Mincho ProN", "Yu Mincho", "Noto Serif JP", serif` stack, including
the Japanese logo and splash. The variable fonts are bundled through Fontsource
and served locally with the application. Canvas share cards read the same CSS
font variables; particle targets are sampled after their fonts have loaded.
Font licenses are included in `public/fonts/`.
The base `:root` and dark-theme variables match the original hosted stylesheet,
including font, radius, motion and layout variables. The original
`data-font="sans"` override keeps the active Latin typeface as Atkinson;
Source Serif 4 is bundled for the base display-font declaration. Japanese font
overrides remain separate from these shared variables.
The splash samples the active language's title into particle targets (`詞光` in
Japanese, `词光` in Chinese), with matching text in reduced-motion mode. The
particle gathering, dispersal and opening-door transitions remain available.
Browser preferences can differ from the macOS display language. A web page uses
the preference exposed by the browser; selecting Japanese in the language menu
keeps Japanese on subsequent visits without changing browser-wide settings.

Clicking the Japanese splash plays `public/sfx/splash-voice-ja-morioki.mp3`,
generated locally with AivisSpeech (`morioki`, `ノーマル`, style `497929760`).
The synthesis text is `アイエルツへの扉を開こう。`, matching the displayed
`IELTSへの扉を開こう` and keeping the IELTS pronunciation natural. Chinese mode
retains its original recording. The voice-specific URL avoids reusing a cached
recording from another synthesizer.

The original English/Chinese vocabulary corpus remains the source of truth. Japanese text uses a
static overlay in `public/atlas/ja/`, with matching entry IDs, order and chunk size:

- `index.json`: Japanese search labels, translation provenance and source hashes.
- `entries/N.json`: `id`, `senses`, `ex`, `col`, `tip` and `note`; optional
  `fam`, `syn`, `ant` arrays translate rare Chinese related-word labels while
  keeping every English item unchanged (for example `glutinous.syn`).
- `scripts/atlas/ja-reviewed-*.json`: separately authored entry-level translations.
- `scripts/atlas/ja-field-reviewed-*.json`: reviewed Chinese-source → Japanese-text
  corrections for Chinese-only tips and notes. Both correction types take
  precedence over contextual translations.

The canonical Japanese source chunks live in `data/ja/entries/`. They are written
with English as the source for paired meanings, examples and collocations, and
Chinese as the source for Chinese-only tips and notes. Each entry retains its
full context and is then checked for IDs, array lengths,
English literals and linguistic consistency. Separately reviewed entry and field
corrections take precedence. Structural validation and local-model verification
are not a claim of professional human certification.

## Preparing and assembling the corpus

The optional local worker uses the user-selected Ollama models
`translategemma:12b-it-q8_0` and `qwen3.5:9b-q8_0`. TranslateGemma drafts each entry with its
native translation prompt. The v5 reviewer pairs each authoritative source field
with its existing Japanese draft and proposes only substantive corrections,
including the exact previous text, reason and source quote. The program rejects
language regressions, malformed patches and lost literals, keeps the draft for
rejected fields, and holds the entry for review. Unaligned drafts are held before
any reviewer call. See [the v5 review workflow](ja-review-v5.md).

```sh
ollama serve
ollama pull translategemma:12b-it-q8_0
ollama pull qwen3.5:9b-q8_0
python3 scripts/atlas/translate-ja-local.py
```

The worker connects only to a loopback Ollama URL, records the exact model digests
and source-entry hashes, writes atomic checkpoints in ignored `.local/ja-local-v5/`,
and skips already completed contextual source chunks. Eligible chunks are staged
in the cache's `candidate-chunks/` directory for independent semantic review;
the local worker never writes `data/ja/entries/` or the public corpus. Model and
language-gate approval are insufficient for publication: the v5 targeted pilot
still found semantic errors in 4 of 5 gate-approved entries. Independent
source-grounded review is required before adopting candidates. No translation service, API key or model
is used by the website itself.

The engine-independent assembler refuses public output until all 7,298 source
entries have contextual Japanese text. A Chinese-keyed cache cannot fill in
missing bilingual entries. It merges reviewed corrections and records
SHA-256 hashes of the source index and every source entry chunk.

```sh
python3 scripts/atlas/translate_ja.py
npm run check:japanese
```

After editing a reviewed correction, rerun these commands. Local model results
must be calibrated against representative examples and reviewed before release;
no output from rejected translation experiments belongs in the corpus.

The validator checks every entry, array length, nonempty field, English collocation
prefix, English/IPA literal in notes, search label, and source hash. It also reports
linguistic smoke warnings (simplified Chinese characters, unknown tokens, repeated
output, or a long sentence without Japanese kana). Changing a Chinese source
entry invalidates its chunk hash, so regenerate/review the corresponding Japanese
text before release.

## Reviewed terminology

The `tetrad` translation checks cytogenetics terminology against the
[Tokyo Medical and Dental University cell-division text](https://www.tmd.ac.jp/artsci/biol/textbook/celldiv.htm)
and the [Japanese Environmental Mutagen and Genome Society glossary](https://www.j-ems.org/info/glossary_a.html).
Corpus licensing and attribution in `CONTENT_LICENSE.md` continue to apply.

## Source corrections

`data/ja/source-corrections.json` records source defects repaired during localization.
The corrupt `gram` tip was corrected to 1 kilogram = 1,000 grams, consistent with
its English definition. The Chinese public chunk and JSON/CSV source exports were
updated together. This entry is outside the frozen quantization sample.

The `transport` tip had an incoherent `/t/`/`/n/` fragment removed. Its noun/verb
stress guidance remains, consistent with [Cambridge pronunciation](https://dictionary.cambridge.org/pronunciation/english/transport).
This entry is also outside the frozen quantization sample.

## Quantization comparison

The fixed 100-entry comparison, substantive-error annotations, timing measurements
and decision are documented in [the 2026-10-26 comparison](ja-quant-benchmark-2026-10-26.md).
Both precision variants use the same source prompts and sampling parameters.
That historical comparison explicitly uses the archived `translate-ja-local-v4.py`
worker; it never silently adopts the current v5 review protocol.
Review-model approval is separate from source-grounded correctness. The current
result does not justify switching the whole pipeline or replacing the completed
contextual Japanese corpus with model candidates.

Portable helpers `export-ja-quant-blind.py`, `evaluate-ja-quant.py` and
`audit-ja-quant-requests.py` accept `--artifacts` for a new frozen run. Unmasking
requires complete field coverage and all 20 blinded secondary-review records.
