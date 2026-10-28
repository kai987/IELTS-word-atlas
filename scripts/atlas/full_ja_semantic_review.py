#!/usr/bin/env python3
"""Independent source-review ledger. Never calls a model or edits corpus/gold.

Source decisions and model assessments are deliberately separate. A batch's
unlisted fields become pass only after a named independent reviewer explicitly
attests to comparing every translate field in the complete ordered entry list.
This validates declarations and bindings; it cannot prove a reviewer read text.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
VERSION = 1
CATEGORIES = {"wrong_meaning", "omission", "addition_or_fabrication",
              "negation_or_modality", "quantity_time_or_entity",
              "grammar_or_terminology", "untranslated"}
SEVERITIES = {"minor", "major", "critical"}
STATUSES = {"pass", "error", "uncertain"}
SAFE_BATCH = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,100}\Z")
FIELD_BINDINGS = ("path", "mode", "sourceLanguage", "sourceText", "currentJapanese")


class ReviewError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ReviewError(message)


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else encoded(value)).hexdigest()


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON object key")
        result[key] = value
    return result


def read(path):
    try:
        return json.loads(Path(path).read_bytes(), object_pairs_hook=_unique_pairs)
    except (OSError, json.JSONDecodeError) as error:
        raise ReviewError("Missing or malformed JSON: " + str(path)) from error


def artifact_path(value):
    require(isinstance(value, (str, Path)), "Artifact path must be text")
    path = (ROOT / value).resolve()
    require(ROOT.resolve() in path.parents, "Artifact path escaped repository")
    return path


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT.resolve()))


def file_ref(path):
    path = artifact_path(path)
    require(path.is_file(), "Missing bound artifact: " + relative(path))
    return {"path": relative(path), "fileSha256": sha(path.read_bytes())}


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(encoded(value) + b"\n")
    temporary.replace(path)


def exclusive_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(encoded(value) + b"\n")


def context_sha(entry):
    return sha({"source": entry["source"], "japanese": entry["japanese"]})


def field_key(entry_id, path):
    return entry_id + "\t" + path


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _quotes(source_quote, target_quote, field):
    require(_text(source_quote) and source_quote in field["sourceText"], "Invalid same-field sourceQuote")
    require(isinstance(target_quote, str) and target_quote in field["currentJapanese"]
            and (bool(target_quote.strip()) or not field["currentJapanese"]), "Invalid same-field targetQuote")


def load_snapshot(run):
    run = artifact_path(run)
    require(not any(part in {"data", "public", ".git"} for part in run.relative_to(ROOT).parts),
            "Review run must be outside production directories")
    snapshot = read(run / "snapshot.json")
    require(isinstance(snapshot.get("entries"), list), "Snapshot lacks entries")
    entries = {}
    for entry in snapshot["entries"]:
        require(entry["id"] not in entries, "Duplicate snapshot entry ID")
        require(entry.get("sourceSha256") == sha(entry["source"])
                and entry.get("japaneseSha256") == sha(entry["japanese"]), "Snapshot entry object hash mismatch")
        paths = [f["path"] for f in entry["fields"]]
        require(len(paths) == len(set(paths)), "Duplicate snapshot field path")
        require(all(f.get("mode") in {"translate", "preserve", "empty"}
                    and isinstance(f.get("sourceText"), str) and isinstance(f.get("currentJapanese"), str)
                    and isinstance(f.get("writeLocation"), dict) for f in entry["fields"]), "Invalid snapshot field")
        entries[entry["id"]] = entry
    for name, expected in snapshot.get("manifest", {}).get("files", {}).items():
        path = artifact_path(name)
        require(path.is_file() and sha(path.read_bytes()) == expected,
                "Frozen corpus source/target changed; source review invalidated: " + name)
    return run, snapshot, entries


def _check_ref(path, expected, label):
    ref = file_ref(path)
    require(ref["fileSha256"] == expected, label + " bytes changed")
    return ref


def import_reuse(snapshot, catalog):
    """Import trusted source-gold catalogs, never machine record/verdict files."""
    if catalog == []:
        return {"fields": {}, "invalidated": [], "sources": [], "conflicts": []}
    require(isinstance(catalog, dict) and catalog.get("kind") == "conservative-independent-source-gold-reuse-catalog"
            and isinstance(catalog.get("sources"), list), "Not a trusted independent source-gold catalog")
    current = {e["id"]: e for e in snapshot["entries"]}
    collected, invalidated, refs, conflicts = {}, [], [], []
    source_ids = set()
    for source in catalog["sources"]:
        require(source.get("kind") == "independent-source-gold" and _text(source.get("id"))
                and source["id"] not in source_ids, "Invalid/duplicate independent source-gold source")
        source_ids.add(source["id"])
        for key in ("goldPath", "selectionPath"):
            require(not ({"records", "calls"} & set(Path(source[key]).parts)), "Machine records cannot be reused as source gold")
        gold_path, selection_path = artifact_path(source["goldPath"]), artifact_path(source["selectionPath"])
        snapshot_path = artifact_path(source["snapshotRun"]) / "snapshot.json"
        bound = [_check_ref(gold_path, source["goldFileSha256"], "Source gold"),
                 _check_ref(selection_path, source["selectionFileSha256"], "Source selection"),
                 _check_ref(snapshot_path, source["snapshotFileSha256"], "Source snapshot")]
        gold, selection, original = read(gold_path), read(selection_path), read(snapshot_path)
        require(not ({"assessmentView", "stage", "calls", "metrics"} & set(gold)), "Machine assessments cannot become independent source decisions")
        reviewer = gold.get("reviewer", {})
        require(reviewer.get("independent") is True and _text(reviewer.get("name"))
                and _text(reviewer.get("method")), "Independent source reviewer identity/method required")
        require(source.get("reviewer") == reviewer, "Catalog/source reviewer mismatch")
        require(gold.get("selectionSha256") == sha(selection) == source["selectionCanonicalSha256"]
                and sha(gold) == source["goldCanonicalSha256"]
                and selection.get("snapshotSha256") == sha(snapshot_path.read_bytes()), "Source gold/selection/snapshot binding mismatch")
        original_entries = {e["id"]: e for e in original["entries"]}
        old_entries = {e["id"]: e for e in selection["entries"]}
        require(len(old_entries) == len(selection["entries"]) and selection["entryIds"] == list(old_entries),
                "Source selection IDs/order invalid")
        require(all(e == original_entries.get(e["id"]) for e in selection["entries"]), "Source selection differs from actual reviewed snapshot")
        expected = {(e["id"], f["path"]): f for e in old_entries.values() for f in e["fields"] if f["mode"] == "translate"}
        rows = {(f["entryId"], f["path"]): f for f in gold["fields"]}
        require(len(rows) == len(gold["fields"]) and set(rows) == set(expected), "Source gold field coverage invalid")
        if source.get("lock"):
            lock = source["lock"]
            bound.append(_check_ref(lock["path"], lock["fileSha256"], "Source gold lock"))
        refs.extend(bound)
        for entry_id, old in old_entries.items():
            candidate = current.get(entry_id)
            same_context = candidate is not None and context_sha(old) == context_sha(candidate)
            old_fields = {f["path"]: f for f in old["fields"]}
            new_fields = {f["path"]: f for f in candidate["fields"]} if candidate else {}
            same_fields = set(old_fields) == set(new_fields) and all(
                all(old_fields[path].get(k) == new_fields[path].get(k) for k in FIELD_BINDINGS)
                for path in old_fields)
            if not same_context or not same_fields:
                invalidated.append({"sourceId": source["id"], "entryId": entry_id,
                    "reason": "entry-context-changed" if not same_context else "entry-field-bindings-changed",
                    "translateFields": sum(f["mode"] == "translate" for f in old["fields"])})
                continue
            for path, field in new_fields.items():
                if field["mode"] != "translate":
                    continue
                row = rows[entry_id, path]
                require(not ({"modelAssessment", "predicted", "prediction"} & set(row)), "Machine verdict in source-gold row")
                status = row.get("expectedStatus")
                if status is None:
                    require(row.get("reviewStatus") == "uncertain", "Null/unreviewed gold is never a pass")
                    status = "uncertain"
                require(status in STATUSES and _text(row.get("note")), "Source gold needs explicit status and source-grounded note")
                quote_origin = "reviewer"
                if "sourceQuote" in row and "targetQuote" in row:
                    sq, tq = row["sourceQuote"], row["targetQuote"]
                else:
                    require(source.get("quoteAdapter", {}).get("reviewerQuotesProvided") is False,
                            "Missing reviewer quotes are allowed only by explicit pilot adapter")
                    sq, tq, quote_origin = field["sourceText"], field["currentJapanese"], "snapshot-binding"
                _quotes(sq, tq, field)
                categories = row.get("categories", [])
                require(isinstance(categories, list) and set(categories) <= CATEGORIES, "Unknown source-gold category")
                severity = row.get("severity")
                require(severity is None or severity in SEVERITIES, "Unknown source-gold severity")
                record = {"entryId": entry_id, "path": path, "contextSha256": context_sha(candidate),
                    "status": status, "categories": categories, "severity": severity,
                    "sourceQuote": sq, "targetQuote": tq, "quoteOrigin": quote_origin,
                    "explanation": row["note"], "reviewer": reviewer,
                    "provenance": {"kind": "independent-source-gold", "sourceId": source["id"],
                        "gold": bound[0], "selection": bound[1],
                        "snapshot": bound[2], "originalRowCanonicalSha256": sha(row),
                        "originalRow": row, "reviewExposureBoundary": source.get("reviewExposureBoundary"),
                        "professionalHumanCertification": False}}
                collected.setdefault(field_key(entry_id, path), []).append(record)
    result = {}
    for key, records in collected.items():
        value = dict(records[0])
        value["reuseSources"] = records
        if len({r["status"] for r in records}) > 1:
            value.update(status="uncertain", severity=None,
                categories=sorted({c for r in records for c in r["categories"]}),
                explanation="Conflicting independent source judgments: " + "; ".join(
                    r["provenance"]["sourceId"] + "=" + r["status"] for r in records),
                quoteOrigin="snapshot-binding")
            conflicts.append({"entryId": value["entryId"], "path": value["path"], "sourceIds": [r["provenance"]["sourceId"] for r in records]})
        result[key] = value
    return {"fields": result, "invalidated": invalidated, "sources": refs, "conflicts": conflicts}


def _verify_batches(run, snapshot, entries, reused):
    path = run / "batches.json"
    document = read(path)
    pending = [e["id"] for e in snapshot["entries"] if any(
        f["mode"] == "translate" and field_key(e["id"], f["path"]) not in reused for f in e["fields"])]
    expected_reused = [e["id"] for e in snapshot["entries"] if e["id"] not in set(pending)]
    actual_ids, batch_ids, refs = [], set(), []
    snapshot_hash = sha((run / "snapshot.json").read_bytes())
    for batch in document["batches"]:
        bid = batch.get("batchId")
        require(isinstance(bid, str) and SAFE_BATCH.fullmatch(bid) and bid not in batch_ids, "Invalid/duplicate batch ID")
        batch_ids.add(bid)
        require(batch.get("shard") in {1, 2, 3} and 1 <= len(batch["entryIds"]) <= 25
                and batch.get("entryCount") == len(batch["entryIds"]), "Batch shard/size invalid")
        input_path = artifact_path(batch["inputPath"])
        require(input_path.parent == run / "inputs" and input_path.name == bid + ".json", "Unexpected batch input path")
        require(file_ref(input_path)["fileSha256"] == batch["inputFileSha256"], "Batch input bytes changed")
        packet = read(input_path)
        require(set(packet) == {"schemaVersion", "batchId", "snapshotSha256", "entryIds", "translateFieldCount", "entries"},
                "Unexpected batch input fields")
        require(packet["batchId"] == bid and packet["snapshotSha256"] == snapshot_hash
                and packet["entryIds"] == batch["entryIds"] == [e["id"] for e in packet["entries"]], "Batch input IDs/snapshot/order mismatch")
        for supplied in packet["entries"]:
            require(supplied["id"] in entries, "Unknown batch entry")
            actual = dict(supplied)
            recorded_context = actual.pop("contextSha256", None)
            require(actual == entries[supplied["id"]] and recorded_context == context_sha(actual), "Batch source/context changed")
        count = sum(f["mode"] == "translate" for e in packet["entries"] for f in e["fields"])
        require(packet["translateFieldCount"] == batch["translateFieldCount"] == count, "Batch field denominator mismatch")
        actual_ids.extend(batch["entryIds"])
        refs.append(file_ref(input_path))
    require(len(actual_ids) == len(set(actual_ids)) and actual_ids == pending, "Pending batches do not exactly cover complete ordered pending entries")
    pending_fields = sum(f["mode"] == "translate" for eid in pending for f in entries[eid]["fields"])
    require(document["pendingEntries"] == len(pending) and document["pendingTranslateFields"] == pending_fields
            and len(document["reusedEntryIds"]) == len(expected_reused)
            and set(document["reusedEntryIds"]) == set(expected_reused), "Pending/reused entry/field counts mismatch")
    return document, refs


def prepare(run, reuse_catalog):
    run, snapshot, entries = load_snapshot(run)
    catalog_path = artifact_path(reuse_catalog)
    reuse = import_reuse(snapshot, read(catalog_path))
    batches, input_refs = _verify_batches(run, snapshot, entries, reuse["fields"])
    folder = run / "source-ledger"
    require(not (folder / "manifest.json").exists(), "Source ledger already prepared; never overwrite its frozen inputs")
    field_manifest = []
    for entry in snapshot["entries"]:
        entry_context = context_sha(entry)
        for field in entry["fields"]:
            if field["mode"] == "translate":
                field_manifest.append({"entryId": entry["id"], "path": field["path"], "mode": "translate",
                    "sourceLanguage": field["sourceLanguage"], "contextSha256": entry_context,
                    "sourceTextRawUTF8Sha256": sha(field["sourceText"].encode()),
                    "targetTextRawUTF8Sha256": sha(field["currentJapanese"].encode()),
                    "writeLocation": field["writeLocation"]})
    folder.mkdir(parents=True, exist_ok=True)
    exclusive_json(folder / "reuse.json", reuse)
    exclusive_json(folder / "fields.json", field_manifest)
    manifest = {"schemaVersion": VERSION, "kind": "independent-full-source-review-ledger",
        "preparedAt": datetime.now(timezone.utc).isoformat(), "snapshot": file_ref(run / "snapshot.json"),
        "catalog": file_ref(catalog_path), "batches": file_ref(run / "batches.json"), "inputFiles": input_refs,
        "reuse": file_ref(folder / "reuse.json"), "fields": file_ref(folder / "fields.json"),
        "sourceArtifacts": reuse["sources"], "helper": file_ref(Path(__file__)),
        "counts": {"entries": len(entries), "translateFields": len(field_manifest),
            "reusedFields": len(reuse["fields"]), "reusedStatus": dict(Counter(x["status"] for x in reuse["fields"].values())),
            "pendingEntries": batches["pendingEntries"], "pendingTranslateFields": batches["pendingTranslateFields"]},
        "policy": {"context": "sha({source: complete entry.source, japanese: complete entry.japanese})",
            "machineAssessmentIsIndependentReview": False, "attestationDoesNotProveActualReading": True,
            "resultsAreImmutablePerBatch": True, "productionWrites": False}}
    exclusive_json(folder / "manifest.json", manifest)
    return {"prepared": True, "manifest": relative(folder / "manifest.json"), "counts": manifest["counts"]}


def preflight(run):
    run, snapshot, entries = load_snapshot(run)
    folder = run / "source-ledger"
    manifest = read(folder / "manifest.json")
    require(manifest.get("kind") == "independent-full-source-review-ledger", "Unexpected source-ledger kind")
    refs = [manifest[k] for k in ("snapshot", "catalog", "batches", "reuse", "fields", "helper")]
    refs += manifest["inputFiles"] + manifest["sourceArtifacts"]
    for ref in refs:
        require(file_ref(ref["path"])["fileSha256"] == ref["fileSha256"], "Frozen source-review input changed: " + ref["path"])
    require(manifest["snapshot"]["fileSha256"] == sha((run / "snapshot.json").read_bytes()), "Snapshot changed; reuse invalidated")
    return run, snapshot, entries, manifest, read(run / "batches.json")


def validate_payload(run, payload, prepared=None):
    run, snapshot, entries, manifest, batches = prepared or preflight(run)
    require(isinstance(payload, dict), "Review result must be an object")
    required = {"batchId", "inputFileSha256", "reviewer", "reviewedEntryIds", "attestation", "issues"}
    require(required <= set(payload) <= required | {"notes", "schemaVersion", "reviewedAt", "viewReceipts"},
            "Missing/unknown review result fields")
    if "schemaVersion" in payload:
        require(payload["schemaVersion"] == VERSION, "Unsupported review result schema")
    indexed = {b["batchId"]: b for b in batches["batches"]}
    require(payload["batchId"] in indexed, "Unknown review batch")
    batch = indexed[payload["batchId"]]
    require(payload["inputFileSha256"] == batch["inputFileSha256"], "Review input hash mismatch")
    require(payload["reviewedEntryIds"] == batch["entryIds"], "Review must explicitly cover every ordered entry exactly once")
    reviewer = payload["reviewer"]
    require(isinstance(reviewer, dict) and set(reviewer) == {"name", "kind", "independent"}
            and _text(reviewer["name"]) and reviewer["kind"] == "codex-independent-source"
            and reviewer["independent"] is True, "Named independent source reviewer required")
    attestation = payload["attestation"]
    require(isinstance(attestation, dict) and set(attestation) == {"allTranslationFieldsCompared", "sourcePriority"}
            and attestation["allTranslationFieldsCompared"] is True and attestation["sourcePriority"] == "en-when-available",
            "Complete per-field source comparison attestation required")
    require("reviewedAt" not in payload or _text(payload["reviewedAt"]), "Invalid reviewedAt metadata")
    require("viewReceipts" not in payload or isinstance(payload["viewReceipts"], list), "Invalid viewReceipts metadata")
    require(isinstance(payload["issues"], list), "Issues must be a complete array")
    field_index = {(eid, f["path"]): f for eid in batch["entryIds"] for f in entries[eid]["fields"] if f["mode"] == "translate"}
    issues = {}
    issue_required = {"entryId", "path", "status", "categories", "severity", "sourceQuote", "targetQuote", "explanation"}
    for issue in payload["issues"]:
        require(isinstance(issue, dict) and issue_required <= set(issue) <= issue_required | {"suggestion"},
                "Missing/unknown issue fields")
        key = (issue["entryId"], issue["path"])
        require(key in field_index and key not in issues, "Unknown/nontranslate/duplicate issue field")
        require(issue["status"] in {"error", "uncertain"}, "Issue must be error or uncertain")
        categories = issue["categories"]
        require(isinstance(categories, list) and len(categories) == len(set(categories))
                and set(categories) <= CATEGORIES, "Unknown/duplicate issue categories")
        require((issue["status"] == "error" and bool(categories) and issue["severity"] in SEVERITIES)
                or (issue["status"] == "uncertain" and (issue["severity"] is None or issue["severity"] in SEVERITIES)),
                "Issue severity/category invalid")
        _quotes(issue["sourceQuote"], issue["targetQuote"], field_index[key])
        require(_text(issue["explanation"]), "Source-grounded issue explanation required")
        require("suggestion" not in issue or _text(issue["suggestion"]), "Suggestion must be nonempty text")
        issues[key] = issue
    notes = payload.get("notes")
    # Opaque reviewer metadata never contributes field coverage or decisions.
    require(notes is None or isinstance(notes, (str, list, dict)), "Invalid notes metadata")
    decisions = []
    for (eid, path), field in field_index.items():
        issue = issues.get((eid, path))
        value = dict(issue) if issue else {"entryId": eid, "path": path, "status": "pass", "categories": [],
            "severity": None, "sourceQuote": field["sourceText"], "targetQuote": field["currentJapanese"],
            "explanation": "Named reviewer explicitly attested to the complete batch comparison; no issue reported."}
        value.update(contextSha256=context_sha(entries[eid]), reviewer=reviewer,
            quoteOrigin="reviewer" if issue else "attested-full-field-binding",
            provenance={"kind": "completed-independent-source-batch", "batchId": batch["batchId"],
                "inputFileSha256": batch["inputFileSha256"], "attestation": payload["attestation"],
                "reviewerSelectedBindingQuote": bool(issue)})
        decisions.append(value)
    return {"schemaVersion": VERSION, "batchId": batch["batchId"], "snapshotSha256": manifest["snapshot"]["fileSha256"],
        "inputFileSha256": batch["inputFileSha256"], "reviewer": reviewer,
        "reviewedEntryIds": batch["entryIds"], "attestation": payload["attestation"],
        "notes": notes, "reviewedAt": payload.get("reviewedAt"),
        "viewReceipts": payload.get("viewReceipts", []), "decisions": decisions}


def _result_path(run, value):
    path = Path(value)
    if not path.is_absolute():
        path = run / path if path.parts and path.parts[0] == "primary" else ROOT / path
    path = path.resolve()
    require(path.parent == run / "primary" and path.suffix == ".json", "Results must be exclusive primary/<batchId>.json files")
    return path


def validate(run, result):
    prepared = preflight(run)
    run = prepared[0]
    path = _result_path(run, result)
    payload = read(path)
    require(path.name == payload.get("batchId", "") + ".json", "Result filename/batch mismatch")
    validated = validate_payload(run, payload, prepared)
    validated["rawResult"] = file_ref(path)
    validated["rawResultCanonicalSha256"] = sha(payload)
    destination = run / "source-ledger" / "validated" / path.name
    if destination.exists():
        require(read(destination) == validated, "Previously validated batch result changed; never overwrite")
    else:
        exclusive_json(destination, validated)
    return {"validated": True, "batchId": payload["batchId"], "path": relative(destination),
            "counts": dict(Counter(x["status"] for x in validated["decisions"]))}


def _issue(record, entry, field):
    return {**record, "sourceText": field["sourceText"], "currentJapanese": field["currentJapanese"],
        "sourceLanguage": field["sourceLanguage"], "chineseContext": field.get("chineseContext"),
        "word": entry["word"], "pos": field.get("pos"), "writeLocation": field["writeLocation"],
        "context": {"source": entry["source"], "japanese": entry["japanese"]},
        "nextStep": "independent-second-source-review" if record["status"] == "error" else "source-adjudication",
        "severityTentative": record["status"] == "uncertain" and record.get("severity") is not None,
        "productionApplied": False}


def assemble(run):
    prepared = preflight(run)
    run, snapshot, entries, manifest, batches = prepared
    folder = run / "source-ledger"
    reused = read(folder / "reuse.json")
    decisions = dict(reused["fields"])
    validated_results = []
    for path in sorted((run / "primary").glob("*.json")):
        payload = read(path)
        require(path.name == payload.get("batchId", "") + ".json", "Result filename/batch mismatch")
        review = validate_payload(run, payload, prepared)
        review["rawResult"] = file_ref(path)
        review["rawResultCanonicalSha256"] = sha(payload)
        old = folder / "validated" / path.name
        require(not old.exists() or read(old) == review, "Validated result changed; assemble refused")
        validated_results.append((old, review))
        for decision in review["decisions"]:
            decision = deepcopy(decision)
            key = field_key(decision["entryId"], decision["path"])
            require(key not in decisions, "Batch overlaps reused/previous source-reviewed fields")
            decision["provenance"]["rawResult"] = review["rawResult"]
            decisions[key] = decision
    ledger, issues, integrity = [], [], []
    statuses = Counter({"pass": 0, "error": 0, "uncertain": 0, "not_reviewed": 0})
    nontranslate = Counter({"preserve": 0, "empty": 0, "pass": 0, "error": 0})
    for entry in snapshot["entries"]:
        entry_context = context_sha(entry)
        for field in entry["fields"]:
            if field["mode"] != "translate":
                nontranslate[field["mode"]] += 1
                passed = field["currentJapanese"] == (field["sourceText"] if field["mode"] == "preserve" else "")
                nontranslate["pass" if passed else "error"] += 1
                if not passed:
                    integrity.append({"entryId": entry["id"], "path": field["path"], "mode": field["mode"],
                        "sourceText": field["sourceText"], "currentJapanese": field["currentJapanese"], "writeLocation": field["writeLocation"]})
                continue
            key = field_key(entry["id"], field["path"])
            review = decisions.get(key)
            status = review["status"] if review else "not_reviewed"
            statuses[status] += 1
            value = {"entryId": entry["id"], "path": field["path"], "status": status,
                "contextSha256": entry_context, "sourceTextRawUTF8Sha256": sha(field["sourceText"].encode()),
                "targetTextRawUTF8Sha256": sha(field["currentJapanese"].encode()), "writeLocation": field["writeLocation"],
                "sourceReview": review, "machineAssessment": None}
            ledger.append(value)
            if review and status in {"error", "uncertain"}:
                issues.append(_issue(review, entry, field))
    require(sum(statuses.values()) == len(ledger) == manifest["counts"]["translateFields"], "Source status denominator mismatch")
    # All results validate before any new completion marker/derived output is written.
    for destination, review in validated_results:
        if not destination.exists():
            exclusive_json(destination, review)
    for _, review in validated_results:
        require(file_ref(review["rawResult"]["path"])["fileSha256"] == review["rawResult"]["fileSha256"], "Result changed during assembly")
    preflight(run)
    status = {"schemaVersion": VERSION, "kind": "independent-source-review-progress", "snapshotSha256": manifest["snapshot"]["fileSha256"],
        "counts": dict(statuses), "translateFields": len(ledger),
        "reviewedCurrentFields": statuses["pass"] + statuses["error"] + statuses["uncertain"],
        "reusedStatusCounts": dict(Counter(x["status"] for x in reused["fields"].values())),
        "completedBatches": len(validated_results), "totalBatches": len(batches["batches"]),
        "rawResults": [review["rawResult"] for _, review in validated_results],
        "invalidatedHistoricalEntries": reused["invalidated"], "reuseConflicts": reused["conflicts"],
        "deterministicNontranslate": dict(nontranslate), "semanticIssueCount": len(issues),
        "sourceTraversalComplete": statuses["not_reviewed"] == 0,
        "semanticAcceptanceClear": statuses["not_reviewed"] == statuses["error"] == statuses["uncertain"] == nontranslate["error"] == 0,
        "machinePassCountsAsSourceReview": False, "professionalHumanCertification": False,
        "productionModified": False, "note": "Derived source-only state. Model records are never inputs. Error/uncertain remain unresolved work; complete traversal is not semantic clearance."}
    atomic_json(folder / "ledger.json", ledger)
    atomic_json(folder / "status.json", status)
    (folder / "issues.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in issues))
    (folder / "integrity-issues.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in integrity))
    markdown = ["# Independent source-review issues", "", "These are unresolved source findings, not automatic production patches.", ""]
    for issue in issues:
        markdown += ["## " + issue["entryId"] + " / " + issue["path"], "", "Status: " + issue["status"], "",
            "Source: " + json.dumps(issue["sourceText"], ensure_ascii=False), "",
            "Japanese: " + json.dumps(issue["currentJapanese"], ensure_ascii=False), "",
            "Explanation: " + issue["explanation"], "", "````json", json.dumps(issue, ensure_ascii=False, indent=2), "````", ""]
    (folder / "issues.md").write_text("\n".join(markdown))
    return {"assembled": True, "status": relative(folder / "status.json"), "ledger": relative(folder / "ledger.json"),
            "issues": relative(folder / "issues.jsonl"), "counts": dict(statuses), "semanticAcceptanceClear": status["semanticAcceptanceClear"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare")
    p.add_argument("--run", required=True)
    p.add_argument("--reuse-catalog", required=True)
    p = commands.add_parser("validate")
    p.add_argument("--run", required=True)
    p.add_argument("--result", required=True)
    p = commands.add_parser("assemble")
    p.add_argument("--run", required=True)
    args = parser.parse_args(argv)
    try:
        value = prepare(args.run, args.reuse_catalog) if args.command == "prepare" else (
            validate(args.run, args.result) if args.command == "validate" else assemble(args.run))
        print(json.dumps(value, ensure_ascii=False))
        return 0
    except (ReviewError, OSError, KeyError, TypeError) as error:
        # No source text or model generation is included in validation errors.
        message = str(error) if isinstance(error, ReviewError) else "Malformed review artifact; no new batch completion accepted"
        print(json.dumps({"status": "refused", "reason": message}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
