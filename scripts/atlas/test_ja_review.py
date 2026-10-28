#!/usr/bin/env python3
"""Offline regression tests for conservative Japanese review patch acceptance.

Run with ``python3 scripts/atlas/test_ja_review.py``. No model or network is used.
The examples exercise the English/Chinese regressions observed in the local
benchmark without depending on private benchmark artifacts.
"""
from __future__ import annotations

import copy
from contextlib import redirect_stdout
import hashlib
import io
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


WORKER_PATH = Path(__file__).with_name("translate-ja-local.py")
SPEC = importlib.util.spec_from_file_location("ja_review_worker", WORKER_PATH)
worker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(worker)


def source_entry():
    return {
        "id": "library",
        "w": "library",
        "senses": [{"pos": "n.", "en": "a place where books are kept for people to read or borrow", "zh": "图书馆"}],
        "ex": [
            {"en": "I borrowed three books from the library.", "zh": "我从图书馆借了三本书。"},
            {"en": "The library is closed on Sundays.", "zh": "图书馆周日不开放。"},
        ],
        "col": ["public library｜公共图书馆"],
        "tip": "library指图书馆；library也可指资料集。",
        "note": "发音为/ˈlaɪbrəri/。",
    }


def good_fields():
    return {
        "senses.0": "図書館",
        "ex.0": "図書館で本を3冊借りました。",
        "ex.1": "図書館は日曜日には閉まっています。",
        "col.0": "公共図書館",
        "tip": "libraryは図書館を指し、libraryは資料の集まりも表します。",
        "note": "発音は/ˈlaɪbrəri/です。",
    }


def patch(fields, path="ex.0", text="図書館で本を3冊借りました。", *, before=None,
          reason="quantity", evidence="three books"):
    return {"path": path, "before": fields.get(path, "") if before is None else before,
            "text": text, "reason": reason, "evidence": evidence}


def response(*patches, approved=True, issues=None):
    return {"approved": approved, "patches": list(patches), "issues": [] if issues is None else issues}


class ReviewPatchTests(unittest.TestCase):
    def setUp(self):
        self.entry = source_entry()
        self.fields = good_fields()

    def assert_blocked(self, review, *, fields=None):
        original = self.fields if fields is None else fields
        final, audit = worker.apply_review(self.entry, original, review)
        self.assertFalse(audit["approved"])
        self.assertTrue(audit["needsReview"])
        return final, audit

    def test_unchanged_acceptable_draft_passes_without_rewriting(self):
        final, audit = worker.apply_review(self.entry, self.fields, response())
        self.assertEqual(final, self.fields)
        self.assertTrue(audit["approved"])
        self.assertFalse(audit["needsReview"])
        self.assertEqual(audit["acceptedPatches"], [])
        self.assertEqual(audit["rejectedPatches"], [])

    def test_source_evidenced_quantity_repair_preserves_other_fields_and_inputs(self):
        self.fields["ex.0"] = "図書館で本を2冊借りました。"
        review = response(patch(self.fields))
        snapshots = copy.deepcopy((self.entry, self.fields, review))
        final, audit = worker.apply_review(self.entry, self.fields, review)
        self.assertEqual(final["ex.0"], "図書館で本を3冊借りました。")
        self.assertEqual({k: v for k, v in final.items() if k != "ex.0"},
                         {k: v for k, v in self.fields.items() if k != "ex.0"})
        self.assertTrue(audit["approved"])
        self.assertEqual(len(audit["acceptedPatches"]), 1)
        self.assertEqual((self.entry, self.fields, review), snapshots)

    def test_english_sentence_rollback_keeps_draft_and_requires_review(self):
        attempted = patch(self.fields, path="ex.1", text=self.entry["ex"][1]["en"],
                          reason="mistranslation", evidence="closed on Sundays")
        final, audit = self.assert_blocked(response(attempted))
        self.assertEqual(final, self.fields)
        self.assertEqual(audit["modelApproved"], True)
        self.assertEqual(audit["rejectedPatches"][0]["path"], "ex.1")

    def test_chinese_tip_rollback_keeps_draft(self):
        attempted = patch(self.fields, path="tip", text=self.entry["tip"],
                          reason="mistranslation", evidence="library指图书馆")
        final, audit = self.assert_blocked(response(attempted))
        self.assertEqual(final["tip"], self.fields["tip"])
        self.assertTrue(audit["rejectedPatches"])

    def test_english_dictionary_definition_is_not_a_japanese_gloss(self):
        source = next(row["text"] for row in worker.translation_rows(self.entry) if row["path"] == "senses.0")
        attempted = patch(self.fields, path="senses.0", text=source,
                          reason="mistranslation", evidence="books are kept")
        final, _ = self.assert_blocked(response(attempted))
        self.assertEqual(final["senses.0"], "図書館")

    def test_safe_repair_survives_other_rejected_patch_but_cannot_be_approved(self):
        self.fields["ex.0"] = "図書館で本を2冊借りました。"
        safe = patch(self.fields)
        bad = patch(self.fields, path="ex.1", text=self.entry["ex"][1]["en"],
                    reason="negation", evidence="closed on Sundays")
        final, audit = self.assert_blocked(response(safe, bad))
        self.assertEqual(final["ex.0"], "図書館で本を3冊借りました。")
        self.assertEqual(final["ex.1"], self.fields["ex.1"])
        self.assertEqual(len(audit["acceptedPatches"]), 1)
        self.assertEqual(len(audit["rejectedPatches"]), 1)

    def test_before_must_match_exactly(self):
        self.fields["ex.0"] = "図書館で本を2冊借りました。"
        attempted = patch(self.fields, before="図書館で本を2冊借りました。 ")
        final, audit = self.assert_blocked(response(attempted))
        self.assertEqual(final, self.fields)
        self.assertTrue(audit["rejectedPatches"])

    def test_evidence_must_come_from_same_source_field(self):
        self.fields["ex.0"] = "図書館で本を2冊借りました。"
        final, _ = self.assert_blocked(response(patch(self.fields, evidence="Sundays")))
        self.assertEqual(final, self.fields)

    def test_number_already_matching_source_cannot_be_changed_by_review(self):
        self.entry["ex"][0]["en"] = "I borrowed 3 books from the library."
        attempted = patch(self.fields, text="図書館で本を4冊借りました。", evidence="3 books")
        final, audit = self.assert_blocked(response(attempted))
        self.assertEqual(final["ex.0"], self.fields["ex.0"])
        self.assertTrue(audit["rejectedPatches"])

    def test_duplicate_path_rejects_all_competing_replacements(self):
        self.fields["ex.0"] = "図書館で本を2冊借りました。"
        self.fields["ex.1"] = "図書館は日曜日に開いています。"
        duplicate_one = patch(self.fields)
        duplicate_two = patch(self.fields, text="私は図書館から本を3冊借りました。")
        independent = patch(self.fields, path="ex.1", text="図書館は日曜日には閉まっています。",
                            reason="negation", evidence="is closed on Sundays")
        final, audit = self.assert_blocked(response(duplicate_one, independent, duplicate_two))
        self.assertEqual(final["ex.0"], self.fields["ex.0"])
        self.assertEqual(final["ex.1"], "図書館は日曜日には閉まっています。")
        self.assertEqual(len(audit["acceptedPatches"]), 1)
        self.assertEqual(len(audit["rejectedPatches"]), 2)

    def test_unknown_path_cannot_add_or_remove_draft_fields(self):
        attempted = patch(self.fields, path="unknown.0", text="翻訳です。", evidence="three books")
        final, _ = self.assert_blocked(response(attempted))
        self.assertEqual(final, self.fields)

    def test_patch_contract_rejects_unexplained_or_invalid_replacements(self):
        self.fields["ex.0"] = "図書館で本を2冊借りました。"
        good = patch(self.fields)
        malformed = [
            {**good, "text": ""},
            {**good, "text": 3},
            {**good, "reason": "style"},
            {**good, "evidence": ""},
            {key: value for key, value in good.items() if key != "before"},
            {key: value for key, value in good.items() if key != "reason"},
            {key: value for key, value in good.items() if key != "evidence"},
        ]
        for attempted in malformed:
            with self.subTest(attempted=attempted):
                final, _ = self.assert_blocked(response(attempted))
                self.assertEqual(final, self.fields)

    def test_model_disapproval_or_remaining_issues_cannot_become_final(self):
        for review in [response(approved=False), response(issues=["Meaning remains uncertain."])]:
            with self.subTest(review=review):
                final, _ = self.assert_blocked(review)
                self.assertEqual(final, self.fields)

    def test_malformed_review_is_a_blocked_checkpoint_not_a_rewrite(self):
        malformed = [None, [], "approved", {}, {"approved": "true", "patches": [], "issues": []},
                     {"approved": True, "patches": {}, "issues": []},
                     {"approved": True, "patches": [], "issues": "no problems"}]
        for review in malformed:
            with self.subTest(review=review):
                final, audit = self.assert_blocked(review)
                self.assertEqual(final, self.fields)
                self.assertTrue(audit["errors"])

    def test_untranslated_unpatched_draft_does_not_pass_model_self_approval(self):
        self.fields["ex.0"] = self.entry["ex"][0]["en"]
        final, audit = self.assert_blocked(response())
        self.assertEqual(final, self.fields)
        self.assertTrue(audit["errors"])

    def test_missing_or_wrong_type_draft_requires_separate_alignment(self):
        incomplete = dict(self.fields)
        incomplete.pop("tip")
        extra = {**self.fields, "unknown": "余分な項目です。"}
        wrong_type = {**self.fields, "ex.0": ["翻訳です。"]}
        for fields in [None, [], incomplete, extra, wrong_type]:
            with self.subTest(fields=fields):
                with self.assertRaises(ValueError):
                    worker.apply_review(self.entry, fields, response())


class FieldLanguageTests(unittest.TestCase):
    def setUp(self):
        self.entry = source_entry()

    def test_short_kanji_glosses_and_collocations_are_valid_japanese(self):
        for path, text in [("senses.0", "図書館"), ("senses.0", "資料集"), ("col.0", "公共図書館")]:
            with self.subTest(path=path, text=text):
                self.assertEqual(worker.field_errors(self.entry, path, text), [])

    def test_numeric_glosses_do_not_require_japanese_script(self):
        entry = copy.deepcopy(self.entry)
        entry["w"] = "two hundred"
        entry["senses"][0] = {"pos": "num.", "en": "200", "zh": "两百"}
        entry["col"] = ["200｜两百"]
        for path in ["senses.0", "col.0"]:
            with self.subTest(path=path):
                self.assertEqual(worker.field_errors(entry, path, "200"), [])

    def test_untranslated_headword_in_japanese_text_is_held_for_contextual_review(self):
        # A HOLD is a conservative language signal, not a semantic error count.
        for path, text in [("senses.0", "libraryを利用する"),
                           ("ex.0", "私はlibraryを利用します。"),
                           ("col.0", "libraryの利用")]:
            with self.subTest(path=path, text=text):
                signals = worker.field_errors(self.entry, path, text)
                self.assertTrue(any("headword" in signal for signal in signals))

    def test_uppercase_acronym_in_japanese_is_not_held_as_an_untranslated_headword(self):
        entry = copy.deepcopy(self.entry)
        entry["w"] = "DNA"
        entry["senses"][0] = {"pos": "n.", "en": "the genetic material in cells", "zh": "脱氧核糖核酸"}
        entry["ex"][0]["en"] = "DNA carries genetic information."
        entry["col"] = ["DNA sequence｜DNA序列"]
        cases = [("senses.0", "DNA（デオキシリボ核酸）"),
                 ("ex.0", "DNAは遺伝情報を運びます。"),
                 ("col.0", "DNAの配列")]
        for path, text in cases:
            with self.subTest(path=path, text=text):
                self.assertEqual(worker.field_errors(entry, path, text), [])

    def test_mixed_chinese_wording_and_bengali_script_are_held_for_review(self):
        # The gate requests contextual review; these signals do not certify a
        # substantive translation error or replace source-based adjudication.
        cases = ["資料の検索用于です。", "図書館で本を借りました。 বাংলা"]
        for text in cases:
            with self.subTest(text=text):
                self.assertTrue(worker.field_errors(self.entry, "ex.0", text))

    def test_shared_han_characters_in_modern_japanese_are_not_simplified_chinese(self):
        # These characters also occur in simplified Chinese, but are standard
        # Japanese. A language smoke gate must not reject them on that basis.
        cases = [
            ("The library provides learning opportunities.", "図書館は学習の機会を与えています。"),
            ("The library will have more books in the future.", "図書館の蔵書は将来さらに増えるでしょう。"),
            ("Please read the terms before using the library.", "図書館を利用する前に条件を読んでください。"),
            ("I was absorbed in reading at the library.", "私は図書館で読書に没頭していました。"),
        ]
        for source, target in cases:
            with self.subTest(target=target):
                entry = copy.deepcopy(self.entry)
                entry["ex"][0]["en"] = source
                self.assertEqual(worker.field_errors(entry, "ex.0", target), [])

    def test_japanese_tip_and_ipa_note_retain_legitimate_english(self):
        fields = good_fields()
        for path in ["tip", "note"]:
            with self.subTest(path=path):
                self.assertEqual(worker.field_errors(self.entry, path, fields[path]), [])

    def test_repeated_literal_must_not_be_silently_dropped(self):
        self.assertTrue(worker.field_errors(self.entry, "tip", "libraryは図書館や資料の集まりを指します。"))

    def test_ipa_must_remain_verbatim(self):
        self.assertTrue(worker.field_errors(self.entry, "note", "発音は/ˈlaɪbrɛri/です。"))

    def test_source_language_echoes_and_placeholders_are_blocked(self):
        cases = [
            ("ex.0", self.entry["ex"][0]["en"]),
            ("ex.0", self.entry["ex"][0]["zh"]),
            ("tip", self.entry["tip"]),
            ("col.0", "public library｜公共図書館"),
            ("senses.0", "<unk>"),
            ("senses.0", "ZXQTERM"),
            ("ex.0", "[翻訳待ち]"),
            ("ex.0", "这是日文翻译。"),
        ]
        for path, text in cases:
            with self.subTest(path=path, text=text):
                self.assertTrue(worker.field_errors(self.entry, path, text))

    def test_adding_japanese_suffix_does_not_make_a_copied_english_sentence_a_translation(self):
        cases = [
            ("ex.0", self.entry["ex"][0]["en"] + "あ"),
            ("ex.1", self.entry["ex"][1]["en"] + "です。"),
            ("ex.1", "The library is closed。日曜日です。"),
        ]
        for path, text in cases:
            with self.subTest(path=path, text=text):
                self.assertTrue(worker.field_errors(self.entry, path, text))


class VerificationBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.entry = source_entry()
        self.fields = good_fields()

    def test_unaligned_draft_never_calls_model(self):
        class NeverCalled:
            args = SimpleNamespace(review_model="test-review")
            calls = 0

            def chat(self, *args, **kwargs):
                self.calls += 1
                raise AssertionError("The model must not align an incomplete draft")

        for fields in [None, {"senses.0": "図書館"}]:
            with self.subTest(fields=fields):
                client = NeverCalled()
                with self.assertRaises(ValueError):
                    worker.verify_entry(client, self.entry, fields, [{"text": "unaligned raw output"}])
                self.assertEqual(client.calls, 0)

    def test_verify_entry_returns_guarded_candidate_and_raw_review_audit(self):
        attempted = patch(self.fields, path="ex.1", text=self.entry["ex"][1]["en"],
                          reason="negation", evidence="closed on Sundays")
        raw_review = response(attempted)

        class FakeClient:
            args = SimpleNamespace(review_model="test-review")

            def chat(self, model, messages, **kwargs):
                return json.dumps(raw_review), {"eval_count": 10}

        result, audit, metrics = worker.verify_entry(FakeClient(), self.entry, self.fields, [])
        self.assertEqual(result, worker.overlay(self.entry, self.fields))
        self.assertFalse(audit["approved"])
        self.assertTrue(audit["needsReview"])
        self.assertEqual(audit["rawReview"], raw_review)
        self.assertEqual(metrics["eval_count"], 10)


class CandidateCacheTests(unittest.TestCase):
    def setUp(self):
        self.entry = source_entry()
        self.provenance = {"pipelineVersion": 5, "reviewModel": "test-review", "reviewDigest": "test-digest"}
        self.record = {
            "sourceSha256": hashlib.sha256(json.dumps(self.entry, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
            "provenance": copy.deepcopy(self.provenance),
            "verification": {"approved": True},
            "machineEligible": True,
            "needsReview": False,
            "candidate": worker.overlay(self.entry, good_fields()),
        }

    def test_current_machine_eligible_safe_candidate_can_be_reused_for_staging(self):
        original = copy.deepcopy((self.entry, self.record, self.provenance))
        self.assertTrue(worker.approved_cache(self.entry, self.record, self.provenance))
        self.assertEqual((self.entry, self.record, self.provenance), original)

    def test_old_pipeline_or_other_model_provenance_is_not_reused(self):
        for changed in [{"pipelineVersion": 4}, {"reviewDigest": "another-model-digest"}]:
            with self.subTest(changed=changed):
                record = copy.deepcopy(self.record)
                record["provenance"].update(changed)
                self.assertFalse(worker.approved_cache(self.entry, record, self.provenance))

    def test_different_source_cannot_reuse_old_candidate(self):
        changed = copy.deepcopy(self.entry)
        changed["ex"][0]["en"] = "I borrowed four books from the library."
        self.assertFalse(worker.approved_cache(changed, self.record, self.provenance))
        record = {**self.record, "sourceSha256": "wrong-source-hash"}
        self.assertFalse(worker.approved_cache(self.entry, record, self.provenance))

    def test_waiting_review_or_missing_machine_eligibility_cannot_be_reused(self):
        for change in [{"needsReview": True}, {"verification": {"approved": False}}, {"verification": {}},
                       {"machineEligible": False}, {"machineEligible": None}]:
            with self.subTest(change=change):
                record = {**self.record, **change}
                self.assertFalse(worker.approved_cache(self.entry, record, self.provenance))

    def test_machine_eligibility_does_not_bypass_candidate_language_checks(self):
        record = copy.deepcopy(self.record)
        record["candidate"]["ex"][0] = self.entry["ex"][0]["en"]
        self.assertFalse(worker.approved_cache(self.entry, record, self.provenance))
        record = copy.deepcopy(self.record)
        record["candidate"]["tip"] = self.entry["tip"]
        self.assertFalse(worker.approved_cache(self.entry, record, self.provenance))

    def test_invalid_or_missing_candidate_cannot_be_reused(self):
        for candidate in [None, {}, {**self.record["candidate"], "senses": []}, {**self.record["candidate"], "id": "wrong-id"}]:
            with self.subTest(candidate=candidate):
                record = {**self.record, "candidate": candidate}
                self.assertFalse(worker.approved_cache(self.entry, record, self.provenance))


class CandidateStagingIntegrationTests(unittest.TestCase):
    def test_machine_approved_translation_is_staged_without_writing_canonical_corpus(self):
        entry = source_entry()
        fields = good_fields()
        candidate = worker.overlay(entry, fields)
        audit = {"approved": True, "modelApproved": True, "acceptedPatches": [],
                 "rejectedPatches": [], "errors": [], "issues": [], "needsReview": False}
        tags = {"models": [
            {"name": "translategemma:12b-it-q8_0", "digest": "test-draft-digest"},
            {"name": "qwen3.5:9b-q8_0", "digest": "test-review-digest"},
        ]}
        with tempfile.TemporaryDirectory(prefix="ja-review-staging-test-") as directory:
            root = Path(directory)
            source = root / "public/atlas/entries/0.json"
            source.parent.mkdir(parents=True)
            source.write_text(json.dumps([entry], ensure_ascii=False), encoding="utf-8")
            cache = root / ".local/ja-local-v5/entries.json"
            canonical = root / "data/ja/entries/0.json"
            argv = [str(WORKER_PATH), "--cache", str(cache), "--start-chunk", "0", "--end-chunk", "0"]
            with mock.patch.object(worker, "ROOT", root), \
                    mock.patch("sys.argv", argv), \
                    mock.patch.object(worker, "Ollama"), \
                    mock.patch.object(worker.urllib.request, "urlopen", return_value=io.BytesIO(json.dumps(tags).encode())), \
                    mock.patch.object(worker, "draft_entry", return_value=(fields, [], {})), \
                    mock.patch.object(worker, "verify_entry", return_value=(candidate, audit, {})), \
                    redirect_stdout(io.StringIO()):
                worker.main()
            record = json.loads(cache.read_text(encoding="utf-8"))[entry["id"]]
            self.assertTrue(record["machineEligible"])
            self.assertEqual(record["candidate"], candidate)
            self.assertNotIn("final", record)
            self.assertIn("independent", record["semanticStatus"])
            staged_path = cache.parent / "candidate-chunks/0.json"
            self.assertTrue(staged_path.is_file())
            staged = json.loads(staged_path.read_text(encoding="utf-8"))
            self.assertEqual(staged["entries"], [candidate])
            self.assertEqual(staged["provenance"], record["provenance"])
            self.assertIn("independent", staged["semanticStatus"])
            self.assertFalse(canonical.exists(), "Model self-approval must never publish a canonical translation")


if __name__ == "__main__":
    unittest.main(verbosity=2)
