"""Source binding and immutable second-review regression checks, entirely offline."""
import copy
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.dont_write_bytecode = True
import test_ja_full_semantic_review as fixtures

SPEC = importlib.util.spec_from_file_location("tested_focus_review", Path(__file__).with_name("adjudicate_ja_full_review.py"))
a = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(a)


class FocusReviewTests(unittest.TestCase):
    prepare = fixtures.FullSourceLedgerTests.prepare
    payload = fixtures.FullSourceLedgerTests.payload
    issue = fixtures.FullSourceLedgerTests.issue
    result = fixtures.FullSourceLedgerTests.result
    source_catalog = fixtures.FullSourceLedgerTests.source_catalog

    def setUp(self):
        fixtures.FullSourceLedgerTests.setUp(self)
        patch = mock.patch.object(a, "first", fixtures.m)
        patch.start(); self.addCleanup(patch.stop)

    def fixture(self):
        self.prepare()
        original = self.result(self.payload([self.issue()]))
        fixtures.m.validate(self.run, original)
        a.prepare(self.run)
        tickets = a.current_tickets(self.run)[2]
        ticket_id, ticket = next(iter(tickets.items()))
        ticket_path = self.run / "focus-review/tickets" / (ticket_id + ".json")
        result = {"schemaVersion": 1, "ticketId": ticket_id,
                  "ticketFileSha256": fixtures.m.sha(ticket_path.read_bytes()),
                  "reviewer": {"name": "Different source reviewer", "kind": "codex-independent-source", "independent": True},
                  "status": "pass", "categories": [], "severity": None,
                  "sourceQuote": "house", "targetQuote": "家", "explanation": "The Japanese means house; first issue was not supported.",
                  "attestation": {"fieldAndFullContextCompared": True, "sourcePriority": "en-when-available"}}
        return original, tickets, result

    def save(self, result):
        path = self.run / "focus-review/results" / (result["ticketId"] + ".json")
        fixtures.write(path, result)
        return path

    def test_no_primary_review_creates_no_focus_or_approval(self):
        self.prepare()
        self.assertEqual(a.prepare(self.run)["tickets"], 0)
        self.assertEqual(a.assemble(self.run)["tickets"], 0)
        fixtures.m.assemble(self.run)
        self.assertEqual(fixtures.m.read(self.run / "source-ledger/status.json")["counts"]["not_reviewed"], 2)

    def test_second_pass_keeps_first_record_and_separate_denominator(self):
        original, tickets, result = self.fixture()
        before = original.read_bytes()
        self.save(result)
        status = a.assemble(self.run)
        self.assertEqual(status["counts"]["pass"], 1)
        self.assertEqual(status["unresolved"], 0)
        self.assertEqual(original.read_bytes(), before)
        fixtures.m.assemble(self.run)
        self.assertEqual(fixtures.m.read(self.run / "source-ledger/status.json")["counts"]["error"], 1)

    def test_same_reviewer_or_missing_actual_comparison_is_rejected(self):
        _, tickets, result = self.fixture()
        result["reviewer"]["name"] = "Synthetic complete reviewer"
        with self.assertRaises(fixtures.m.ReviewError): a.validate_result(result, tickets)
        result["reviewer"]["name"] = "Other"
        for value in [False, 1, "true", None]:
            result["attestation"]["fieldAndFullContextCompared"] = value
            with self.assertRaises(fixtures.m.ReviewError): a.validate_result(result, tickets)

    def test_stale_ticket_and_cross_field_quotes_are_rejected(self):
        _, tickets, result = self.fixture()
        for change in [{"ticketId": "bad"}, {"sourceQuote": "tree"}, {"targetQuote": "木"}, {"status": "approved"}]:
            invalid = copy.deepcopy(result); invalid.update(change)
            with self.assertRaises(fixtures.m.ReviewError): a.validate_result(invalid, tickets)

    def test_input_byte_change_is_rejected_before_accepting_result(self):
        _, _, result = self.fixture()
        result["ticketFileSha256"] = "0" * 64
        self.save(result)
        with self.assertRaises(fixtures.m.ReviewError): a.assemble(self.run)
        self.assertFalse((self.run / "focus-review/validated").exists())

    def test_validated_result_cannot_be_rewritten(self):
        _, _, result = self.fixture()
        self.save(result); a.assemble(self.run)
        result["explanation"] = "Changed after validation"
        self.save(result)
        with self.assertRaises(fixtures.m.ReviewError): a.assemble(self.run)

    def test_primary_record_and_current_corpus_must_remain_frozen(self):
        original, _, result = self.fixture()
        changed = fixtures.m.read(original); changed["notes"] = "changed"
        fixtures.write(original, changed)
        with self.assertRaises(fixtures.m.ReviewError): a.prepare(self.run)
        self.guard.write_text("changed corpus")
        with self.assertRaises(fixtures.m.ReviewError): a.assemble(self.run)

    def withdrawal(self, result):
        result["status"] = "error"
        result["categories"] = ["wrong_meaning"]
        result["severity"] = "minor"
        path = self.save(result)
        a.assemble(self.run)
        updated = copy.deepcopy(result)
        updated["status"] = "uncertain"
        updated["explanation"] = "New source evidence permits a different interpretation; confirmation withdrawn."
        tid = result["ticketId"]
        ticket = a.current_tickets(self.run)[2][tid]
        value = {"schemaVersion": 1, "ticketId": tid, "contextSha256": ticket["contextSha256"],
                 "supersedesResultFileSha256": fixtures.m.sha(path.read_bytes()), "reason": "New dictionary evidence",
                 "assessment": updated}
        dest = self.run / "focus-review/reconsiderations" / (tid + ".json")
        return path, dest, value

    def test_conservative_withdrawal_preserves_error_history(self):
        _, _, result = self.fixture()
        original, dest, value = self.withdrawal(result)
        before = original.read_bytes()
        fixtures.write(dest, value)
        status = a.assemble(self.run)
        self.assertEqual(status["conservativeWithdrawals"], 1)
        self.assertEqual(status["counts"]["uncertain"], 1)
        self.assertEqual(original.read_bytes(), before)
        row = fixtures.m.read(self.run / "focus-review/ledger.json")[0]
        self.assertEqual(row["secondReview"]["assessment"]["status"], "error")
        self.assertEqual(row["effectiveStatus"], "uncertain")

    def test_withdrawal_cannot_approve_or_change_reviewer_or_source(self):
        _, _, result = self.fixture()
        _, dest, value = self.withdrawal(result)
        for mutate in [lambda v: v["assessment"].update(status="pass", categories=[], severity=None),
                       lambda v: v["assessment"]["reviewer"].update(name="Other reviewer"),
                       lambda v: v.update(contextSha256="changed"),
                       lambda v: v.update(supersedesResultFileSha256="changed")]:
            changed = copy.deepcopy(value); mutate(changed); fixtures.write(dest, changed)
            with self.assertRaises(fixtures.m.ReviewError): a.assemble(self.run)
        self.assertFalse((self.run / "focus-review/validated-reconsiderations").exists())

    def test_validated_withdrawal_is_immutable(self):
        _, _, result = self.fixture()
        _, dest, value = self.withdrawal(result)
        fixtures.write(dest, value); a.assemble(self.run)
        value["reason"] = "Changed after validation"; fixtures.write(dest, value)
        with self.assertRaises(fixtures.m.ReviewError): a.assemble(self.run)

    def source_finding(self):
        self.prepare()
        self.result(self.payload()); fixtures.m.assemble(self.run)
        initial = fixtures.m.read(self.run / "source-ledger/ledger.json")[0]
        value = {"schemaVersion": 1, "entryId": initial["entryId"], "path": initial["path"],
                 "contextSha256": initial["contextSha256"], "originalSourceReviewSha256": fixtures.m.sha(initial["sourceReview"]),
                 "reviewer": {"name": "Different source auditor", "kind": "codex-independent-source", "independent": True},
                 "status": "uncertain", "categories": ["wrong_meaning"], "severity": "minor",
                 "sourceQuote": "house", "targetQuote": "家", "explanation": "Synthetic field reopened for another independent comparison.",
                 "attestation": {"fieldAndFullContextCompared": True, "sourcePriority": "en-when-available"}}
        dest = self.run / "source-findings" / (fixtures.m.sha({"entryId": initial["entryId"], "path": initial["path"]}) + ".json")
        return dest, value

    def test_source_pass_reopened_without_overwriting_original_or_creating_second_approval(self):
        dest, value = self.source_finding(); fixtures.write(dest, value)
        self.assertEqual(a.prepare(self.run)["tickets"], 1)
        status = a.assemble(self.run)
        self.assertEqual(status["supplementarySourceFindings"], 1)
        self.assertEqual(status["counts"]["awaiting_second_review"], 1)
        self.assertEqual(fixtures.m.read(self.run / "source-ledger/ledger.json")[0]["status"], "pass")
        row = fixtures.m.read(self.run / "focus-review/ledger.json")[0]
        self.assertEqual(row["effectiveStatus"], "uncertain")
        self.assertEqual(row["firstReview"]["provenance"]["originalSourceReview"]["status"], "pass")

    def test_supplement_requires_unchanged_source_original_pass_and_different_auditor(self):
        dest, value = self.source_finding()
        for mutate in [lambda v: v.update(originalSourceReviewSha256="changed"),
                       lambda v: v.update(contextSha256="changed"),
                       lambda v: v.update(sourceQuote="tree"),
                       lambda v: v.update(status="pass", categories=[], severity=None),
                       lambda v: v["reviewer"].update(name="Synthetic complete reviewer")]:
            changed = copy.deepcopy(value); mutate(changed); fixtures.write(dest, changed)
            with self.assertRaises(fixtures.m.ReviewError): a.prepare(self.run)

    def test_validated_source_finding_is_immutable(self):
        dest, value = self.source_finding(); fixtures.write(dest, value); a.prepare(self.run); a.assemble(self.run)
        value["explanation"] = "Changed after validation"; fixtures.write(dest, value)
        with self.assertRaises(fixtures.m.ReviewError): a.prepare(self.run)


if __name__ == "__main__":
    unittest.main()
