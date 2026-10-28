#!/usr/bin/env python3
"""Review the frozen final Japanese corpus without regenerating or publishing it."""
from __future__ import annotations

import argparse
from collections import Counter
import fcntl
import importlib.util
import json
from pathlib import Path
import re

import ja_review_core as core
import ja_review_models as models

ROOT = Path(__file__).resolve().parents[2]


def select_entries(snapshot, args):
    indexed = {entry["id"]: entry for entry in snapshot["entries"]}
    if sum(bool(value) for value in (args.ids, args.selection, args.all)) != 1:
        raise ValueError("Choose exactly one of --ids, --selection and --all")
    if args.ids:
        ids = args.ids.split(",")
    elif args.selection:
        selection = core.read(args.selection)
        if selection.get("snapshotSha256") != core.sha((args.run / "snapshot.json").read_bytes()):
            raise ValueError("Selection refers to a different frozen corpus")
        ids = selection["entryIds"]
    elif args.all:
        ids = list(indexed)
    else:
        raise ValueError("Choose --ids, --selection or explicit --all; no implicit full-corpus inference")
    if len(set(ids)) != len(ids) or any(word not in indexed for word in ids):
        raise ValueError("Unknown or duplicate frozen entry IDs")
    return [indexed[word] for word in ids]


def prepare_probes(run, dataset):
    run = core.safe_output(ROOT, run)
    value = core.read(dataset)
    if value.get("kind") != "controlled-probes" or not value.get("reviewer", {}).get("independent"):
        raise ValueError("Controlled probes require separate source-grounded fixture review")
    entries = value["entries"]
    seen = set()
    for entry in entries:
        if not core.SAFE_ID.fullmatch(entry["id"]) or entry["id"] in seen:
            raise ValueError("Duplicate/unsafe probe ID")
        seen.add(entry["id"])
        entry.setdefault("cefr", "probe")
        entry.setdefault("topic", "controlled")
        entry.setdefault("sourceSha256", core.sha([{k: f[k] for k in ("path", "sourceLanguage", "sourceText")} for f in entry["fields"]]))
        entry.setdefault("japaneseSha256", core.sha([f["currentJapanese"] for f in entry["fields"]]))
    snapshot = {"schemaVersion": 1, "manifest": {"entryCount": len(entries),
        "counts": dict(Counter(f["mode"] for e in entries for f in e["fields"])),
        "fieldCount": sum(len(e["fields"]) for e in entries), "canonicalDifferences": [],
        "files": {}, "kind": "controlled-probes", "datasetSha256": core.sha(Path(dataset).read_bytes())}, "entries": entries}
    if run.exists() and any(run.iterdir()):
        if core.load_snapshot(run) != snapshot:
            raise ValueError("Probe inputs changed; use a new run")
        return snapshot
    run.mkdir(parents=True)
    core.atomic_json(run / "snapshot.json", snapshot)
    (run / "snapshot-sha256.txt").write_text(core.sha((run / "snapshot.json").read_bytes()) + "\n")
    selection = {"schemaVersion": 1, "kind": "controlled-probes", "entryIds": list(seen),
                 "snapshotSha256": core.sha((run / "snapshot.json").read_bytes()), "entries": entries}
    # Preserve dataset order, not set iteration order.
    selection["entryIds"] = [entry["id"] for entry in entries]
    core.atomic_json(run / "selection.json", selection)
    gold = {"schemaVersion": 1, "selectionSha256": core.sha(selection),
            "reviewer": value["reviewer"], "fields": value["gold"]}
    core.atomic_json(run / "gold.json", gold)
    return snapshot


class RecordedClient(models.LocalClient):
    def __init__(self, args, profile, stage, word, attempt):
        super().__init__(args.base_url, profile["model"], profile["options"], profile["think"])
        self.folder = args.run / "calls" / stage / word / f"attempt-{attempt:06d}"
        self.calls = []

    def chat(self, messages, schema=None):
        path = self.folder / f"{len(self.calls)+1:04d}.json"
        record = {"status": "running", "startedAt": core.now()}
        if path.exists():
            raise ValueError("Refusing to overwrite a model request")
        self.calls.append(path.relative_to(self.folder.parents[3]).as_posix())
        self.on_request = lambda payload: core.atomic_json(path, {**record, "request": payload})
        try:
            result = super().chat(messages, schema)
            record.update({"status": "complete", **result})
            return result
        except models.ModelCallError as error:
            record.update({"status": "error", **error.result})
            raise
        finally:
            record["finishedAt"] = core.now()
            core.atomic_json(path, record)


def fields_for(entry):
    return {field["path"]: field for field in entry["fields"]}


def proposal_errors(entry, proposal):
    """Conservative patch gates are not a semantic correctness verdict."""
    field = fields_for(entry).get(proposal.get("path"))
    if field is None or proposal.get("before") != field["currentJapanese"]:
        return ["Proposal is not bound to the frozen field/before"]
    text = proposal.get("text")
    if not isinstance(text, str) or text == field["currentJapanese"]:
        return ["Missing or unchanged correction"]
    if field["mode"] == "empty":
        return [] if not text.strip() else ["Empty source must remain empty"]
    if field["mode"] == "preserve":
        return [] if text == field["sourceText"] else ["Original English must remain unchanged"]
    try:
        models.validate_repair(field, proposal)
    except ValueError as error:
        return [str(error)]
    # Adapt any semantic field, including the rare Chinese related-word label,
    # to the existing conservative language/literal smoke checks.
    spec = importlib.util.spec_from_file_location("legacy_ja_patch_guards", ROOT / "scripts/atlas/translate-ja-local.py")
    worker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(worker)
    path = field["path"]
    key = path.split(".")[0]
    fake = {"id": entry["id"], "w": entry["word"], "senses": [], "ex": [], "col": [], "tip": "", "note": ""}
    if key in {"tip", "note"}:
        fake[key] = field["sourceText"]
    elif key == "ex":
        fake["ex"] = [{"en": field["sourceText"] if field["sourceLanguage"] == "en" else "", "zh": field["sourceText"]}]
        path = "ex.0"
    elif key == "col":
        fake["col"] = [field["sourceText"]]
        path = "col.0"
    else:
        fake["senses"] = [{"pos": field.get("pos", ""), "en": field["sourceText"] if field["sourceLanguage"] == "en" else "", "zh": field["sourceText"]}]
        path = "senses.0"
    errors = worker.field_errors(fake, path, text)
    numbers = lambda value: Counter(re.findall(r"\d+(?:[.,:]\d+)*", value))
    preserved = numbers(field["sourceText"]) & numbers(field["currentJapanese"])
    if preserved - numbers(text):
        errors.append("Number already preserved in the existing translation was changed/removed")
    return errors


def stage_records(run, stage):
    records = core.latest_records(run, stage)
    if not records:
        return records
    protocol = core.read(Path(run) / "protocols" / f"{stage}.json")
    expected = (Path(run) / "snapshot-sha256.txt").read_text().strip()
    if protocol.get("snapshotSha256") != expected:
        raise ValueError("Upstream protocol belongs to another frozen snapshot")
    digest = core.sha(protocol)
    for word, record in records.items():
        if (record.get("id") != word or record.get("protocolSha256") != digest
                or record.get("snapshotSha256") not in {None, expected}
                or (record.get("status") == "complete" and record.get("snapshotSha256") != expected)):
            raise ValueError("Upstream attempt ID/protocol/snapshot binding is invalid")
    return records


def parent_inputs(run, stage, word, records=None):
    record = (stage_records(run, stage) if records is None else records).get(word)
    if not record or record.get("status") != "complete":
        return None, {stage: core.sha(record) if record else None}
    return record, {stage: core.sha(record)}


def model_stage(args, snapshot):
    stage = args.command
    role = {"detect": "detect", "reference": "translate", "repair": "repair", "crosscheck": "adjudicate"}[stage]
    profile = models.profile_for(role, args.preset)
    if args.model:
        profile["model"] = args.model
    for name in ("temperature", "top_k", "top_p", "num_ctx", "num_predict"):
        value = getattr(args, name)
        if value is not None:
            profile["options"][name] = value
    if args.thinking is not None:
        profile["think"] = args.thinking
    if role == "translate" and profile["think"]:
        raise ValueError("TranslateGemma is a translator, not a thinking-mode reviewer")
    lane = args.lane or stage
    entries = select_entries(snapshot, args)
    tags = models._request(args.base_url, "/api/tags")
    installed = {item["name"]: item for item in tags.get("models", [])}
    if profile["model"] not in installed:
        raise ValueError("Required selected local model is not installed; models are never downloaded automatically")
    protocol = {"schemaVersion": 1, "role": role, "lane": lane,
                "snapshotSha256": core.sha((args.run / "snapshot.json").read_bytes()),
                "profile": profile, "modelDigest": installed[profile["model"]]["digest"],
                "modelDetails": installed[profile["model"]].get("details", {}),
                "runtimeVersion": models._request(args.base_url, "/api/version").get("version"),
                "modelTemplateSha256": core.sha(models._request(args.base_url, "/api/show", {"model": profile["model"]}).get("template", "")),
                "code": {name: core.sha((ROOT / "scripts/atlas" / name).read_bytes()) for name in
                         ["review-ja-corpus.py", "ja_review_core.py", "ja_review_models.py", "translate-ja-local.py"]},
                "parentLanes": {"detect": args.detect_lane, "reference": args.reference_lane, "repair": args.repair_lane},
                "retrySourceLane": args.from_lane if stage == "detect" else None}
    models.ensure_single_model(args.base_url, profile["model"])
    store = core.AttemptStore(args.run, lane, protocol)
    for name, expected in protocol["code"].items():
        original = ROOT / "scripts/atlas" / name
        target = args.run / "code-snapshots" / expected / name
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(original.read_bytes())
        if core.sha(target.read_bytes()) != expected:
            raise ValueError("Frozen stage source code changed")
    processed = 0
    parent_stages = ({args.detect_lane, args.reference_lane} if stage == "repair" else
                     {args.repair_lane} if stage == "crosscheck" else {args.detect_lane} if stage == "reference" else set())
    # Read each parent ledger once. Scanning all prior entries for every new
    # entry would turn a full corpus run into quadratic filesystem work.
    parents = {name: stage_records(args.run, name) for name in parent_stages}
    retry_source = {}
    if stage == "detect" and args.from_lane:
        source_protocol = core.read(args.run / "protocols" / f"{args.from_lane}.json")
        if source_protocol.get("snapshotSha256") != protocol["snapshotSha256"]:
            raise ValueError("Retry source lane belongs to another frozen snapshot")
        retry_source = stage_records(args.run, args.from_lane)
    try:
        for entry in entries:
            word = entry["id"]
            previous = store.read_latest(word) or retry_source.get(word)
            parent = args.repair_lane if stage == "crosscheck" else args.detect_lane
            dependency, inputs = (None, {}) if stage == "detect" else parent_inputs(args.run, parent, word, parents[parent])
            if stage == "detect" and retry_source:
                inputs = {args.from_lane: core.sha(retry_source.get(word))}
            if stage == "repair":
                reference, ref_inputs = parent_inputs(args.run, args.reference_lane, word, parents[args.reference_lane])
                inputs.update(ref_inputs)
            else:
                reference = None
            if previous and previous.get("inputs") != inputs and not args.retry:
                raise ValueError(f"Upstream attempt changed for {word}; explicit --retry preserves both attempts")
            record = store.begin(word, args.retry)
            if record is None:
                continue
            record.update({"inputs": inputs, "snapshotSha256": protocol["snapshotSha256"],
                           "sourceSha256": entry.get("sourceSha256"), "japaneseSha256": entry.get("japaneseSha256")})
            core.atomic_json(args.run / "records" / lane / word / f"attempt-{record['attempt']:06d}.json", record)
            client = RecordedClient(args, profile, lane, word, record["attempt"])
            try:
                if stage != "detect" and dependency is None:
                    raise ValueError("Upstream review is incomplete; never infer a pass from missing evidence")
                if stage == "detect":
                    assessments = []
                    retained = {a["path"]: a for a in (previous or {}).get("result", {}).get("assessments", [])
                                if a["status"] != "unavailable"} if args.retry else {}
                    pending = [f for f in entry["fields"] if f["mode"] == "translate" and f["path"] not in retained]
                    validations = {"fieldValidationErrors": {}, "structuralErrors": []}
                    if pending:
                        request_entry = {**entry, "fields": pending}
                        messages, schema = models.build_detection(request_entry)
                        response = client.chat(messages, schema)
                        parsed = models.parse_detection(request_entry, response["text"])
                        assessments = parsed.pop("assessments")
                        validations.update(parsed)
                    assessments += [a for path, a in retained.items() if fields_for(entry).get(path, {}).get("mode") == "translate"]
                    assessments = core.guard_assessments(entry, assessments)
                    assessments += core.integrity_assessments(entry)
                    if Counter(a["path"] for a in assessments) != Counter(f["path"] for f in entry["fields"]):
                        raise ValueError("Review coverage does not match the complete field manifest")
                    result = {"assessments": assessments, **validations}
                else:
                    field_index = fields_for(entry)
                    key = {"reference": "references", "repair": "proposals", "crosscheck": "decisions"}[stage]
                    result = {key: []}
                    if stage == "crosscheck":
                        work = dependency["result"].get("proposals", [])
                    else:
                        work = [a for a in dependency["result"]["assessments"] if a["status"] in ({"error", "uncertain"} if stage == "reference" else {"error"})]
                    reference_map = {r["path"]: r for r in (reference or {}).get("result", {}).get("references", []) if r.get("status") == "complete"}
                    reusable = {r["path"]: r for r in (previous or {}).get("result", {}).get(key, [])
                                if r.get("status") == "complete" and previous.get("inputs") == inputs}
                    for item in work:
                        field = field_index[item["path"]]
                        if stage == "reference" and field["mode"] != "translate":
                            continue
                        if stage == "crosscheck" and item.get("status") != "complete":
                            continue
                        if field["path"] in reusable:
                            result[key].append({**reusable[field["path"]], "reusedFromAttempt": previous["attempt"]})
                            continue
                        output = {"path": field["path"], "status": "running"}
                        try:
                            if stage == "reference":
                                response = models.translate_field(client, field)
                                output.update({"text": response["text"], "semanticStatus": "reference only"})
                            elif stage == "repair":
                                if field["mode"] != "translate":
                                    proposal = {"path": field["path"], "before": field["currentJapanese"],
                                                "text": "" if field["mode"] == "empty" else field["sourceText"],
                                                "reason": "addition" if field["mode"] == "empty" else "mistranslation", "evidence": field["sourceText"]}
                                else:
                                    messages, schema = models.build_repair(entry, field, item, reference_map.get(field["path"]))
                                    response = client.chat(messages, schema)
                                    proposal = models.validate_repair(field, response["text"])
                                gates = proposal_errors(entry, proposal)
                                semantic_risks = core.semantic_risks({**field, "currentJapanese": proposal["text"]})
                                output.update({"proposal": proposal, "proposalSha256": core.sha(proposal),
                                               "gateErrors": gates, "semanticRiskFlags": semantic_risks,
                                               "needsIndependentDecision": True})
                                if gates:
                                    output["status"] = "blocked"
                            else:
                                proposal = item["proposal"]
                                if field["mode"] != "translate":
                                    output.update({"decision": "uncertain", "explanation": "Deterministic integrity correction requires independent final decision"})
                                else:
                                    messages, schema = models.build_adjudication(entry, field, proposal)
                                    response = client.chat(messages, schema)
                                    output.update(models.validate_adjudication(field, proposal, response["text"]))
                                output.update({"proposalSha256": item["proposalSha256"], "semanticStatus": "model cross-check only; not an independent final decision"})
                            if output["status"] == "running":
                                output["status"] = "complete"
                        except Exception as error:
                            output.update({"status": "error", "error": str(error)})
                        result[key].append(output)
                        # Preserve successful per-field work even if the process
                        # is interrupted before this entry's remaining requests.
                        core.atomic_json(args.run / "records" / lane / word / f"attempt-{record['attempt']:06d}.json", {**record, "result": result, "calls": client.calls})
                record.update({"status": "complete", "result": result})
            except Exception as error:
                record.update({"status": "error", "error": str(error)})
            record["calls"] = client.calls
            store.finish(word, record)
            processed += 1
            print(json.dumps({"event": stage, "id": word, "status": record["status"], "calls": len(client.calls)}, ensure_ascii=False), flush=True)
            if args.limit and processed >= args.limit:
                break
    finally:
        models.release_model(args.base_url, profile["model"])


def status_report(run, snapshot, lane="detect"):
    records = core.latest_records(run, lane)
    semantic, integrity = Counter(), Counter()
    for entry in snapshot["entries"]:
        record = records.get(entry["id"], {})
        by_path = {a["path"]: a for a in record.get("result", {}).get("assessments", [])} if record.get("status") == "complete" else {}
        for field in entry["fields"]:
            count = semantic if field["mode"] == "translate" else integrity
            count[by_path.get(field["path"], {}).get("status", "not_reviewed")] += 1
    return {"entryCount": snapshot["manifest"]["entryCount"], "lane": lane,
            "semanticFields": dict(semantic), "integrityFields": dict(integrity),
            "recordStatus": dict(Counter(record["status"] for record in records.values())),
            "sourceDrift": core.source_drift(ROOT, snapshot),
            "finalSemantics": "Independent final decisions are separate; model pass/accept never publishes data"}


def reparse_detection(args, snapshot):
    """Revalidate the exact original output, without generating or editing text."""
    if not args.from_lane or not args.lane or args.from_lane == args.lane:
        raise ValueError("reparse requires distinct --from-lane and --lane")
    source_protocol = core.read(args.run / "protocols" / f"{args.from_lane}.json")
    if source_protocol.get("snapshotSha256") != core.sha((args.run / "snapshot.json").read_bytes()):
        raise ValueError("Original inference belongs to another snapshot")
    protocol = {"schemaVersion": 1, "role": "offline-detection-reparse", "inferencePerformed": False,
                "snapshotSha256": source_protocol["snapshotSha256"], "sourceProtocolSha256": core.sha(source_protocol),
                "parserSha256": core.sha((ROOT / "scripts/atlas/ja_review_models.py").read_bytes()),
                "riskPolicySha256": core.sha((ROOT / "scripts/atlas/ja_review_core.py").read_bytes())}
    store = core.AttemptStore(args.run, args.lane, protocol)
    parser_snapshot = args.run / "code-snapshots" / protocol["parserSha256"] / "ja_review_models.py"
    if not parser_snapshot.exists():
        parser_snapshot.parent.mkdir(parents=True, exist_ok=True)
        parser_snapshot.write_bytes((ROOT / "scripts/atlas/ja_review_models.py").read_bytes())
    policy_snapshot = args.run / "code-snapshots" / protocol["riskPolicySha256"] / "ja_review_core.py"
    if not policy_snapshot.exists():
        policy_snapshot.parent.mkdir(parents=True, exist_ok=True)
        policy_snapshot.write_bytes((ROOT / "scripts/atlas/ja_review_core.py").read_bytes())
    records = stage_records(args.run, args.from_lane)
    for entry in select_entries(snapshot, args):
        original = records.get(entry["id"])
        if not original:
            continue
        record = store.begin(entry["id"], args.retry)
        if record is None:
            continue
        record.update({"snapshotSha256": protocol["snapshotSha256"], "inferencePerformed": False,
                       "derivedFrom": {"lane": args.from_lane, "attemptSha256": core.sha(original)}})
        try:
            calls = original.get("calls", [])
            if len(calls) != 1:
                raise ValueError("Reparse requires exactly the original single detection request")
            call_path = (args.run / calls[0]).resolve()
            if args.run.resolve() not in call_path.parents:
                raise ValueError("Unsafe original call path")
            call = core.read(call_path)
            if call.get("status") != "complete":
                raise ValueError("Incomplete model output cannot be promoted by reparsing")
            parsed = models.parse_detection(entry, call["text"])
            parsed["assessments"] = core.guard_assessments(entry, parsed["assessments"])
            parsed["assessments"] += core.integrity_assessments(entry)
            record.update({"status": "complete", "result": parsed,
                           "originalCallSha256": core.sha(call_path.read_bytes()), "calls": []})
        except Exception as error:
            record.update({"status": "error", "error": str(error)})
        store.finish(entry["id"], record)
    return status_report(args.run, snapshot, args.lane)


def export_bundle(args, snapshot):
    if snapshot["manifest"].get("kind") == "controlled-probes":
        raise ValueError("Controlled probes cannot be exported as corpus changes")
    if core.source_drift(ROOT, snapshot):
        raise ValueError("Source/final Japanese/override files changed since review; export is held")
    decisions = core.read(args.decisions)
    reviewer = decisions.get("reviewer", {})
    if (decisions.get("snapshotSha256") != core.sha((args.run / "snapshot.json").read_bytes())
            or reviewer.get("independent") is not True or not reviewer.get("name", "").strip() or not reviewer.get("method", "").strip()):
        raise ValueError("Final decisions need independent reviewer provenance and the exact frozen snapshot hash")
    entries = {entry["id"]: entry for entry in snapshot["entries"]}
    proposals = stage_records(args.run, args.repair_lane)
    patches, seen = [], set()
    for item in decisions.get("decisions", []):
        key = (item.get("entryId"), item.get("path"))
        if key in seen:
            raise ValueError("Duplicate independent final decision")
        seen.add(key)
        entry = entries.get(key[0])
        field = fields_for(entry).get(key[1]) if entry else None
        if field is None or item.get("decision") not in {"accept", "reject", "uncertain", "pass"}:
            raise ValueError("Unknown field or independent decision")
        if not isinstance(item.get("explanation"), str) or not item["explanation"].strip():
            raise ValueError("Independent decisions require source-grounded explanations")
        if item.get("sourceSha256") != core.sha(field["sourceText"]):
            raise ValueError("Independent decision source field hash does not match")
        if item["decision"] == "pass":
            if item.get("targetSha256") != core.sha(field["currentJapanese"]):
                raise ValueError("Pass decision must cover the frozen original translation")
            for name, original in [("sourceQuote", field["sourceText"]), ("targetQuote", field["currentJapanese"])]:
                quote = item.get(name)
                if not isinstance(quote, str) or (original.strip() and not quote.strip()) or (quote and quote not in original):
                    raise ValueError("Independent pass needs matching source and target evidence")
            continue
        if item["decision"] != "accept":
            continue
        record = proposals.get(entry["id"], {})
        candidates = [p for p in record.get("result", {}).get("proposals", []) if p["path"] == field["path"]]
        if (record.get("status") != "complete" or record.get("snapshotSha256") != decisions["snapshotSha256"]
                or len(candidates) != 1):
            raise ValueError("Accepted change lacks a complete matching proposal")
        proposed = candidates[0]
        proposal = proposed.get("proposal", {})
        if (proposed.get("status") != "complete" or item.get("proposalSha256") != core.sha(proposal)
                or item.get("targetSha256") != core.sha(proposal.get("text")) or proposal_errors(entry, proposal)):
            raise ValueError("Accepted proposal hash/gates do not match the independent decision")
        for key_name, original in [("sourceQuote", field["sourceText"]), ("targetQuote", proposal["text"])]:
            quote = item.get(key_name)
            if not isinstance(quote, str) or (original.strip() and not quote.strip()) or (quote and quote not in original):
                raise ValueError("Independent source/target evidence does not match the accepted field")
        patches.append({"entryId": entry["id"], **proposal, "writeLocation": field["writeLocation"],
                        "independentDecision": item})
    bundle = {"schemaVersion": 1, "snapshotSha256": decisions["snapshotSha256"], "reviewer": reviewer,
              "decisionsSha256": core.sha(Path(args.decisions).read_bytes()), "patches": patches,
              "sourceFiles": snapshot["manifest"]["files"],
              "independentCoverage": {"decisions": dict(Counter(d["decision"] for d in decisions.get("decisions", []))),
                                      "notReviewed": snapshot["manifest"]["fieldCount"] - len(seen)},
              "applicationStatus": "Reviewable changes only; no corpus files modified"}
    output = core.safe_output(ROOT, args.out)
    if output.exists():
        if core.read(output) != bundle:
            raise ValueError("Refusing to overwrite a different reviewed change bundle")
    else:
        core.atomic_json(output, bundle)
    return {"exportedPatches": len(patches), "corpusFilesModified": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "status", "detect", "reparse", "reference", "repair", "crosscheck", "decision-template", "export"])
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--probes", type=Path)
    parser.add_argument("--ids")
    parser.add_argument("--selection", type=Path)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--retry", action="store_true", help="Create a new attempt; reuse successful per-field work and retain all failures")
    parser.add_argument("--lane")
    parser.add_argument("--from-lane")
    parser.add_argument("--detect-lane", default="detect")
    parser.add_argument("--reference-lane", default="reference")
    parser.add_argument("--repair-lane", default="repair")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--model")
    parser.add_argument("--preset", choices=list(models.SAMPLING_PRESETS), default="baseline")
    parser.add_argument("--thinking", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--top-k", type=int)
    parser.add_argument("--top-p", type=float)
    parser.add_argument("--num-ctx", type=int)
    parser.add_argument("--num-predict", type=int)
    parser.add_argument("--decisions", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    args.run = core.safe_output(ROOT, args.run)
    if args.command == "prepare":
        snapshot = prepare_probes(args.run, args.probes) if args.probes else core.prepare_run(ROOT, args.run)
        manifest = snapshot["manifest"]
        print(json.dumps({**{k: v for k, v in manifest.items() if k not in {"files", "canonicalDifferences"}},
                          "frozenFiles": len(manifest["files"]), "canonicalDifferences": len(manifest["canonicalDifferences"])}, ensure_ascii=False))
        return
    snapshot = core.load_snapshot(args.run)
    if args.command == "status":
        print(json.dumps(status_report(args.run, snapshot, args.lane or "detect"), ensure_ascii=False))
    elif args.command == "reparse":
        print(json.dumps(reparse_detection(args, snapshot), ensure_ascii=False))
    elif args.command == "export":
        if not args.decisions or not args.out:
            parser.error("export requires --decisions and --out")
        print(json.dumps(export_bundle(args, snapshot), ensure_ascii=False))
    elif args.command == "decision-template":
        if not args.out:
            parser.error("decision-template requires --out")
        records = core.latest_records(args.run, args.repair_lane)
        items = []
        for entry in select_entries(snapshot, args):
            proposals = {p["path"]: p for p in records.get(entry["id"], {}).get("result", {}).get("proposals", []) if "proposal" in p}
            for field in entry["fields"]:
                proposed = proposals.get(field["path"])
                target = proposed["proposal"]["text"] if proposed else field["currentJapanese"]
                items.append({"entryId": entry["id"], "path": field["path"], "mode": field["mode"],
                              "sourceLanguage": field["sourceLanguage"], "sourceText": field["sourceText"],
                              "before": field["currentJapanese"], "proposedText": target,
                              "sourceSha256": core.sha(field["sourceText"]), "targetSha256": core.sha(target),
                              "proposalSha256": proposed["proposalSha256"] if proposed else None,
                              "decision": "uncertain", "sourceQuote": "", "targetQuote": "", "explanation": ""})
        output = core.safe_output(ROOT, args.out)
        if output.exists():
            raise ValueError("Refusing to overwrite independent review work")
        core.atomic_json(output, {"schemaVersion": 1, "snapshotSha256": core.sha((args.run / "snapshot.json").read_bytes()),
                                 "reviewer": {"name": "", "method": "", "independent": False}, "decisions": items})
        print(json.dumps({"decisionItems": len(items), "independentReviewComplete": False}))
    else:
        with (args.run / ".inference.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            model_stage(args, snapshot)


if __name__ == "__main__":
    main()
