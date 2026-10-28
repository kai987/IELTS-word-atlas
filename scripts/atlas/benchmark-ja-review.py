#!/usr/bin/env python3
"""Replay frozen local drafts through the current Japanese review worker.

No draft is regenerated and no corpus file is published. Offline mode compares
the new language gates on historical draft/review fields; it does not measure
semantic correctness. Live mode records each actual Ollama request and response
in a separate resumable experiment directory, without private thinking text.
"""
from __future__ import annotations

import argparse
import datetime
import fcntl
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import time
import types
import urllib.parse
import urllib.request
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
WORKER = ROOT / "scripts/atlas/translate-ja-local.py"
DEFAULT_IDS = "relax,behalf,probable,make,winter,novice,horrible,aesthetic,zero,refinement,o-clock,sister,stripes"
OPTIONS = {"seed": 42, "temperature": 0.1, "top_k": 40, "top_p": 0.95,
           "repeat_penalty": 1, "presence_penalty": 0, "num_ctx": 4096, "num_predict": 2048}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def read(path):
    return json.loads(path.read_text())


def local_json(base, suffix):
    with urllib.request.urlopen(base.rstrip("/") + suffix, timeout=20) as response:
        return json.load(response)


def load_worker(path):
    spec = importlib.util.spec_from_file_location("ja_review_replay_worker", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.PIPELINE_VERSION != 5:
        raise ValueError("This review experiment requires worker v5")
    return module


def gate_fields(worker, entry, fields):
    paths = [row["path"] for row in worker.translation_rows(entry)]
    if not isinstance(fields, dict):
        return {"__draft__": ["missing or unaligned fields"]}
    errors = {}
    for key in paths:
        found = worker.field_errors(entry, key, fields.get(key))
        if found:
            errors[key] = found
    unknown = sorted(set(fields) - set(paths))
    if unknown:
        errors["__unknown__"] = unknown
    return errors


def overlay_fields(worker, entry, candidate):
    fields = {}
    for row in worker.translation_rows(entry):
        key = row["path"]
        if "." in key:
            group, index = key.split(".")
            value = candidate[group][int(index)]
            if group == "col" and "｜" in entry["col"][int(index)]:
                value = value.split("｜", 1)[1]
            fields[key] = value
        else:
            fields[key] = candidate[key]
    return fields


def captured_client(worker, args, entry_id):
    class CapturedOllama(worker.Ollama):
        def __init__(self):
            super().__init__(types.SimpleNamespace(
                base_url=args.base_url, draft_model="__unused_frozen_draft__",
                review_model=args.model, num_ctx=OPTIONS["num_ctx"],
                cache=args.artifacts / "diagnostics" / f"{entry_id}.json"))
            self.calls = []

        def chat(self, model, messages, *, schema=None, predict=1536, thinking=False):
            if model != args.model or predict != OPTIONS["num_predict"] or thinking:
                raise ValueError("Unexpected replay model or generation controls")
            call_path = args.artifacts / "calls" / entry_id / f"{len(self.calls) + 1:03d}.json"
            if call_path.exists():
                raise ValueError("Refusing to overwrite an earlier generation request")
            call = {"entryId": entry_id, "startedAt": now(), "status": "running"}
            self.calls.append(call)
            save(call_path, call)
            original_open = urllib.request.urlopen

            def capture(request, *positional, **keyword):
                # Capture bytes actually sent by the frozen worker, rather than
                # reconstructing a similar payload in this experiment harness.
                if isinstance(request, urllib.request.Request) and request.data:
                    payload = json.loads(request.data)
                    if (payload.get("model") != args.model or payload.get("options") != OPTIONS
                            or payload.get("think") is not False):
                        raise ValueError("Actual worker request differs from frozen replay options")
                    call["request"] = payload
                    call["requestSha256"] = sha(request.data)
                    call["url"] = request.full_url
                    save(call_path, call)
                return original_open(request, *positional, **keyword)

            started = time.monotonic_ns()
            try:
                with patch.object(urllib.request, "urlopen", capture):
                    response, metrics = super().chat(model, messages, schema=schema, predict=predict, thinking=thinking)
                call.update({"status": "complete", "responseText": response, "metrics": metrics})
                return response, metrics
            except Exception as error:
                call.update({"status": "error", "error": str(error)})
                diagnostic = self.args.cache.with_name(self.args.cache.stem + ".rejected.json")
                if diagnostic.exists():
                    rejected = read(diagnostic)
                    call["responseText"] = rejected.get("output", "")
                    call["incompleteOutput"] = True
                    call["thinkingChars"] = rejected.get("thinkingChars", 0)
                raise
            finally:
                call.update({"finishedAt": now(), "wallLatencyNs": time.monotonic_ns() - started})
                save(call_path, call)

    return CapturedOllama()


def offline_record(worker, entry, draft, old_review):
    draft_errors = gate_fields(worker, entry, draft.get("fields"))
    candidate = old_review.get("candidateFields")
    old_errors = gate_fields(worker, entry, candidate)
    draft_paths = set(draft_errors) - {"__draft__", "__unknown__"}
    old_paths = set(old_errors) - {"__draft__", "__unknown__"}
    return {"id": entry["id"], "mode": "offline", "status": "complete",
            "draftGateErrors": draft_errors, "historicalReviewGateErrors": old_errors,
            "newlyFailingHistoricalReviewFields": sorted(old_paths - draft_paths),
            "draftAlignmentHeld": not isinstance(draft.get("fields"), dict),
            "historicalModelApproval": old_review.get("approval"),
            "calls": 0, "independentSemanticStatus": "not evaluated"}


def summarize(args, entries):
    records = [read(args.artifacts / "records" / f"{entry['id']}.json") for entry in entries
               if (args.artifacts / "records" / f"{entry['id']}.json").exists()]
    summary = {"mode": "offline" if args.offline else "live", "selectedEntries": len(entries),
               "recordedEntries": len(records), "statusCounts": {},
               "independentSemanticStatus": "not evaluated", "inferencePerformed": False}
    for record in records:
        status = record["status"]
        summary["statusCounts"][status] = summary["statusCounts"].get(status, 0) + 1
    if args.offline:
        summary.update({
            "draftAlignmentHeld": sum(r.get("draftAlignmentHeld", False) for r in records),
            "draftFieldsFailingLanguageGate": sum(len(set(r.get("draftGateErrors", {})) - {"__draft__", "__unknown__"}) for r in records),
            "historicalReviewFieldsFailingLanguageGate": sum(len(set(r.get("historicalReviewGateErrors", {})) - {"__draft__", "__unknown__"}) for r in records),
            "newlyFailingHistoricalReviewFields": sum(len(r.get("newlyFailingHistoricalReviewFields", [])) for r in records),
            "calls": 0})
    else:
        verification = [r.get("verification", {}) for r in records]
        calls = [read(p) for p in (args.artifacts / "calls").glob("*/*.json")]
        summary.update({"approvedEntries": sum(v.get("approved") is True for v in verification),
                        "modelApprovedEntries": sum(v.get("modelApproved") is True for v in verification),
                        "acceptedPatches": sum(len(v.get("acceptedPatches", [])) for v in verification),
                        "rejectedPatches": sum(len(v.get("rejectedPatches", [])) for v in verification),
                        "entriesHeldForReview": sum(r.get("status") != "complete" or r.get("verification", {}).get("approved") is not True for r in records),
                        "finalFieldsFailingLanguageGate": sum(len(set(r.get("finalGateErrors", {})) - {"__draft__", "__unknown__"}) for r in records),
                        "calls": len(calls), "actualRequests": sum("request" in c for c in calls),
                        "inferencePerformed": any("request" in c for c in calls),
                        "completedCalls": sum(c.get("status") == "complete" for c in calls),
                        "failedCalls": sum(c.get("status") == "error" for c in calls),
                        "generationWallLatencyNs": sum(c.get("wallLatencyNs", 0) for c in calls)})
    save(args.artifacts / "summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / ".local/ja-quant-benchmark")
    parser.add_argument("--variant", choices=["q4", "q8"], default="q8")
    parser.add_argument("--ids", default=DEFAULT_IDS, help="Comma-separated frozen entry IDs")
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--model", default="qwen3.5:9b-q8_0")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--offline", action="store_true")
    modes.add_argument("--live", action="store_true")
    args = parser.parse_args()
    args.source, args.artifacts = args.source.resolve(), args.artifacts.resolve()
    if args.artifacts == args.source or args.source in args.artifacts.parents:
        raise ValueError("Experiment output must be outside the historical source artifacts")
    if any(args.artifacts == protected or protected in args.artifacts.parents
           for protected in (ROOT / "public", ROOT / "data")):
        raise ValueError("Experiment output cannot be written into public or canonical corpus data")
    if urllib.parse.urlparse(args.base_url).hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Replay is restricted to a local Ollama server")
    ids = [value.strip() for value in args.ids.split(",") if value.strip()]
    if not ids or len(set(ids)) != len(ids) or any(not re.fullmatch(r"[a-z0-9][a-z0-9-]*", value) for value in ids):
        raise ValueError("Entry IDs must be unique safe nonempty source IDs")
    source_path = args.source / "source-snapshot.json"
    indexed = {entry["id"]: entry for entry in read(source_path)}
    entries = [indexed[value] for value in ids]
    drafts, old_reviews, source_hashes = {}, {}, {}
    for entry in entries:
        word = entry["id"]
        draft_path = args.source / args.variant / "drafts" / f"{word}.json"
        review_path = args.source / args.variant / "reviews" / f"{word}.json"
        drafts[word], old_reviews[word] = read(draft_path), read(review_path)
        source_hashes[word] = {"draftSha256": sha(draft_path.read_bytes()),
                               "oldReviewSha256": sha(review_path.read_bytes()),
                               "entrySha256": sha(json.dumps(entry, ensure_ascii=False, sort_keys=True).encode())}
    worker = load_worker(WORKER)
    model_digest = None
    if args.live:
        tags = {row["name"]: row for row in local_json(args.base_url, "/api/tags").get("models", [])}
        if args.model not in tags:
            raise ValueError("Selected review model is not installed; replay never downloads a model")
        model_digest = tags[args.model]["digest"]
        resident = [row.get("name", row.get("model")) for row in local_json(args.base_url, "/api/ps").get("models", [])]
        if any(name != args.model for name in resident):
            raise ValueError("Another model is resident; replay will not unload or interrupt it")
    protocol = {"schemaVersion": 1, "workerVersion": 5, "workerSha256": sha(WORKER.read_bytes()),
                "harnessSha256": sha(Path(__file__).read_bytes()), "mode": "offline" if args.offline else "live",
                "sourceSnapshotSha256": sha(source_path.read_bytes()), "sourceVariant": args.variant,
                "entryIds": ids, "sourceHashes": source_hashes, "model": args.model if args.live else None,
                "modelDigest": model_digest, "options": OPTIONS, "thinking": False,
                "inferenceEnabled": args.live, "draftsRegenerated": False,
                "independentSemanticStatus": "not evaluated"}
    args.artifacts.mkdir(parents=True, exist_ok=True)
    with (args.artifacts / ".run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        protocol_path = args.artifacts / "protocol.json"
        if protocol_path.exists():
            if read(protocol_path) != protocol:
                raise ValueError("Replay protocol/input/model/code changed; use a fresh artifact directory")
        else:
            if any(p.name != ".run.lock" for p in args.artifacts.iterdir()):
                raise ValueError("Refusing to reuse a nonempty experiment directory without its protocol")
            save(protocol_path, protocol)
            (args.artifacts / "worker-v5.py").write_bytes(WORKER.read_bytes())
            (args.artifacts / "harness-frozen.py").write_bytes(Path(__file__).read_bytes())
            save(args.artifacts / "source-snapshot.json", entries)
            save(args.artifacts / "draft-snapshot.json", drafts)
        frozen_worker = args.artifacts / "worker-v5.py"
        if sha(frozen_worker.read_bytes()) != protocol["workerSha256"]:
            raise ValueError("Frozen replay worker was changed")
        worker = load_worker(frozen_worker)
        for entry in entries:
            word = entry["id"]
            record_path = args.artifacts / "records" / f"{word}.json"
            if record_path.exists():
                previous = read(record_path)
                if previous.get("status") == "running":
                    previous.update({"status": "interrupted", "finishedAt": now(),
                                     "error": "Previous generation was interrupted; no automatic retry"})
                    save(record_path, previous)
                continue
            draft = drafts[word]
            if args.offline:
                record = offline_record(worker, entry, draft, old_reviews[word])
            else:
                record = {"id": word, "status": "running", "startedAt": now(),
                          "sourceHashes": source_hashes[word], "independentSemanticStatus": "not evaluated"}
                save(record_path, record)
                client = captured_client(worker, args, word)
                try:
                    worker.require_draft(entry, draft.get("fields"))
                except ValueError as error:
                    record.update({"status": "held-draft", "error": str(error), "calls": 0})
                else:
                    try:
                        candidate, verification, metrics = worker.verify_entry(client, entry, draft["fields"], draft.get("raw"))
                        final_fields = overlay_fields(worker, entry, candidate)
                        record.update({"status": "complete", "candidate": candidate,
                                       "candidateFields": final_fields, "verification": verification,
                                       "metrics": metrics, "finalGateErrors": gate_fields(worker, entry, final_fields)})
                    except Exception as error:
                        record.update({"status": "error", "error": str(error)})
                    record["calls"] = len(client.calls)
                record["finishedAt"] = now()
            save(record_path, record)
            print(json.dumps({"event": "entry", "id": word, "status": record["status"],
                              "calls": record.get("calls", 0)}, ensure_ascii=False), flush=True)
        print(json.dumps(summarize(args, entries), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
