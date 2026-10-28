#!/usr/bin/env python3
"""Controlled Q4/Q8 Japanese-translation benchmark; never publishes corpus data.

Freeze a 100-entry sample and the archived worker v4. This historical quantization
protocol deliberately keeps v4 prompts; the current local translation worker uses
v5. Each precision runs all draft entries with one resident TranslateGemma model,
unloads it, then runs all Qwen reviews. Raw outputs, rejected candidates and
metrics are retained without manual repair.
"""
from __future__ import annotations
import argparse
import datetime
import fcntl
import hashlib
import importlib.util
import json
import pathlib
import platform
import random
import time
import types
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKER = ROOT / "scripts/atlas/translate-ja-local-v4.py"
MODELS = {
    "q4": {"draft": "translategemma:12b", "review": "qwen3.5:9b"},
    "q8": {"draft": "translategemma:12b-it-q8_0", "review": "qwen3.5:9b-q8_0"},
}
OPTIONS = {"seed": 42, "temperature": 0.1, "top_k": 40, "top_p": 0.95,
           "repeat_penalty": 1, "presence_penalty": 0, "num_ctx": 4096, "num_predict": 2048}
EXPECTED_SAMPLE_SHA256 = "309400696e9f66c226faf65b2fa0eb8829b8b2c23ed69246b164c5f6ce8221cd"


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(value):
    raw = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def request_json(base, endpoint, payload=None, timeout=30):
    request = urllib.request.Request(base.rstrip("/") + endpoint,
                                     data=json.dumps(payload).encode() if payload is not None else None,
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def load_sample(path):
    manifest = json.loads(path.read_text())
    rows = manifest if isinstance(manifest, list) else manifest.get("entries", manifest.get("ids", []))
    ids = [row if isinstance(row, str) else row["id"] for row in rows]
    if len(ids) != 100 or len(set(ids)) != 100:
        raise ValueError("The frozen sample must contain exactly 100 unique entry IDs")
    indexed = {}
    for file in (ROOT / "public/atlas/entries").glob("*.json"):
        indexed.update((entry["id"], entry) for entry in json.loads(file.read_text()))
    if any(word not in indexed for word in ids):
        raise ValueError("Sample contains an unknown source entry")
    for row in rows:
        if isinstance(row, dict) and row.get("sourceSha256"):
            entry = indexed[row["id"]]
            legacy = hashlib.sha256(json.dumps(entry, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            if row["sourceSha256"] not in {digest(entry), legacy}:
                raise ValueError(f"Source differs from frozen sample: {row['id']}")
    if isinstance(manifest, dict) and manifest.get("models") != MODELS:
        raise ValueError("Frozen manifest model tags differ from the controlled comparison")
    return manifest, [indexed[word] for word in ids]


def model_metadata(base):
    tags = request_json(base, "/api/tags")
    available = {model["name"]: model for model in tags.get("models", [])}
    metadata = {}
    missing = []
    for variant, phases in MODELS.items():
        for phase, name in phases.items():
            if name not in available:
                missing.append(name)
                continue
            shown = request_json(base, "/api/show", {"model": name})
            details = shown.get("details", {})
            quantization = details.get("quantization_level", "")
            if not quantization.startswith("Q4" if variant == "q4" else "Q8"):
                raise ValueError(f"Unexpected quantization for {name}: {quantization}")
            info = shown.get("model_info", {})
            dimensions = {key: value for key, value in info.items()
                          if any(part in key for part in ["block_count", "layer_count", "embedding_length", "feed_forward_length", "head_count", "vocab_size", "context_length"])}
            tokenizer = {key: value for key, value in info.items() if key.startswith("tokenizer.") and "chat_template" not in key}
            metadata[name] = {
                "digest": available[name]["digest"], "size": available[name].get("size"),
                "quantization": quantization, "parameterSize": details.get("parameter_size"),
                "family": details.get("family"), "families": details.get("families"),
                "templateSha256": digest(shown.get("template", "")),
                "systemSha256": digest(shown.get("system", "")),
                "defaultParameters": shown.get("parameters", ""),
                "capabilities": shown.get("capabilities", []),
                "modelInfoSha256": digest(info), "architecture": info.get("general.architecture"),
                "layerAndTokenizerDimensions": dimensions,
                "tokenizerMetadataSha256": digest(tokenizer),
                "tokenizerChatTemplateSha256": digest(info.get("tokenizer.chat_template", "")),
            }
    return metadata, missing


def comparison_issues(models):
    issues = []
    for phase in ["draft", "review"]:
        left, right = MODELS["q4"][phase], MODELS["q8"][phase]
        if left not in models or right not in models:
            continue
        for key in ["family", "families", "parameterSize", "architecture", "templateSha256", "systemSha256",
                    "tokenizerChatTemplateSha256", "tokenizerMetadataSha256", "layerAndTokenizerDimensions"]:
            if models[left].get(key) != models[right].get(key):
                issues.append({"phase": phase, "field": key, "q4": models[left].get(key), "q8": models[right].get(key)})
    return issues


def resident(base):
    return [row.get("name", row.get("model")) for row in request_json(base, "/api/ps").get("models", [])]


def unload_all_known(base):
    known = {name for phases in MODELS.values() for name in phases.values()}
    loaded = resident(base)
    unknown = [name for name in loaded if name not in known]
    if unknown:
        raise ValueError("Unrelated models are resident; refusing to unload them: " + ", ".join(unknown))
    for name in loaded:
        request_json(base, "/api/generate", {"model": name, "keep_alive": 0}, timeout=120)
    # Ollama may acknowledge keep_alive=0 before /api/ps reflects the unload.
    deadline = time.monotonic() + 120
    remaining = resident(base)
    while remaining:
        if time.monotonic() >= deadline:
            raise ValueError("Models did not unload at the phase boundary: " + ", ".join(remaining))
        time.sleep(0.25)
        remaining = resident(base)


def freeze(args, manifest, entries, models):
    harness_snapshot = args.artifacts / "harness-frozen.py"
    if not harness_snapshot.exists():
        harness_snapshot.write_bytes(pathlib.Path(__file__).read_bytes())
    snapshot = args.artifacts / "worker-v4.py"
    if not snapshot.exists():
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(WORKER.read_bytes())
    spec = importlib.util.spec_from_file_location("frozen_ja_worker", snapshot)
    worker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(worker)
    if worker.PIPELINE_VERSION != 4:
        raise ValueError("This comparison requires the frozen v4 translation prompts")
    protocol = {
        "schemaVersion": 1, "workerVersion": 4, "workerSha256": digest(snapshot.read_bytes()),
        "harnessSha256": digest(pathlib.Path(__file__).read_bytes()),
        "sampleFileSha256": digest(args.sample.read_bytes()), "sample": manifest,
        "entryIds": [entry["id"] for entry in entries],
        "sourceSha256": {entry["id"]: digest(entry) for entry in entries},
        "options": OPTIONS, "models": models, "thinking": False,
        "sourcePolicy": "English authoritative for bilingual senses/examples/collocations; Chinese for Chinese-only fields",
        "manualRepairsBeforeComparison": False, "independentSemanticStatus": "unscored",
        "runtimeVersion": request_json(args.base_url, "/api/version").get("version"),
        "platform": {"machine": platform.machine(), "system": platform.system(), "release": platform.release()},
        "phaseProtocol": "all 100 drafts -> unload -> all 100 reviews -> unload; one resident model",
        "primaryEstimand": "end-to-end pipeline precision; each reviewer consumes its precision's own drafts",
    }
    source_snapshot = args.artifacts / "source-snapshot.json"
    sample_snapshot = args.artifacts / "sample.json"
    if source_snapshot.exists() and json.loads(source_snapshot.read_text()) != entries:
        raise ValueError("Frozen source snapshot changed")
    if sample_snapshot.exists() and sample_snapshot.read_bytes() != args.sample.read_bytes():
        raise ValueError("Frozen sample snapshot changed")
    save(source_snapshot, entries)
    sample_snapshot.write_bytes(args.sample.read_bytes())
    destination = args.artifacts / "protocol.json"
    if destination.exists():
        old = json.loads(destination.read_text())
        if old != protocol:
            raise ValueError("Frozen sample/source/model/protocol changed; use a new artifact root")
    else:
        save(destination, protocol)
    return worker, protocol


def make_client(worker, args, variant, phase):
    class AuditedOllama(worker.Ollama):
        def __init__(self):
            super().__init__(types.SimpleNamespace(
                base_url=args.base_url, draft_model=MODELS[variant]["draft"], review_model=MODELS[variant]["review"],
                num_ctx=4096, cache=args.artifacts / variant / phase / "worker-diagnostic.json"))
            self.entry_id = ""
            self.calls = []
            self.attempt = 1

        def begin(self, entry_id, attempt):
            self.entry_id, self.calls, self.attempt = entry_id, [], attempt

        def chat(self, model, messages, *, schema=None, predict=1536, thinking=False):
            if predict != 2048 or thinking:
                raise ValueError("Worker attempted to change frozen generation controls")
            unexpected = [name for name in resident(args.base_url) if name != model]
            if unexpected:
                raise ValueError("More than the phase model is resident: " + ", ".join(unexpected))
            call_number = len(self.calls) + 1
            path = args.artifacts / variant / "calls" / phase / self.entry_id / f"attempt-{self.attempt}" / f"{call_number}.json"
            payload = {"model": model, "messages": messages, "stream": True, "keep_alive": "30m", "options": dict(OPTIONS)}
            if phase == "review":
                payload["think"] = False
            if schema is not None:
                payload["format"] = schema
            record = {"status": "running", "startedAt": now(), "model": model,
                      "promptSha256": digest(messages), "schemaSha256": digest(schema),
                      "optionsSha256": digest(OPTIONS), "request": payload}
            self.calls.append(record)
            save(path, record)
            chunks = []
            final = None
            thinking_chars = 0
            started = time.monotonic_ns()
            checkpoint = time.monotonic()
            try:
                request = urllib.request.Request(args.base_url.rstrip("/") + "/api/chat", data=json.dumps(payload).encode(),
                                                 headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(request, timeout=600) as response:
                    for line in response:
                        if not line.strip():
                            continue
                        item = json.loads(line)
                        if item.get("error"):
                            raise RuntimeError(item["error"])
                        # Never persist private reasoning text, including on failure.
                        thinking_chars += len(item.get("message", {}).get("thinking", ""))
                        chunks.append(item.get("message", {}).get("content", ""))
                        if time.monotonic() - checkpoint >= 1:
                            record.update({"status": "streaming", "output": "".join(chunks), "thinkingChars": thinking_chars})
                            save(path, record)
                            checkpoint = time.monotonic()
                        if item.get("done"):
                            final = item
                text = "".join(chunks).strip()
                metrics = {key: (final or {}).get(key, 0) for key in
                           ["total_duration", "load_duration", "prompt_eval_count", "prompt_eval_duration", "eval_count", "eval_duration"]}
                metrics["tokens_per_second"] = round(metrics["eval_count"] / max(metrics["eval_duration"] / 1e9, .001), 2)
                metrics["wallLatencyNs"] = time.monotonic_ns() - started
                record.update({"status": "complete", "finishedAt": now(), "output": text,
                               "doneReason": (final or {}).get("done_reason"), "thinkingChars": thinking_chars, "metrics": metrics})
                save(path, record)
                if not final or final.get("done_reason") == "length":
                    raise ValueError("Generation missing completion or reached the fixed token limit")
                if thinking_chars:
                    raise ValueError("Thinking output occurred despite the frozen no-thinking condition")
                return text, metrics
            except BaseException as error:
                record.update({"status": "error", "finishedAt": now(), "error": str(error),
                               "output": "".join(chunks).strip(), "thinkingChars": thinking_chars,
                               "wallLatencyNs": time.monotonic_ns() - started})
                save(path, record)
                raise
    return AuditedOllama()


def reconstruct_review(worker, entry, fields, calls):
    """Record the actual candidate even if the production validator rejects it."""
    output = calls[-1].get("output", "") if calls else ""
    result = {"rawOutput": output, "approval": None, "candidate": None, "errors": []}
    try:
        review = json.loads(output)
        result["review"] = review
        result["approval"] = review.get("approved")
        candidate_fields = dict(fields or {})
        allowed = {row["path"] for row in worker.translation_rows(entry)}
        seen = set()
        for patch in review.get("patches", []):
            key, value = patch.get("path"), patch.get("text")
            if key not in allowed or not isinstance(value, str) or not value.strip():
                result["errors"].append("invalid patch")
                continue
            if key in seen:
                result["errors"].append("duplicate patch path")
            seen.add(key)
            candidate_fields[key] = value
        result["candidateFields"] = candidate_fields
        if set(candidate_fields) != allowed:
            result["errors"].append("missing or unknown candidate fields")
        else:
            candidate = worker.overlay(entry, candidate_fields)
            result["candidate"] = candidate
            result["errors"] += worker.validate(entry, candidate)
    except (ValueError, TypeError, KeyError) as error:
        result["errors"].append("candidate parsing: " + str(error))
    result["passesStructuralChecks"] = not result["errors"]
    result["independentSemanticStatus"] = "unscored"
    return result


def run_phase(worker, protocol, args, entries, variant, phase):
    model = MODELS[variant][phase]
    if phase == "review":
        draft_variant = variant if args.review_drafts == "own" else args.review_drafts
        missing_drafts = [entry["id"] for entry in entries
                          if not (args.artifacts / draft_variant / "drafts" / f"{entry['id']}.json").exists()]
        if missing_drafts:
            raise ValueError("Review phase requires all 100 draft records, including recorded failures")
    unload_all_known(args.base_url)
    started = time.monotonic_ns()
    phase_record = {"variant": variant, "phase": phase, "model": model, "modelDigest": protocol["models"][model]["digest"],
                    "startedAt": now(), "reviewInputVariant": args.review_drafts if phase == "review" else None,
                    "initialResidentModels": resident(args.base_url), "status": "running"}
    phase_path = args.artifacts / variant / f"{phase}-phase.json"
    save(phase_path, phase_record)
    client = make_client(worker, args, variant, phase)
    try:
        for i, entry in enumerate(entries, 1):
            path = args.artifacts / variant / ("drafts" if phase == "draft" else "reviews") / f"{entry['id']}.json"
            if path.exists():
                existing = json.loads(path.read_text())
                if existing.get("status") in {"complete", "error", "skipped"}:
                    continue
            attempt = 1
            if path.exists():
                previous = json.loads(path.read_text())
                attempt = previous.get("attempt", 1) + 1
                save(args.artifacts / variant / "history" / phase / entry["id"] / f"attempt-{attempt-1}.json", previous)
            client.begin(entry["id"], attempt)
            record = {"id": entry["id"], "sourceSha256": protocol["sourceSha256"][entry["id"]],
                      "model": model, "modelDigest": protocol["models"][model]["digest"], "startedAt": now(), "status": "running", "attempt": attempt,
                      "independentSemanticStatus": "unscored"}
            save(path, record)
            error_text = None
            try:
                if phase == "draft":
                    fields, raw, metrics = worker.draft_entry(client, entry)
                    draft_overlay = None
                    errors = []
                    if fields is None:
                        errors.append("numbered field alignment failed")
                    else:
                        try:
                            draft_overlay = worker.overlay(entry, fields)
                            errors = worker.validate(entry, draft_overlay)
                        except (ValueError, KeyError, TypeError) as error:
                            errors.append(str(error))
                    record.update({"fields": fields, "raw": raw, "draft": draft_overlay,
                                   "structuralErrors": errors, "metrics": metrics, "status": "complete"})
                else:
                    draft_variant = variant if args.review_drafts == "own" else args.review_drafts
                    draft_path = args.artifacts / draft_variant / "drafts" / f"{entry['id']}.json"
                    if not draft_path.exists():
                        raise ValueError("The complete draft phase must precede the review phase")
                    draft = json.loads(draft_path.read_text())
                    record["draftVariant"] = draft_variant
                    record["draftArtifactSha256"] = digest(draft_path.read_bytes())
                    if draft.get("status") != "complete":
                        record.update({"status": "skipped", "error": "draft generation failed"})
                    else:
                        try:
                            candidate, review, metrics = worker.verify_entry(client, entry, draft.get("fields"), draft.get("raw"))
                            record.update(reconstruct_review(worker, entry, draft.get("fields"), client.calls))
                            record.update({"metrics": metrics, "status": "complete"})
                        except Exception as error:
                            record.update(reconstruct_review(worker, entry, draft.get("fields"), client.calls))
                            raise
            except Exception as error:
                error_text = str(error)
                record.update({"status": "error", "error": error_text})
            record.update({"finishedAt": now(), "calls": [
                {key: call.get(key) for key in ["status", "promptSha256", "schemaSha256", "optionsSha256", "metrics", "error"]}
                for call in client.calls]})
            save(path, record)
            print(json.dumps({"event": "entry", "variant": variant, "phase": phase, "index": i,
                              "id": entry["id"], "status": record["status"], "modelApproval": record.get("approval"), "error": error_text}), flush=True)
        phase_record.update({"finishedAt": now(), "wallLatencyNs": time.monotonic_ns() - started,
                             "status": "complete"})
    finally:
        if phase_record.get("status") != "complete":
            phase_record.update({"status": "interrupted", "finishedAt": now(), "wallLatencyNs": time.monotonic_ns() - started})
        unload_all_known(args.base_url)
        phase_record["finalResidentModels"] = resident(args.base_url)
        folder = "drafts" if phase == "draft" else "reviews"
        records = [json.loads(file.read_text()) for file in (args.artifacts / variant / folder).glob("*.json")]
        phase_record["counts"] = {"total": len(records), "complete": sum(r.get("status") == "complete" for r in records),
                                 "generationOrValidationErrors": sum(r.get("status") == "error" for r in records),
                                 "skipped": sum(r.get("status") == "skipped" for r in records),
                                 "modelApproved": sum(r.get("approval") is True for r in records),
                                 "modelRejected": sum(r.get("approval") is False for r in records),
                                 "structuralBlocked": sum(bool(r.get("errors") or r.get("structuralErrors")) for r in records),
                                 "pipelineBlocked": sum(r.get("status") != "complete" or r.get("approval") is not True or bool(r.get("errors")) for r in records) if phase == "review" else None,
                                 "semanticallyScored": 0}
        save(phase_path, phase_record)
    print(json.dumps({"event": "phase-complete", "variant": variant, "phase": phase}), flush=True)


def export_blind(worker, args, entries):
    rng = random.Random(914827)
    tasks, key = [], {}
    for stage in ["draft", "final"]:
        for entry in entries:
            candidates = []
            for variant in ["q4", "q8"]:
                folder = "drafts" if stage == "draft" else "reviews"
                file = args.artifacts / variant / folder / f"{entry['id']}.json"
                record = json.loads(file.read_text()) if file.exists() else {}
                candidate = record.get("draft" if stage == "draft" else "candidate")
                candidates.append((variant, candidate))
            rng.shuffle(candidates)
            for variant, candidate in candidates:
                case = f"case-{len(tasks)+1:04d}"
                tasks.append({"case": case, "stage": stage, "word": entry["w"],
                              "sourceFields": worker.translation_rows(entry), "candidate": candidate})
                key[case] = {"variant": variant, "id": entry["id"], "stage": stage}
    save(args.artifacts / "blind/tasks.json", tasks)
    save(args.artifacts / "blinding-key.json", key)
    print(json.dumps({"event": "blind-export", "tasks": len(tasks)}))


def dry_run(args, manifest, entries):
    """Exercise prompt/schema construction offline; no generation or candidates."""
    spec = importlib.util.spec_from_file_location("dry_run_worker", WORKER)
    worker = importlib.util.module_from_spec(spec); spec.loader.exec_module(worker)
    if worker.PIPELINE_VERSION != 4:
        raise ValueError("Dry run requires worker v4")
    class Captured(Exception):
        pass
    class Recorder:
        def __init__(self):
            self.args = types.SimpleNamespace(draft_model="DRAFT", review_model="REVIEW")
            self.calls = []
        def chat(self, model, messages, *, schema=None, predict=1536, thinking=False):
            if predict != 2048 or thinking:
                raise ValueError("Non-frozen worker generation control")
            self.calls.append({"role": model, "messages": messages, "schema": schema})
            if model == "REVIEW":
                raise Captured()
            import re
            # Internal sentinel text only: it is never emitted as translation data.
            ids = re.findall(r"【(\d+)】", messages[0]["content"])
            raw = "\n".join(f"【{i}】__OFFLINE_PROMPT_CHECK__" for i in ids)
            return raw, {key: 0 for key in ["total_duration", "load_duration", "prompt_eval_count", "prompt_eval_duration", "eval_count", "eval_duration"]}
    records = []
    total_calls = 0
    for entry in entries:
        client = Recorder()
        fields, raw, _ = worker.draft_entry(client, entry)
        try:
            worker.verify_entry(client, entry, fields, raw)
        except Captured:
            pass
        draft_calls = [call for call in client.calls if call["role"] == "DRAFT"]
        reviews = [call for call in client.calls if call["role"] == "REVIEW"]
        if len(reviews) != 1:
            raise ValueError("Review schema was not constructed exactly once")
        total_calls += len(draft_calls)
        records.append({"id": entry["id"], "sourceSha256": digest(entry),
                        "fieldCount": len(worker.translation_rows(entry)),
                        "draftPromptSha256": [digest(call["messages"]) for call in draft_calls],
                        "reviewSystemPromptSha256": digest(reviews[0]["messages"][0]),
                        "reviewSchemaSha256": digest(reviews[0]["schema"])})
    report = {"inferencePerformed": False, "sampleSha256": digest(args.sample.read_bytes()),
              "workerSha256": digest(WORKER.read_bytes()), "harnessSha256": digest(pathlib.Path(__file__).read_bytes()),
              "entries": len(entries), "fields": sum(row["fieldCount"] for row in records),
              "draftRequestsPerPrecision": total_calls, "reviewRequestsPerPrecision": len(entries),
              "sourceManifestValidated": True, "options": OPTIONS, "cases": records}
    save(args.artifacts / "dry-run.json", report)
    print(json.dumps({key: value for key, value in report.items() if key != "cases"}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--sample", type=pathlib.Path, default=ROOT / "scripts/atlas/ja-benchmark-100.json")
    parser.add_argument("--artifacts", type=pathlib.Path, default=ROOT / ".local/ja-quant-benchmark")
    parser.add_argument("--expected-sample-sha256", default=EXPECTED_SAMPLE_SHA256)
    parser.add_argument("--dry-run", action="store_true", help="Validate frozen sample and construct prompts/schemas offline, with no model calls")
    parser.add_argument("--variant", choices=["q4", "q8", "all"], default="all")
    parser.add_argument("--phase", choices=["draft", "review", "both"], default="both")
    parser.add_argument("--review-drafts", choices=["own", "q4", "q8"], default="own")
    parser.add_argument("--preflight", action="store_true", help="Read readiness only; never loads or generates with models")
    parser.add_argument("--export-blind", action="store_true", help="Export paired blinded drafts/finals after generation")
    args = parser.parse_args()
    if urllib.parse.urlparse(args.base_url).hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Benchmark restricted to the local Ollama instance")
    if digest(args.sample.read_bytes()) != args.expected_sample_sha256:
        raise ValueError("Sample file does not match its frozen SHA-256")
    manifest, entries = load_sample(args.sample)
    if args.dry_run:
        dry_run(args, manifest, entries)
        return
    if args.export_blind:
        snapshot = args.artifacts / "worker-v4.py"
        spec = importlib.util.spec_from_file_location("frozen_ja_worker", snapshot)
        worker = importlib.util.module_from_spec(spec); spec.loader.exec_module(worker)
        export_blind(worker, args, entries)
        return
    models, missing = model_metadata(args.base_url)
    if args.preflight:
        print(json.dumps({"sampleEntries": len(entries), "models": models, "missingModels": missing,
                          "residentModels": resident(args.base_url), "options": OPTIONS,
                          "comparabilityIssues": comparison_issues(models)}, ensure_ascii=False))
        return
    if missing:
        raise ValueError("Required comparison models are not ready: " + ", ".join(missing))
    issues = comparison_issues(models)
    if issues:
        save(args.artifacts / "preflight-comparability-issues.json", issues)
        raise ValueError("Native templates/tokenizer/architecture differ; review preflight before inference")
    args.artifacts.mkdir(parents=True, exist_ok=True)
    with (args.artifacts / ".run.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        worker, protocol = freeze(args, manifest, entries, models)
        variants = ["q4", "q8"] if args.variant == "all" else [args.variant]
        phases = ["draft", "review"] if args.phase == "both" else [args.phase]
        for variant in variants:
            for phase in phases:
                run_phase(worker, protocol, args, entries, variant, phase)


if __name__ == "__main__":
    main()
