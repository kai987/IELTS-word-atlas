#!/usr/bin/env python3
"""Local model adapters for source-grounded Japanese semantic review.

Detection, independent reference translation, repair and model cross-checks are
separate tasks. No function in this module publishes translations or claims
that model agreement is an independent final semantic decision.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request


CATEGORIES = [
    "wrong_meaning", "omission", "addition_or_fabrication",
    "negation_or_modality", "quantity_time_or_entity",
    "grammar_or_terminology", "untranslated",
]
REASONS = ["mistranslation", "omission", "addition", "negation", "quantity", "relationship", "grammar", "untranslated"]
STATUSES = ["pass", "error", "uncertain", "unavailable"]
COMMON_OPTIONS = {"seed": 42, "repeat_penalty": 1.0, "presence_penalty": 0.0}
# These are distinct stage profiles, not a claim that one sampling recipe is
# best for both models. Calibration must compare accuracy and regressions.
PROFILES = {
    "translate": {"model": "translategemma:12b-it-q8_0", "think": False,
                  "options": {**COMMON_OPTIONS, "temperature": 0.1, "top_k": 64, "top_p": 0.95,
                              "num_ctx": 4096, "num_predict": 2048}},
    "detect": {"model": "qwen3.5:9b-q8_0", "think": False,
               "options": {**COMMON_OPTIONS, "temperature": 0.1, "top_k": 40, "top_p": 0.95,
                           "num_ctx": 8192, "num_predict": 4096}},
    "repair": {"model": "qwen3.5:9b-q8_0", "think": False,
               "options": {**COMMON_OPTIONS, "temperature": 0.1, "top_k": 40, "top_p": 0.95,
                           "num_ctx": 8192, "num_predict": 2048}},
    "adjudicate": {"model": "qwen3.5:9b-q8_0", "think": False,
                   "options": {**COMMON_OPTIONS, "temperature": 0.1, "top_k": 40, "top_p": 0.95,
                               "num_ctx": 8192, "num_predict": 2048}},
}
SAMPLING_PRESETS = {
    "baseline": {"temperature": 0.1, "top_p": 0.95, "top_k": 40,
                 "presence_penalty": 0.0, "repeat_penalty": 1.0, "think": False},
    "official-instruct": {"temperature": 0.7, "top_p": 0.8, "top_k": 20,
                          "min_p": 0.0, "presence_penalty": 1.5,
                          "repeat_penalty": 1.0, "think": False},
    "official-thinking": {"temperature": 1.0, "top_p": 0.95, "top_k": 20,
                         "min_p": 0.0, "presence_penalty": 1.5,
                         "repeat_penalty": 1.0, "think": True},
}


def profile_for(stage, preset="baseline"):
    """Return a fresh stage configuration; Qwen recipes never alter TranslateGemma."""
    if stage not in PROFILES:
        raise ValueError(f"Unknown model stage: {stage}")
    result = deepcopy(PROFILES[stage])
    if stage == "translate":
        if preset != "baseline":
            raise ValueError("Qwen sampling presets cannot be used for TranslateGemma")
        return result
    if preset not in SAMPLING_PRESETS:
        raise ValueError(f"Unknown sampling preset: {preset}")
    values = deepcopy(SAMPLING_PRESETS[preset])
    result["think"] = values.pop("think")
    result["options"].update(values)
    return result


def _base_url(value):
    parsed = urllib.parse.urlparse(value)
    if (parsed.scheme not in {"http", "https"}
            or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in {"", "/"}):
        raise ValueError("Model calls are restricted to an unauthenticated loopback Ollama URL")
    return value.rstrip("/")


def _request(base_url, suffix, payload=None, timeout=15):
    request = urllib.request.Request(
        _base_url(base_url) + suffix,
        data=None if payload is None else json.dumps(payload, ensure_ascii=False).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def _resident(base_url, timeout=15):
    return [row.get("name", row.get("model"))
            for row in _request(base_url, "/api/ps", timeout=timeout).get("models", [])]


def _is_gemma4_model(name):
    return name.lower().rsplit("/", 1)[-1].split(":", 1)[0] == "gemma4"


def _sanitized_content(parts, allow_empty_thought_prefix=False):
    """Redact reasoning; only Gemma's documented empty prefix is harmless."""
    text = "".join(parts)
    original_length = len(text)
    text = re.sub(r"<think(?:ing)?>.*?(?:</think(?:ing)?>|$)", "", text, flags=re.S | re.I)
    text = re.sub(r"</think(?:ing)?>", "", text, flags=re.I)
    held_chars = original_length - len(text)
    empty_prefixes = 0
    opening, closing = "<|channel>", "<channel|>"
    while opening in text:
        start = text.index(opening)
        end = text.find(closing, start + len(opening))
        if end < 0:
            held_chars += len(text) - start
            text = text[:start]
            break
        body = text[start + len(opening):end]
        stop = end + len(closing)
        if (allow_empty_thought_prefix and not text[:start].strip()
                and re.fullmatch(r"thought\r?\n\s*", body)):
            empty_prefixes += 1
        else:
            held_chars += stop - start
        text = text[:start] + text[stop:]
    # An orphan close can follow a backend-prefilled opener. Its preceding
    # content may be private, so discard that whole prefix and hold the call.
    while closing in text:
        stop = text.index(closing) + len(closing)
        held_chars += stop
        text = text[stop:]
    for marker in (opening, closing):
        partial = marker[:-1]
        if partial in text:
            start = text.index(partial) if marker == opening else 0
            held_chars += len(text) - start
            text = text[:start]
        # Streaming may end halfway through a marker. A partial close also
        # makes the entire preceding content unsafe to retain.
        for length in range(len(marker) - 1, 0, -1):
            if text.endswith(marker[:length]):
                stop = len(text) - length if marker == opening else 0
                held_chars += len(text) - stop
                text = text[:stop]
                break
    return text, held_chars, empty_prefixes


def _public_content(parts):
    """Defensively discard inline reasoning, including native Gemma channels."""
    text, held_chars, _ = _sanitized_content(parts)
    return text, held_chars


def ensure_single_model(base_url, selected_model):
    """Refuse to interrupt a different resident model; never unload it implicitly."""
    loaded = _resident(base_url)
    other = [name for name in loaded if name != selected_model]
    if other:
        raise ValueError("Another model is resident; run model stages separately: " + ", ".join(other))
    return loaded


def release_model(base_url, model):
    """Release only this stage's model, allowing up to 15 seconds for async unload."""
    deadline = time.monotonic() + 15
    loaded = _resident(base_url, timeout=5)
    if model not in loaded:
        return loaded
    _request(base_url, "/api/generate", {"model": model, "keep_alive": 0},
             timeout=max(0.1, deadline - time.monotonic()))
    while time.monotonic() < deadline:
        loaded = _resident(base_url, timeout=max(0.1, min(2, deadline - time.monotonic())))
        if model not in loaded:
            return loaded
        time.sleep(min(0.2, max(0, deadline - time.monotonic())))
    raise RuntimeError("Selected model did not finish unloading within 15 seconds")


class ModelCallError(RuntimeError):
    """A terminal recorded attempt; diagnostic output excludes private thinking."""

    def __init__(self, message, result):
        message, _ = _public_content([str(message)])
        if re.search(r'["\x27]thinking["\x27]\s*:', message):
            message = "Backend reported an error; private diagnostic fields omitted"
        message = message[:2200]
        super().__init__(message)
        self.result = {**result, "error": message}
        if isinstance(self.result.get("text"), str):
            self.result["text"], _ = _public_content([self.result["text"]])
        self.output = self.result.get("text", "")


class LocalClient:
    def __init__(self, base_url, model, options, think=False, keep_alive="5m", timeout=600):
        self.base_url = _base_url(base_url)
        if not isinstance(model, str) or not model:
            raise ValueError("An installed local model name is required")
        if not isinstance(options, dict) or not options:
            raise ValueError("Explicit model sampling and token options are required")
        self.model, self.options = model, deepcopy(options)
        self.think, self.keep_alive, self.timeout = bool(think), keep_alive, timeout
        self.on_request = None

    def chat(self, messages, schema=None):
        payload = {"model": self.model, "messages": deepcopy(messages), "stream": True,
                   "keep_alive": self.keep_alive, "options": deepcopy(self.options)}
        if "qwen" in self.model.lower() or _is_gemma4_model(self.model) or self.think:
            payload["think"] = self.think
        if schema is not None:
            payload["format"] = deepcopy(schema)
        if self.on_request is not None:
            self.on_request(deepcopy(payload))
        result = {"text": "", "metrics": {}, "request": payload}
        request = urllib.request.Request(
            self.base_url + "/api/chat", data=json.dumps(payload, ensure_ascii=False).encode(),
            headers={"Content-Type": "application/json"},
        )
        parts, final, thinking_chars = [], None, 0
        started = time.monotonic_ns()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                for line in response:
                    if not line.strip():
                        continue
                    message = json.loads(line)
                    if message.get("error"):
                        backend = message["error"]
                        if isinstance(backend, dict):
                            backend = backend.get("message", "Backend returned a structured error")
                        raise ValueError(backend if isinstance(backend, str) else "Backend returned a non-text error")
                    body = message.get("message", {})
                    # Never retain the private thinking text, even on failure.
                    thinking_chars += len(body.get("thinking", ""))
                    text = body.get("content", "")
                    if not isinstance(text, str):
                        raise ValueError("Model returned non-text content")
                    parts.append(text)
                    if message.get("done"):
                        final = message
            result["text"], inline_thinking_chars, empty_prefixes = _sanitized_content(
                parts, _is_gemma4_model(self.model) and not self.think)
            result["metrics"]["inline_thinking_chars"] = inline_thinking_chars
            if empty_prefixes:
                result["metrics"]["empty_thought_prefixes_removed"] = empty_prefixes
            if final:
                for key in ["total_duration", "load_duration", "prompt_eval_count", "prompt_eval_duration", "eval_count", "eval_duration"]:
                    result["metrics"][key] = final.get(key, 0)
                result["metrics"]["done_reason"] = final.get("done_reason")
            if not final or final.get("done_reason") in {"length", "max_tokens"}:
                raise ValueError("Generation incomplete or token budget exhausted; hold this attempt")
            if inline_thinking_chars:
                raise ValueError("Backend returned inline thinking in content; stripped output is held")
            if _is_gemma4_model(self.model) and not self.think and thinking_chars:
                raise ValueError("Backend returned thinking while disabled; hold this attempt")
            if not result["text"].strip():
                raise ValueError("Generation returned empty content")
        except Exception as error:
            result["text"], inline_thinking_chars, empty_prefixes = _sanitized_content(
                parts, _is_gemma4_model(self.model) and not self.think)
            result["metrics"].update({"wall_latency_ns": time.monotonic_ns() - started,
                                      "thinking_chars": thinking_chars,
                                      "inline_thinking_chars": inline_thinking_chars})
            if empty_prefixes:
                result["metrics"]["empty_thought_prefixes_removed"] = empty_prefixes
            error_message = str(error)
            if isinstance(error, urllib.error.HTTPError):
                result["httpStatus"] = error.code
                # Ollama returns backend failures before an NDJSON stream starts.
                # Retain only its error message, not a general response object
                # that might contain request data or a private reasoning field.
                try:
                    body = error.read(8192).decode("utf-8", errors="replace")
                    try:
                        data = json.loads(body)
                    except json.JSONDecodeError:
                        data = None
                    if isinstance(data, dict):
                        backend = data.get("error", "")
                        if isinstance(backend, dict):
                            backend = backend.get("message", "")
                        if not isinstance(backend, str):
                            backend = "Backend returned a non-text error"
                    elif data is not None:
                        backend = "Backend returned a non-object error response"
                    elif body.lstrip().startswith(("{", "[")) or re.search(r'["\']thinking["\']\s*:', body):
                        backend = "Backend returned malformed or truncated JSON error details"
                    else:
                        backend = body
                    backend, _ = _public_content([backend])
                    if re.search(r'["\x27]thinking["\x27]\s*:', backend):
                        backend = "Backend returned private diagnostic fields; details omitted"
                    result["backendError"] = backend[:2000]
                    result["backendErrorTruncated"] = len(backend) > 2000
                except Exception:
                    result["backendError"] = "Unable to read backend error details"
                error_message = f"HTTP {error.code}: {result['backendError']}"
            raise ModelCallError(error_message, result) from None
        result["metrics"].update({"wall_latency_ns": time.monotonic_ns() - started,
                                  "thinking_chars": thinking_chars})
        return result


def _object(response):
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except json.JSONDecodeError as error:
            raise ValueError("Model response is not complete JSON") from error
    if not isinstance(response, dict):
        raise ValueError("Model response must be a JSON object")
    return response


def _translated_fields(entry):
    if any(not isinstance(field, dict) or not isinstance(field.get("mode"), str)
           or field.get("mode") not in {"translate", "empty", "preserve"} for field in entry["fields"]):
        raise ValueError("Unknown field review mode")
    fields = [field for field in entry["fields"] if field["mode"] == "translate"]
    for field in fields:
        if not isinstance(field.get("path"), str) or not field["path"]:
            raise ValueError("Review field path must be a nonempty string")
        if not isinstance(field.get("sourceLanguage"), str) or field.get("sourceLanguage") not in {"en", "zh", "zh-Hans", "zh-CN"}:
            raise ValueError("Unknown authoritative source language")
        if not isinstance(field.get("sourceText"), str) or not field["sourceText"].strip():
            raise ValueError("Translation review requires a nonempty authoritative source")
        if not isinstance(field.get("currentJapanese"), str):
            raise ValueError("Current Japanese must be a string")
    paths = [field["path"] for field in fields]
    if len(set(paths)) != len(paths):
        raise ValueError("Input entry contains duplicate field paths")
    return fields


def build_detection(entry):
    fields = _translated_fields(entry)
    if not fields:
        raise ValueError("No semantic translation fields need a model call")
    paths = [field["path"] for field in fields]
    item = {"type": "object", "properties": {
        "path": {"type": "string", "enum": paths},
        "status": {"type": "string", "enum": STATUSES},
        "categories": {"type": "array", "items": {"type": "string", "enum": CATEGORIES}, "uniqueItems": True, "maxItems": len(CATEGORIES)},
        "sourceQuote": {"type": "string", "maxLength": 500},
        "targetQuote": {"type": "string", "maxLength": 500},
        "explanation": {"type": "string", "minLength": 1, "maxLength": 600}},
        "required": ["path", "status", "categories", "sourceQuote", "targetQuote", "explanation"],
        "additionalProperties": False}
    schema = {"type": "object", "properties": {"assessments": {"type": "array", "items": item,
              "minItems": len(paths), "maxItems": len(paths)}}, "required": ["assessments"], "additionalProperties": False}
    system = (
        "You are auditing existing Japanese learner-dictionary translations against authoritative sources. "
        "This stage DETECTS errors; do not propose replacements or rewrite anything. Review EVERY supplied field separately. "
        "For sourceLanguage=en, English is authoritative; for zh/zh-Hans, translate the Chinese explanation into Japanese. "
        "First identify the source's checkable facts, then compare their Japanese counterparts: the exact sense, all clauses, "
        "negation, possibility/obligation, comparison and range boundaries, numbers and units, times and deadlines, "
        "age/gender/relationships, technical meaning, and grammar permissions/prohibitions. "
        "Do not add a.m./p.m. or older/younger unless stated. A religious sister is distinct from a female sibling. "
        "A proper noun, valid English quotation, shared-Han Japanese word or harmless synonymous wording is not automatically an error. "
        "senses.N is a concise Japanese dictionary gloss; ex.N is a complete Japanese translation; col.N is ONLY the Japanese "
        "meaning because the program retains the English phrase separately. tip/note require complete Japanese explanations "
        "with embedded English/IPA literals unchanged and repeated where required. "
        "Output exactly one assessment per field. pass requires an actual source-based comparison, never inferred from no edits. "
        "error means a demonstrable substantive error and requires at least one category. uncertain means the supplied context "
        "does not settle correctness; unavailable means the assessment cannot be completed. "
        "For pass/error/uncertain quote a short exact source substring and a short exact currentJapanese substring "
        "(targetQuote may be empty only when the current translation is empty). Explain the factual comparison briefly, "
        "not private reasoning. Categories must be empty for pass. Return only the required JSON."
    )
    content = {"entryId": entry["id"], "word": entry["word"], "fields": [
        {key: field[key] for key in ["path", "sourceLanguage", "sourceText", "currentJapanese", "pos"] if key in field}
        for field in fields]}
    return [{"role": "system", "content": system},
            {"role": "user", "content": json.dumps(content, ensure_ascii=False)}], schema


def _quote(value, original, label, required=True):
    if not isinstance(original, str):
        raise ValueError(f"{label} has no matching text source")
    if not isinstance(value, str) or (required and not value.strip()):
        raise ValueError(f"{label} requires an exact nonempty quote")
    if value and value not in original:
        raise ValueError(f"{label} is not a quote from the matching field")


def validate_detection(entry, response):
    response = _object(response)
    if set(response) != {"assessments"} or not isinstance(response["assessments"], list):
        raise ValueError("Detection response requires only assessments")
    fields = {field["path"]: field for field in _translated_fields(entry)}
    assessments = response["assessments"]
    if len(assessments) != len(fields):
        raise ValueError("Every semantic field must have exactly one assessment")
    seen, validated = set(), []
    required = {"path", "status", "categories", "sourceQuote", "targetQuote", "explanation"}
    for item in assessments:
        if not isinstance(item, dict) or set(item) != required:
            raise ValueError("Malformed detection assessment")
        path = item["path"]
        if not isinstance(path, str) or path not in fields or path in seen:
            raise ValueError("Missing, duplicate or unknown detection field")
        seen.add(path)
        status, categories = item["status"], item["categories"]
        if status not in STATUSES or not isinstance(categories, list) or any(not isinstance(c, str) or c not in CATEGORIES for c in categories):
            raise ValueError("Invalid assessment status or category")
        if (status == "pass" and categories) or (status == "error" and not categories):
            raise ValueError("Assessment categories contradict its status")
        if not isinstance(item["explanation"], str) or not item["explanation"].strip():
            raise ValueError("Every field requires an explicit comparison or unresolved reason")
        if len(item["explanation"]) > 600 or any(isinstance(item[key], str) and len(item[key]) > 500 for key in ["sourceQuote", "targetQuote"]):
            raise ValueError("Detection response exceeds its declared schema limits")
        field = fields[path]
        _quote(item["sourceQuote"], field["sourceText"], "sourceQuote", status != "unavailable")
        _quote(item["targetQuote"], field["currentJapanese"], "targetQuote",
               status != "unavailable" and bool(field["currentJapanese"].strip()))
        normalized = deepcopy(item)
        # A repeated category label carries no additional semantic information.
        # Preserve the original response in the call artifact and record this
        # lossless metadata normalization; duplicate FIELD paths remain invalid.
        if len(set(categories)) != len(categories):
            normalized["categories"] = list(dict.fromkeys(categories))
            normalized["formatNormalizations"] = ["repeated category labels deduplicated; raw response retained"]
        validated.append(normalized)
    if seen != set(fields):
        raise ValueError("Detection omitted fields")
    return validated


def parse_detection(entry, response):
    """Keep valid assessments and hold only fields whose output cannot be checked.

    This does not repair model JSON, invent quotes, or reinterpret a failed
    assessment as a pass. Every translation field receives one explicit result;
    the raw response remains the caller's immutable attempt evidence.
    """
    fields = _translated_fields(entry)
    indexed = {field["path"]: field for field in fields}
    structural_errors, field_errors = [], {}
    try:
        document = _object(response)
    except ValueError as error:
        document = None
        structural_errors.append(str(error))
    groups = {path: [] for path in indexed}
    if document is not None:
        if set(document) != {"assessments"}:
            structural_errors.append("Detection response contains missing or unknown top-level keys")
        items = document.get("assessments")
        if not isinstance(items, list):
            structural_errors.append("Detection response requires an assessments array")
        else:
            for item in items:
                if not isinstance(item, dict):
                    structural_errors.append("Detection assessment is not an object")
                    continue
                path = item.get("path")
                if not isinstance(path, str) or path not in indexed:
                    structural_errors.append("Detection assessment has an unknown or missing field path")
                    continue
                groups[path].append(item)
    assessments = []
    for field in fields:
        path = field["path"]
        items = groups[path]
        if len(items) == 0:
            reasons = ["Detection did not provide a usable assessment for this field"]
        elif len(items) > 1:
            reasons = ["Detection repeated this field path; no competing assessment was selected"]
        else:
            try:
                validated = validate_detection({**entry, "fields": [field]}, {"assessments": items})
            except (ValueError, TypeError, KeyError) as error:
                reasons = [str(error)[:300]]
            else:
                assessments.append(validated[0])
                continue
        field_errors[path] = reasons
        assessments.append({"path": path, "status": "unavailable", "categories": [],
                            "sourceQuote": "", "targetQuote": "",
                            "explanation": "; ".join(reasons)[:300],
                            "method": "program_validation_hold"})
    return {"assessments": assessments, "fieldValidationErrors": field_errors,
            "structuralErrors": structural_errors}


def build_reference(field):
    """One native TranslateGemma translation, with no current Japanese or verdict."""
    if field.get("mode", "translate") != "translate":
        raise ValueError("Only translation fields need a reference model call")
    source = field.get("sourceText")
    language = field.get("sourceLanguage")
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Reference translation requires nonempty source text")
    if language == "en":
        name, code = "English", "en"
    elif language in {"zh", "zh-Hans", "zh-CN"}:
        name, code = "Chinese", "zh"
    else:
        raise ValueError("Unsupported authoritative source language")
    prompt = (
        f"You are a professional {name} ({code}) to Japanese (ja) translator. "
        f"Your goal is to accurately convey the meaning and nuances of the original {name} text while adhering to Japanese grammar, vocabulary, and cultural sensitivities.\n"
        "Produce only the Japanese translation, without any additional explanations or commentary. "
        f"Please translate the following {name} text into Japanese:\n\n\n" + source
    )
    return [{"role": "user", "content": prompt}]


def _literals(text):
    pattern = r"/[^/\n\u3400-\u9fff]+/|[A-Za-z][A-Za-z0-9 /'’+()_.-]*"
    return Counter(value.strip() for value in re.findall(pattern, text) if value.strip())


def translate_field(client, field):
    result = client.chat(build_reference(field))
    text = result["text"].strip()
    errors = []
    if not text or re.search(r"<unk>|ZXQTERM|QXZ|⁇|```", text):
        errors.append("empty, placeholder or marked-up reference translation")
    if field["path"] in {"tip", "note"}:
        for term, count in _literals(field["sourceText"]).items():
            if text.count(term) < count:
                errors.append("reference lost protected literal/occurrence: " + term)
    if errors:
        raise ModelCallError("; ".join(errors), result)
    return {**result, "text": text, "semanticStatus": "reference only; not a correctness verdict"}


def build_repair(entry, field, assessment, reference=None):
    if field["mode"] != "translate" or assessment.get("path") != field["path"] or assessment.get("status") not in {"error", "uncertain"}:
        raise ValueError("Only a matching flagged semantic field can enter repair")
    schema = {"type": "object", "properties": {
        "path": {"type": "string", "enum": [field["path"]]},
        "before": {"type": "string"}, "text": {"type": "string", "minLength": 1, "maxLength": 1600},
        "reason": {"type": "string", "enum": REASONS},
        "evidence": {"type": "string", "minLength": 1, "maxLength": 600}},
        "required": ["path", "before", "text", "reason", "evidence"], "additionalProperties": False}
    system = (
        "Repair only the supplied flagged Japanese translation against its authoritative source. "
        "Return a minimal substantive correction, not style polishing. Source English controls en fields; Chinese controls zh fields. "
        "Copy currentJapanese exactly into before; evidence must be an exact quote from sourceText, not a paraphrase. "
        "text must be Japanese. col.N contains ONLY its Japanese meaning, never the original English prefix. "
        "Preserve every clause, negation, modality, numerical/range boundary, time and relationship; do not infer older/younger or a.m./p.m. "
        "Preserve English/IPA literals and occurrences in tips/notes. Do not invent readings, names, definitions or facts. "
        "Any reference translation is fallible evidence, not a verdict: do not copy it without comparison. "
        "If the issue cannot be resolved from source/context, keep the original text; the unchanged proposal will be held. "
        "Do not claim approval. Return only the required JSON."
    )
    content = {"entryId": entry["id"], "word": entry["word"],
               "field": {key: field[key] for key in ["path", "sourceLanguage", "sourceText", "currentJapanese", "pos"] if key in field},
               "assessment": deepcopy(assessment)}
    if reference is not None:
        value = reference.get("text") if isinstance(reference, dict) else reference
        if not isinstance(value, str):
            raise ValueError("Reference must contain text")
        content["independentReferenceTranslation"] = value
    return [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(content, ensure_ascii=False)}], schema


def validate_repair(field, response):
    result = _object(response)
    if set(result) != {"path", "before", "text", "reason", "evidence"}:
        raise ValueError("Malformed repair proposal")
    if result["path"] != field["path"] or result["before"] != field["currentJapanese"]:
        raise ValueError("Repair path/before does not match frozen current translation")
    if not isinstance(result["text"], str) or not result["text"].strip() or result["text"] == result["before"]:
        raise ValueError("Repair must be a nonempty actual correction; unresolved proposal remains held")
    if len(result["text"]) > 1600 or (isinstance(result["evidence"], str) and len(result["evidence"]) > 600):
        raise ValueError("Repair exceeds its declared schema limits")
    if result["reason"] not in REASONS:
        raise ValueError("Unknown repair reason")
    _quote(result["evidence"], field["sourceText"], "repair evidence")
    return deepcopy(result)


def build_adjudication(entry, field, proposal):
    # No detection verdict, repair explanation, confidence or model approval is
    # supplied. This is a fresh model cross-check, not independent final approval.
    if (not isinstance(proposal, dict) or proposal.get("path") != field["path"]
            or proposal.get("before") != field["currentJapanese"]
            or not isinstance(proposal.get("text"), str) or not proposal["text"].strip()):
        raise ValueError("Adjudication proposal does not match frozen field")
    schema = {"type": "object", "properties": {
        "path": {"type": "string", "enum": [field["path"]]},
        "decision": {"type": "string", "enum": ["accept", "reject", "uncertain"]},
        "sourceQuote": {"type": "string", "minLength": 1, "maxLength": 600},
        "beforeQuote": {"type": "string", "maxLength": 600},
        "afterQuote": {"type": "string", "minLength": 1, "maxLength": 600},
        "explanation": {"type": "string", "minLength": 1, "maxLength": 600}},
        "required": ["path", "decision", "sourceQuote", "beforeQuote", "afterQuote", "explanation"], "additionalProperties": False}
    system = (
        "Compare the authoritative source with an existing Japanese translation and a proposed replacement. "
        "Make a fresh source-based comparison; neither Japanese text is ground truth. "
        "Accept only if the replacement fixes an actual substantive error and preserves ALL source facts without introducing new errors. "
        "Reject style-only edits, wrong senses, omissions, invented details/readings, added age/gender/a.m./p.m., changed numerical ranges, "
        "negation, modality or grammar permissions. A female sibling is not a brother and a religious sister has a different sense. "
        "For col.N evaluate only the Japanese meaning; the program retains original English elsewhere. "
        "For tips/notes embedded English/IPA must remain literal while the surrounding explanation is Japanese. "
        "Use uncertain if evidence is insufficient. Quote exact substrings from source, before and after to support a brief factual explanation. "
        "This is a MODEL CROSS-CHECK, not an independent final semantic approval. Return only the required JSON."
    )
    content = {"entryId": entry["id"], "word": entry["word"], "path": field["path"],
               "sourceLanguage": field["sourceLanguage"], "sourceText": field["sourceText"],
               "before": field["currentJapanese"], "after": proposal["text"]}
    return [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(content, ensure_ascii=False)}], schema


def validate_adjudication(field, proposal, response):
    result = _object(response)
    required = {"path", "decision", "sourceQuote", "beforeQuote", "afterQuote", "explanation"}
    if (set(result) != required or result["path"] != field["path"]
            or not isinstance(result["decision"], str) or result["decision"] not in {"accept", "reject", "uncertain"}):
        raise ValueError("Malformed model cross-check")
    if (not isinstance(proposal, dict) or proposal.get("path") != field["path"]
            or proposal.get("before") != field["currentJapanese"]
            or not isinstance(proposal.get("text"), str) or not proposal["text"].strip()):
        raise ValueError("Model cross-check does not match the frozen proposal")
    _quote(result["sourceQuote"], field["sourceText"], "cross-check sourceQuote")
    _quote(result["beforeQuote"], field["currentJapanese"], "cross-check beforeQuote", bool(field["currentJapanese"].strip()))
    _quote(result["afterQuote"], proposal["text"], "cross-check afterQuote")
    if not isinstance(result["explanation"], str) or not result["explanation"].strip():
        raise ValueError("Model cross-check requires a factual explanation")
    if any(len(result[key]) > 600 for key in ["sourceQuote", "beforeQuote", "afterQuote", "explanation"]):
        raise ValueError("Model cross-check exceeds its declared schema limits")
    return deepcopy(result)
