"""Frozen inputs and append-only checkpoints for source-grounded corpus review."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

SCHEMA_VERSION = 1
SAFE_ID = re.compile(r"[a-z0-9][a-z0-9-]*\Z")


def now():
    return datetime.now(timezone.utc).isoformat()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else encoded(value)).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(encoded(value) + b"\n")
    temporary.replace(path)


def read(path):
    return json.loads(Path(path).read_text())


def safe_output(root, destination):
    root, destination = Path(root).resolve(), Path(destination).resolve()
    for name in ("data", "public", ".git"):
        protected = root / name
        if destination == protected or protected in destination.parents:
            raise ValueError("Review artifacts must stay outside data/, public/ and .git/")
    if destination == root:
        raise ValueError("Review artifacts require a dedicated directory")
    return destination


def risk_tags(text, path):
    tags = []
    patterns = {
        "negation": r"\b(?:not|no|never|without|unless|neither)\b|不用|不能|不得|禁止|不宜",
        "modality": r"\b(?:must|should|may|might|can|could|probable|likely|possible)\b|必须|应当|可能",
        "quantity": r"\d|\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|hundred|thousand|million)\b",
        "time_or_range": r"\b(?:before|after|by|until|earlier|later|rather than|at least|at most|below|above|o'clock)\b",
        "relationship": r"\b(?:sister|brother|aunt|uncle|cousin|female|male|woman|man|older|younger)\b|姐姐|妹妹|哥哥|弟弟|年龄",
    }
    for name, pattern in patterns.items():
        if re.search(pattern, text, re.I):
            tags.append(name)
    if path in {"tip", "note"}:
        tags.append("explanatory_note")
    return tags


def entry_fields(source, japanese):
    fields = []

    def add(path, text, language, target, mode="translate", **extra):
        if not isinstance(text, str) or not isinstance(target, str):
            raise ValueError(f"Non-string field: {source['id']}.{path}")
        fields.append({"path": path, "sourceLanguage": language, "sourceText": text,
                       "currentJapanese": target, "mode": mode,
                       "riskTags": risk_tags(text, path), **extra})

    for group in ("senses", "ex", "col"):
        if not isinstance(japanese.get(group), list) or len(source[group]) != len(japanese[group]):
            raise ValueError(f"Source/target array mismatch: {source['id']}.{group}")
    for i, sense in enumerate(source["senses"]):
        english = sense.get("en", "").strip()
        add(f"senses.{i}", english or sense["zh"], "en" if english else "zh-Hans",
            japanese["senses"][i], pos=sense.get("pos", ""), chineseContext=sense.get("zh", ""))
    for i, example in enumerate(source["ex"]):
        english = example.get("en", "").strip()
        add(f"ex.{i}", english or example["zh"], "en" if english else "zh-Hans",
            japanese["ex"][i], chineseContext=example.get("zh", ""))
    for i, value in enumerate(source["col"]):
        phrase, separator, chinese = value.partition("｜")
        target = japanese["col"][i]
        if separator:
            left, target_separator, target = target.partition("｜")
            if not target_separator or left != phrase:
                raise ValueError(f"English collocation prefix changed: {source['id']}.{i}")
        add(f"col.{i}", phrase, "en", target, chineseContext=chinese)
    for key in ("tip", "note"):
        text = source.get(key, "")
        add(key, text, "zh-Hans", japanese.get(key, ""), "translate" if text.strip() else "empty")
    for key in ("fam", "syn", "ant"):
        original = source.get(key, [])
        translated = japanese.get(key, original)
        if not isinstance(translated, list) or len(original) != len(translated):
            raise ValueError(f"Related-word array mismatch: {source['id']}.{key}")
        for i, text in enumerate(original):
            chinese = bool(re.search(r"[\u3400-\u9fff]", text))
            if chinese and key not in japanese:
                raise ValueError(f"Missing related-word Japanese: {source['id']}.{key}.{i}")
            add(f"{key}.{i}", text, "zh-Hans" if chinese else "en", translated[i],
                "translate" if chinese else "preserve")
    return fields


def integrity_assessments(entry):
    results = []
    for field in entry["fields"]:
        if field["mode"] == "translate":
            continue
        source, target = field["sourceText"], field["currentJapanese"]
        acceptable = not target.strip() if field["mode"] == "empty" else source == target
        results.append({"path": field["path"], "status": "pass" if acceptable else "error",
                        "categories": [] if acceptable else ["addition_or_fabrication" if field["mode"] == "empty" else "wrong_meaning"],
                        "sourceQuote": source, "targetQuote": target,
                        "explanation": "Empty-source/no-addition check" if field["mode"] == "empty" else "Original English related-word integrity check",
                        "method": "deterministic_integrity"})
    return results


def build_snapshot(root):
    root = Path(root)
    atlas = root / "public/atlas"
    index_path, ja_index_path = atlas / "index.json", atlas / "ja/index.json"
    index, ja_index = read(index_path), read(ja_index_path)
    files = {}

    def remember(path):
        files[path.relative_to(root).as_posix()] = sha(path.read_bytes())

    remember(index_path)
    remember(ja_index_path)
    if ja_index.get("sourceIndexSha256") != sha(index_path.read_bytes()):
        raise ValueError("Final Japanese index is stale relative to its source")
    entries, differences, seen = [], [], set()
    count = (index["count"] + index["chunk"] - 1) // index["chunk"]
    for n in range(count):
        source_path, target_path = atlas / f"entries/{n}.json", atlas / f"ja/entries/{n}.json"
        remember(source_path)
        remember(target_path)
        if ja_index.get("sourceChunksSha256", [])[n] != sha(source_path.read_bytes()):
            raise ValueError(f"Final Japanese source chunk hash is stale: {n}")
        source, target = read(source_path), read(target_path)
        canonical_path = root / f"data/ja/entries/{n}.json"
        canonical = read(canonical_path) if canonical_path.exists() else None
        if canonical is not None:
            remember(canonical_path)
        if len(source) != len(target):
            raise ValueError(f"Chunk length mismatch: {n}")
        for i, (original, japanese) in enumerate(zip(source, target)):
            word = original["id"]
            if not SAFE_ID.fullmatch(word) or word in seen or japanese.get("id") != word:
                raise ValueError("Source/Japanese IDs are unsafe, duplicated or out of order")
            seen.add(word)
            if canonical is not None and (i >= len(canonical) or canonical[i] != japanese):
                differences.append(word)
            fields = entry_fields(original, japanese)
            entries.append({"id": word, "word": original["w"], "chunk": n, "order": len(entries),
                            "cefr": original.get("cefr", ""), "topic": original.get("topic", ""),
                            "sourceSha256": sha(original), "japaneseSha256": sha(japanese),
                            "source": original, "japanese": japanese, "fields": fields})
    if len(entries) != index["count"]:
        raise ValueError("Source count differs from frozen entries")
    for pattern in ("ja-reviewed-*.json", "ja-field-reviewed-*.json"):
        for path in sorted((root / "scripts/atlas").glob(pattern)):
            remember(path)
    entry_owners, field_owners = {}, {}
    for path in sorted((root / "scripts/atlas").glob("ja-reviewed-*.json")):
        for item in read(path):
            entry_owners[item["id"]] = path.relative_to(root).as_posix()
    for path in sorted((root / "scripts/atlas").glob("ja-field-reviewed-*.json")):
        for text in read(path):
            field_owners[text] = path.relative_to(root).as_posix()
    for entry in entries:
        for field in entry["fields"]:
            owner = {"file": entry_owners.get(entry["id"], f"data/ja/entries/{entry['chunk']}.json"),
                     "kind": "entry-array", "entryId": entry["id"], "path": field["path"]}
            if entry["id"] not in entry_owners and field["path"] in {"tip", "note"} and field["sourceText"] in field_owners:
                owner = {"file": field_owners[field["sourceText"]], "kind": "field-map", "key": field["sourceText"]}
            field["writeLocation"] = owner
    for name in ("data/word-atlas.json", "data/word-atlas.csv", "data/ja/source-corrections.json"):
        path = root / name
        if path.exists():
            remember(path)
    modes = Counter(field["mode"] for entry in entries for field in entry["fields"])
    manifest = {"entryCount": len(entries), "counts": dict(modes), "fieldCount": sum(modes.values()),
                "canonicalDifferences": differences, "files": files,
                "sourcePolicy": "English authoritative for bilingual fields; Chinese for Chinese-only fields",
                "reviewTarget": "Final public Japanese overlays after all reviewed corrections",
                "coverageNote": "Translation semantics, empty-source no-addition and English preservation are separate denominators"}
    return {"schemaVersion": SCHEMA_VERSION, "manifest": manifest, "entries": entries}


def prepare_run(root, run):
    run = safe_output(root, run)
    snapshot = build_snapshot(root)
    if run.exists() and any(run.iterdir()):
        known = load_snapshot(run)
        if known != snapshot:
            raise ValueError("Frozen source/final Japanese/override inputs changed; use a new run")
        return known
    run.mkdir(parents=True, exist_ok=True)
    atomic_json(run / "snapshot.json", snapshot)
    (run / "snapshot-sha256.txt").write_text(sha((run / "snapshot.json").read_bytes()) + "\n")
    return snapshot


def load_snapshot(run):
    run = Path(run)
    raw = (run / "snapshot.json").read_bytes()
    if sha(raw) != (run / "snapshot-sha256.txt").read_text().strip():
        raise ValueError("Frozen snapshot content/hash changed")
    snapshot = json.loads(raw)
    if snapshot.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("Unsupported review snapshot version")
    return snapshot


def source_drift(root, snapshot):
    if snapshot["manifest"].get("kind") == "controlled-probes":
        return []
    drift = []
    for name, expected in snapshot["manifest"]["files"].items():
        path = Path(root) / name
        if not path.is_file() or sha(path.read_bytes()) != expected:
            drift.append(name)
    expected_overrides = {name for name in snapshot["manifest"]["files"]
                          if re.fullmatch(r"scripts/atlas/ja-(?:field-)?reviewed-.*\.json", name)}
    current_overrides = {path.relative_to(Path(root)).as_posix() for pattern in ("ja-reviewed-*.json", "ja-field-reviewed-*.json")
                         for path in (Path(root) / "scripts/atlas").glob(pattern)}
    drift += sorted(current_overrides - expected_overrides)
    return drift


class AttemptStore:
    """One immutable attempt per ID, including failures and unresolved verdicts."""
    TERMINAL = {"complete", "error", "interrupted"}

    def __init__(self, run, stage, protocol):
        if not SAFE_ID.fullmatch(stage):
            raise ValueError("Unsafe stage name")
        self.run, self.stage = Path(run), stage
        self.folder = self.run / "records" / stage
        self.protocol = protocol
        self.protocol_hash = sha(protocol)
        protocol_path = self.run / "protocols" / f"{stage}.json"
        if protocol_path.exists():
            if read(protocol_path) != protocol:
                raise ValueError("Stage model/prompt/code/profile changed; use another lane")
        else:
            atomic_json(protocol_path, protocol)

    def paths(self, word):
        if not SAFE_ID.fullmatch(word):
            raise ValueError("Unsafe entry ID")
        return sorted((self.folder / word).glob("attempt-*.json"))

    def read_latest(self, word):
        paths = self.paths(word)
        return read(paths[-1]) if paths else None

    def begin(self, word, retry=False):
        paths = self.paths(word)
        if paths:
            previous = read(paths[-1])
            if previous.get("status") == "running":
                previous.update({"status": "interrupted", "finishedAt": now(), "error": "Previous attempt did not complete; explicit retry required"})
                atomic_json(paths[-1], previous)
            if not retry:
                return None
        attempt = len(paths) + 1
        record = {"id": word, "stage": self.stage, "attempt": attempt, "status": "running",
                  "startedAt": now(), "protocolSha256": self.protocol_hash}
        path = self.folder / word / f"attempt-{attempt:06d}.json"
        if path.exists():
            raise ValueError("Refusing to overwrite an attempt")
        atomic_json(path, record)
        return record

    def finish(self, word, record):
        latest = self.read_latest(word)
        if (not latest or latest.get("status") != "running" or record.get("id") != word
                or record.get("attempt") != latest.get("attempt")
                or record.get("protocolSha256") != self.protocol_hash
                or record.get("status") not in self.TERMINAL):
            raise ValueError("Cannot overwrite, misbind or reopen a terminal attempt")
        record = {**record, "finishedAt": now()}
        atomic_json(self.folder / word / f"attempt-{record['attempt']:06d}.json", record)


def latest_records(run, stage):
    folder = Path(run) / "records" / stage
    result = {}
    for directory in sorted(folder.iterdir()) if folder.exists() else []:
        if directory.is_dir():
            paths = sorted(directory.glob("attempt-*.json"))
            if paths:
                result[directory.name] = read(paths[-1])
    return result


def semantic_risks(field):
    """Find a few explicit unsupported facts for conservative contextual HOLD.

    This is deliberately not a general semantic classifier. It uses only
    positive source/target substrings and never guesses numerical equivalence
    or negation. Presence of both sibling-age characters or any explicit source
    age/time clue suppresses the corresponding rule, even if another semantic
    problem remains. Proper names, quotations and unusual contexts can still
    require independent review; a flag is not a certified translation error.
    """
    if field.get("sourceLanguage") != "en" or field.get("mode", "translate") != "translate":
        return []
    source, target = field.get("sourceText"), field.get("currentJapanese")
    if not isinstance(source, str) or not source.strip() or not isinstance(target, str) or not target:
        return []
    risks = []
    female = re.search(r"\bsisters?\b|\bfemale\s+siblings?\b", source, re.I)
    male = re.search(r"\bbrothers?\b|\bmale\s+siblings?\b", source, re.I)
    age_clue = re.search(r"\b(?:older|oldest|younger|youngest|elder|eldest|big|little|senior|junior)\b", source, re.I)
    religious_title = re.search(r"\b(?:religious|religion|convent|nun|nuns|church|monastery|monastic|sisterhood)\b", source, re.I)
    if not age_clue and not religious_title:
        for cue, older, younger in [(female, "姉", "妹"), (male, "兄", "弟")]:
            if cue and ((older in target) != (younger in target)):
                target_quote = older if older in target else younger
                risks.append({"tag": "unsupported_sibling_age", "sourceQuote": cue.group(0),
                              "targetQuote": target_quote,
                              "explanation": "The English sibling expression gives no relative age, but this Japanese wording selects only older or only younger. Hold for source-grounded review."})
    # A male alternative is suspicious only when no male role is stated in the
    # source. This avoids interpreting an explicitly mixed brother/sister list
    # or a sentence about a sister's male classmates as a gender contradiction.
    male_source_clue = re.search(r"\b(?:male|males|man|men|boy|boys|brother|brothers)\b", source, re.I)
    gender_alternative = re.search(
        r"(?:または|又は|あるいは|もしくは)\s*(?:兄弟|男(?:性)?(?:の)?(?:きょうだい|兄弟))|男(?:性)?の(?:きょうだい|兄弟)",
        target,
    )
    if female and not male_source_clue and gender_alternative:
        risks.append({"tag": "unsupported_sibling_gender", "sourceQuote": female.group(0),
                      "targetQuote": gender_alternative.group(0),
                      "explanation": "The English identifies a female sibling without a male alternative, but the Japanese adds an explicit male-sibling option. Hold for source-grounded review."})
    # Recognise meridiem notation without treating the auxiliary in 'I am ...'
    # as a morning cue. Other explicit day-part words suppress this addition
    # rule; it does not attempt to decide whether a supplied day-part is right.
    day_part = re.search(r"\b(?:morning|afternoon|evening|night|tonight|noon|midnight|dawn|dusk|sunrise|sunset|breakfast|lunch|dinner)\b", source, re.I)
    meridiem = (re.search(r"\b(?:a\s*\.\s*m\s*\.|p\s*\.\s*m\s*\.)", source, re.I)
                or re.search(r"(?<![A-Za-z])(?:AM|PM)(?![A-Za-z])", source)
                or re.search(r"\b\d{1,2}(?::\d{2})?\s*(?:a\.?\s*m\.?|p\.?\s*m\.?)(?![A-Za-z])", source, re.I)
                or re.search(r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+(?:am|pm)\b", source, re.I))
    target_time = re.search(r"午前|午後", target)
    if target_time and not day_part and not meridiem:
        risks.append({"tag": "unsupported_time_of_day", "sourceQuote": source[:300],
                      "targetQuote": target_time.group(0),
                      "explanation": "The English provides no explicit morning/afternoon/evening or meridiem cue, but the Japanese adds 午前 or 午後. Hold for source-grounded review."})
    # This is an absence-of-source-cue HOLD, not a general ranking parser.
    # Explicit English superlatives suppress the rule; their presence does not
    # prove the Japanese superlative is attached to the correct constituent.
    superlative_source = re.search(
        r"\b(?:most|least|best|worst|maximum|minimum|maximal|minimal|"
        r"highest|lowest|greatest|largest|smallest|biggest|longest|shortest|"
        r"fastest|slowest|strongest|weakest|earliest|latest|oldest|youngest|"
        r"nearest|farthest|furthest|cheapest|richest|poorest|easiest|hardest|"
        r"hottest|coldest|newest|safest|widest|narrowest|deepest|shallowest|"
        r"brightest|darkest|loudest|quietest|lightest|heaviest|first)\b|"
        r"\bnumber\s+one\b|\bno\.?\s*1\b",
        source, re.I,
    )
    superlative_target = re.search(r"最も|もっとも|一番|いちばん", target)
    if superlative_target and not superlative_source:
        risks.append({"tag": "unsupported_superlative", "sourceQuote": source[:300],
                      "targetQuote": superlative_target.group(0),
                      "explanation": "The English has no recognised explicit superlative or first-rank cue, but the Japanese adds a strongest/first-rank expression. Hold for independent source comparison; this rule does not certify an error."})
    # Definitions may explicitly combine intransitive and causative frames.
    # Do not guess whether Japanese morphology has expressed both: even a
    # correct target receives a contextual HOLD until that coverage is checked.
    if isinstance(field.get("path"), str) and field["path"].startswith("senses."):
        frame = (re.search(r"\bbecome\b[^.;!?]{0,240}?\bor\b[^.;!?]{0,120}?\b(?:make|cause)\b", source, re.I)
                 or re.search(r"\b(?:make|cause)\b[^.;!?]{0,240}?\bor\b[^.;!?]{0,120}?\bbecome\b", source, re.I))
        if frame:
            risks.append({"tag": "multi_frame_definition", "sourceQuote": frame.group(0),
                          "targetQuote": target[:300],
                          "explanation": "The English definition explicitly combines become and make/cause alternatives. Independently check that both intransitive and causative meanings are represented; this flag does not judge Japanese morphology or declare an error."})
    return risks


def guard_assessments(entry, assessments):
    """Keep model verdicts visible and conservatively hold unsupported facts."""
    from copy import deepcopy

    fields = {field["path"]: field for field in entry["fields"]}
    guarded = []
    for assessment in assessments:
        result = deepcopy(assessment)
        # Reapplying the guard must not nest or overwrite the original verdict.
        original = assessment.get("modelAssessment", assessment)
        result["modelAssessment"] = deepcopy(original)
        field = fields.get(assessment.get("path"))
        risks = semantic_risks(field) if field is not None else []
        result["programRiskFlags"] = risks
        if risks and result.get("status") == "pass":
            result["status"] = "uncertain"
        guarded.append(result)
    return guarded
