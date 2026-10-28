#!/usr/bin/env python3
"""Offline coverage, provenance and semantic-review contract regressions.

These tests use a small temporary corpus and fake model responses. No model or
network is used; a passing test suite is not a translation-quality certificate.
"""
from __future__ import annotations

import copy
import hashlib
import io
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
import urllib.error


HERE = Path(__file__).resolve().parent


def load_module(filename, name):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def corpus_fixture(root):
    """The final public overlay differs from canonical, as real overrides do."""
    source = {
        "id": "library", "w": "library", "uk": "/ˈlaɪbrəri/", "us": "/ˈlaɪbreri/",
        "senses": [{"pos": "n.", "en": "a place where people read or borrow books", "zh": "图书馆"}],
        "ex": [{"en": "I borrowed 3 books from the library.", "zh": "我从图书馆借了3本书。"}],
        "col": ["public library｜公共图书馆"],
        "fam": ["librarian (n.)"], "syn": ["sticky", "粘稠"], "ant": [],
        "tip": "library指图书馆。", "note": "", "cefr": "A1", "topic": "education", "m": 0,
    }
    public = {
        "id": "library", "senses": ["図書館"],
        "ex": ["図書館で本を3冊借りました。"],
        "col": ["public library｜公共図書館"],
        "tip": "libraryは図書館を指します。", "note": "",
        "syn": ["sticky", "粘り気の強い"],
    }
    canonical = copy.deepcopy(public)
    canonical["senses"][0] = "基礎ファイルの旧訳"
    source_index = {
        "id": "word-atlas-open", "version": 1, "count": 1, "chunk": 100,
        "examples": 1, "illustrated": 0, "voiced": 0,
        "cefr": ["A1"], "topics": [["education", "教育"]],
        "words": [["library", "library", "n. 图书馆", "/ˈlaɪbrəri/", 0, 0, 0]],
    }
    index_hash = write_json(root / "public/atlas/index.json", source_index)
    chunk_hash = write_json(root / "public/atlas/entries/0.json", [source])
    write_json(root / "data/ja/entries/0.json", [canonical])
    write_json(root / "public/atlas/ja/entries/0.json", [public])
    write_json(root / "public/atlas/ja/index.json", {
        "version": 1, "language": "ja", "chunk": 100,
        "sourceIndexSha256": index_hash, "sourceChunksSha256": [chunk_hash],
        "words": {"library": "n. 図書館"},
        "translation": {"provider": "fixture"},
    })
    write_json(root / "scripts/atlas/ja-reviewed-0.json", [public])
    write_json(root / "scripts/atlas/ja-field-reviewed-0.json", {source["tip"]: public["tip"]})
    write_json(root / "data/word-atlas.json", [source])
    return source, public, canonical


def review_entry():
    return {
        "id": "library", "word": "library", "cefr": "A1", "topic": "education",
        "fields": [
            {"path": "senses.0", "sourceLanguage": "en", "sourceText": "a place where people read or borrow books", "currentJapanese": "図書館", "mode": "translate", "pos": "n."},
            {"path": "ex.0", "sourceLanguage": "en", "sourceText": "I borrowed 3 books from the library.", "currentJapanese": "図書館で本を3冊借りました。", "mode": "translate"},
            {"path": "note", "sourceLanguage": "zh-Hans", "sourceText": "", "currentJapanese": "", "mode": "empty"},
            {"path": "syn.0", "sourceLanguage": "en", "sourceText": "sticky", "currentJapanese": "sticky", "mode": "preserve"},
        ],
    }


def pass_assessment(field):
    return {"path": field["path"], "status": "pass", "categories": [],
            "sourceQuote": field["sourceText"], "targetQuote": field["currentJapanese"],
            "explanation": "The Japanese preserves the source meaning."}


class FrozenCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = load_module("ja_review_core.py", "semantic_core_tests")

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        self.source, self.public, self.canonical = corpus_fixture(self.root)

    def test_snapshot_reviews_public_final_overlay_not_stale_canonical(self):
        snapshot = self.core.build_snapshot(self.root)
        entry = snapshot["entries"][0]
        fields = {f["path"]: f for f in entry["fields"]}
        self.assertEqual(fields["senses.0"]["currentJapanese"], self.public["senses"][0])
        self.assertNotEqual(fields["senses.0"]["currentJapanese"], self.canonical["senses"][0])
        self.assertEqual(snapshot["manifest"]["entryCount"], 1)

    def test_chinese_related_word_empty_note_and_english_integrity_are_covered(self):
        entry = self.core.build_snapshot(self.root)["entries"][0]
        fields = {f["path"]: f for f in entry["fields"]}
        self.assertEqual(fields["syn.1"]["mode"], "translate")
        self.assertEqual(fields["syn.1"]["sourceText"], "粘稠")
        self.assertEqual(fields["syn.1"]["currentJapanese"], "粘り気の強い")
        self.assertEqual(fields["syn.0"]["mode"], "preserve")
        self.assertEqual(fields["note"]["mode"], "empty")
        self.assertEqual(fields["note"]["currentJapanese"], "")

    def test_english_sources_are_authoritative_and_collocation_target_is_japanese_only(self):
        fields = {f["path"]: f for f in self.core.build_snapshot(self.root)["entries"][0]["fields"]}
        self.assertEqual(fields["ex.0"]["sourceLanguage"], "en")
        self.assertEqual(fields["ex.0"]["sourceText"], self.source["ex"][0]["en"])
        self.assertEqual(fields["col.0"]["sourceText"], "public library")
        self.assertEqual(fields["col.0"]["currentJapanese"], "公共図書館")

    def test_empty_note_and_english_related_word_have_explicit_integrity_verdicts(self):
        entry = review_entry()
        verdicts = {r["path"]: r for r in self.core.integrity_assessments(entry)}
        self.assertEqual(set(verdicts), {"note", "syn.0"})
        self.assertTrue(all(r["status"] == "pass" for r in verdicts.values()))
        entry["fields"][2]["currentJapanese"] = "原文にない説明を追加しました。"
        entry["fields"][3]["currentJapanese"] = "changed English synonym"
        verdicts = {r["path"]: r for r in self.core.integrity_assessments(entry)}
        self.assertEqual(verdicts["note"]["status"], "error")
        self.assertEqual(verdicts["syn.0"]["status"], "error")

    def test_snapshot_tracks_source_final_canonical_and_override_files(self):
        files = self.core.build_snapshot(self.root)["manifest"]["files"]
        for rel in ("public/atlas/index.json", "public/atlas/entries/0.json", "public/atlas/ja/index.json",
                    "public/atlas/ja/entries/0.json", "data/ja/entries/0.json",
                    "scripts/atlas/ja-reviewed-0.json", "scripts/atlas/ja-field-reviewed-0.json"):
            with self.subTest(rel=rel):
                self.assertIn(rel, files)
                self.assertEqual(files[rel], hashlib.sha256((self.root / rel).read_bytes()).hexdigest())

    def test_correction_write_location_respects_actual_override_precedence(self):
        entry = self.core.build_snapshot(self.root)["entries"][0]
        fields = {f["path"]: f for f in entry["fields"]}
        self.assertEqual(fields["senses.0"]["writeLocation"]["file"], "scripts/atlas/ja-reviewed-0.json")
        self.assertEqual(fields["tip"]["writeLocation"]["kind"], "entry-array")
        (self.root / "scripts/atlas/ja-reviewed-0.json").unlink()
        entry = self.core.build_snapshot(self.root)["entries"][0]
        fields = {f["path"]: f for f in entry["fields"]}
        self.assertEqual(fields["tip"]["writeLocation"]["kind"], "field-map")
        self.assertEqual(fields["tip"]["writeLocation"]["file"], "scripts/atlas/ja-field-reviewed-0.json")
        self.assertEqual(fields["senses.0"]["writeLocation"]["file"], "data/ja/entries/0.json")

    def test_new_override_file_is_detected_as_source_drift(self):
        snapshot = self.core.build_snapshot(self.root)
        write_json(self.root / "scripts/atlas/ja-reviewed-1.json", [])
        self.assertIn("scripts/atlas/ja-reviewed-1.json", self.core.source_drift(self.root, snapshot))

    def test_prepare_and_load_are_idempotent_and_never_write_formal_corpus(self):
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        run = Path(self.temporary.name) / "review-run"
        first = self.core.prepare_run(self.root, run)
        second = self.core.prepare_run(self.root, run)
        loaded = self.core.load_snapshot(run)
        self.assertEqual(first, second)
        self.assertEqual(first, loaded)
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_output_cannot_be_inside_formal_data_or_public(self):
        for run in [self.root / "data/review", self.root / "public/review"]:
            with self.subTest(run=run):
                with self.assertRaises(ValueError):
                    self.core.prepare_run(self.root, run)

    def test_changed_override_invalidates_existing_frozen_run(self):
        run = Path(self.temporary.name) / "review-run"
        self.core.prepare_run(self.root, run)
        override = self.root / "scripts/atlas/ja-field-reviewed-0.json"
        write_json(override, {self.source["tip"]: "変更された翻訳です。"})
        with self.assertRaises(ValueError):
            self.core.prepare_run(self.root, run)

    def test_tampered_snapshot_is_not_silently_resumed(self):
        run = Path(self.temporary.name) / "review-run"
        self.core.prepare_run(self.root, run)
        path = run / "snapshot.json"
        content = json.loads(path.read_text())
        content["entries"][0]["fields"][0]["currentJapanese"] = "改ざんされた訳"
        write_json(path, content)
        with self.assertRaises(ValueError):
            self.core.load_snapshot(run)


class DetectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models = load_module("ja_review_models.py", "semantic_models_tests")

    def setUp(self):
        self.entry = review_entry()
        self.semantic_fields = [f for f in self.entry["fields"] if f["mode"] == "translate"]
        self.response = {"assessments": [pass_assessment(f) for f in self.semantic_fields]}

    def test_each_translated_field_has_an_explicit_verdict(self):
        rows = self.models.validate_detection(self.entry, self.response)
        self.assertEqual({r["path"] for r in rows}, {f["path"] for f in self.semantic_fields})
        self.assertEqual(len(rows), len(self.semantic_fields))

    def test_partial_duplicate_unknown_and_invalid_verdicts_are_rejected(self):
        one = self.response["assessments"][0]
        bad = [
            {"assessments": [one]},
            {"assessments": [one, one]},
            {"assessments": [{**one, "path": "unknown"}, self.response["assessments"][1]]},
            {"assessments": [{**one, "status": "approved"}, self.response["assessments"][1]]},
        ]
        for response in bad:
            with self.subTest(response=response):
                with self.assertRaises(ValueError):
                    self.models.validate_detection(self.entry, response)

    def test_evidence_must_point_to_the_same_source_and_translation(self):
        for key in ["sourceQuote", "targetQuote"]:
            response = copy.deepcopy(self.response)
            response["assessments"][0][key] = "a quote that does not occur in this field"
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    self.models.validate_detection(self.entry, response)

    def test_unknown_categories_extra_keys_and_empty_explanation_are_rejected(self):
        variants = []
        for change in [{"categories": ["style_preference"]}, {"status": "pass", "categories": ["wrong_meaning"]},
                       {"status": "error", "categories": []}, {"explanation": ""}, {"extra": True}]:
            response = copy.deepcopy(self.response)
            response["assessments"][0].update(change)
            variants.append(response)
        variants.append({**self.response, "approved": True})
        for response in variants:
            with self.subTest(response=response):
                with self.assertRaises(ValueError):
                    self.models.validate_detection(self.entry, response)

    def test_error_and_uncertain_are_not_silently_returned_as_pass(self):
        for status in ["error", "uncertain", "unavailable"]:
            response = copy.deepcopy(self.response)
            response["assessments"][0]["status"] = status
            response["assessments"][0]["categories"] = ["wrong_meaning"] if status != "unavailable" else []
            rows = self.models.validate_detection(self.entry, response)
            self.assertEqual(rows[0]["status"], status)

    def test_independent_reference_prompt_contains_no_existing_japanese(self):
        field = copy.deepcopy(self.semantic_fields[0])
        field["currentJapanese"] = "秘密の既存訳は参考翻訳に見せない"
        messages = self.models.build_reference(field)
        rendered = json.dumps(messages, ensure_ascii=False)
        self.assertIn(field["sourceText"], rendered)
        self.assertNotIn(field["currentJapanese"], rendered)

    def test_detection_prompt_keeps_facts_and_current_translation_in_separate_fields(self):
        messages, schema = self.models.build_detection(self.entry)
        rendered = json.dumps(messages, ensure_ascii=False)
        for field in self.semantic_fields:
            self.assertIn(field["sourceText"], rendered)
            self.assertIn(field["currentJapanese"], rendered)
        self.assertIn("assessments", schema["properties"])

    def test_duplicate_categories_are_losslessly_normalized_without_changing_raw_verdict(self):
        raw = copy.deepcopy(self.response)
        raw["assessments"][0].update({"status": "error", "categories": ["wrong_meaning", "wrong_meaning"]})
        untouched = copy.deepcopy(raw)
        parsed = self.models.validate_detection(self.entry, raw)
        self.assertEqual(parsed[0]["categories"], ["wrong_meaning"])
        self.assertTrue(parsed[0]["formatNormalizations"])
        self.assertEqual(raw, untouched)

    def test_partial_parser_keeps_valid_fields_and_holds_only_bad_quote_field(self):
        raw = copy.deepcopy(self.response)
        raw["assessments"][1]["sourceQuote"] = "not actually in this source"
        parsed = self.models.parse_detection(self.entry, raw)
        by_path = {r["path"]: r for r in parsed["assessments"]}
        self.assertEqual(by_path["senses.0"]["status"], "pass")
        self.assertEqual(by_path["ex.0"]["status"], "unavailable")
        self.assertEqual(by_path["ex.0"]["method"], "program_validation_hold")
        self.assertEqual(by_path["ex.0"]["sourceQuote"], "")
        self.assertTrue(parsed["fieldValidationErrors"])

    def test_partial_parser_never_chooses_one_of_duplicate_field_verdicts(self):
        raw = copy.deepcopy(self.response)
        raw["assessments"].append(copy.deepcopy(raw["assessments"][0]))
        parsed = self.models.parse_detection(self.entry, raw)
        by_path = {r["path"]: r for r in parsed["assessments"]}
        self.assertEqual(by_path["senses.0"]["status"], "unavailable")
        self.assertEqual(by_path["ex.0"]["status"], "pass")
        self.assertEqual(len(by_path), len(self.semantic_fields))

    def test_partial_parser_reports_unknown_fields_and_holds_missing_or_malformed_output(self):
        raw = copy.deepcopy(self.response)
        raw["assessments"].append({**raw["assessments"][0], "path": "unknown.0"})
        parsed = self.models.parse_detection(self.entry, raw)
        self.assertTrue(parsed["structuralErrors"])
        self.assertEqual({r["path"] for r in parsed["assessments"]}, {f["path"] for f in self.semantic_fields})
        for response in ["{not complete JSON", {"assessments": []}]:
            with self.subTest(response=response):
                parsed = self.models.parse_detection(self.entry, response)
                self.assertTrue(all(r["status"] == "unavailable" for r in parsed["assessments"]))
                self.assertTrue(all(r["sourceQuote"] == r["targetQuote"] == "" for r in parsed["assessments"]))


class AttemptHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = load_module("ja_review_core.py", "semantic_history_tests")

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.run = Path(self.temporary.name) / "run"
        self.protocol = {"version": 1, "modelDigest": "fixture-digest", "snapshotSha256": "fixture-source"}
        self.store = self.core.AttemptStore(self.run, "detect", self.protocol)

    def test_terminal_failure_is_checkpointed_and_not_automatically_retried(self):
        first = self.store.begin("library")
        self.store.finish("library", {**first, "status": "error", "error": "timeout"})
        self.assertIsNone(self.store.begin("library"))
        self.assertEqual(self.store.read_latest("library")["status"], "error")

    def test_completed_uncertain_result_is_not_regenerated_on_resume(self):
        first = self.store.begin("library")
        result = {"assessments": [{"path": "senses.0", "status": "uncertain"}]}
        self.store.finish("library", {**first, "status": "complete", "result": result})
        self.assertIsNone(self.store.begin("library"))
        self.assertEqual(self.store.read_latest("library")["result"], result)

    def test_explicit_retry_keeps_previous_terminal_attempt_intact(self):
        first = self.store.begin("library")
        self.store.finish("library", {**first, "status": "error", "error": "first failure"})
        old_path = self.run / "records/detect/library/attempt-000001.json"
        old_bytes = old_path.read_bytes()
        second = self.store.begin("library", retry=True)
        self.assertNotEqual(first["attempt"], second["attempt"])
        self.store.finish("library", {**second, "status": "complete", "result": {"assessments": []}})
        self.assertEqual(old_path.read_bytes(), old_bytes)
        self.assertTrue((self.run / "records/detect/library/attempt-000002.json").exists())

    def test_interrupted_running_attempt_requires_explicit_retry(self):
        self.store.begin("library")
        self.assertIsNone(self.store.begin("library"))
        self.assertEqual(self.store.read_latest("library")["status"], "interrupted")
        self.assertIsNotNone(self.store.begin("library", retry=True))

    def test_changed_protocol_cannot_mix_into_an_existing_stage(self):
        self.store.begin("library")
        with self.assertRaises(ValueError):
            changed = self.core.AttemptStore(self.run, "detect", {**self.protocol, "modelDigest": "another-model"})
            changed.begin("library")

    def test_unknown_id_cannot_escape_the_attempt_directory(self):
        for word in ["../library", "library/other", "/tmp/library"]:
            with self.subTest(word=word):
                with self.assertRaises(ValueError):
                    self.store.begin(word)

    def test_finish_cannot_replace_another_entry_or_protocol_attempt(self):
        first = self.store.begin("library")
        for changed in [{**first, "id": "other", "status": "complete"},
                        {**first, "attempt": 999, "status": "complete"}]:
            with self.subTest(changed=changed):
                with self.assertRaises(ValueError):
                    self.store.finish("library", changed)

    def test_terminal_attempt_cannot_be_overwritten_after_completion(self):
        first = self.store.begin("library")
        self.store.finish("library", {**first, "status": "error", "error": "original evidence"})
        with self.assertRaises(ValueError):
            self.store.finish("library", {**first, "status": "complete", "result": {}})


class RepairAndCrossCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models = load_module("ja_review_models.py", "semantic_repair_tests")

    def setUp(self):
        self.entry = review_entry()
        self.field = copy.deepcopy(self.entry["fields"][1])
        self.field["currentJapanese"] = "図書館で本を2冊借りました。"
        self.proposal = {"path": "ex.0", "before": self.field["currentJapanese"],
                         "text": "図書館で本を3冊借りました。", "reason": "quantity", "evidence": "3 books"}
        self.crosscheck = {"path": "ex.0", "decision": "accept", "sourceQuote": "3 books",
                           "beforeQuote": "2冊", "afterQuote": "3冊", "explanation": "The proposed number matches the source."}

    def test_repair_must_match_frozen_before_and_source_evidence(self):
        self.assertEqual(self.models.validate_repair(self.field, self.proposal), self.proposal)
        for change in [{"before": self.field["currentJapanese"] + " "}, {"path": "ex.1"},
                       {"evidence": "three books"}, {"text": self.field["currentJapanese"]}, {"text": ""},
                       {"reason": "style_preference"}]:
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    self.models.validate_repair(self.field, {**self.proposal, **change})

    def test_model_crosscheck_quotes_are_bound_to_their_exact_before_after_source(self):
        self.assertEqual(self.models.validate_adjudication(self.field, self.proposal, self.crosscheck), self.crosscheck)
        for key in ["sourceQuote", "beforeQuote", "afterQuote"]:
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    self.models.validate_adjudication(self.field, self.proposal, {**self.crosscheck, key: "not present"})

    def test_fresh_crosscheck_does_not_receive_the_prior_verdict_or_justification(self):
        proposal = {**self.proposal, "priorApproval": True, "priorExplanation": "TRUST_PRIOR_REVIEW_SENTINEL"}
        messages, schema = self.models.build_adjudication(self.entry, self.field, proposal)
        content = json.loads(messages[1]["content"])
        self.assertNotIn("priorApproval", content)
        self.assertNotIn("TRUST_PRIOR_REVIEW_SENTINEL", json.dumps(messages))
        self.assertNotIn("evidence", content)
        self.assertNotIn("reason", content)
        self.assertEqual(content["before"], self.field["currentJapanese"])
        self.assertEqual(content["after"], self.proposal["text"])
        self.assertIn("decision", schema["properties"])

    def test_model_crosscheck_cannot_accept_a_different_frozen_proposal(self):
        with self.assertRaises(ValueError):
            self.models.validate_adjudication(self.field, {**self.proposal, "before": "another draft"}, self.crosscheck)

    def test_repair_schema_and_parser_share_the_backend_supported_text_limit(self):
        assessment = {"path": "ex.0", "status": "error"}
        _, schema = self.models.build_repair(self.entry, self.field, assessment)
        self.assertEqual(schema["properties"]["text"]["maxLength"], 1600)
        with self.assertRaises(ValueError):
            self.models.validate_repair(self.field, {**self.proposal, "text": "あ" * 1601})


class LocalModelTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models = load_module("ja_review_models.py", "semantic_transport_tests")

    def response_stream(self, text="{\"assessments\":[]}", reason="stop", final=True):
        messages = [{"message": {"thinking": "PRIVATE_THINKING_SENTINEL", "content": text}, "done": False}]
        if final:
            messages.append({"message": {}, "done": True, "done_reason": reason, "eval_count": 5})
        return io.BytesIO(b"".join(json.dumps(m).encode() + b"\n" for m in messages))

    def test_client_rejects_remote_authenticated_and_non_ollama_base_urls(self):
        authenticated = "http://" + "user:pass" + "@localhost:11434"
        for url in ["https://example.com", "http://localhost:11434/v1", authenticated, "file:///tmp/model"]:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    self.models.LocalClient(url, "qwen-test", {"num_ctx": 1024})

    def test_actual_request_and_output_are_captured_without_private_thinking(self):
        options = {"num_ctx": 2048, "num_predict": 200, "temperature": 0.1}
        client = self.models.LocalClient("http://127.0.0.1:11434", "qwen-test", options, think=False)
        with mock.patch.object(self.models.urllib.request, "urlopen", return_value=self.response_stream()) as opened:
            result = client.chat([{"role": "user", "content": "fixture"}], schema={"type": "object"})
        sent = json.loads(opened.call_args.args[0].data)
        self.assertEqual(sent, result["request"])
        self.assertEqual(sent["options"], options)
        self.assertIs(sent["think"], False)
        self.assertIn("assessments", result["text"])
        self.assertEqual(result["metrics"]["thinking_chars"], len("PRIVATE_THINKING_SENTINEL"))
        self.assertNotIn("PRIVATE_THINKING_SENTINEL", json.dumps(result))

    def test_truncated_or_missing_completion_is_preserved_as_a_failed_attempt(self):
        client = self.models.LocalClient("http://127.0.0.1:11434", "qwen-test", {"num_predict": 1})
        for stream in [self.response_stream(text="partial output", reason="length"), self.response_stream(text="partial output", final=False)]:
            with self.subTest(stream=stream):
                with mock.patch.object(self.models.urllib.request, "urlopen", return_value=stream):
                    with self.assertRaises(self.models.ModelCallError) as caught:
                        client.chat([{"role": "user", "content": "fixture"}])
                self.assertEqual(caught.exception.result["text"], "partial output")
                self.assertIn("error", caught.exception.result)
                self.assertNotIn("PRIVATE_THINKING_SENTINEL", json.dumps(caught.exception.result))

    def test_inline_private_thinking_is_redacted_and_held_even_across_chunks(self):
        client = self.models.LocalClient("http://127.0.0.1:11434", "qwen-test", {"num_predict": 200})
        for fragments in [["<think>PRIVATE_INLINE_SENTINEL</think>public output"],
                          ["<thi", "nk>PRIVATE_INLINE_SENTINEL</th", "ink>public output"],
                          ["<think>PRIVATE_INLINE_SENTINEL"]]:
            lines = [{"message": {"content": text}, "done": False} for text in fragments]
            lines.append({"message": {}, "done": True, "done_reason": "stop"})
            stream = io.BytesIO(b"".join(json.dumps(line).encode() + b"\n" for line in lines))
            with self.subTest(fragments=fragments):
                with mock.patch.object(self.models.urllib.request, "urlopen", return_value=stream):
                    with self.assertRaises(self.models.ModelCallError) as caught:
                        client.chat([{"role": "user", "content": "fixture"}])
                self.assertNotIn("PRIVATE_INLINE_SENTINEL", json.dumps(caught.exception.result))

    def test_translate_and_qwen_profiles_remain_independently_configured(self):
        translation = self.models.profile_for("translate")
        detection = self.models.profile_for("detect", "official-instruct")
        self.assertNotEqual(translation["model"], detection["model"])
        self.assertNotEqual(translation["options"]["top_k"], detection["options"]["top_k"])
        translation["options"]["top_k"] = 999
        self.assertNotEqual(self.models.profile_for("translate")["options"]["top_k"], 999)
        with self.assertRaises(ValueError):
            self.models.profile_for("translate", "official-instruct")

    def test_other_resident_model_is_not_silently_unloaded(self):
        with mock.patch.object(self.models, "_resident", return_value=["someone-elses-model"]), mock.patch.object(self.models, "_request") as request:
            with self.assertRaises(ValueError):
                self.models.ensure_single_model("http://127.0.0.1:11434", "qwen-test")
            request.assert_not_called()

    def test_http_error_retains_bounded_backend_diagnostic_without_private_content(self):
        client = self.models.LocalClient("http://127.0.0.1:11434", "qwen-test", {"num_predict": 200})
        body = json.dumps({"error": {"message": "Bad schema <think>HTTP_PRIVATE_SENTINEL</think>" + "x" * 2500},
                           "thinking": "EXTRA_PRIVATE_SENTINEL"}).encode()
        error = urllib.error.HTTPError("http://127.0.0.1:11434/api/chat", 400, "Bad Request", {}, io.BytesIO(body))
        with mock.patch.object(self.models.urllib.request, "urlopen", side_effect=error):
            with self.assertRaises(self.models.ModelCallError) as caught:
                client.chat([{"role": "user", "content": "fixture"}])
        result = caught.exception.result
        self.assertEqual(result["httpStatus"], 400)
        self.assertLessEqual(len(result["backendError"]), 2000)
        self.assertTrue(result["backendErrorTruncated"])
        self.assertNotIn("HTTP_PRIVATE_SENTINEL", json.dumps(result))
        self.assertNotIn("EXTRA_PRIVATE_SENTINEL", json.dumps(result))

    def test_ndjson_backend_error_drops_inline_and_nested_private_fields_before_checkpoint_or_stderr(self):
        client = self.models.LocalClient("http://127.0.0.1:11434", "qwen-test", {"num_predict": 10})
        errors = ["Backend failed <think>SYNTHETIC_PRIVATE_SENTINEL</think>",
                  {"message": "Backend failed", "thinking": "SYNTHETIC_PRIVATE_SENTINEL"}]
        for backend in errors:
            stream = io.BytesIO((json.dumps({"error": backend}) + "\n").encode())
            with self.subTest(backend=backend):
                with mock.patch.object(self.models.urllib.request, "urlopen", return_value=stream):
                    with self.assertRaises(self.models.ModelCallError) as caught:
                        client.chat([{"role": "user", "content": "synthetic fixture"}])
                self.assertIn("Backend failed", str(caught.exception))
                self.assertNotIn("SYNTHETIC_PRIVATE_SENTINEL", str(caught.exception))
                self.assertNotIn("SYNTHETIC_PRIVATE_SENTINEL", json.dumps(caught.exception.result))
                self.assertIsNone(caught.exception.__cause__)
                self.assertTrue(caught.exception.__suppress_context__)

    def test_all_model_call_error_messages_are_bounded_and_private_json_diagnostics_are_omitted(self):
        result = {"text": "", "metrics": {}, "request": {}}
        messages = ["Backend <think>SYNTHETIC_PRIVATE_SENTINEL</think>" + "x" * 3000,
                    json.dumps({"message": "failure", "thinking": "SYNTHETIC_PRIVATE_SENTINEL"})]
        for message in messages:
            with self.subTest(kind="inline" if "<think>" in message else "quoted-field"):
                error = self.models.ModelCallError(message, result)
                self.assertLessEqual(len(str(error)), 2200)
                self.assertNotIn("SYNTHETIC_PRIVATE_SENTINEL", str(error))
                self.assertNotIn("SYNTHETIC_PRIVATE_SENTINEL", json.dumps(error.result))


class Gemma4TransportCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models = load_module("ja_review_models.py", "gemma4_transport_tests")

    def stream(self, fragments, thinking="", reason="stop"):
        rows = [{"message": {"content": fragment}, "done": False} for fragment in fragments]
        if thinking:
            rows.append({"message": {"thinking": thinking}, "done": False})
        rows.append({"message": {}, "done": True, "done_reason": reason})
        return io.BytesIO(b"".join(json.dumps(row).encode() + b"\n" for row in rows))

    def client(self, name="gemma4:12b-it-q8_0"):
        return self.models.LocalClient("http://127.0.0.1:11434", name,
                                       self.models.profile_for("detect")["options"], think=False)

    def test_gemma4_explicit_false_preserves_task_input_and_legacy_model_requests(self):
        messages = [{"role": "system", "content": "unchanged task"},
                    {"role": "user", "content": "unchanged source"}]
        schema = {"type": "object"}
        for name, expected_think in [("gemma4:12b-it-q8_0", False),
                                     ("namespace/gemma4:12b-it-q8_0", False),
                                     ("qwen3.5:9b-q8_0", False),
                                     ("mistral-small3.2:24b-instruct-2506-q4_K_M", None),
                                     ("translategemma:12b-it-q8_0", None)]:
            with self.subTest(model=name):
                client = self.client(name)
                with mock.patch.object(self.models.urllib.request, "urlopen",
                                       return_value=self.stream(['{"assessments":[]}'])) as opened:
                    result = client.chat(messages, schema)
                sent = json.loads(opened.call_args.args[0].data)
                expected = {"model": name, "messages": messages, "stream": True,
                            "keep_alive": "5m", "options": client.options, "format": schema}
                if expected_think is not None:
                    expected["think"] = expected_think
                self.assertEqual(sent, expected)
                self.assertEqual(result["request"], expected)

    def test_complete_empty_thought_prefix_is_only_a_recorded_normalization(self):
        public = '{"assessments":[]}'
        for fragments in [["<|channel>thought\n<channel|>" + public],
                          [" \n<|cha", "nnel>thought", "\n  \t<chan", "nel|>", public]]:
            with self.subTest(fragments=fragments):
                with mock.patch.object(self.models.urllib.request, "urlopen",
                                       return_value=self.stream(fragments)):
                    result = self.client().chat([{"role": "user", "content": "fixture"}])
                self.assertEqual(result["text"].strip(), public)
                self.assertEqual(result["metrics"]["inline_thinking_chars"], 0)
                self.assertEqual(result["metrics"]["empty_thought_prefixes_removed"], 1)

    def test_nonempty_unknown_and_truncated_native_channels_are_redacted_and_held(self):
        sentinel = "PRIVATE_GEMMA_SENTINEL"
        public = '{"assessments":[]}'
        variants = [["<|channel>thought\n" + sentinel + "<channel|>" + public],
                    ["<|chan", "nel>thought\n" + sentinel, "<channel|>" + public],
                    ["<|channel>thought\n" + sentinel],
                    ["<|channel>analysis\n" + sentinel + "<channel|>" + public],
                    [sentinel + "<channel|>" + public],
                    [sentinel + "<channel|"],
                    ["<|channel>thought\n<channel|><|channel>thought\n" + sentinel]]
        for fragments in variants:
            with self.subTest(fragments=fragments):
                with mock.patch.object(self.models.urllib.request, "urlopen",
                                       return_value=self.stream(fragments)):
                    with self.assertRaises(self.models.ModelCallError) as caught:
                        self.client().chat([{"role": "user", "content": "fixture"}])
                self.assertNotIn(sentinel, str(caught.exception))
                self.assertNotIn(sentinel, json.dumps(caught.exception.result))
                self.assertGreater(caught.exception.result["metrics"]["inline_thinking_chars"], 0)

    def test_partial_openers_and_nonprefix_empty_blocks_are_not_promoted(self):
        for text in ["<|chan", "<|channel", '<|channel>thought<channel|>{"assessments":[]}',
                     '{"assessments":[]}<|channel>thought\n<channel|>']:
            with self.subTest(text=text):
                with mock.patch.object(self.models.urllib.request, "urlopen", return_value=self.stream([text])):
                    with self.assertRaises(self.models.ModelCallError):
                        self.client().chat([{"role": "user", "content": "fixture"}])

    def test_native_markers_inside_valid_json_are_held_instead_of_silently_accepted(self):
        # A quoted literal is not the documented leading protocol prefix.
        public = json.dumps({"literal": "<|channel>thought\n<channel|>"})
        with mock.patch.object(self.models.urllib.request, "urlopen", return_value=self.stream([public])):
            with self.assertRaises(self.models.ModelCallError) as caught:
                self.client().chat([{"role": "user", "content": "fixture"}])
        self.assertGreater(caught.exception.result["metrics"]["inline_thinking_chars"], 0)
        self.assertNotIn("empty_thought_prefixes_removed", caught.exception.result["metrics"])

    def test_separated_thinking_while_disabled_is_counted_redacted_and_held(self):
        sentinel = "PRIVATE_SEPARATE_GEMMA_SENTINEL"
        with mock.patch.object(self.models.urllib.request, "urlopen",
                               return_value=self.stream(['{"assessments":[]}'], thinking=sentinel)):
            with self.assertRaises(self.models.ModelCallError) as caught:
                self.client().chat([{"role": "user", "content": "fixture"}])
        self.assertEqual(caught.exception.result["metrics"]["thinking_chars"], len(sentinel))
        self.assertNotIn(sentinel, json.dumps(caught.exception.result))
        self.assertNotIn(sentinel, str(caught.exception))

    def test_empty_prefix_cannot_mask_generation_truncation(self):
        with mock.patch.object(self.models.urllib.request, "urlopen",
                               return_value=self.stream(['<|channel>thought\n<channel|>{"assessments":[]'],
                                                        reason="length")):
            with self.assertRaises(self.models.ModelCallError) as caught:
                self.client().chat([{"role": "user", "content": "fixture"}])
        self.assertEqual(caught.exception.result["metrics"]["done_reason"], "length")

    def test_http_and_ndjson_native_thinking_errors_never_retain_private_text(self):
        sentinel = "PRIVATE_GEMMA_ERROR_SENTINEL"
        backend = "Backend failed <|channel>thought\n" + sentinel + "<channel|>"
        body = json.dumps({"error": {"message": backend}}).encode()
        error = urllib.error.HTTPError("http://127.0.0.1:11434/api/chat", 400, "Bad Request", {}, io.BytesIO(body))
        with mock.patch.object(self.models.urllib.request, "urlopen", side_effect=error):
            with self.assertRaises(self.models.ModelCallError) as caught:
                self.client().chat([{"role": "user", "content": "fixture"}])
        self.assertNotIn(sentinel, json.dumps(caught.exception.result))
        self.assertNotIn(sentinel, str(caught.exception))
        stream = io.BytesIO((json.dumps({"error": {"message": backend}}) + "\n").encode())
        with mock.patch.object(self.models.urllib.request, "urlopen", return_value=stream):
            with self.assertRaises(self.models.ModelCallError) as caught:
                self.client().chat([{"role": "user", "content": "fixture"}])
        self.assertNotIn(sentinel, json.dumps(caught.exception.result))
        self.assertNotIn(sentinel, str(caught.exception))

    def test_direct_model_error_redacts_native_channels_in_message_and_output(self):
        sentinel = "PRIVATE_GEMMA_DIRECT_SENTINEL"
        native = "<|channel>thought\n" + sentinel + "<channel|>"
        error = self.models.ModelCallError("failure " + native, {"text": native + "public", "request": {}})
        self.assertEqual(error.output, "public")
        self.assertNotIn(sentinel, str(error))
        self.assertNotIn(sentinel, json.dumps(error.result))


class CalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calibration = load_module("calibrate-ja-review.py", "semantic_calibration_tests")

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        entry = review_entry()
        self.selection = {"schemaVersion": 1, "entryIds": [entry["id"]], "entries": [entry]}
        self.gold = {
            "schemaVersion": 1, "selectionSha256": self.calibration.digest(self.selection),
            "reviewer": {"name": "independent fixture reviewer", "method": "source-grounded manual fixture", "independent": True},
            "fields": [
                {"entryId": "library", "path": "senses.0", "expectedStatus": "pass", "severity": "minor", "categories": [], "note": "Valid fixture gloss."},
                {"entryId": "library", "path": "ex.0", "expectedStatus": "error", "severity": "major", "categories": ["wrong_meaning"], "note": "Controlled test label."},
            ],
        }

    def record(self, assessments, status="complete"):
        path = self.root / "records/detect/library/attempt-001.json"
        write_json(path, {"id": "library", "attempt": 1, "status": status,
                          "result": {"assessments": assessments}})

    def test_selection_is_deterministic_and_excludes_used_development_ids(self):
        entries = [{"id": f"word-{i}", "cefr": ["A1", "B1", "C1"][i % 3], "topic": ["daily", "science"][i % 2],
                    "fields": [copy.deepcopy(review_entry()["fields"][0])]} for i in range(30)]
        excluded = {"word-0", "word-1", "word-2"}
        first = self.calibration.select_entries(entries, count=12, seed=42, excluded_ids=excluded)
        second = self.calibration.select_entries(entries, count=12, seed=42, excluded_ids=excluded)
        self.assertEqual(first, second)
        self.assertEqual(len({e["id"] for e in first}), 12)
        self.assertFalse(excluded & {e["id"] for e in first})

    def test_unlabeled_gold_cannot_be_reported_as_passed(self):
        self.gold["fields"][0]["expectedStatus"] = None
        report = self.calibration.evaluate(self.selection, self.gold, self.root)
        self.assertEqual(report["status"], "incomplete")
        self.assertIs(report["passed"], False)
        self.assertIsNone(report.get("metrics"))

    def test_absent_independent_reviewer_blocks_calibration_approval(self):
        self.gold["reviewer"]["independent"] = False
        report = self.calibration.evaluate(self.selection, self.gold, self.root)
        self.assertIs(report["passed"], False)
        self.assertEqual(report["status"], "incomplete")

    def test_gold_must_exactly_cover_the_frozen_translation_fields(self):
        for fields in [self.gold["fields"][:1], self.gold["fields"] + [self.gold["fields"][0]]]:
            with self.subTest(fields=fields):
                changed = {**self.gold, "fields": fields}
                report = self.calibration.evaluate(self.selection, changed, self.root)
                self.assertEqual(report["status"], "incomplete")
                self.assertIs(report["passed"], False)

    def test_uncertain_unavailable_and_missing_results_are_not_counted_as_pass(self):
        for assessments in [
            [{"path": "senses.0", "status": "uncertain"}, {"path": "ex.0", "status": "unavailable"}],
            [],
        ]:
            with self.subTest(assessments=assessments):
                self.record(assessments)
                report = self.calibration.evaluate(self.selection, self.gold, self.root)
                self.assertIsNot(report.get("passed"), True)
                counts = report["counts"]
                self.assertEqual(counts["correctPasses"], 0)
                self.assertEqual(counts["errorsApprovedAsPass"], 0)
                self.assertEqual(report["metrics"]["conclusiveCoverage"], 0)
                if assessments:
                    self.assertEqual(counts["uncertain"], 1)
                    self.assertEqual(counts["unavailable"], 1)
                    self.assertEqual(counts["missing"], 0)
                else:
                    self.assertEqual(counts["missing"], 2)

    def test_error_detection_false_approval_and_false_alarm_are_distinct_metrics(self):
        self.record([{"path": "senses.0", "status": "error"}, {"path": "ex.0", "status": "pass"}])
        report = self.calibration.evaluate(self.selection, self.gold, self.root)
        self.assertEqual(report["counts"]["falseErrorReports"], 1)
        self.assertEqual(report["counts"]["errorsApprovedAsPass"], 1)
        self.assertEqual(report["metrics"]["errorDetectionRecall"], 0)
        self.assertEqual(report["metrics"]["falsePositiveRate"], 1)
        self.assertEqual(report["metrics"]["errorsApprovedAsPassRate"], 1)
        self.assertEqual(report["metrics"]["residualErrorAmongPasses"], 1)
        self.assertIsNot(report["passed"], True)

    def test_failed_latest_attempt_is_not_replaced_by_an_older_success(self):
        self.record([{"path": "senses.0", "status": "pass"}, {"path": "ex.0", "status": "error"}])
        write_json(self.root / "records/detect/library/attempt-002.json",
                   {"id": "library", "attempt": 2, "status": "error", "error": "token budget exhausted"})
        report = self.calibration.evaluate(self.selection, self.gold, self.root)
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["counts"]["missing"], 2)
        self.assertEqual(report["counts"]["trueErrorDetections"], 0)

    def test_selection_hash_mismatch_never_uses_stale_gold(self):
        changed = {**self.gold, "selectionSha256": "not-the-frozen-selection"}
        report = self.calibration.evaluate(self.selection, changed, self.root)
        self.assertEqual(report["status"], "incomplete")
        self.assertIs(report["passed"], False)

    def test_prepare_preserves_independently_filled_gold_on_repeat(self):
        core = load_module("ja_review_core.py", "semantic_calibration_fixture_core")
        project = self.root / "project"
        corpus_fixture(project)
        run = self.root / "run"
        core.prepare_run(project, run)
        out = self.root / "holdout"
        with mock.patch.object(self.calibration, "excluded_benchmark_ids", return_value=set()):
            selection, gold = self.calibration.prepare(run, out, count=1, seed=42)
            gold["reviewer"] = {"name": "independent fixture reviewer", "method": "field comparison", "independent": True}
            gold["fields"][0]["expectedStatus"] = "pass"
            write_json(out / "gold-template.json", gold)
            before = (out / "gold-template.json").read_bytes()
            _, repeated = self.calibration.prepare(run, out, count=1, seed=42)
        self.assertEqual(repeated, gold)
        self.assertEqual(before, (out / "gold-template.json").read_bytes())
        self.assertEqual(selection["entryIds"], ["library"])

    def test_prepare_refuses_a_tampered_snapshot_even_before_gold_is_created(self):
        core = load_module("ja_review_core.py", "semantic_calibration_tamper_core")
        project = self.root / "project"
        corpus_fixture(project)
        run = self.root / "run"
        core.prepare_run(project, run)
        path = run / "snapshot.json"
        frozen = json.loads(path.read_text())
        frozen["entries"][0]["fields"][0]["currentJapanese"] = "改ざん"
        write_json(path, frozen)
        with mock.patch.object(self.calibration, "excluded_benchmark_ids", return_value=set()):
            with self.assertRaises(ValueError):
                self.calibration.prepare(run, self.root / "holdout", count=1)
        self.assertFalse((self.root / "holdout/gold-template.json").exists())

    def test_real_holdout_predictions_must_match_frozen_snapshot_and_protocol_hash(self):
        snapshot_hash = write_json(self.root / "snapshot.json", {"schemaVersion": 1, "entries": self.selection["entries"]})
        self.selection["snapshotSha256"] = snapshot_hash
        self.gold["selectionSha256"] = self.calibration.digest(self.selection)
        self.record([{"path": "senses.0", "status": "pass"}, {"path": "ex.0", "status": "error"}])
        for protocol_snapshot, record_hash in [("another-snapshot", "any-hash"), (snapshot_hash, "wrong-protocol-hash")]:
            with self.subTest(snapshot_hash=protocol_snapshot, record_hash=record_hash):
                protocol = {"snapshotSha256": protocol_snapshot, "modelDigest": "fixture-model"}
                write_json(self.root / "protocols/detect.json", protocol)
                path = self.root / "records/detect/library/attempt-001.json"
                record = json.loads(path.read_text())
                record["protocolSha256"] = record_hash
                write_json(path, record)
                report = self.calibration.evaluate(self.selection, self.gold, self.root)
                self.assertEqual(report["status"], "incomplete")
                self.assertEqual(report["counts"]["missing"], 2)
                self.assertIs(report["passed"], False)

    def test_bound_holdout_accepts_only_records_of_the_actual_frozen_entry_content(self):
        snapshot_hash = write_json(self.root / "snapshot.json", {"schemaVersion": 1, "entries": self.selection["entries"]})
        self.selection["snapshotSha256"] = snapshot_hash
        self.gold["selectionSha256"] = self.calibration.digest(self.selection)
        protocol = {"snapshotSha256": snapshot_hash, "modelDigest": "fixture-model"}
        write_json(self.root / "protocols/detect.json", protocol)
        self.record([{"path": "senses.0", "status": "pass"}, {"path": "ex.0", "status": "error"}])
        path = self.root / "records/detect/library/attempt-001.json"
        record = json.loads(path.read_text())
        record["protocolSha256"] = self.calibration.digest(protocol)
        write_json(path, record)
        report = self.calibration.evaluate(self.selection, self.gold, self.root)
        self.assertEqual(report["status"], "complete")
        self.assertEqual(report["counts"]["correctPasses"], 1)
        self.assertEqual(report["counts"]["trueErrorDetections"], 1)
        changed = copy.deepcopy(self.selection)
        changed["entries"][0]["fields"][0]["currentJapanese"] = "変更された対象訳"
        changed_gold = {**self.gold, "selectionSha256": self.calibration.digest(changed)}
        report = self.calibration.evaluate(changed, changed_gold, self.root)
        self.assertEqual(report["status"], "incomplete")
        self.assertIs(report["passed"], False)


    def test_raw_model_error_approval_and_program_hold_are_measured_as_separate_views(self):
        self.record([
            {"path": "senses.0", "status": "pass", "modelAssessment": {"path": "senses.0", "status": "pass"}},
            {"path": "ex.0", "status": "uncertain", "modelAssessment": {"path": "ex.0", "status": "pass"},
             "programRiskFlags": [{"tag": "fixture_hold"}]},
        ])
        raw = self.calibration.evaluate(self.selection, self.gold, self.root, view="model")
        guarded = self.calibration.evaluate(self.selection, self.gold, self.root, view="guarded")
        self.assertEqual(raw["assessmentView"], "model")
        self.assertEqual(guarded["assessmentView"], "guarded")
        self.assertEqual(raw["counts"]["errorsApprovedAsPass"], 1)
        self.assertEqual(guarded["counts"]["errorsApprovedAsPass"], 0)
        self.assertEqual(guarded["counts"]["errorUncertain"], 1)
        self.assertEqual(raw["metrics"]["errorDetectionRecall"], 0)
        self.assertEqual(guarded["metrics"]["errorDetectionRecall"], 0)
        self.assertEqual(guarded["views"]["model"]["metrics"]["errorsApprovedAsPassRate"], 1)
        self.assertEqual(guarded["views"]["guarded"]["metrics"]["errorsApprovedAsPassRate"], 0)

    def test_model_view_falls_back_only_for_legacy_verdicts_without_a_program_overlay(self):
        self.record([{"path": "senses.0", "status": "pass"}, {"path": "ex.0", "status": "error"}])
        raw = self.calibration.evaluate(self.selection, self.gold, self.root, view="model")
        guarded = self.calibration.evaluate(self.selection, self.gold, self.root, view="guarded")
        self.assertEqual(raw["counts"], guarded["counts"])
        self.assertEqual(raw["metrics"], guarded["metrics"])


class CorpusCliIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cli = load_module("review-ja-corpus.py", "semantic_cli_tests")

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.project = self.folder / "project"
        self.source, self.public, _ = corpus_fixture(self.project)
        # A demonstrably wrong current number, consistently represented in the
        # final overlay and its owning correction file, gives a real repair.
        self.public["ex"][0] = "図書館で本を2冊借りました。"
        write_json(self.project / "public/atlas/ja/entries/0.json", [self.public])
        write_json(self.project / "scripts/atlas/ja-reviewed-0.json", [self.public])
        for name in ["review-ja-corpus.py", "ja_review_core.py", "ja_review_models.py", "translate-ja-local.py"]:
            (self.project / "scripts/atlas" / name).write_bytes((HERE / name).read_bytes())
        self.root_patch = mock.patch.object(self.cli, "ROOT", self.project)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.run = self.folder / "run"
        self.snapshot = self.cli.core.prepare_run(self.project, self.run)
        self.entry = self.snapshot["entries"][0]
        self.field = next(f for f in self.entry["fields"] if f["path"] == "ex.0")
        self.proposal = {"path": "ex.0", "before": self.field["currentJapanese"],
                         "text": "図書館で本を3冊借りました。", "reason": "quantity", "evidence": "3 books"}
        store = self.cli.core.AttemptStore(self.run, "repair", {"fixture": True, "snapshotSha256": self.cli.core.sha((self.run / "snapshot.json").read_bytes())})
        record = store.begin("library")
        store.finish("library", {**record, "status": "complete", "snapshotSha256": self.cli.core.sha((self.run / "snapshot.json").read_bytes()), "result": {"proposals": [
            {"path": "ex.0", "status": "complete", "proposal": self.proposal,
             "proposalSha256": self.cli.core.sha(self.proposal), "gateErrors": []}]}})
        self.decisions = {"snapshotSha256": self.cli.core.sha((self.run / "snapshot.json").read_bytes()),
                          "reviewer": {"name": "independent fixture reviewer", "method": "source/old/new quantity comparison", "independent": True},
                          "decisions": [{"entryId": "library", "path": "ex.0", "decision": "accept",
                                         "proposalSha256": self.cli.core.sha(self.proposal),
                                         "sourceSha256": self.cli.core.sha(self.field["sourceText"]),
                                         "targetSha256": self.cli.core.sha(self.proposal["text"]),
                                         "sourceQuote": "3 books", "targetQuote": "3冊",
                                         "explanation": "Source says three; replace the incorrect two with three."}]}
        self.args = SimpleNamespace(run=self.run, decisions=self.folder / "decisions.json",
                                    out=self.folder / "bundle.json", repair_lane="repair")

    def export(self, decisions=None):
        write_json(self.args.decisions, self.decisions if decisions is None else decisions)
        self.cli.export_bundle(self.args, self.snapshot)
        return json.loads(self.args.out.read_text())

    def test_export_requires_independent_reviewer_and_exact_snapshot_and_proposal(self):
        bad = []
        bad.append({**self.decisions, "reviewer": {**self.decisions["reviewer"], "independent": False}})
        bad.append({**self.decisions, "reviewer": {**self.decisions["reviewer"], "name": ""}})
        bad.append({**self.decisions, "snapshotSha256": "another-snapshot"})
        changed = copy.deepcopy(self.decisions)
        changed["decisions"][0]["proposalSha256"] = "same-field-but-a-different-proposal"
        bad.append(changed)
        for decisions in bad:
            with self.subTest(decisions=decisions):
                with self.assertRaises(ValueError):
                    self.export(decisions)
                self.assertFalse(self.args.out.exists())

    def test_accepted_bundle_points_to_effective_override_and_does_not_write_corpus(self):
        before = {str(p.relative_to(self.project)): p.read_bytes() for p in self.project.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        bundle = self.export()
        after = {str(p.relative_to(self.project)): p.read_bytes() for p in self.project.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        self.assertEqual(before, after)
        self.assertEqual(len(bundle["patches"]), 1)
        patch = bundle["patches"][0]
        self.assertEqual(patch["writeLocation"]["file"], "scripts/atlas/ja-reviewed-0.json")
        self.assertEqual(patch["writeLocation"]["kind"], "entry-array")
        self.assertEqual(patch["before"], "図書館で本を2冊借りました。")
        self.assertTrue(self.args.out.exists())

    def test_reject_uncertain_and_pass_decisions_never_export_a_change(self):
        for decision in ["reject", "uncertain", "pass"]:
            changed = copy.deepcopy(self.decisions)
            changed["decisions"][0]["decision"] = decision
            if decision == "pass":
                changed["decisions"][0]["targetSha256"] = self.cli.core.sha(self.field["currentJapanese"])
                changed["decisions"][0]["targetQuote"] = "2冊"
            self.args.out = self.folder / f"{decision}-bundle.json"
            with self.subTest(decision=decision):
                self.assertEqual(self.export(changed)["patches"], [])

    def test_export_is_held_when_an_input_or_override_changes(self):
        path = self.project / "scripts/atlas/ja-reviewed-0.json"
        write_json(path, [])
        with self.assertRaises(ValueError):
            self.export()
        self.assertFalse(self.args.out.exists())

    def test_export_cannot_place_a_bundle_in_the_formal_corpus(self):
        for destination in [self.project / "data/bundle.json", self.project / "public/bundle.json"]:
            with self.subTest(destination=destination):
                self.args.out = destination
                with self.assertRaises(ValueError):
                    self.export()
                self.assertFalse(destination.exists())

    def test_recorded_client_writes_the_actual_payload_before_transport_and_keeps_response(self):
        profile = self.cli.models.profile_for("detect")
        args = SimpleNamespace(run=self.run, base_url="http://127.0.0.1:11434")
        client = self.cli.RecordedClient(args, profile, "detect-fixture", "library", 1)
        path = self.run / "calls/detect-fixture/library/attempt-000001/0001.json"
        raw_text = '{"assessments":[]}'

        def transport(request, **kwargs):
            pending = json.loads(path.read_text())
            self.assertEqual(pending["status"], "running")
            self.assertEqual(pending["request"], json.loads(request.data))
            return io.BytesIO((json.dumps({"message": {"thinking": "PRIVATE_TRANSPORT_SENTINEL", "content": raw_text}, "done": True,
                                          "done_reason": "stop"}) + "\n").encode())

        with mock.patch.object(self.cli.models.urllib.request, "urlopen", side_effect=transport):
            result = client.chat([{"role": "user", "content": "fixture"}], {"type": "object"})
        saved = json.loads(path.read_text())
        self.assertEqual(saved["status"], "complete")
        self.assertEqual(saved["request"], result["request"])
        self.assertEqual(saved["text"], raw_text)
        self.assertNotIn("PRIVATE_TRANSPORT_SENTINEL", path.read_text())

    def test_status_keeps_semantic_and_integrity_coverage_separate(self):
        protocol = {"fixture": "status"}
        store = self.cli.core.AttemptStore(self.run, "detect-fixture", protocol)
        record = store.begin("library")
        assessments = [{"path": f["path"], "status": "pass"} for f in self.entry["fields"]]
        next(a for a in assessments if a["path"] == "ex.0")["status"] = "uncertain"
        next(a for a in assessments if a["path"] == "syn.0")["status"] = "error"
        store.finish("library", {**record, "status": "complete", "result": {"assessments": assessments}})
        report = self.cli.status_report(self.run, self.snapshot, "detect-fixture")
        modes = self.snapshot["manifest"]["counts"]
        self.assertEqual(sum(report["semanticFields"].values()), modes["translate"])
        self.assertEqual(sum(report["integrityFields"].values()), modes["empty"] + modes["preserve"])
        self.assertEqual(report["semanticFields"]["uncertain"], 1)
        self.assertEqual(report["integrityFields"]["error"], 1)

    def test_explicit_reference_retry_reuses_completed_fields_instead_of_regenerating_them(self):
        snapshot_hash = self.cli.core.sha((self.run / "snapshot.json").read_bytes())
        detection = self.cli.core.AttemptStore(self.run, "detect", {"fixture": "detection", "snapshotSha256": snapshot_hash})
        record = detection.begin("library")
        assessments = [{"path": f["path"], "status": "error" if f["path"] in {"senses.0", "ex.0"} else "pass"}
                       for f in self.entry["fields"]]
        detection.finish("library", {**record, "status": "complete", "snapshotSha256": snapshot_hash, "result": {"assessments": assessments}})
        args = SimpleNamespace(command="reference", run=self.run, ids="library", selection=None, all=False,
                               preset="baseline", model=None, temperature=None, top_k=None, top_p=None,
                               num_ctx=None, num_predict=None, thinking=None, lane=None, detect_lane="detect",
                               reference_lane="reference", repair_lane="repair", retry=False, limit=None, from_lane=None,
                               base_url="http://127.0.0.1:11434")
        model = self.cli.models.profile_for("translate")["model"]

        def request(base, endpoint, payload=None):
            return {"models": [{"name": model, "digest": "fixture-model"}]} if endpoint == "/api/tags" else {"template": "fixture"}

        with mock.patch.object(self.cli.models, "_request", side_effect=request), \
             mock.patch.object(self.cli.models, "ensure_single_model", return_value=[]), \
             mock.patch.object(self.cli.models, "release_model", return_value=[]), \
             mock.patch.object(self.cli.models, "translate_field", side_effect=[{"text": "図書館"}, RuntimeError("fixture interruption")]) as translate:
            self.cli.model_stage(args, self.snapshot)
            self.assertEqual(translate.call_count, 2)
        args.retry = True
        with mock.patch.object(self.cli.models, "_request", side_effect=request), \
             mock.patch.object(self.cli.models, "ensure_single_model", return_value=[]), \
             mock.patch.object(self.cli.models, "release_model", return_value=[]), \
             mock.patch.object(self.cli.models, "translate_field", return_value={"text": "図書館で本を3冊借りました。"}) as translate:
            self.cli.model_stage(args, self.snapshot)
            self.assertEqual(translate.call_count, 1)
            self.assertEqual(translate.call_args.args[1]["path"], "ex.0")
        latest = self.cli.core.latest_records(self.run, "reference")["library"]
        references = {r["path"]: r for r in latest["result"]["references"]}
        self.assertEqual(references["senses.0"]["reusedFromAttempt"], 1)
        self.assertTrue(all(r["status"] == "complete" for r in references.values()))


    def make_original_detection_attempt(self, call_status="complete"):
        lane = "detect-original"
        protocol = {"snapshotSha256": self.cli.core.sha((self.run / "snapshot.json").read_bytes()), "role": "detect", "fixture": True}
        store = self.cli.core.AttemptStore(self.run, lane, protocol)
        record = store.begin("library")
        assessments = [pass_assessment(field) for field in self.entry["fields"] if field["mode"] == "translate"]
        assessments[0].update({"status": "error", "categories": ["wrong_meaning", "wrong_meaning"]})
        call_rel = "calls/detect-original/library/attempt-000001/0001.json"
        call = {"status": call_status, "text": json.dumps({"assessments": assessments}, ensure_ascii=False),
                "request": {"model": "fixture-model", "messages": []},
                "metrics": {"done_reason": "stop" if call_status == "complete" else "length"}}
        write_json(self.run / call_rel, call)
        store.finish("library", {**record, "snapshotSha256": protocol["snapshotSha256"], "status": "error",
                                 "calls": [call_rel], "error": "original strict parser rejected repeated categories"})
        args = SimpleNamespace(run=self.run, from_lane=lane, lane="detect-reparsed", retry=False,
                               ids="library", selection=None, all=False)
        return args, self.run / call_rel

    def test_reparse_uses_the_exact_complete_original_output_without_network_or_overwriting_evidence(self):
        args, call_path = self.make_original_detection_attempt()
        raw_call = call_path.read_bytes()
        original_path = self.run / "records/detect-original/library/attempt-000001.json"
        old_record = original_path.read_bytes()
        with mock.patch.object(self.cli.models.LocalClient, "chat", side_effect=AssertionError("Offline reparse must not infer")):
            report = self.cli.reparse_detection(args, self.snapshot)
        parsed = self.cli.core.latest_records(self.run, args.lane)["library"]
        self.assertEqual(parsed["status"], "complete")
        self.assertIs(parsed["inferencePerformed"], False)
        self.assertEqual(parsed["calls"], [])
        self.assertEqual(parsed["originalCallSha256"], self.cli.core.sha(raw_call))
        self.assertEqual(parsed["derivedFrom"]["lane"], args.from_lane)
        self.assertEqual(call_path.read_bytes(), raw_call)
        self.assertEqual(original_path.read_bytes(), old_record)
        self.assertEqual(report["recordStatus"]["complete"], 1)

    def test_reparse_cannot_promote_a_token_truncated_original_even_if_its_text_looks_like_json(self):
        args, call_path = self.make_original_detection_attempt(call_status="error")
        before = call_path.read_bytes()
        with mock.patch.object(self.cli.models.LocalClient, "chat", side_effect=AssertionError("No generation allowed")):
            self.cli.reparse_detection(args, self.snapshot)
        held = self.cli.core.latest_records(self.run, args.lane)["library"]
        self.assertEqual(held["status"], "error")
        self.assertNotIn("result", held)
        self.assertEqual(call_path.read_bytes(), before)

    def test_upstream_stage_records_reject_wrong_entry_protocol_and_snapshot_binding(self):
        original = self.run / "records/repair/library/attempt-000001.json"
        record = json.loads(original.read_text())
        self.assertIn("library", self.cli.stage_records(self.run, "repair"))
        for key, value in [("id", "another-entry"), ("protocolSha256", "wrong-protocol"), ("snapshotSha256", "wrong-snapshot")]:
            with self.subTest(key=key):
                write_json(original, {**record, key: value})
                with self.assertRaises(ValueError):
                    self.cli.parent_inputs(self.run, "repair", "library")
        write_json(original, record)

    def test_cross_lane_detection_retry_requests_only_unavailable_fields_and_retains_all_valid_verdicts(self):
        snapshot_hash = self.cli.core.sha((self.run / "snapshot.json").read_bytes())
        source_lane = "detect-previous"
        source_store = self.cli.core.AttemptStore(self.run, source_lane, {"role": "detect", "snapshotSha256": snapshot_hash})
        original = source_store.begin("library")
        assessments = [pass_assessment(f) for f in self.entry["fields"]]
        by_path = {a["path"]: a for a in assessments}
        by_path["senses.0"].update({"status": "error", "categories": ["wrong_meaning"]})
        by_path["col.0"]["status"] = "uncertain"
        by_path["ex.0"].update({"status": "unavailable", "sourceQuote": "", "targetQuote": ""})
        source_store.finish("library", {**original, "status": "complete", "snapshotSha256": snapshot_hash,
                                         "inputs": {}, "result": {"assessments": assessments}})
        old_path = self.run / f"records/{source_lane}/library/attempt-000001.json"
        old_bytes = old_path.read_bytes()
        args = SimpleNamespace(command="detect", run=self.run, ids="library", selection=None, all=False,
                               preset="baseline", model=None, temperature=None, top_k=None, top_p=None,
                               num_ctx=None, num_predict=None, thinking=None, lane="detect-retry", from_lane=source_lane,
                               detect_lane="detect", reference_lane="reference", repair_lane="repair", retry=True,
                               limit=None, base_url="http://127.0.0.1:11434")
        model = self.cli.models.profile_for("detect")["model"]
        requested_paths = []

        def request(base, endpoint, payload=None):
            if endpoint == "/api/tags":
                return {"models": [{"name": model, "digest": "fixture-model"}]}
            return {"template": "fixture", "version": "fixture-runtime"}

        def chat(client, messages, schema=None):
            payload = json.loads(messages[1]["content"])
            requested_paths.extend(f["path"] for f in payload["fields"])
            field = next(f for f in self.entry["fields"] if f["path"] == "ex.0")
            return {"text": json.dumps({"assessments": [pass_assessment(field)]}, ensure_ascii=False), "metrics": {}, "request": {}}

        with mock.patch.object(self.cli.models, "_request", side_effect=request), \
             mock.patch.object(self.cli.models, "ensure_single_model", return_value=[]), \
             mock.patch.object(self.cli.models, "release_model", return_value=[]), \
             mock.patch.object(self.cli.RecordedClient, "chat", autospec=True, side_effect=chat):
            self.cli.model_stage(args, self.snapshot)
        self.assertEqual(requested_paths, ["ex.0"])
        current = self.cli.core.latest_records(self.run, args.lane)["library"]
        result = {a["path"]: a for a in current["result"]["assessments"]}
        self.assertEqual(result["senses.0"]["status"], "error")
        self.assertEqual(result["col.0"]["status"], "uncertain")
        self.assertEqual(result["ex.0"]["status"], "pass")
        self.assertEqual(len(result), len(self.entry["fields"]))
        self.assertEqual(old_path.read_bytes(), old_bytes)


    def test_interrupted_first_request_keeps_snapshot_bound_running_checkpoint_for_cross_lane_resume(self):
        args = SimpleNamespace(command="detect", run=self.run, ids="library", selection=None, all=False,
                               preset="baseline", model=None, temperature=None, top_k=None, top_p=None,
                               num_ctx=None, num_predict=None, thinking=None, lane="detect-interrupted", from_lane=None,
                               detect_lane="detect", reference_lane="reference", repair_lane="repair", retry=False,
                               limit=None, base_url="http://127.0.0.1:11434")
        model = self.cli.models.profile_for("detect")["model"]

        def request(base, endpoint, payload=None):
            return {"models": [{"name": model, "digest": "fixture-model"}]} if endpoint == "/api/tags" else {"template": "fixture", "version": "fixture-runtime"}

        with mock.patch.object(self.cli.models, "_request", side_effect=request), \
             mock.patch.object(self.cli.models, "ensure_single_model", return_value=[]), \
             mock.patch.object(self.cli.models, "release_model", return_value=[]), \
             mock.patch.object(self.cli.RecordedClient, "chat", side_effect=KeyboardInterrupt("simulated user/process interruption")):
            with self.assertRaises(KeyboardInterrupt):
                self.cli.model_stage(args, self.snapshot)
        record = self.cli.core.latest_records(self.run, args.lane)["library"]
        self.assertEqual(record["status"], "running")
        self.assertEqual(record["snapshotSha256"], self.cli.core.sha((self.run / "snapshot.json").read_bytes()))
        self.assertEqual(record["inputs"], {})
        self.assertIn("library", self.cli.stage_records(self.run, args.lane))


class ConservativeSemanticRiskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = load_module("ja_review_core.py", "semantic_risk_tests")

    def field(self, source, target, **extra):
        return {"path": "ex.0", "sourceLanguage": "en", "sourceText": source,
                "currentJapanese": target, "mode": "translate", **extra}

    def test_unspecified_sibling_age_and_added_male_alternative_are_held_with_real_substrings(self):
        cases = [
            ("I called my sister.", "姉に電話しました。", "unsupported_sibling_age"),
            ("I called my sister.", "妹に電話しました。", "unsupported_sibling_age"),
            ("I called my brother.", "兄に電話しました。", "unsupported_sibling_age"),
            ("I called my brother.", "弟に電話しました。", "unsupported_sibling_age"),
            ("a female sibling", "姉妹（または兄弟）", "unsupported_sibling_gender"),
        ]
        for source, target, tag in cases:
            with self.subTest(source=source, target=target):
                risks = self.core.semantic_risks(self.field(source, target))
                self.assertIn(tag, {risk["tag"] for risk in risks})
                for risk in risks:
                    self.assertIn(risk["sourceQuote"], source)
                    self.assertIn(risk["targetQuote"], target)

    def test_explicit_age_religious_sense_and_unrestricted_japanese_sibling_wording_are_not_age_flags(self):
        cases = [
            ("I called my older sister.", "姉に電話しました。"),
            ("I called my younger brother.", "弟に電話しました。"),
            ("a woman belonging to a religious community", "宗教共同体に属する女性"),
            ("a religious sister", "姉という宗教上の呼称"),
            ("I called my sister.", "姉（または妹）に電話しました。"),
            ("I called my brother.", "兄（または弟）に電話しました。"),
        ]
        for source, target in cases:
            with self.subTest(source=source, target=target):
                self.assertFalse(self.core.semantic_risks(self.field(source, target)))

    def test_unspecified_time_and_auxiliary_am_do_not_authorize_added_morning(self):
        for source in ["The train leaves at six.", "I am leaving at six."]:
            with self.subTest(source=source):
                flags = self.core.semantic_risks(self.field(source, "午前6時に出発します。"))
                self.assertIn("unsupported_time_of_day", {f["tag"] for f in flags})
        for source in ["The train leaves at six am.", "The train leaves at 6am.", "The train leaves at 6 a.m.",
                       "The train leaves at six in the morning.", "The train leaves at 6 AM."]:
            with self.subTest(source=source):
                self.assertFalse(self.core.semantic_risks(self.field(source, "列車は午前6時に出発します。")))

    def test_shared_kanji_quoted_english_and_non_english_integrity_fields_are_unaffected(self):
        cases = [self.field("a place where people read books", "図書館", path="senses.0"),
                 self.field("The library sign says 'Open'.", "図書館の看板には「Open」と書かれています。"),
                 self.field("姐姐", "姉", sourceLanguage="zh-Hans"),
                 self.field("sister", "sister", mode="preserve")]
        for field in cases:
            with self.subTest(field=field):
                self.assertEqual(self.core.semantic_risks(field), [])

    def test_guard_preserves_the_original_verdict_and_only_holds_model_pass(self):
        field = self.field("I called my sister.", "姉に電話しました。")
        entry = {"id": "sister", "fields": [field]}
        for status in ["pass", "error", "uncertain", "unavailable"]:
            assessment = pass_assessment(field)
            assessment["status"] = status
            original = copy.deepcopy(assessment)
            with self.subTest(status=status):
                result = self.core.guard_assessments(entry, [assessment])[0]
                self.assertEqual(result["status"], "uncertain" if status == "pass" else status)
                self.assertEqual(result["modelAssessment"], original)
                self.assertTrue(result["programRiskFlags"])
                self.assertEqual(assessment, original)
                repeated = self.core.guard_assessments(entry, [result])[0]
                self.assertEqual(repeated["modelAssessment"], original)
                self.assertNotIn("modelAssessment", repeated["modelAssessment"])

    def test_added_superlative_is_held_but_explicit_english_ranking_cues_are_not(self):
        for target in ["最も影響が小さいです。", "一番影響が小さいです。"]:
            field = self.field("It has a small impact.", target)
            risks = self.core.semantic_risks(field)
            self.assertIn("unsupported_superlative", {risk["tag"] for risk in risks})
            self.assertTrue(all(risk["sourceQuote"] in field["sourceText"] and risk["targetQuote"] in target for risk in risks))
        for source in ["It has the smallest impact.", "It has the highest value.", "It happens at the earliest time.",
                       "It is the most effective option.", "It is number one."]:
            with self.subTest(source=source):
                self.assertFalse(self.core.semantic_risks(self.field(source, "最も高い値です。")))

    def test_multi_frame_definitions_are_held_even_when_both_japanese_frames_are_correct(self):
        source = "to become less tense or make a muscle less tense"
        for target in ["筋肉を緩める", "緩む；筋肉を緩める"]:
            field = self.field(source, target, path="senses.0")
            with self.subTest(target=target):
                risks = self.core.semantic_risks(field)
                self.assertIn("multi_frame_definition", {risk["tag"] for risk in risks})
                self.assertTrue(all(risk["sourceQuote"] in source and risk["targetQuote"] in target for risk in risks))
                assessment = pass_assessment(field)
                guarded = self.core.guard_assessments({"fields": [field]}, [assessment])[0]
                self.assertEqual(guarded["status"], "uncertain")
                self.assertEqual(guarded["modelAssessment"]["status"], "pass")

    def test_multi_frame_hold_is_definition_specific_and_does_not_guess_other_languages_or_plain_glosses(self):
        source = "to make a muscle less tense or become less tense"
        self.assertIn("multi_frame_definition", {r["tag"] for r in self.core.semantic_risks(self.field(source, "緩む；緩める", path="senses.0"))})
        self.assertEqual(self.core.semantic_risks(self.field(source, "緩む；緩める", path="ex.0")), [])
        self.assertEqual(self.core.semantic_risks(self.field(source, "緩む；緩める", path="senses.0", sourceLanguage="zh-Hans")), [])
        self.assertEqual(self.core.semantic_risks(self.field("a place where people read books", "図書館", path="senses.0")), [])


class RepairQualityCalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calibration = load_module("calibrate-ja-review.py", "semantic_repair_calibration_tests")
        cls.core = load_module("ja_review_core.py", "semantic_repair_calibration_core")

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.run = Path(self.temporary.name) / "run"
        field_specs = [
            ("She bought three tickets.", "切符を2枚買いました。", "切符を3枚買いました。"),
            ("The door is not locked.", "ドアには鍵がかかっていません。", "ドアには鍵がかかっています。"),
            ("a female sibling", "姉", "男性のきょうだい"),
            ("The library is open.", "図書館は開いています。", "図書館は開館しています。"),
            ("She bought two tickets.", "切符を3枚買いました。", "切符を2枚買いました。"),
            ("The field could not be reviewed.", "確認できませんでした。", "unused"),
        ]
        fields = [{"path": f"ex.{i}", "mode": "translate", "sourceLanguage": "en", "sourceText": source,
                   "currentJapanese": before} for i, (source, before, after) in enumerate(field_specs)]
        entries = [{"id": "quality", "word": "quality", "fields": fields},
                   {"id": "failed-entry", "word": "failure", "fields": [copy.deepcopy(fields[0])]},
                   {"id": "unprocessed-entry", "word": "unprocessed", "fields": [copy.deepcopy(fields[0])]}]
        self.snapshot_hash = write_json(self.run / "snapshot.json", {"schemaVersion": 1, "entries": entries})
        (self.run / "snapshot-sha256.txt").write_text(self.snapshot_hash + "\n")
        self.protocol = {"role": "repair", "snapshotSha256": self.snapshot_hash, "modelDigest": "fixture-model"}
        store = self.core.AttemptStore(self.run, "repair", self.protocol)
        record = store.begin("quality")
        proposals = []
        for i, (_, before, after) in enumerate(field_specs[:5]):
            proposal = {"path": f"ex.{i}", "before": before, "text": after, "reason": "mistranslation", "evidence": fields[i]["sourceText"]}
            proposals.append({"path": f"ex.{i}", "status": "blocked" if i == 4 else "complete", "proposal": proposal,
                              "proposalSha256": self.calibration.digest(proposal), "gateErrors": ["conservative hold"] if i == 4 else []})
        proposals.append({"path": "ex.5", "status": "error", "error": "no actual proposal was produced"})
        store.finish("quality", {**record, "snapshotSha256": self.snapshot_hash, "status": "complete", "result": {"proposals": proposals}})
        failed = store.begin("failed-entry")
        store.finish("failed-entry", {**failed, "snapshotSha256": self.snapshot_hash, "status": "error", "error": "transport failure"})

    def labeled(self):
        gold = self.calibration.repair_template(self.run)
        gold["reviewer"] = {"name": "independent fixture reviewer", "method": "source/before/after controlled semantic labels", "independent": True}
        labels = [("error", "pass", "major", None), ("pass", "error", None, "critical"),
                  ("error", "error", "major", "critical"), ("pass", "pass", None, None),
                  ("error", "pass", "major", None)]
        for item, (before, after, before_severity, after_severity) in zip(gold["items"], labels):
            item.update({"beforeStatus": before, "afterStatus": after, "beforeSeverity": before_severity,
                         "afterSeverity": after_severity, "note": "Controlled source-grounded fixture classification."})
        return gold

    def test_unlabeled_repair_template_has_no_semantic_success_metrics(self):
        template = self.calibration.repair_template(self.run)
        self.assertEqual(len(template["items"]), 5)
        report = self.calibration.repair_evaluate(self.run, template)
        self.assertEqual(report["status"], "incomplete")
        self.assertIs(report["passed"], False)
        self.assertIsNone(report["metrics"])

    def test_repairs_regressions_worsening_and_style_only_edits_have_distinct_denominators(self):
        report = self.calibration.repair_evaluate(self.run, self.labeled())
        self.assertEqual(report["status"], "complete")
        counts = report["counts"]
        for key, expected in {"reviewedProposals": 5, "validRepairCount": 2, "regressionCount": 1,
                              "stillErroneousCount": 1, "worsenedCount": 1, "styleOnlyCount": 1,
                              "machineBlocked": 1, "fieldFailed": 1, "failedRecords": 1,
                              "entriesWithoutRepairRecords": 1}.items():
            with self.subTest(key=key):
                self.assertEqual(counts[key], expected)
        self.assertEqual(report["metrics"]["patchCorrectness"], 2 / 5)
        self.assertEqual(report["metrics"]["trueFixRate"], 2 / 3)
        self.assertEqual(report["metrics"]["regressionRate"], 1 / 2)
        self.assertEqual(report["metrics"]["worseningRate"], 1 / 3)
        self.assertEqual(report["metrics"]["eligiblePatchCorrectness"], 1 / 4)
        self.assertIsNot(report["passed"], True)

    def test_machine_blocked_candidates_and_failed_no_proposal_attempts_remain_visible(self):
        template = self.calibration.repair_template(self.run)
        blocked = [item for item in template["items"] if item["machineBlocked"]]
        self.assertEqual(len(blocked), 1)
        self.assertFalse(blocked[0]["machineEligible"])
        self.assertFalse(any(item["entryId"] == "failed-entry" for item in template["items"]))
        self.assertFalse(any(item["path"] == "ex.5" for item in template["items"]))
        self.assertEqual(template["materialCounts"]["failedRecords"], 1)
        self.assertEqual(template["materialCounts"]["fieldFailed"], 1)

    def test_independent_labels_become_stale_when_a_proposal_attempt_changes(self):
        gold = self.labeled()
        path = self.run / "records/repair/quality/attempt-000001.json"
        record = json.loads(path.read_text())
        record["checkpointAnnotation"] = "attempt bytes changed after independent review"
        write_json(path, record)
        report = self.calibration.repair_evaluate(self.run, gold)
        self.assertEqual(report["status"], "incomplete")
        self.assertIsNone(report["metrics"])
        self.assertGreater(report["counts"]["staleIndependentLabels"], 0)

    def test_repair_labels_cannot_alter_displayed_context_while_retaining_bound_hashes(self):
        gold = self.labeled()
        for key in ["sourceText", "beforeText", "afterText"]:
            changed = copy.deepcopy(gold)
            changed["items"][0][key] = "a different displayed source or translation"
            with self.subTest(key=key):
                report = self.calibration.repair_evaluate(self.run, changed)
                self.assertEqual(report["status"], "incomplete")
                self.assertIsNone(report["metrics"])

    def test_snapshot_tampering_invalidates_repair_labels_before_metrics(self):
        gold = self.labeled()
        path = self.run / "snapshot.json"
        snapshot = json.loads(path.read_text())
        snapshot["entries"][0]["fields"][0]["sourceText"] = "changed authoritative source"
        write_json(path, snapshot)
        with self.assertRaises(ValueError):
            self.calibration.repair_evaluate(self.run, gold)


class ReviewedUnresolvedGoldTests(unittest.TestCase):
    """Explicit reviewed uncertainty is held, never silently labeled correct.

    All labels and predictions here are synthetic fixtures; no real holdout,
    model output, corpus file or reviewer annotation is read or modified.
    """

    @classmethod
    def setUpClass(cls):
        cls.calibration = load_module("calibrate-ja-review.py", "reviewed_unresolved_gold_tests")

    def setUp(self):
        fields = [{"path": f"ex.{i}", "sourceLanguage": "en", "sourceText": "The signal is active.",
                   "currentJapanese": "信号は無効です。" if i == 1 else "信号は有効です。", "mode": "translate"}
                  for i in range(825)]
        self.selection = {"schemaVersion": 1, "kind": "synthetic-test-fixture",
                          "entries": [{"id": "fixture", "fields": fields}]}
        self.gold = {
            "schemaVersion": 1, "selectionSha256": self.calibration.digest(self.selection),
            "reviewer": {"name": "Independent fixture reviewer", "method": "Controlled fixture only", "independent": True},
            "fields": [{"entryId": "fixture", "path": f"ex.{i}",
                        "expectedStatus": "pass" if i == 0 else "error" if i == 1 else None,
                        "reviewStatus": "pass" if i == 0 else "error" if i == 1 else "uncertain",
                        "categories": ["wrong_meaning"] if i == 1 else [], "severity": "major" if i == 1 else None,
                        "note": "Known controlled meaning." if i < 2 else "Independently reviewed; ambiguity remains."}
                       for i in range(825)],
        }
        self.predictions = {name: {("fixture", f"ex.{i}"): "error" for i in range(825)}
                            for name in ("model", "guarded")}
        for view in self.predictions.values():
            view[("fixture", "ex.0")] = "pass"
        self.predictions["model"][("fixture", "ex.1")] = "pass"
        self.predictions["guarded"][("fixture", "ex.1")] = "uncertain"

    def evaluate_fixture(self, gold=None, allow=True):
        with mock.patch.object(self.calibration, "_load_prediction_views",
                               return_value=(self.predictions, [], [])) as loader:
            report = self.calibration.evaluate(self.selection, self.gold if gold is None else gold,
                                               "unused-synthetic-records", allow_unresolved_gold=allow)
            loader.assert_called_once()
        return report

    def test_default_strict_evaluation_still_rejects_null_gold(self):
        report = self.evaluate_fixture(allow=False)
        self.assertIsNone(report["metrics"])
        self.assertFalse(report["passed"])
        self.assertNotIn("scorableFields", report["counts"])
        self.assertNotIn("unresolvedGold", report)

    def test_explicit_reviewed_uncertainty_scores_only_resolved_subset_and_stays_held(self):
        original = copy.deepcopy(self.gold)
        report = self.evaluate_fixture()
        self.assertEqual(report["counts"]["selectedFields"], 825)
        self.assertEqual(report["counts"]["scorableFields"], 2)
        self.assertEqual(report["resolvedGoldCoverage"], 2 / 825)
        self.assertEqual(len(report["unresolvedGold"]), 823)
        self.assertTrue(all(item["note"] for item in report["unresolvedGold"]))
        self.assertEqual(len(report["fields"]), 2)
        for view in report["views"].values():
            self.assertEqual(view["status"], "incomplete")
            self.assertFalse(view["passed"])
            self.assertEqual(view["acceptanceDecision"], "held: unresolved independent gold")
            self.assertEqual(view["counts"]["falseErrorReports"], 0)
            self.assertEqual(view["counts"]["goldCorrect"], 1)
            self.assertEqual(view["counts"]["goldErrors"], 1)
        self.assertEqual(self.gold, original)

    def test_raw_and_guarded_views_use_scorable_denominators_without_counting_hold_as_detection(self):
        report = self.evaluate_fixture()
        model, guarded = report["views"]["model"], report["views"]["guarded"]
        self.assertEqual(model["counts"]["errorsApprovedAsPass"], 1)
        self.assertEqual(guarded["counts"]["errorsApprovedAsPass"], 0)
        self.assertEqual(guarded["counts"]["errorUncertain"], 1)
        self.assertEqual(model["metrics"]["errorDetectionRecall"], 0)
        self.assertEqual(guarded["metrics"]["errorDetectionRecall"], 0)
        self.assertEqual(model["metrics"]["conclusiveCoverage"], 1)
        self.assertEqual(guarded["metrics"]["conclusiveCoverage"], 0.5)
        self.assertEqual(guarded["metrics"]["uncertainRate"], 0.5)

    def test_unreviewed_missing_unknown_and_unattested_gold_cannot_be_opted_out(self):
        variants = []
        unreviewed = copy.deepcopy(self.gold)
        unreviewed["fields"][2].pop("reviewStatus")
        unreviewed["fields"][2]["note"] = ""
        variants.append(unreviewed)
        missing = copy.deepcopy(self.gold)
        missing["fields"].pop()
        variants.append(missing)
        unattested = copy.deepcopy(self.gold)
        unattested["reviewer"]["independent"] = False
        variants.append(unattested)
        for value in ("unknown", "uncertain", [], {}):
            unknown = copy.deepcopy(self.gold)
            unknown["fields"][2]["expectedStatus"] = value
            variants.append(unknown)
        contradictory = copy.deepcopy(self.gold)
        contradictory["fields"][0]["reviewStatus"] = "uncertain"
        variants.append(contradictory)
        for gold in variants:
            with self.subTest(gold=gold["fields"][2]):
                self.assertIsNone(self.evaluate_fixture(gold)["metrics"])

    def test_all_reviewed_but_unresolved_gold_has_no_scoring_metrics(self):
        gold = copy.deepcopy(self.gold)
        for field in gold["fields"]:
            field.update(expectedStatus=None, reviewStatus="uncertain", note="Reviewed but unresolved.")
        report = self.evaluate_fixture(gold)
        self.assertIsNone(report["metrics"])
        self.assertEqual(report["counts"]["selectedFields"], 825)
        self.assertEqual(report["counts"]["scorableFields"], 0)
        self.assertEqual(report["resolvedGoldCoverage"], 0)
        self.assertFalse(report["passed"])
        self.assertEqual(report["acceptanceDecision"], "held: unresolved independent gold")


if __name__ == "__main__":
    unittest.main(verbosity=2)
