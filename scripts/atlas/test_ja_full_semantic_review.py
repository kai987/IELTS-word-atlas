"""Synthetic, offline tests for independent full-source review accounting."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).with_name("full_ja_semantic_review.py")
SPEC = importlib.util.spec_from_file_location("full_source_review_tested", SCRIPT)
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(m.encoded(value) + b"\n")


def entry(eid, en, ja):
    source = {"id": eid, "w": en, "meaning": en}
    japanese = {"id": eid, "senses": [ja], "note": ""}
    fields = []
    for path, mode, text, target in [("senses.0", "translate", en, ja),
                                     ("fam.0", "preserve", en + " (n.)", en + " (n.)"),
                                     ("note", "empty", "", "")]:
        fields.append({"path": path, "mode": mode, "sourceLanguage": "en", "sourceText": text,
            "currentJapanese": target, "writeLocation": {"file": "data/guard.json", "entryId": eid, "path": path, "kind": "entry-array"}})
    return {"id": eid, "word": en, "source": source, "japanese": japanese,
        "sourceSha256": m.sha(source), "japaneseSha256": m.sha(japanese), "fields": fields}


class FullSourceLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.patchers = [mock.patch.object(m, "ROOT", self.root),
                         mock.patch("urllib.request.urlopen", side_effect=AssertionError("No network")),
                         mock.patch("socket.create_connection", side_effect=AssertionError("No network"))]
        for p in self.patchers:
            p.start(); self.addCleanup(p.stop)
        helper = self.root / "scripts/atlas/full_ja_semantic_review.py"
        helper.parent.mkdir(parents=True); helper.write_bytes(SCRIPT.read_bytes())
        p = mock.patch.object(m, "__file__", str(helper)); p.start(); self.addCleanup(p.stop)
        self.run = self.root / ".local/current"
        self.guard = self.root / "data/guard.json"
        write(self.guard, {"frozen": True})
        self.snapshot = {"schemaVersion": 1, "entries": [entry("a", "house", "家"), entry("b", "tree", "木")],
            "manifest": {"files": {"data/guard.json": m.sha(self.guard.read_bytes())}}}
        write(self.run / "snapshot.json", self.snapshot)
        self.catalog = []

    def source_catalog(self, status="pass", quotes=True, suffix="one"):
        old = self.root / (".local/old-" + suffix)
        write(old / "snapshot.json", self.snapshot)
        selected = {"schemaVersion": 1, "snapshotSha256": m.sha((old / "snapshot.json").read_bytes()),
            "entryIds": ["a"], "entries": [self.snapshot["entries"][0]]}
        write(old / "selection.json", selected)
        reviewer = {"name": "Synthetic source reviewer " + suffix, "independent": True, "method": "Synthetic source comparison"}
        row = {"entryId": "a", "path": "senses.0", "expectedStatus": status,
            "note": "Synthetic source-grounded comparison", "categories": [] if status == "pass" else ["wrong_meaning"],
            "severity": None if status == "pass" else "minor"}
        if quotes:
            row.update(sourceQuote="house", targetQuote="家")
        gold = {"schemaVersion": 1, "reviewer": reviewer, "selectionSha256": m.sha(selected), "fields": [row]}
        write(old / "gold.json", gold)
        source = {"id": suffix, "kind": "independent-source-gold", "goldPath": m.relative(old / "gold.json"),
            "selectionPath": m.relative(old / "selection.json"), "snapshotRun": m.relative(old),
            "goldFileSha256": m.sha((old / "gold.json").read_bytes()), "goldCanonicalSha256": m.sha(gold),
            "selectionFileSha256": m.sha((old / "selection.json").read_bytes()), "selectionCanonicalSha256": m.sha(selected),
            "snapshotFileSha256": m.sha((old / "snapshot.json").read_bytes()), "reviewer": reviewer,
            "quoteAdapter": {"reviewerQuotesProvided": quotes}}
        return {"kind": "conservative-independent-source-gold-reuse-catalog", "sources": [source]}

    def prepare(self, catalog=None):
        self.catalog = [] if catalog is None else catalog
        catalog_path = self.run / "catalog.json"
        write(catalog_path, self.catalog)
        reused = m.import_reuse(self.snapshot, self.catalog)["fields"]
        pending = [e for e in self.snapshot["entries"] if any(f["mode"] == "translate" and
            m.field_key(e["id"], f["path"]) not in reused for f in e["fields"])]
        batches = []
        if pending:
            self.ids = [e["id"] for e in pending]
            packet = {"schemaVersion": 1, "batchId": "primary-0001", "snapshotSha256": m.sha((self.run / "snapshot.json").read_bytes()),
                "entryIds": self.ids, "translateFieldCount": len(pending),
                "entries": [{**e, "contextSha256": m.context_sha(e)} for e in pending]}
            path = self.run / "inputs/primary-0001.json"; write(path, packet)
            self.input_sha = m.sha(path.read_bytes())
            batches = [{"batchId": "primary-0001", "inputPath": m.relative(path), "inputFileSha256": self.input_sha,
                        "entryIds": self.ids, "entryCount": len(self.ids), "translateFieldCount": len(pending), "shard": 1}]
        write(self.run / "batches.json", {"schemaVersion": 1, "pendingEntries": len(pending),
            "pendingTranslateFields": len(pending), "reusedEntryIds": [e["id"] for e in self.snapshot["entries"] if e not in pending], "batches": batches})
        return m.prepare(self.run, catalog_path)

    def payload(self, issues=None):
        return {"batchId": "primary-0001", "inputFileSha256": self.input_sha,
            "reviewer": {"name": "Synthetic complete reviewer", "kind": "codex-independent-source", "independent": True},
            "reviewedEntryIds": self.ids, "attestation": {"allTranslationFieldsCompared": True, "sourcePriority": "en-when-available"},
            "issues": issues or [], "reviewedAt": "2026-10-27T00:00:00Z", "viewReceipts": [],
            "notes": {"method": {"sourceOnly": True}}}

    def issue(self, eid="a", status="error"):
        return {"entryId": eid, "path": "senses.0", "status": status, "categories": ["wrong_meaning"],
            "severity": "minor", "sourceQuote": "house" if eid == "a" else "tree",
            "targetQuote": "家" if eid == "a" else "木", "explanation": "Synthetic explicit source comparison"}

    def result(self, payload):
        path = self.run / "primary/primary-0001.json"; write(path, payload); return path

    def test_no_results_never_generate_source_pass_and_nontranslate_is_separate(self):
        self.prepare(); m.assemble(self.run)
        d = m.read(self.run / "source-ledger/status.json")
        self.assertEqual(d["counts"], {"pass": 0, "error": 0, "uncertain": 0, "not_reviewed": 2})
        self.assertEqual(d["deterministicNontranslate"], {"preserve": 2, "empty": 2, "pass": 4, "error": 0})
        self.assertFalse(d["semanticAcceptanceClear"])

    def test_explicit_complete_batch_pass_and_immutable_validation(self):
        self.prepare(); path = self.result(self.payload()); m.validate(self.run, path)
        m.assemble(self.run); m.assemble(self.run)
        self.assertEqual(m.read(self.run / "source-ledger/status.json")["counts"]["pass"], 2)
        changed = self.payload(); changed["notes"] = "Changed after validation"; write(path, changed)
        with self.assertRaises(m.ReviewError): m.assemble(self.run)

    def test_partial_duplicate_or_reordered_ids_never_make_pass(self):
        self.prepare()
        for ids in [["a"], ["a", "a"], ["b", "a"]]:
            value = self.payload(); value["reviewedEntryIds"] = ids; path = self.result(value)
            with self.assertRaises(m.ReviewError): m.validate(self.run, path)
            self.assertFalse((self.run / "source-ledger/validated/primary-0001.json").exists())

    def test_missing_false_or_numeric_attestation_is_refused(self):
        self.prepare()
        for flag in [False, 1, "true", None]:
            value = self.payload(); value["attestation"]["allTranslationFieldsCompared"] = flag
            with self.assertRaises(m.ReviewError): m.validate_payload(self.run, value)

    def test_wrong_quotes_unknown_nontranslate_and_duplicate_issues_refused(self):
        self.prepare()
        for mutate in [lambda x: x.update(sourceQuote="absent"), lambda x: x.update(targetQuote="不存在"),
                       lambda x: x.update(path="fam.0"), lambda x: x.update(entryId="unknown"),
                       lambda x: x.update(unrecognized=True)]:
            issue = self.issue(); mutate(issue)
            with self.assertRaises(m.ReviewError): m.validate_payload(self.run, self.payload([issue]))
        with self.assertRaises(m.ReviewError): m.validate_payload(self.run, self.payload([self.issue(), self.issue()]))

    def test_error_uncertain_and_pass_counts_keep_tentative_severity(self):
        self.prepare(); self.result(self.payload([self.issue("a", "uncertain")]))
        m.assemble(self.run); status = m.read(self.run / "source-ledger/status.json")
        self.assertEqual(status["counts"], {"pass": 1, "error": 0, "uncertain": 1, "not_reviewed": 0})
        issue = json.loads((self.run / "source-ledger/issues.jsonl").read_text())
        self.assertTrue(issue["severityTentative"]); self.assertFalse(status["semanticAcceptanceClear"])

    def test_unknown_result_field_or_machine_reviewer_is_refused(self):
        self.prepare(); value = self.payload(); value["prediction"] = "pass"
        with self.assertRaises(m.ReviewError): m.validate_payload(self.run, value)
        value = self.payload(); value["reviewer"]["kind"] = "local-model"
        with self.assertRaises(m.ReviewError): m.validate_payload(self.run, value)

    def test_reuse_pass_and_missing_pilot_quotes_keep_origin_honest(self):
        self.prepare(self.source_catalog(quotes=False)); m.assemble(self.run)
        reuse = m.read(self.run / "source-ledger/reuse.json")["fields"]["a\tsenses.0"]
        self.assertEqual(reuse["status"], "pass"); self.assertEqual(reuse["quoteOrigin"], "snapshot-binding")
        self.assertNotIn("sourceQuote", reuse["provenance"]["originalRow"])
        self.assertEqual(m.read(self.run / "source-ledger/status.json")["counts"]["not_reviewed"], 1)

    def test_source_target_and_other_entry_context_change_invalidate_reuse(self):
        catalog = self.source_catalog()
        for kind in ["source", "target", "context", "field-source", "field-target", "field-language"]:
            snapshot = copy.deepcopy(self.snapshot); e = snapshot["entries"][0]
            if kind == "source": e["source"]["meaning"] = "different source"
            elif kind == "target": e["japanese"]["senses"][0] = "違う"
            elif kind == "context": e["japanese"]["note"] = "Changed sibling context"
            elif kind == "field-source": e["fields"][0]["sourceText"] = "other"
            elif kind == "field-target": e["fields"][0]["currentJapanese"] = "他"
            else: e["fields"][0]["sourceLanguage"] = "zh-Hans"
            imported = m.import_reuse(snapshot, catalog)
            self.assertEqual(imported["fields"], {}); self.assertEqual(len(imported["invalidated"]), 1)

    def test_conflicting_same_context_gold_becomes_uncertain(self):
        first = self.source_catalog(); second = self.source_catalog(status="error", suffix="two")
        first["sources"] += second["sources"]
        imported = m.import_reuse(self.snapshot, first)
        self.assertEqual(imported["fields"]["a\tsenses.0"]["status"], "uncertain")
        self.assertEqual(len(imported["conflicts"]), 1)

    def test_non_independent_or_machine_catalog_is_refused(self):
        value = self.source_catalog(); value["sources"][0]["kind"] = "machine-assessment"
        with self.assertRaises(m.ReviewError): m.import_reuse(self.snapshot, value)
        with self.assertRaises(m.ReviewError): m.import_reuse(self.snapshot, {"records": [{"status": "pass"}]})

    def test_snapshot_or_input_or_production_drift_blocks_preflight(self):
        self.prepare()
        for path in [self.run / "snapshot.json", self.run / "inputs/primary-0001.json", self.guard]:
            old = path.read_bytes(); path.write_bytes(old + b"\n")
            with self.assertRaises(m.ReviewError): m.preflight(self.run)
            path.write_bytes(old)

    def test_invalid_result_assemble_writes_no_completion(self):
        self.prepare(); value = self.payload(); value["reviewedEntryIds"] = ["a"]; self.result(value)
        with self.assertRaises(m.ReviewError): m.assemble(self.run)
        self.assertFalse((self.run / "source-ledger/status.json").exists())
        self.assertFalse((self.run / "source-ledger/validated/primary-0001.json").exists())

    def test_prepare_never_overwrites_frozen_ledger(self):
        self.prepare()
        with self.assertRaises(m.ReviewError): m.prepare(self.run, self.run / "catalog.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
