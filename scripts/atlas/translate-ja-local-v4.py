#!/usr/bin/env python3
"""Translate vocabulary locally with TranslateGemma drafts and Qwen verification.

Uses only the explicitly selected Ollama instance. Progress and rejected entries
stay in a resumable cache outside public/. A canonical source chunk is written
only when all its entries have a structurally valid verified translation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
PIPELINE_VERSION = 4
ENGLISH = re.compile(r"/[^/\n\u3400-\u9fff]+/|[A-Za-z][A-Za-z0-9 /'’+()_.-]*")


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def translation_rows(entry):
    """English is authoritative for bilingual fields; Chinese only resolves sense."""
    rows = []
    for i, sense in enumerate(entry["senses"]):
        if sense.get("en", "").strip():
            text = f"{entry['w']} ({sense['pos']}): {sense['en']}"
            language = "en"
        else:
            text, language = sense["zh"], "zh-Hans"
        rows.append({"path": f"senses.{i}", "text": text, "language": language})
    for i, example in enumerate(entry["ex"]):
        text = example.get("en", "").strip() or example["zh"]
        rows.append({"path": f"ex.{i}", "text": text, "language": "en" if example.get("en", "").strip() else "zh-Hans"})
    for i, collocation in enumerate(entry["col"]):
        phrase = collocation.split("｜", 1)[0].strip()
        rows.append({"path": f"col.{i}", "text": phrase, "language": "en"})
    rows += [{"path": key, "text": entry[key], "language": "zh-Hans"}
             for key in ["tip", "note"] if entry.get(key, "")]
    return rows


def flatten(entry):
    return [(row["path"], row["text"]) for row in translation_rows(entry)]


def overlay(entry, fields):
    return {"id": entry["id"],
            "senses": [fields[f"senses.{i}"] for i in range(len(entry["senses"]))],
            "ex": [fields[f"ex.{i}"] for i in range(len(entry["ex"]))],
            "col": [f"{value.split('｜', 1)[0]}｜{fields[f'col.{i}']}" if "｜" in value else fields[f"col.{i}"]
                    for i, value in enumerate(entry["col"])],
            "tip": fields.get("tip", ""), "note": fields.get("note", "")}


def validate(entry, result):
    errors = []
    if result.get("id") != entry["id"]:
        errors.append("id changed")
    for key, source in [("senses", entry["senses"]), ("ex", entry["ex"]), ("col", entry["col"])]:
        values = result.get(key)
        if not isinstance(values, list) or len(values) != len(source):
            errors.append(f"{key} length changed")
        elif any(not isinstance(value, str) or not value.strip() for value in values):
            errors.append(f"empty {key}")
    if errors:
        return errors
    for source, target in zip(entry["col"], result["col"]):
        if "｜" in source and source.split("｜", 1)[0] != target.split("｜", 1)[0]:
            errors.append("English collocation changed")
    for key in ["tip", "note"]:
        value = result.get(key)
        if not isinstance(value, str) or (entry.get(key, "") and not value.strip()):
            errors.append(f"empty {key}")
            continue
        for term in ENGLISH.findall(entry.get(key, "")):
            if term.strip() not in value:
                errors.append(f"{key} English/IPA literal missing: {term.strip()}")
    for value in result["senses"] + result["ex"] + result["col"] + [result["tip"], result["note"]]:
        if re.search(r"<unk>|ZXQTERM|⁇|\[待翻译\]|\[翻訳待ち\]", value):
            errors.append("placeholder or unknown token")
    return errors


class Ollama:
    def __init__(self, args):
        parsed = urllib.parse.urlparse(args.base_url)
        if parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError("This worker is restricted to a local Ollama server")
        self.args = args

    def chat(self, model, messages, *, schema=None, predict=1536, thinking=False):
        payload = {"model": model, "messages": messages, "stream": True, "keep_alive": "30m",
                   "options": {"num_ctx": self.args.num_ctx, "num_predict": predict, "temperature": 0.1,
                               "presence_penalty": 0, "repeat_penalty": 1, "seed": 42}}
        if model == self.args.review_model:
            payload["think"] = thinking
        if schema:
            payload["format"] = schema
        request = urllib.request.Request(self.args.base_url.rstrip("/") + "/api/chat",
                                         data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
        parts = []
        final = None
        thinking_chars = 0
        with urllib.request.urlopen(request, timeout=600) as response:
            for line in response:
                if not line.strip():
                    continue
                message = json.loads(line)
                if message.get("error"):
                    raise RuntimeError(message["error"])
                thinking_chars += len(message.get("message", {}).get("thinking", ""))
                parts.append(message.get("message", {}).get("content", ""))
                if message.get("done"):
                    final = message
        if not final or final.get("done_reason") == "length":
            # Record only output JSON/text and counts; never save private thinking.
            atomic_json(self.args.cache.with_name(self.args.cache.stem + ".rejected.json"), {
                "model": model, "output": "".join(parts), "thinkingChars": thinking_chars,
                "doneReason": final.get("done_reason") if final else "missing completion",
                "evalCount": final.get("eval_count") if final else 0,
            })
            raise ValueError("Generation incomplete or token limit reached; diagnostic checkpoint saved")
        metrics = {key: final.get(key, 0) for key in ["total_duration", "load_duration", "prompt_eval_count", "prompt_eval_duration", "eval_count", "eval_duration"]}
        metrics["tokens_per_second"] = round(metrics["eval_count"] / max(metrics["eval_duration"] / 1e9, 0.001), 2)
        return "".join(parts).strip(), metrics


def draft_entry(client, entry):
    rows = translation_rows(entry)
    fields = {}
    raw_groups = []
    call_metrics = []
    parse_failed = False
    for language in ["en", "zh-Hans"]:
        selected = [(i, row) for i, row in enumerate(rows, 1) if row["language"] == language]
        if not selected:
            continue
        language_name = "English" if language == "en" else "Chinese"
        numbered = "\n".join(f"【{i}】{row['text']}" for i, row in selected)
        text = f"{entry['w']}\n{numbered}"
        prompt = (f"You are a professional {language_name} ({language}) to Japanese (ja) translator. "
                  f"Your goal is to accurately convey the meaning and nuances of the original {language_name} text while adhering to Japanese grammar, vocabulary, and cultural sensitivities.\n"
                  "Produce only the Japanese translation, without any additional explanations or commentary. "
                  f"Please translate the following {language_name} text into Japanese:\n\n\n" + text)
        raw, metrics = client.chat(client.args.draft_model, [{"role": "user", "content": prompt}], predict=2048)
        raw_groups.append({"sourceLanguage": language, "text": raw})
        call_metrics.append(metrics)
        markers = list(re.finditer(r"【\s*(\d+)\s*】", raw))
        if [int(match[1]) for match in markers] != [i for i, _ in selected]:
            parse_failed = True
            continue
        for i, marker in enumerate(markers):
            end = markers[i+1].start() if i+1 < len(markers) else len(raw)
            fields[selected[i][1]["path"]] = raw[marker.end():end].strip()
    totals = {key: sum(row[key] for row in call_metrics) for key in
              ["total_duration", "load_duration", "prompt_eval_count", "prompt_eval_duration", "eval_count", "eval_duration"]}
    totals["tokens_per_second"] = round(totals["eval_count"] / max(totals["eval_duration"] / 1e9, 0.001), 2)
    totals["calls"] = len(call_metrics)
    return None if parse_failed else fields, raw_groups, totals


def verify_entry(client, entry, fields, raw):
    rows = flatten(entry)
    paths = [path for path, _ in rows]
    item_schema = {"type": "object", "properties": {"path": {"type": "string", "enum": paths}, "text": {"type": "string", "maxLength": 800}},
                   "required": ["path", "text"], "additionalProperties": False}
    schema = {"type": "object", "properties": {"approved": {"type": "boolean"},
              "patches": {"type": "array", "items": item_schema, "maxItems": len(paths)}, "issues": {"type": "array", "items": {"type": "string", "maxLength": 200}, "maxItems": 5}},
              "required": ["approved", "patches", "issues"], "additionalProperties": False}
    system = (
        "You are a precise Japanese learner-dictionary editor. Check each draft field against sourceFields. "
        "Fields marked en must be translated from English; fields marked zh-Hans from Chinese. "
        "English is authoritative wherever it exists. Preserve every clause, negation, number, tense, modality and relationship. "
        "Senses must be concise natural Japanese dictionary glosses, without copying the English headword, POS label or a long definition. "
        "Example sentences must be complete translations. Collocations retain the intended English phrase meaning. "
        "Keep every English expression and IPA literal in tips/notes verbatim. "
        "For age-unspecified singular sister/brother use 姉（または妹）/兄（または弟）; generic aunt/uncle おば/おじ and cousin いとこ. "
        "Return only the required JSON. approved=true means every field is acceptable after patches; otherwise false with brief issues. "
        "Only patch actual errors, never repeat a path or reproduce unchanged fields. If a draft field is missing, supply it. "
        "Do not add explanations to Japanese text. Do not invent details or use Chinese-style Japanese."
    )
    content = json.dumps({"word": entry["w"], "sourceFields": translation_rows(entry),
                          "draft": fields if fields is not None else raw}, ensure_ascii=False)
    response, metrics = client.chat(client.args.review_model, [{"role": "system", "content": system}, {"role": "user", "content": content}], schema=schema, predict=2048)
    reviewed = json.loads(response)
    final = dict(fields or {})
    for patch in reviewed["patches"]:
        if patch["path"] not in paths or not patch["text"].strip():
            raise ValueError("Invalid verifier patch")
        final[patch["path"]] = patch["text"]
    if set(final) != set(paths):
        raise ValueError("Verifier omitted fields")
    result = overlay(entry, final)
    errors = validate(entry, result)
    if errors:
        raise ValueError("Post-verification validation: " + "; ".join(errors))
    return result, reviewed, metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--draft-model", default="translategemma:12b")
    parser.add_argument("--review-model", default="qwen3.5:9b")
    parser.add_argument("--num-ctx", type=int, default=4096)
    parser.add_argument("--cache", type=pathlib.Path, default=ROOT / ".local/ja-local/entries.json")
    parser.add_argument("--start-chunk", type=int, default=0)
    parser.add_argument("--end-chunk", type=int, default=72)
    parser.add_argument("--max-entries", type=int)
    parser.add_argument("--continue-on-review", action="store_true", help="Keep rejected entries as review checkpoints and continue; never publish them")
    parser.add_argument("--benchmark-ids", type=pathlib.Path, help="JSON array of source entry IDs; suppress canonical output")
    args = parser.parse_args()
    client = Ollama(args)
    with urllib.request.urlopen(args.base_url.rstrip("/") + "/api/tags", timeout=10) as response:
        tags = json.load(response)
    digests = {model["name"]: model["digest"] for model in tags.get("models", [])}
    for model in [args.draft_model, args.review_model]:
        if model not in digests:
            raise ValueError(f"Required local model is not ready: {model}")
    provenance = {"pipelineVersion": PIPELINE_VERSION, "draftModel": args.draft_model,
                  "draftDigest": digests[args.draft_model], "reviewModel": args.review_model,
                  "reviewDigest": digests[args.review_model], "numCtx": args.num_ctx, "sourcePolicy": "English primary for bilingual fields; Chinese for Chinese-only fields"}
    atomic_json(args.cache.with_name(args.cache.stem + ".meta.json"), provenance)
    cache = json.loads(args.cache.read_text()) if args.cache.exists() else {}
    benchmark = set(json.loads(args.benchmark_ids.read_text())) if args.benchmark_ids else None
    count = 0
    started = time.monotonic()
    for n in range(args.start_chunk, args.end_chunk + 1):
        source_path = ROOT / f"public/atlas/entries/{n}.json"
        if not source_path.exists():
            break
        source = json.loads(source_path.read_text())
        canonical = ROOT / f"data/ja/entries/{n}.json"
        if canonical.exists() and benchmark is None:
            known = json.loads(canonical.read_text())
            if len(known) != len(source) or any(validate(s, t) for s, t in zip(source, known)):
                raise ValueError(f"Existing contextual chunk is invalid: {n}")
            continue
        for entry in source:
            if benchmark is not None and entry["id"] not in benchmark:
                continue
            digest = hashlib.sha256(json.dumps(entry, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            if (cache.get(entry["id"], {}).get("sourceSha256") == digest and cache[entry["id"]].get("final")
                    and cache[entry["id"]].get("provenance") == provenance):
                continue
            print(json.dumps({"event": "start", "chunk": n, "id": entry["id"]}), flush=True)
            fields, raw, draft_metrics = draft_entry(client, entry)
            # Keep the draft checkpoint even if verification later requires repair.
            cache[entry["id"]] = {"sourceSha256": digest, "provenance": provenance, "draft": fields, "draftRaw": raw,
                                   "draftModel": args.draft_model, "draftMetrics": draft_metrics}
            atomic_json(args.cache, cache)
            try:
                result, review, review_metrics = verify_entry(client, entry, fields, raw)
                record = {"candidate": result, "verification": review, "reviewModel": args.review_model,
                          "reviewMetrics": review_metrics}
                if review.get("approved"):
                    record["final"] = result
                else:
                    record["needsReview"] = True
                cache[entry["id"]].update(record)
                atomic_json(args.cache, cache)
                if not review.get("approved") and not args.continue_on_review:
                    raise ValueError("Verifier requires contextual review: " + json.dumps(review.get("issues"), ensure_ascii=False))
            except ValueError as error:
                cache[entry["id"]].update({"needsReview": True, "reviewError": str(error)})
                atomic_json(args.cache, cache)
                if not args.continue_on_review:
                    raise
            count += 1
            print(json.dumps({"event": "verified" if cache[entry["id"]].get("final") else "needs-review",
                              "id": entry["id"], "completedThisRun": count,
                              "elapsedSeconds": round(time.monotonic()-started), "draft": draft_metrics,
                              "review": cache[entry["id"]].get("reviewMetrics", {})}), flush=True)
            if args.max_entries and count >= args.max_entries:
                return
        if benchmark is None:
            missing = [e["id"] for e in source if not cache.get(e["id"], {}).get("final")]
            if not missing:
                atomic_json(canonical, [cache[e["id"]]["final"] for e in source])
                print(json.dumps({"event": "chunk-complete", "chunk": n, "entries": len(source)}), flush=True)
    print(json.dumps({"event": "complete", "entriesThisRun": count, "elapsedSeconds": round(time.monotonic()-started)}), flush=True)


if __name__ == "__main__":
    main()
