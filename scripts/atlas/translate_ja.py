#!/usr/bin/env python3
"""Assemble complete static Japanese overlays from contextual Japanese entry chunks.

Entry translations live in data/ja/entries/N.json. Every source entry must have
a contextual translation. Reviewed corrections override contextual entries.
The assembler has no translation engine, network calls, or external dependencies.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROVIDER = "Codex contextual translation"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entries", type=pathlib.Path, default=ROOT / "data/ja/entries", help="Complete contextual Japanese entry chunks")
    parser.add_argument("--provider", default=PROVIDER)
    args = parser.parse_args()
    atlas = ROOT / "public/atlas"
    index_raw = (atlas / "index.json").read_bytes()
    index = json.loads(index_raw)
    chunk_raw = [(atlas / f"entries/{n}.json").read_bytes()
                 for n in range((index["count"] + index["chunk"] - 1) // index["chunk"])]
    chunks = [json.loads(raw) for raw in chunk_raw]
    contextual = {}
    for n, chunk in enumerate(chunks):
        file = args.entries / f"{n}.json"
        if not file.exists():
            continue
        localized_chunk = json.loads(file.read_text())
        if not isinstance(localized_chunk, list) or len(localized_chunk) != len(chunk):
            raise ValueError(f"Contextual chunk length mismatch: {file}")
        for source, localized in zip(chunk, localized_chunk):
            if localized.get("id") != source["id"]:
                raise ValueError(f"Contextual chunk ID/order mismatch: {file}")
            contextual[source["id"]] = localized
    reviewed_fields = {}
    for file in sorted((ROOT / "scripts/atlas").glob("ja-field-reviewed-*.json")):
        corrections = json.loads(file.read_text())
        if not isinstance(corrections, dict) or any(not isinstance(k, str) or not isinstance(v, str) or not v.strip()
                                                   for k, v in corrections.items()):
            raise ValueError(f"Invalid reviewed field map: {file}")
        for source, japanese in corrections.items():
            if source in reviewed_fields and reviewed_fields[source] != japanese:
                raise ValueError(f"Conflicting reviewed field: {source}")
            reviewed_fields[source] = japanese
    reviewed_entries = {}
    for file in sorted((ROOT / "scripts/atlas").glob("ja-reviewed-*.json")):
        for entry in json.loads(file.read_text()):
            if entry["id"] in reviewed_entries:
                raise ValueError(f"Duplicate reviewed entry: {entry['id']}")
            reviewed_entries[entry["id"]] = entry
    missing = []
    for chunk in chunks:
        for entry in chunk:
            if entry["id"] in contextual or entry["id"] in reviewed_entries:
                continue
            missing.append(entry["id"])
    if missing:
        raise ValueError(f"{len(missing)} entries lack contextual Japanese translations; no incomplete output written")
    words = {}
    overlays = []
    for chunk in chunks:
        overlay = []
        for entry in chunk:
            if entry["id"] in contextual:
                localized = json.loads(json.dumps(contextual[entry["id"]]))
            elif entry["id"] in reviewed_entries:
                localized = json.loads(json.dumps(reviewed_entries[entry["id"]]))
            # Legacy Chinese-keyed maps cannot override English-authoritative
            # vocabulary, example or collocation translations.
            for key in ["tip", "note"]:
                if entry.get(key, "") in reviewed_fields:
                    localized[key] = reviewed_fields[entry[key]]
            if entry["id"] in reviewed_entries:
                localized = reviewed_entries[entry["id"]]
            for key, source in [("senses", entry["senses"]), ("ex", entry["ex"]), ("col", entry["col"])]:
                values = localized.get(key)
                if not isinstance(values, list) or len(values) != len(source) or any(not isinstance(v, str) or not v.strip() for v in values):
                    raise ValueError(f"Invalid localized array: {entry['id']}.{key}")
            for original, translated in zip(entry["col"], localized["col"]):
                if "｜" in original and original.split("｜", 1)[0] != translated.split("｜", 1)[0]:
                    raise ValueError(f"English collocation changed: {entry['id']}")
            for key in ["fam", "syn", "ant"]:
                original = entry[key]
                if key not in localized and not any(re.search(r"[\u3400-\u9fff]", text) for text in original):
                    continue
                translated = localized.get(key)
                if not isinstance(translated, list) or len(translated) != len(original) or any(not isinstance(v, str) or not v.strip() for v in translated):
                    raise ValueError(f"Missing localized related-word text: {entry['id']}.{key}")
                for source_text, target_text in zip(original, translated):
                    if not re.search(r"[\u3400-\u9fff]", source_text) and source_text != target_text:
                        raise ValueError(f"English related word changed: {entry['id']}.{key}")
            for key in ["tip", "note"]:
                original, translated = entry.get(key, ""), localized.get(key)
                if not isinstance(translated, str) or (original.strip() and not translated.strip()):
                    raise ValueError(f"Invalid localized text: {entry['id']}.{key}")
                for term in re.findall(r"/[^/\n]+/|[A-Za-z][A-Za-z0-9 /'’+()_.-]*", original):
                    if translated.count(term.strip()) < original.count(term.strip()):
                        raise ValueError(f"English/IPA literal changed: {entry['id']}.{key}: {term.strip()}")
            overlay.append(localized)
            words[entry["id"]] = f"{entry['senses'][0]['pos']} {localized['senses'][0]}".strip()
        overlays.append(overlay)
    if len(words) != index["count"] or not set(reviewed_entries).issubset(words):
        raise ValueError("Translation/source ID mismatch")
    # Completeness is checked before writing any public file.
    target = atlas / "ja"
    (target / "entries").mkdir(parents=True, exist_ok=True)
    for n, overlay in enumerate(overlays):
        (target / f"entries/{n}.json").write_text(json.dumps(overlay, ensure_ascii=False, separators=(",", ":")) + "\n")
    metadata = {"version": 1, "language": "ja", "chunk": index["chunk"],
                "sourceIndexSha256": hashlib.sha256(index_raw).hexdigest(),
                "sourceChunksSha256": [hashlib.sha256(raw).hexdigest() for raw in chunk_raw],
                "translation": {"provider": args.provider, "reviewedEntries": len(reviewed_entries),
                                "reviewedFields": len(reviewed_fields), "contextualEntries": len(contextual)}, "words": words}
    (target / "index.json").write_text(json.dumps(metadata, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"Wrote {len(words)} Japanese entries ({len(reviewed_entries)} reviewed entries, "
          f"{len(reviewed_fields)} reviewed fields) in {len(overlays)} chunks.")


if __name__ == "__main__":
    main()
