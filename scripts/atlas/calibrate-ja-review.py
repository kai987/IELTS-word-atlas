#!/usr/bin/env python3
"""Prepare an unseen Japanese-review holdout and measure detection and repairs.

This tool never calls models or edits the corpus. Gold labels are deliberately
blank until an independent source-grounded reviewer supplies them. A completed
metric report is not permission to publish or proof of semantic correctness.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
OLD_SAMPLE = ROOT / "scripts/atlas/ja-benchmark-100.json"
GOLD_STATUSES = {"pass", "error"}
MODEL_STATUSES = GOLD_STATUSES | {"uncertain", "unavailable"}
SEVERITIES = {"minor", "major", "critical"}


def digest(value):
    raw = value if isinstance(value, bytes) else json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save_new_or_same(path, value):
    path = Path(path).resolve()
    if any(protected == path or protected in path.parents for protected in [ROOT / "data", ROOT / "public", ROOT / ".git"]):
        raise ValueError("Calibration material must stay outside data/, public/ and .git/")
    if path.exists():
        if read(path) != value:
            raise ValueError(f"Refusing to overwrite different calibration material: {path.name}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def excluded_benchmark_ids(path=OLD_SAMPLE):
    sample = read(path)
    return {entry["id"] for entry in sample["entries"]}


def select_entries(entries, count=100, seed=20261026, excluded_ids=None):
    """Deterministic balanced CEFR selection, preferring underrepresented topics.

    Topics are covered rarest first where CEFR quotas permit; uncovered topics
    are reported by prepare rather than silently claiming universal coverage.
    """
    if type(count) is not int or count < 1:
        raise ValueError("Holdout count must be a positive integer")
    excluded_ids = set(excluded_ids or ())
    eligible = [entry for entry in entries if entry["id"] not in excluded_ids
                and any(field.get("mode") == "translate" for field in entry["fields"])]
    if len({entry["id"] for entry in eligible}) != len(eligible):
        raise ValueError("Duplicate entry IDs in snapshot")
    if count > len(eligible):
        raise ValueError("Not enough unseen translatable entries for the requested holdout")
    rank = lambda entry: digest(f"{seed}:{entry['id']}".encode())
    levels = sorted({str(entry.get("cefr", "unknown")) for entry in eligible})
    groups = {level: sorted([entry for entry in eligible if str(entry.get("cefr", "unknown")) == level], key=rank)
              for level in levels}
    quotas = Counter()
    while sum(quotas.values()) < count:
        for level in levels:
            if quotas[level] < len(groups[level]) and sum(quotas.values()) < count:
                quotas[level] += 1
    selected, seen, level_counts, topic_counts = [], set(), Counter(), Counter()
    topics = defaultdict(list)
    for entry in eligible:
        topics[str(entry.get("topic", "unknown"))].append(entry)

    def choose(candidates):
        options = [entry for entry in candidates if entry["id"] not in seen
                   and level_counts[str(entry.get("cefr", "unknown"))] < quotas[str(entry.get("cefr", "unknown"))]]
        if not options or len(selected) >= count:
            return False
        chosen = min(options, key=lambda entry: (
            topic_counts[str(entry.get("topic", "unknown"))],
            level_counts[str(entry.get("cefr", "unknown"))] / max(quotas[str(entry.get("cefr", "unknown"))], 1),
            rank(entry)))
        selected.append(chosen)
        seen.add(chosen["id"])
        level_counts[str(chosen.get("cefr", "unknown"))] += 1
        topic_counts[str(chosen.get("topic", "unknown"))] += 1
        return True

    for topic in sorted(topics, key=lambda topic: (len(topics[topic]), topic)):
        choose(topics[topic])
    while len(selected) < count:
        if not choose(eligible):
            raise ValueError("Unable to fulfill holdout quotas")
    return selected


def prepare(run, out, count=100, seed=20261026, exclude_selections=None):
    run, out = Path(run).resolve(), Path(out).resolve()
    if any(protected == out or protected in out.parents for protected in [(ROOT / "data").resolve(), (ROOT / "public").resolve()]):
        raise ValueError("Calibration outputs must stay outside data/ and public/")
    snapshot_path = run if run.is_file() else run / "snapshot.json"
    snapshot_raw = snapshot_path.read_bytes()
    sidecar = snapshot_path.parent / "snapshot-sha256.txt"
    if not sidecar.is_file() or sidecar.read_text().strip() != digest(snapshot_raw):
        raise ValueError("Frozen review snapshot hash is missing or changed; prepare the run before calibration")
    snapshot = json.loads(snapshot_raw)
    if snapshot.get("schemaVersion") != 1 or not isinstance(snapshot.get("entries"), list):
        raise ValueError("Expected the frozen semantic-review snapshot schema")
    if snapshot.get("manifest", {}).get("kind") == "controlled-probes":
        raise ValueError("Controlled probes must stay separate from the unseen natural holdout")
    entries = snapshot["entries"]
    excluded = excluded_benchmark_ids()
    additional_exclusions = []
    for exclusion_path in exclude_selections or []:
        exclusion_path = Path(exclusion_path)
        prior = read(exclusion_path)
        ids = prior.get("entryIds")
        if not isinstance(ids, list) or any(not isinstance(value, str) for value in ids):
            raise ValueError("Exclusion selections must contain string entryIds")
        excluded.update(ids)
        additional_exclusions.append({"sha256": digest(exclusion_path.read_bytes()), "entryIds": ids})
    chosen = select_entries(entries, count=count, seed=seed, excluded_ids=excluded)
    fields = [{"entryId": entry["id"], "path": field["path"], "expectedStatus": None,
               "severity": None, "categories": [], "note": ""}
              for entry in chosen for field in entry["fields"] if field["mode"] == "translate"]
    topic_counts = Counter(str(entry.get("topic", "unknown")) for entry in chosen)
    selection = {"schemaVersion": 1, "kind": "unseen-natural-holdout", "seed": seed,
                 "method": "Balanced CEFR quotas; rare-topic coverage first; SHA-256 seeded tie-breaking",
                 "scope": "Unseen stratified calibration material, not a population-random corpus accuracy estimate",
                 "snapshotSha256": digest(snapshot_path.read_bytes()),
                 "manifestSha256": digest(snapshot.get("manifest", {})),
                 "excludedBenchmarkSha256": digest(OLD_SAMPLE.read_bytes()),
                 "additionalExclusionSelections": additional_exclusions,
                 "excludedIds": sorted(excluded), "entryIds": [entry["id"] for entry in chosen],
                 "counts": {"entries": len(chosen), "translateFields": len(fields),
                            "cefr": dict(Counter(str(entry.get("cefr", "unknown")) for entry in chosen)),
                            "topics": dict(topic_counts)},
                 "uncoveredTopics": sorted({str(entry.get("topic", "unknown")) for entry in entries
                                             if entry["id"] not in excluded} - set(topic_counts)),
                 "entries": chosen}
    gold = {"schemaVersion": 1, "selectionSha256": digest(selection),
            "reviewer": {"name": "", "method": "", "independent": False},
            "instructions": "Independently compare every source/currentJapanese field. Fill pass/error; errors require severity, categories and note. Do not label model agreement as gold.",
            "fields": fields}
    selection_path, gold_path = out / "selection.json", out / "gold-template.json"
    # Check both files before writing either; preserve independently filled gold.
    if selection_path.exists() and read(selection_path) != selection:
        raise ValueError("Existing holdout uses different inputs/selection; choose a new directory")
    if gold_path.exists():
        existing_gold = read(gold_path)
        if existing_gold.get("selectionSha256") != digest(selection):
            raise ValueError("Existing gold template is bound to another selection")
        gold = existing_gold
    save_new_or_same(selection_path, selection)
    save_new_or_same(gold_path, gold)
    return selection, gold


def selected_fields(selection):
    result = {}
    for entry in selection["entries"]:
        for field in entry["fields"]:
            if field["mode"] != "translate":
                continue
            key = (entry["id"], field["path"])
            if key in result:
                raise ValueError("Duplicate selected field")
            result[key] = field
    return result


def _load_prediction_views(selection, records, stage="detect"):
    if not re.fullmatch(r"[a-z][a-z0-9-]*", stage):
        raise ValueError("Invalid record stage/lane name")
    root = Path(records)
    if not (root / stage).exists():
        root = root / "records"
    prediction_views, record_issues, protocols = {"model": {}, "guarded": {}}, [], set()
    bound_protocol = None
    if selection.get("snapshotSha256"):
        protocol_path = root.parent / "protocols" / f"{stage}.json"
        try:
            snapshot_raw = (root.parent / "snapshot.json").read_bytes()
            if digest(snapshot_raw) != selection["snapshotSha256"]:
                raise ValueError("Record run snapshot differs from the frozen selection")
            frozen_entries = {entry["id"]: entry for entry in json.loads(snapshot_raw)["entries"]}
            if any(frozen_entries.get(entry["id"]) != entry for entry in selection["entries"]):
                raise ValueError("Selected entry contents differ from the declared frozen snapshot")
            protocol = read(protocol_path)
            if protocol.get("snapshotSha256") != selection["snapshotSha256"]:
                raise ValueError("Record protocol belongs to another frozen snapshot")
            bound_protocol = digest(protocol)
        except (OSError, ValueError, TypeError, AttributeError, KeyError) as error:
            return prediction_views, [{"entryId": None, "status": "unbound-protocol", "reason": str(error)}], []
    for entry in selection["entries"]:
        word = entry["id"]
        paths = list((root / stage / word).glob("attempt-*.json"))
        attempts = [(int(match[1]), path) for path in paths
                    if (match := re.fullmatch(r"attempt-(\d+)\.json", path.name))]
        if not attempts:
            record_issues.append({"entryId": word, "status": "missing", "reason": "No attempt recorded"})
            continue
        numbers = [number for number, _ in attempts]
        if len(set(numbers)) != len(numbers):
            record_issues.append({"entryId": word, "status": "invalid", "reason": "Duplicate attempt numbers"})
            continue
        _, chosen = max(attempts)
        try:
            record = read(chosen)
            if record.get("status") != "complete":
                record_issues.append({"entryId": word, "status": record.get("status", "invalid"),
                                      "reason": "Latest attempt is not complete"})
                continue
            if record.get("id") != word:
                raise ValueError("Attempt ID does not match its directory")
            if bound_protocol is not None and record.get("protocolSha256") != bound_protocol:
                raise ValueError("Attempt is not bound to the matching frozen protocol")
            if record.get("snapshotSha256") not in {None, selection.get("snapshotSha256")}:
                raise ValueError("Attempt belongs to another frozen snapshot")
            if record.get("protocolSha256"):
                protocols.add(record["protocolSha256"])
            assessments = record["result"]["assessments"]
            if not isinstance(assessments, list):
                raise ValueError("Expected an assessment array")
            seen = set()
            allowed = {field["path"] for field in entry["fields"]}
            for assessment in assessments:
                path = assessment.get("path")
                if path not in allowed or path in seen or assessment.get("status") not in MODEL_STATUSES:
                    raise ValueError("Invalid, duplicate or unknown assessment")
                original = assessment.get("modelAssessment", assessment)
                if (not isinstance(original, dict) or original.get("status") not in MODEL_STATUSES
                        or original.get("path", path) != path):
                    raise ValueError("Invalid or misbound retained model assessment")
                seen.add(path)
            for assessment in assessments:
                key = (word, assessment["path"])
                prediction_views["guarded"][key] = assessment["status"]
                prediction_views["model"][key] = assessment.get("modelAssessment", assessment)["status"]
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
            record_issues.append({"entryId": word, "status": "invalid", "reason": str(error)})
    if len(protocols) > 1:
        # An experiment lane must have a single frozen inference protocol.
        record_issues.append({"entryId": None, "status": "mixed-protocols", "reason": "Use separate records roots/lanes for different protocols"})
        prediction_views = {"model": {}, "guarded": {}}
    return prediction_views, record_issues, sorted(protocols)


def load_predictions(selection, records, stage="detect", view="guarded"):
    if view not in {"model", "guarded"}:
        raise ValueError("Assessment view must be model or guarded")
    views, issues, protocols = _load_prediction_views(selection, records, stage)
    return views[view], issues, protocols


def _evaluate_view(selection, gold, records, stage="detect", view="guarded", loaded=None,
                   allow_unresolved_gold=False):
    expected = selected_fields(selection)
    problems = []
    if gold.get("selectionSha256") != digest(selection):
        problems.append("Gold labels do not match the frozen selection hash")
    reviewer = gold.get("reviewer", {})
    if (not isinstance(reviewer, dict) or not isinstance(reviewer.get("name"), str) or not reviewer["name"].strip()
            or not isinstance(reviewer.get("method"), str) or not reviewer["method"].strip()
            or reviewer.get("independent") is not True):
        problems.append("Independent gold reviewer name/method/attestation is incomplete")
    labels = {}
    unresolved = []
    if not isinstance(gold.get("fields"), list):
        problems.append("Gold fields must be an array")
    else:
        for item in gold["fields"]:
            if not isinstance(item, dict):
                problems.append("Malformed gold field")
                continue
            if not isinstance(item.get("entryId"), str) or not isinstance(item.get("path"), str):
                problems.append("Gold field ID/path must be strings")
                continue
            key = (item.get("entryId"), item.get("path"))
            if key not in expected or key in labels:
                problems.append(f"Unknown or duplicate gold field: {key}")
                continue
            labels[key] = item
            if allow_unresolved_gold and "reviewStatus" in item:
                review_status = item["reviewStatus"]
                expected_status = item.get("expectedStatus")
                if not isinstance(review_status, str) or review_status not in {"pass", "error", "uncertain"}:
                    problems.append(f"Unknown independent review status: {key}")
                elif isinstance(expected_status, str) and expected_status in GOLD_STATUSES and review_status != expected_status:
                    problems.append(f"Independent review status contradicts resolved label: {key}")
            reviewed_uncertain = (allow_unresolved_gold and "expectedStatus" in item
                                  and item["expectedStatus"] is None
                                  and item.get("reviewStatus") == "uncertain"
                                  and isinstance(item.get("note"), str) and bool(item["note"].strip()))
            if reviewed_uncertain:
                unresolved.append({"entryId": key[0], "path": key[1], "note": item["note"]})
            elif not isinstance(item.get("expectedStatus"), str) or item["expectedStatus"] not in GOLD_STATUSES:
                problems.append(f"Unlabeled gold field: {key}")
            elif item["expectedStatus"] == "error" and (
                    item.get("severity") not in SEVERITIES or not isinstance(item.get("categories"), list)
                    or not item["categories"] or any(not isinstance(value, str) or not value for value in item["categories"])
                    or not isinstance(item.get("note"), str) or not item["note"].strip()):
                problems.append(f"Error label lacks severity/categories/source-grounded note: {key}")
    missing_gold = set(expected) - set(labels)
    if missing_gold:
        problems.append(f"Missing gold fields: {len(missing_gold)}")
    report = {"schemaVersion": 1, "stage": stage, "assessmentView": view, "selectionSha256": digest(selection),
              "selectionKind": selection.get("kind", "unspecified fixture"), "populationAccuracyEstimate": False,
              "calibrationCodeSha256": digest(Path(__file__).read_bytes()),
              "goldSha256": digest(gold), "counts": {"selectedFields": len(expected)},
              "status": "incomplete", "passed": False, "metrics": None,
              "goldProblems": problems, "acceptanceDecision": "not assessed",
              "assessmentMeaning": "Retained model judgment after structural/source-quote validation; not unparsed raw text" if view == "model" else "Judgment after deterministic guards; HOLD is not an error detection or semantic pass",
              "note": "Measurements do not authorize publication/full-corpus acceptance. Uncertain/unavailable/missing are never passes."}
    scorable = sum(isinstance(item.get("expectedStatus"), str) and item["expectedStatus"] in GOLD_STATUSES
                   for item in labels.values())
    if allow_unresolved_gold:
        report.update({"allowUnresolvedGold": True, "unresolvedGold": unresolved,
                       "resolvedGoldCoverage": scorable / len(expected) if expected else None,
                       "metricDenominator": "scorableFields"})
        report["counts"]["scorableFields"] = scorable
        report["note"] += " Explicitly reviewed unresolved gold is excluded from scoring, never treated as correct or passed."
    if problems:
        return report
    if unresolved and not scorable:
        report["acceptanceDecision"] = "held: unresolved independent gold"
        return report
    predictions, record_issues, protocols = load_predictions(selection, records, stage, view) if loaded is None else loaded
    counts = Counter({"goldErrors": 0, "goldCorrect": 0, "trueErrorDetections": 0,
                      "errorsApprovedAsPass": 0, "falseErrorReports": 0, "correctPasses": 0,
                      "uncertain": 0, "unavailable": 0, "missing": 0,
                      "errorUncertain": 0, "errorUnavailable": 0, "errorMissing": 0,
                      "correctUncertain": 0, "correctUnavailable": 0, "correctMissing": 0,
                      "criticalErrors": 0, "criticalErrorsApprovedAsPass": 0})
    per_field = []
    for key, label in labels.items():
        if label["expectedStatus"] is None:
            # Only attested reviewed-uncertain rows can reach this point. All
            # other unlabeled or unknown states returned metrics=None above.
            continue
        truth = label["expectedStatus"]
        prediction = predictions.get(key, "missing")
        is_error = truth == "error"
        counts["goldErrors" if is_error else "goldCorrect"] += 1
        if is_error and label.get("severity") == "critical":
            counts["criticalErrors"] += 1
        if prediction in {"uncertain", "unavailable", "missing"}:
            counts[prediction] += 1
            counts[("error" if is_error else "correct") + prediction.title()] += 1
        elif prediction == "error":
            counts["trueErrorDetections" if is_error else "falseErrorReports"] += 1
        else:
            counts["errorsApprovedAsPass" if is_error else "correctPasses"] += 1
            if is_error and label.get("severity") == "critical":
                counts["criticalErrorsApprovedAsPass"] += 1
        per_field.append({"entryId": key[0], "path": key[1], "expected": truth, "predicted": prediction,
                          "severity": label.get("severity")})
    rate = lambda numerator, denominator: numerator / denominator if denominator else None
    tp, fp, fn, tn = [counts[key] for key in ["trueErrorDetections", "falseErrorReports", "errorsApprovedAsPass", "correctPasses"]]
    denominator = scorable if allow_unresolved_gold else len(expected)
    report.update({"status": "incomplete" if counts["missing"] or record_issues or unresolved else "complete",
                   "passed": None, "reviewer": reviewer, "protocolSha256": protocols,
                   "recordIssues": record_issues, "counts": {"selectedFields": len(expected), **dict(counts)},
                   "metrics": {"errorDetectionRecall": rate(tp, counts["goldErrors"]),
                               "errorReportPrecision": rate(tp, tp + fp),
                               "errorsApprovedAsPassRate": rate(fn, counts["goldErrors"]),
                               "notDetectedErrorRate": rate(counts["goldErrors"] - tp, counts["goldErrors"]),
                               "falsePositiveRate": rate(fp, counts["goldCorrect"]),
                               "residualErrorAmongPasses": rate(fn, fn + tn),
                               "conclusiveCoverage": rate(tp + fp + fn + tn, denominator),
                               "uncertainRate": rate(counts["uncertain"], denominator),
                               "unavailableRate": rate(counts["unavailable"], denominator),
                               "missingRate": rate(counts["missing"], denominator)},
                   "repairMetrics": {"status": "separate evaluation required", "commands": ["repair-template", "repair-evaluate"],
                                     "reason": "Requires independent labels for each proposed correction and its before/after meaning; detection labels cannot prove repair correctness."},
                   "fields": per_field})
    if allow_unresolved_gold:
        report["counts"]["scorableFields"] = scorable
    if unresolved:
        report["acceptanceDecision"] = "held: unresolved independent gold"
    if report["status"] == "incomplete":
        report["passed"] = False
    return report


def evaluate(selection, gold, records, stage="detect", view="guarded", allow_unresolved_gold=False):
    """Report both views from the same attempts, with one selected primary view."""
    if view not in {"model", "guarded"}:
        raise ValueError("Assessment view must be model or guarded")
    predictions, issues, protocols = _load_prediction_views(selection, records, stage)
    reports = {name: _evaluate_view(selection, gold, records, stage, name,
                                  (predictions[name], issues, protocols), allow_unresolved_gold)
               for name in ("model", "guarded")}
    report = reports[view]
    keys = ["assessmentView", "assessmentMeaning", "status", "counts", "metrics", "recordIssues", "protocolSha256"]
    if allow_unresolved_gold:
        keys += ["passed", "acceptanceDecision", "unresolvedGold", "resolvedGoldCoverage", "metricDenominator"]
    report["views"] = {name: {key: result.get(key) for key in keys} for name, result in reports.items()}
    return report


def repair_material(run, stage="repair"):
    """Bind every actual latest proposal, including machine-blocked candidates."""
    run = Path(run).resolve()
    if not re.fullmatch(r"[a-z][a-z0-9-]*", stage):
        raise ValueError("Invalid repair stage/lane")
    snapshot_raw = (run / "snapshot.json").read_bytes()
    snapshot_hash = digest(snapshot_raw)
    if (run / "snapshot-sha256.txt").read_text().strip() != snapshot_hash:
        raise ValueError("Frozen snapshot content/hash changed")
    snapshot = json.loads(snapshot_raw)
    protocol = read(run / "protocols" / f"{stage}.json")
    if protocol.get("snapshotSha256") != snapshot_hash:
        raise ValueError("Repair protocol belongs to another frozen snapshot")
    if protocol.get("role") not in {None, "repair"}:
        raise ValueError("Only a repair stage may be scored as repair proposals")
    protocol_hash = digest(protocol)
    entries = {entry["id"]: entry for entry in snapshot["entries"]}
    items, issues = [], []
    counts = Counter({"entriesWithRecords": 0, "completeRecords": 0, "failedRecords": 0,
                      "unfinishedRecords": 0, "actualProposals": 0, "machineEligible": 0,
                      "machineBlocked": 0, "fieldFailed": 0, "invalidProposals": 0,
                      "unknownRecordEntries": 0})
    folder = run / "records" / stage
    for directory in sorted(folder.iterdir()) if folder.exists() else []:
        if not directory.is_dir():
            continue
        paths = [(int(match[1]), path) for path in directory.glob("attempt-*.json")
                 if (match := re.fullmatch(r"attempt-(\d+)\.json", path.name))]
        if not paths:
            continue
        word = directory.name
        if word not in entries or len({number for number, _ in paths}) != len(paths):
            counts["unknownRecordEntries"] += 1
            issues.append(f"Unknown entry or duplicate attempt numbers: {word}")
            continue
        counts["entriesWithRecords"] += 1
        _, path = max(paths)
        raw = path.read_bytes()
        record = json.loads(raw)
        if (record.get("id") != word or record.get("protocolSha256") != protocol_hash
                or record.get("snapshotSha256") != snapshot_hash):
            issues.append(f"Repair record input/protocol binding mismatch: {word}")
            continue
        status = record.get("status")
        if status == "complete":
            counts["completeRecords"] += 1
        elif status in {"error", "interrupted"}:
            counts["failedRecords"] += 1
        else:
            counts["unfinishedRecords"] += 1
            issues.append(f"Latest record is not terminal: {word}")
            continue
        result_body = record.get("result", {})
        if not isinstance(result_body, dict):
            issues.append(f"Malformed repair result: {word}")
            continue
        proposals = result_body.get("proposals", [])
        if not isinstance(proposals, list):
            issues.append(f"Malformed proposal array: {word}")
            continue
        fields = {field["path"]: field for field in entries[word]["fields"]}
        seen = set()
        for result in proposals:
            if not isinstance(result, dict) or result.get("path") not in fields or result.get("path") in seen:
                counts["invalidProposals"] += 1
                issues.append(f"Unknown or duplicate proposal path: {word}")
                continue
            field_path = result["path"]
            seen.add(field_path)
            proposal = result.get("proposal")
            if not isinstance(proposal, dict):
                counts["fieldFailed"] += 1
                continue
            field = fields[field_path]
            if (proposal.get("path") != field_path or proposal.get("before") != field["currentJapanese"]
                    or not isinstance(proposal.get("text"), str)
                    or result.get("proposalSha256") != digest(proposal)):
                counts["invalidProposals"] += 1
                issues.append(f"Proposal is not bound to its frozen before/hash: {word}.{field_path}")
                continue
            blocked = result.get("status") == "blocked" or bool(result.get("gateErrors"))
            eligible = status == "complete" and result.get("status") == "complete" and not blocked
            counts["actualProposals"] += 1
            counts["machineBlocked"] += bool(blocked)
            counts["machineEligible"] += bool(eligible)
            if result.get("status") not in {"complete", "blocked"}:
                counts["fieldFailed"] += 1
            items.append({"entryId": word, "path": field_path, "word": entries[word].get("word", word),
                          "sourceLanguage": field["sourceLanguage"], "sourceText": field["sourceText"],
                          "beforeText": proposal["before"], "afterText": proposal["text"],
                          "proposalSha256": digest(proposal), "recordSha256": digest(raw),
                          "machineStatus": result.get("status"), "recordStatus": status,
                          "machineEligible": bool(eligible), "machineBlocked": bool(blocked),
                          "beforeStatus": None, "afterStatus": None,
                          "beforeSeverity": None, "afterSeverity": None, "note": ""})
    counts["entriesWithoutRepairRecords"] = len(entries) - counts["entriesWithRecords"]
    return {"snapshotSha256": snapshot_hash, "stageProtocolSha256": protocol_hash,
            "items": items, "counts": dict(counts), "materialProblems": issues}


def repair_template(run, stage="repair"):
    material = repair_material(run, stage)
    return {"schemaVersion": 1, "kind": "independent-repair-labels", "stage": stage,
            "snapshotSha256": material["snapshotSha256"],
            "stageProtocolSha256": material["stageProtocolSha256"],
            "reviewer": {"name": "", "method": "", "independent": False},
            "instructions": "Independently assess source vs beforeText and afterText. Do not copy model cross-check decisions into gold. pass requires severity none/null; error requires minor/major/critical. Record source-grounded evidence in note.",
            "materialCounts": material["counts"], "materialProblems": material["materialProblems"],
            "items": material["items"]}


def repair_evaluate(run, gold, stage="repair"):
    material = repair_material(run, stage)
    problems = list(material["materialProblems"])
    if (gold.get("snapshotSha256") != material["snapshotSha256"] or gold.get("stage") != stage
            or gold.get("stageProtocolSha256") != material["stageProtocolSha256"]):
        problems.append("Repair gold is bound to another snapshot/stage/protocol")
    reviewer = gold.get("reviewer", {})
    if (not isinstance(reviewer, dict) or not isinstance(reviewer.get("name"), str) or not reviewer["name"].strip()
            or not isinstance(reviewer.get("method"), str) or not reviewer["method"].strip()
            or reviewer.get("independent") is not True):
        problems.append("Independent source-grounded reviewer provenance is incomplete")
    expected = {(item["entryId"], item["path"]): item for item in material["items"]}
    labels = {}
    incomplete_labels, stale_labels = set(), set()
    ranks = {None: 0, "none": 0, "minor": 1, "major": 2, "critical": 3}
    if not isinstance(gold.get("items"), list):
        problems.append("Repair gold items must be an array")
    else:
        for item in gold["items"]:
            if not isinstance(item, dict) or not isinstance(item.get("entryId"), str) or not isinstance(item.get("path"), str):
                problems.append("Malformed repair label ID/path")
                continue
            key = (item["entryId"], item["path"])
            if key not in expected or key in labels:
                problems.append(f"Unknown or duplicate repair label: {key}")
                continue
            labels[key] = item
            if any(item.get(name) != expected[key][name] for name in ("proposalSha256", "recordSha256")):
                problems.append(f"Latest record/proposal differs from independent repair label: {key}")
                stale_labels.add(key)
            if any(name in item and item[name] != expected[key][name] for name in ("sourceText", "beforeText", "afterText")):
                problems.append(f"Repair label context differs from its bound source/proposal: {key}")
                stale_labels.add(key)
            for which in ("before", "after"):
                status, severity = item.get(which + "Status"), item.get(which + "Severity")
                if (not isinstance(status, str) or status not in GOLD_STATUSES
                        or (severity is not None and not isinstance(severity, str)) or severity not in ranks
                        or (status == "error" and severity not in SEVERITIES)
                        or (status == "pass" and severity not in {None, "none"})):
                    problems.append(f"Incomplete or contradictory {which} semantic label: {key}")
                    incomplete_labels.add(key)
            if not isinstance(item.get("note"), str) or not item["note"].strip():
                problems.append(f"Repair label needs source-grounded note: {key}")
                incomplete_labels.add(key)
    missing = set(expected) - set(labels)
    if missing:
        problems.append(f"Missing independent repair labels: {len(missing)}")
    if not expected:
        problems.append("No actual repair proposals are available for semantic repair calibration")
    report = {"schemaVersion": 1, "kind": "repair-quality-evaluation", "stage": stage,
              "calibrationCodeSha256": digest(Path(__file__).read_bytes()),
              "snapshotSha256": material["snapshotSha256"], "goldSha256": digest(gold),
              "status": "incomplete", "passed": False, "metrics": None,
              "counts": {**material["counts"], "missingIndependentLabels": len(missing | incomplete_labels),
                         "staleIndependentLabels": len(stale_labels)},
              "goldProblems": problems, "acceptanceDecision": "not assessed",
              "measurementScope": "Latest actual repair proposals; stage failures and whole-corpus coverage are separate",
              "note": "Semantic labels must come from independent source-grounded review. Model cross-check agreement is not gold. Machine-blocked candidates and failed attempts remain visible; unprocessed entries are not successful repairs."}
    if problems:
        return report
    counts = Counter({"validRepairCount": 0, "regressionCount": 0, "stillErroneousCount": 0,
                      "worsenedCount": 0, "styleOnlyCount": 0, "reviewedProposals": len(labels),
                      "beforeErrorCount": 0, "beforeCorrectCount": 0,
                      "eligibleReviewedProposals": 0, "eligibleValidRepairCount": 0,
                      "eligibleRegressionCount": 0, "eligibleWorsenedCount": 0})
    outcomes = []
    for key, label in labels.items():
        before, after = label["beforeStatus"], label["afterStatus"]
        outcome = {("error", "pass"): "validRepairCount", ("pass", "error"): "regressionCount",
                   ("error", "error"): "stillErroneousCount", ("pass", "pass"): "styleOnlyCount"}[(before, after)]
        counts[outcome] += 1
        counts["beforeErrorCount" if before == "error" else "beforeCorrectCount"] += 1
        worsened = before == after == "error" and ranks[label["afterSeverity"]] > ranks[label["beforeSeverity"]]
        counts["worsenedCount"] += bool(worsened)
        eligible = expected[key]["machineEligible"]
        if eligible:
            counts["eligibleReviewedProposals"] += 1
            counts["eligibleValidRepairCount"] += outcome == "validRepairCount"
            counts["eligibleRegressionCount"] += outcome == "regressionCount"
            counts["eligibleWorsenedCount"] += bool(worsened)
        outcomes.append({"entryId": key[0], "path": key[1], "outcome": outcome,
                         "worsened": bool(worsened), "machineEligible": eligible})
    rate = lambda numerator, denominator: numerator / denominator if denominator else None
    report.update({"status": "complete", "passed": None, "reviewer": reviewer,
                   "counts": {**report["counts"], **dict(counts)},
                   "metrics": {"patchCorrectness": rate(counts["validRepairCount"], counts["reviewedProposals"]),
                               "trueFixRate": rate(counts["validRepairCount"], counts["beforeErrorCount"]),
                               "regressionRate": rate(counts["regressionCount"], counts["beforeCorrectCount"]),
                               "worseningRate": rate(counts["worsenedCount"], counts["beforeErrorCount"]),
                               "eligiblePatchCorrectness": rate(counts["eligibleValidRepairCount"], counts["eligibleReviewedProposals"])},
                   "outcomes": outcomes})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    preparation = commands.add_parser("prepare", help="Freeze an unseen selection and a deliberately unlabeled gold template")
    preparation.add_argument("--run", type=Path, required=True)
    preparation.add_argument("--out", type=Path, required=True)
    preparation.add_argument("--count", type=int, default=100)
    preparation.add_argument("--seed", type=int, default=20261026)
    preparation.add_argument("--exclude-selection", action="append", type=Path, default=[],
                             help="Also exclude a previously used holdout selection; may be repeated")
    evaluation = commands.add_parser("evaluate", help="Measure field decisions against complete independent gold labels")
    evaluation.add_argument("--selection", type=Path, required=True)
    evaluation.add_argument("--gold", type=Path, required=True)
    evaluation.add_argument("--records", type=Path, required=True)
    evaluation.add_argument("--stage", default="detect")
    evaluation.add_argument("--view", choices=["model", "guarded"], default="guarded",
                            help="Primary assessment view; both retained model and guarded measurements are reported")
    evaluation.add_argument("--allow-unresolved-gold", action="store_true",
                            help="Score only explicitly resolved labels; independently reviewed uncertain/null rows stay held and excluded")
    evaluation.add_argument("--out", type=Path, required=True)
    evaluation.add_argument("--compare", type=Path)
    evaluation.add_argument("--compare-stage")
    repair_preparation = commands.add_parser("repair-template", help="Bind latest repair candidates to blank independent before/after labels")
    repair_preparation.add_argument("--run", type=Path, required=True)
    repair_preparation.add_argument("--stage", default="repair")
    repair_preparation.add_argument("--out", type=Path, required=True)
    repair_evaluation = commands.add_parser("repair-evaluate", help="Measure fixes, regressions and severity worsening from independent labels")
    repair_evaluation.add_argument("--run", type=Path, required=True)
    repair_evaluation.add_argument("--gold", type=Path, required=True)
    repair_evaluation.add_argument("--stage", default="repair")
    repair_evaluation.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        selection, gold = prepare(args.run, args.out, args.count, args.seed, args.exclude_selection)
        print(json.dumps({"status": "prepared-unlabeled", **selection["counts"],
                          "excludedBenchmarkEntries": len(selection["excludedIds"]),
                          "uncoveredTopics": selection["uncoveredTopics"], "modelCalls": 0}, ensure_ascii=False))
        return
    if args.command == "repair-template":
        template = repair_template(args.run, args.stage)
        save_new_or_same(args.out, template)
        print(json.dumps({"status": "prepared-unlabeled", "items": len(template["items"]),
                          "counts": template["materialCounts"], "modelCalls": 0}, ensure_ascii=False))
        return
    if args.command == "repair-evaluate":
        report = repair_evaluate(args.run, read(args.gold), args.stage)
        save_new_or_same(args.out, report)
        print(json.dumps({**{key: report[key] for key in ["status", "passed", "counts", "metrics"]},
                          "goldProblemCount": len(report["goldProblems"]), "goldProblems": report["goldProblems"][:10]}, ensure_ascii=False))
        return
    selection, gold = read(args.selection), read(args.gold)
    report = evaluate(selection, gold, args.records, args.stage, args.view, args.allow_unresolved_gold)
    if args.compare:
        comparison = evaluate(selection, gold, args.compare, args.compare_stage or args.stage,
                              args.view, args.allow_unresolved_gold)
        comparison_keys = ["status", "stage", "assessmentView", "counts", "metrics", "views", "protocolSha256", "recordIssues"]
        if args.allow_unresolved_gold:
            comparison_keys += ["passed", "acceptanceDecision", "unresolvedGold", "resolvedGoldCoverage", "metricDenominator"]
        report["comparison"] = {key: comparison.get(key) for key in comparison_keys}
    save_new_or_same(args.out, report)
    unresolved_summary = ({"resolvedGoldCoverage": report["resolvedGoldCoverage"],
                           "unresolvedGoldCount": len(report["unresolvedGold"])} if args.allow_unresolved_gold else {})
    print(json.dumps({**{key: report[key] for key in ["status", "passed", "counts", "metrics"]}, **unresolved_summary,
                      "goldProblemCount": len(report["goldProblems"]), "goldProblems": report["goldProblems"][:10]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
