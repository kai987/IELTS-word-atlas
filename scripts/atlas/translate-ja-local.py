#!/usr/bin/env python3
"""Translate vocabulary locally with TranslateGemma drafts and Qwen verification.

Uses only the explicitly selected Ollama instance. Progress and rejected entries
stay in a resumable cache outside public/. Machine-eligible chunks are staged
there for independent source-grounded review, never written to the canonical corpus.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import pathlib
import re
import time
import unicodedata
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
PIPELINE_VERSION = 5
ENGLISH = re.compile(r"/[^/\n\u3400-\u9fff]+/|[A-Za-z][A-Za-z0-9 /'’+()_.-]*")
KANA = re.compile(r"[\u3041-\u3096\u30a1-\u30fa]")
JAPANESE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u3400-\u9fff]")
# Deliberately exclude characters shared with modern Japanese (国, 学, 図, etc.).
# This is a conservative smoke check, not a complete Chinese/Japanese classifier.
SIMPLIFIED = re.compile(r"[这们语说为从该应须词译过还让仅纹较义误则种么样时对关实发书车门马风见话记现动]")
REASONS = ["mistranslation", "omission", "addition", "negation", "quantity", "relationship", "grammar", "untranslated"]


def normalized(text):
    return re.sub(r"[\W_]+", "", unicodedata.normalize("NFKC", text)).casefold()


def literal_counts(text):
    return Counter(term.strip() for term in ENGLISH.findall(text) if term.strip())


def field_errors(entry, path, text):
    """Reject obvious untranslated output; ambiguous shared-Han glosses need review."""
    row = next((row for row in translation_rows(entry) if row["path"] == path), None)
    if row is None:
        return ["unknown field path"]
    if not isinstance(text, str) or not text.strip():
        return ["translation must be a nonempty string"]
    errors = []
    if re.search(r"<unk>|ZXQTERM|QXZ|⁇|\[待翻译\]|\[翻訳待ち\]|```|【\s*\d+\s*】", text):
        errors.append("placeholder, numbering or markup in translation")
    # English/IPA are protected literals only in tips/notes. Remove those before
    # checking the explanatory Japanese so the literals cannot mask a regression.
    explanation = text
    if path in {"tip", "note"}:
        for literal, count in literal_counts(entry.get(path, "")).items():
            if text.count(literal) < count:
                errors.append(f"English/IPA literal missing or occurrence lost: {literal}")
            explanation = explanation.replace(literal, "")
    numeric_gloss = path.startswith(("senses.", "col.")) and re.fullmatch(r"[0-9０-９][0-9０-９,.，．%％+−-]*", text.strip())
    if not JAPANESE.search(explanation) and not numeric_gloss:
        errors.append("Japanese translation/explanation is missing")
    if SIMPLIFIED.search(explanation):
        errors.append("untranslated simplified Chinese character")
    if re.search(r"用于|用来|指的是|意为|例如", explanation):
        errors.append("untranslated Chinese wording")
    if re.search(r"[\u0400-\u04ff\u0600-\u06ff\u0900-\u09ff\uac00-\ud7af]", explanation):
        errors.append("unexpected non-Japanese script; needs contextual review")
    if path.startswith(("senses.", "ex.", "col.")):
        headword = entry.get("w", "")
        if len(headword) > 2 and re.fullmatch(r"[a-z][a-z '-]*", headword) and re.search(r"(?<![A-Za-z])" + re.escape(headword) + r"(?![A-Za-z])", text, re.I):
            errors.append("English headword retained in Japanese translation; needs contextual review")
    if normalized(text) == normalized(row["text"]):
        # A shared-Han short gloss can legitimately equal its Chinese source.
        if (row["language"] == "en" and not numeric_gloss) or path.startswith("ex.") or path in {"tip", "note"}:
            errors.append("translation copies the source text")
    if path.startswith(("ex.", "col.")) and row["language"] == "en":
        original = normalized(row["text"])
        if len(original) > 12 and original in normalized(text):
            errors.append("translation embeds the untranslated source")
        if path.startswith("ex."):
            for phrase in re.findall(r"[A-Za-z]+(?:[ \t]+[A-Za-z]+){2,}", text):
                if len(phrase) >= 12 and normalized(phrase) in original:
                    errors.append("untranslated English clause in Japanese sentence")
                    break
    if (path.startswith("ex.") or path in {"tip", "note"}) and len(row["text"]) > 10 and not KANA.search(explanation):
        errors.append("sentence/explanation has no Japanese kana")
    if path.startswith("col.") and "｜" in text:
        errors.append("collocation patch must contain Japanese only; program retains English")
    if re.search(r"(.{2,8})\1{3,}", explanation):
        errors.append("repeated output sequence")
    return errors


def require_draft(entry, fields):
    paths = {row["path"] for row in translation_rows(entry)}
    if not isinstance(fields, dict) or set(fields) != paths or any(not isinstance(v, str) or not v.strip() for v in fields.values()):
        raise ValueError("Draft fields are missing, malformed or unaligned; hold for draft repair, not Qwen review")


def apply_review(entry, fields, review):
    """Apply evidence-linked safe proposals; every rejected proposal keeps its draft."""
    require_draft(entry, fields)
    final = dict(fields)
    audit = {"approved": False, "modelApproved": False, "acceptedPatches": [],
             "rejectedPatches": [], "errors": [], "needsReview": True, "rawReview": review}
    rows = {row["path"]: row for row in translation_rows(entry)}
    if (not isinstance(review, dict) or set(review) != {"approved", "patches", "issues"}
            or type(review.get("approved")) is not bool or not isinstance(review.get("patches"), list)
            or not isinstance(review.get("issues"), list) or any(not isinstance(v, str) for v in review.get("issues", []))):
        audit["errors"].append("malformed review response")
        patches = []
    else:
        audit["modelApproved"] = review["approved"]
        patches = review["patches"]
        if len(patches) > len(rows):
            audit["errors"].append("too many review patches")
            patches = []
    counts = Counter(p.get("path") for p in patches if isinstance(p, dict) and isinstance(p.get("path"), str))
    for patch in patches:
        errors = []
        if not isinstance(patch, dict):
            audit["rejectedPatches"].append({"patch": patch, "errors": ["patch must be an object"]})
            continue
        path = patch.get("path")
        if not isinstance(path, str) or path not in rows:
            errors.append("unknown field path")
        elif counts[path] > 1:
            errors.append("duplicate patch path")
        if set(patch) != {"path", "before", "text", "reason", "evidence"}:
            errors.append("patch must include path, before, text, reason and evidence only")
        if isinstance(path, str) and path in rows:
            if patch.get("before") != fields[path]:
                errors.append("before does not match the original draft")
            if patch.get("text") == fields[path]:
                errors.append("unchanged field is not a correction")
            evidence = patch.get("evidence")
            if not isinstance(evidence, str) or not evidence.strip() or evidence not in rows[path]["text"]:
                errors.append("evidence is not a quote from this source field")
            if patch.get("reason") not in REASONS:
                errors.append("unknown correction reason")
            errors += field_errors(entry, path, patch.get("text"))
            # A newly lost/changed Arabic number is held for explicit review. This
            # may also hold a valid kanji numeral conversion; never guess silently.
            if isinstance(patch.get("text"), str):
                numbers = lambda value: Counter(re.findall(r"\d+(?:[.,:]\d+)*", unicodedata.normalize("NFKC", value)))
                required = numbers(rows[path]["text"]) & numbers(fields[path])
                if required - numbers(patch["text"]):
                    errors.append("number preserved in draft was removed or changed")
        if errors:
            audit["rejectedPatches"].append({**patch, "errors": errors})
        else:
            final[path] = patch["text"]
            audit["acceptedPatches"].append(patch)
    # Also inspect unchanged and retained draft fields: model approval is not a
    # substitute for the gate (e.g. an existing Chinese tip with patches=[]).
    for path, text in final.items():
        audit["errors"] += [f"{path}: {error}" for error in field_errors(entry, path, text)]
    audit["errors"] += validate(entry, overlay(entry, final))
    audit["issues"] = review.get("issues", []) if isinstance(review, dict) else []
    audit["approved"] = (audit["modelApproved"] and not audit["issues"] and not audit["errors"] and not audit["rejectedPatches"])
    audit["needsReview"] = not audit["approved"]
    return final, audit


def approved_cache(entry, record, provenance):
    """Never stage a chunk by mixing stale machine candidates from another run."""
    if not isinstance(record, dict) or record.get("provenance") != provenance:
        return False
    digest = hashlib.sha256(json.dumps(entry, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    if record.get("sourceSha256") != digest or not record.get("machineEligible") or not record.get("verification", {}).get("approved") or record.get("needsReview"):
        return False
    result = record.get("candidate")
    if not isinstance(result, dict) or validate(entry, result):
        return False
    fields = {}
    for row in translation_rows(entry):
        path = row["path"]
        if "." in path:
            key, index = path.split(".")
            value = result[key][int(index)]
            fields[path] = value.split("｜", 1)[-1] if key == "col" else value
        else:
            fields[path] = result[path]
    return not any(field_errors(entry, key, text) for key, text in fields.items())


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
        for term, count in literal_counts(entry.get(key, "")).items():
            if value.count(term) < count:
                errors.append(f"{key} English/IPA literal missing or occurrence lost: {term}")
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
                               "top_k": 40, "top_p": 0.95,
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
    # raw is retained by the caller as a diagnostic checkpoint, never used as a
    # differently shaped fallback input. Repair draft alignment before review.
    require_draft(entry, fields)
    rows = translation_rows(entry)
    paths = [row["path"] for row in rows]
    item_schema = {"type": "object", "properties": {
        "path": {"type": "string", "enum": paths},
        "before": {"type": "string", "minLength": 1},
        "text": {"type": "string", "minLength": 1, "maxLength": 1600},
        "reason": {"type": "string", "enum": REASONS},
        "evidence": {"type": "string", "minLength": 1, "maxLength": 300}},
        "required": ["path", "before", "text", "reason", "evidence"], "additionalProperties": False}
    schema = {"type": "object", "properties": {"approved": {"type": "boolean"},
              "patches": {"type": "array", "items": item_schema, "maxItems": len(paths)}, "issues": {"type": "array", "items": {"type": "string", "maxLength": 200}, "maxItems": 5}},
              "required": ["approved", "patches", "issues"], "additionalProperties": False}
    system = (
        "Audit Japanese translations against the corresponding sourceText. All text replacements MUST be JAPANESE. "
        "The input field draftJapanese is the existing JAPANESE translation, NOT the source. "
        "English source is authoritative for en; translate Chinese to Japanese only for zh-Hans. "
        "Keep an acceptable draft exactly unchanged; do not polish style, rewrite synonyms, add readings or retranslate the whole entry. "
        "Patch only a demonstrable substantive error. Copy the original draftJapanese exactly into before. "
        "Give a reason code and a short exact quote from that field's sourceText as evidence. "
        "Never return source English/Chinese as a translation. senses.N requires a concise Japanese gloss. "
        "ex.N requires a complete Japanese sentence. col.N requires ONLY the JAPANESE meaning: "
        "the program adds the original English phrase outside your patch. Example: source 'public library', text '公共図書館'. "
        "tip/note require the full JAPANESE explanation while retaining each embedded English/IPA literal and its occurrences verbatim. "
        "Never replace an explanation with just its English terms. Preserve clauses, negation, comparisons, numbers, modality and relationships. "
        "Do not add age to sister/brother: use 姉（または妹）/兄（または弟） where needed. Generic aunt/uncle are おば/おじ, cousin is いとこ. "
        "Return JSON only. approved=true means all fields are acceptable after the proposed patches; issues must then be empty. "
        "If uncertain, keep the draft, set approved=false and describe the unresolved issue in issues. "
        "Use patches=[] when no actual correction is needed; never repeat a path or output unchanged fields."
    )
    content = json.dumps({"word": entry["w"], "targetLanguage": "ja", "fields": [
        {"path": row["path"], "sourceLanguage": row["language"], "sourceText": row["text"],
         "draftJapanese": fields[row["path"]]} for row in rows]}, ensure_ascii=False)
    response, metrics = client.chat(client.args.review_model, [{"role": "system", "content": system}, {"role": "user", "content": content}], schema=schema, predict=2048)
    try:
        reviewed = json.loads(response)
    except (ValueError, TypeError):
        reviewed = {"invalidRawResponse": response}
    final, audit = apply_review(entry, fields, reviewed)
    return overlay(entry, final), audit, metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--draft-model", default="translategemma:12b-it-q8_0")
    parser.add_argument("--review-model", default="qwen3.5:9b-q8_0")
    parser.add_argument("--num-ctx", type=int, default=4096)
    parser.add_argument("--cache", type=pathlib.Path, default=ROOT / ".local/ja-local-v5/entries.json")
    parser.add_argument("--start-chunk", type=int, default=0)
    parser.add_argument("--end-chunk", type=int, default=72)
    parser.add_argument("--max-entries", type=int)
    parser.add_argument("--continue-on-review", action="store_true", help="Keep rejected entries as review checkpoints and continue; never publish them")
    parser.add_argument("--benchmark-ids", type=pathlib.Path, help="Review only this JSON array of source entry IDs; suppress candidate chunk assembly")
    args = parser.parse_args()
    args.cache = args.cache.resolve()
    if any(protected == args.cache or protected in args.cache.parents for protected in [(ROOT / "data").resolve(), (ROOT / "public").resolve()]):
        raise ValueError("Model candidates must stay outside data/ and public/ until independent review")
    client = Ollama(args)
    with urllib.request.urlopen(args.base_url.rstrip("/") + "/api/tags", timeout=10) as response:
        tags = json.load(response)
    digests = {model["name"]: model["digest"] for model in tags.get("models", [])}
    for model in [args.draft_model, args.review_model]:
        if model not in digests:
            raise ValueError(f"Required local model is not ready: {model}")
    provenance = {"pipelineVersion": PIPELINE_VERSION, "workerSha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(), "draftModel": args.draft_model,
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
            if approved_cache(entry, cache.get(entry["id"]), provenance):
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
                          "reviewMetrics": review_metrics, "machineEligible": bool(review.get("approved")),
                          "needsReview": not review.get("approved"),
                          "needsSemanticReview": True,
                          "semanticStatus": "requires independent source-grounded review"}
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
            print(json.dumps({"event": "machine-eligible" if cache[entry["id"]].get("machineEligible") else "needs-review",
                              "id": entry["id"], "completedThisRun": count,
                              "elapsedSeconds": round(time.monotonic()-started), "draft": draft_metrics,
                              "review": cache[entry["id"]].get("reviewMetrics", {})}), flush=True)
            if args.max_entries and count >= args.max_entries:
                return
        if benchmark is None:
            missing = [e["id"] for e in source if not approved_cache(e, cache.get(e["id"]), provenance)]
            if not missing:
                destination = args.cache.parent / "candidate-chunks" / f"{n}.json"
                atomic_json(destination, {"provenance": provenance,
                    "semanticStatus": "requires independent source-grounded review",
                    "entries": [cache[e["id"]]["candidate"] for e in source]})
                print(json.dumps({"event": "candidate-chunk-complete", "chunk": n, "entries": len(source)}), flush=True)
    print(json.dumps({"event": "complete", "entriesThisRun": count, "elapsedSeconds": round(time.monotonic()-started)}), flush=True)


if __name__ == "__main__":
    main()
