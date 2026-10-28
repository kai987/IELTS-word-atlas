#!/usr/bin/env python3
"""Bound second source reviews; preserve every original decision and production byte."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import full_ja_semantic_review as first


def ticket_for(record, entry, field):
    binding = {"entryId": entry["id"], "path": field["path"],
               "contextSha256": first.context_sha(entry), "firstReviewSha256": first.sha(record)}
    return {"schemaVersion": 1, "ticketId": first.sha(binding), **binding,
            "word": entry["word"], "firstReview": record, "field": field,
            "context": {"source": entry["source"], "japanese": entry["japanese"]}}


def supplementary_findings(run, entries, source_decisions):
    """Reopen an already reviewed pass with a separately authored source finding."""
    found = {}
    required = {"schemaVersion", "entryId", "path", "contextSha256", "originalSourceReviewSha256",
                "reviewer", "status", "categories", "severity", "sourceQuote", "targetQuote", "explanation", "attestation"}
    for path in sorted((run / "source-findings").glob("*.json")):
        value = first.read(path)
        first.require(isinstance(value, dict) and required <= set(value) <= required | {"suggestion", "references", "reviewedAt"},
                      "Invalid supplementary source finding")
        key = first.field_key(value["entryId"], value["path"])
        first.require(key in source_decisions and key not in found, "Unknown/duplicate supplementary field")
        original = source_decisions[key]
        first.require(original["status"] == "pass" and value["status"] in {"error", "uncertain"},
                      "A supplementary finding may only reopen an existing pass")
        entry = entries[value["entryId"]]
        field = next(f for f in entry["fields"] if f["path"] == value["path"])
        first.require(value["schemaVersion"] == 1 and field["mode"] == "translate"
                      and value["contextSha256"] == first.context_sha(entry)
                      and value["originalSourceReviewSha256"] == first.sha(original), "Stale supplementary source binding")
        first.require(path.stem == first.sha({"entryId": value["entryId"], "path": value["path"]}), "Supplementary filename mismatch")
        # Reuse strict assessment/quote/attestation checks without manufacturing a persisted source decision.
        prior = ticket_for(original, entry, field)
        common = {k: value[k] for k in ("schemaVersion", "reviewer", "status", "categories", "severity", "sourceQuote",
                                      "targetQuote", "explanation", "attestation")}
        common.update({k: value[k] for k in ("suggestion", "references", "reviewedAt") if k in value})
        common.update(ticketId=prior["ticketId"], ticketFileSha256=first.sha(first.encoded(prior)))
        validate_result(common, {prior["ticketId"]: prior})
        record = {k: value[k] for k in ("entryId", "path", "reviewer", "status", "categories", "severity",
                                       "sourceQuote", "targetQuote", "explanation", "contextSha256")}
        record.update({k: value[k] for k in ("suggestion", "references") if k in value})
        record.update(quoteOrigin="reviewer", provenance={"kind": "supplementary-source-finding",
            "rawFinding": first.file_ref(path), "originalSourceReviewSha256": first.sha(original),
            "originalSourceReview": original, "attestation": value["attestation"]})
        sealed = {"finding": first.file_ref(path), "sourceReview": record}
        marker = run / "focus-review/validated-source-findings" / path.name
        first.require(not marker.exists() or first.read(marker) == sealed, "Validated supplementary finding changed")
        found[key] = sealed
    return found


def current_tickets(run):
    prepared = first.preflight(run)
    run, snapshot, entries, manifest, _ = prepared
    # Recompute from immutable primary inputs rather than trust a possibly old derived ledger.
    decisions = dict(first.read(run / "source-ledger/reuse.json")["fields"])
    for path in sorted((run / "primary").glob("*.json")):
        payload = first.read(path)
        first.require(path.name == payload.get("batchId", "") + ".json", "Primary filename mismatch")
        validated = first.validate_payload(run, payload, prepared)
        validated["rawResult"] = first.file_ref(path)
        validated["rawResultCanonicalSha256"] = first.sha(payload)
        frozen = run / "source-ledger/validated" / path.name
        first.require(not frozen.exists() or first.read(frozen) == validated, "Previously validated primary result changed")
        for record in validated["decisions"]:
            key = first.field_key(record["entryId"], record["path"])
            first.require(key not in decisions, "Overlapping source decisions")
            record["provenance"]["rawResult"] = first.file_ref(path)
            decisions[key] = record
    for key, value in supplementary_findings(run, entries, decisions).items():
        decisions[key] = value["sourceReview"]
    tickets = {}
    for record in decisions.values():
        if record["status"] not in {"error", "uncertain"}:
            continue
        entry = entries[record["entryId"]]
        field = next(f for f in entry["fields"] if f["path"] == record["path"])
        ticket = ticket_for(record, entry, field)
        tickets[ticket["ticketId"]] = ticket
    return run, snapshot, tickets


def prepare(run):
    run, _, tickets = current_tickets(run)
    for ticket_id, ticket in tickets.items():
        path = run / "focus-review/tickets" / (ticket_id + ".json")
        if path.exists():
            first.require(first.read(path) == ticket, "Frozen focus ticket changed")
        else:
            first.exclusive_json(path, ticket)
    return {"tickets": len(tickets), "folder": first.relative(run / "focus-review/tickets")}


def validate_result(payload, tickets):
    required = {"schemaVersion", "ticketId", "ticketFileSha256", "reviewer", "status", "categories",
                "severity", "sourceQuote", "targetQuote", "explanation", "attestation"}
    first.require(isinstance(payload, dict) and required <= set(payload) <= required | {"suggestion", "references", "reviewedAt"},
                  "Missing/unknown focus result fields")
    first.require(payload["schemaVersion"] == 1 and payload["ticketId"] in tickets, "Unknown/stale focus ticket")
    ticket = tickets[payload["ticketId"]]
    reviewer = payload["reviewer"]
    first.require(isinstance(reviewer, dict) and set(reviewer) == {"name", "kind", "independent"}
                  and first._text(reviewer["name"]) and reviewer["kind"] == "codex-independent-source"
                  and reviewer["independent"] is True, "Named independent source reviewer required")
    first.require(reviewer["name"] != ticket["firstReview"]["reviewer"]["name"], "Reviewer cannot adjudicate own first decision")
    first.require(isinstance(payload["attestation"], dict)
                  and set(payload["attestation"]) == {"fieldAndFullContextCompared", "sourcePriority"}
                  and payload["attestation"]["fieldAndFullContextCompared"] is True
                  and payload["attestation"]["sourcePriority"] == "en-when-available",
                  "Explicit source/context comparison required")
    status = payload["status"]
    first.require(status in first.STATUSES, "Invalid focus status")
    categories = payload["categories"]
    first.require(isinstance(categories, list) and len(categories) == len(set(categories))
                  and set(categories) <= first.CATEGORIES, "Invalid focus categories")
    first.require((status == "error" and bool(categories) and payload["severity"] in first.SEVERITIES)
                  or (status == "pass" and categories == [] and payload["severity"] is None)
                  or (status == "uncertain" and payload["severity"] in first.SEVERITIES | {None}), "Invalid focus severity/status")
    first._quotes(payload["sourceQuote"], payload["targetQuote"], ticket["field"])
    first.require(first._text(payload["explanation"]), "Specific source-based explanation required")
    first.require("suggestion" not in payload or first._text(payload["suggestion"]), "Empty suggestion")
    refs = payload.get("references", [])
    first.require(isinstance(refs, list) and all(isinstance(r, dict) and set(r) == {"url", "use"}
                  and isinstance(r["url"], str) and r["url"].startswith("https://") and first._text(r["use"]) for r in refs),
                  "Invalid dictionary/source references")
    return ticket


def reconsiderations(run, tickets, originals):
    """An author may withdraw their own error confirmation; no new approval votes."""
    values = {}
    folder = run / "focus-review"
    for path in sorted((folder / "reconsiderations").glob("*.json")):
        payload = first.read(path)
        required = {"schemaVersion", "ticketId", "contextSha256", "supersedesResultFileSha256", "reason", "assessment"}
        first.require(isinstance(payload, dict) and set(payload) == required and payload["schemaVersion"] == 1,
                      "Invalid reconsideration record")
        tid = payload["ticketId"]
        first.require(tid in tickets and tid in originals and path.name == tid + ".json", "Unknown reconsideration")
        original = originals[tid]
        first.require(payload["contextSha256"] == tickets[tid]["contextSha256"]
                      and payload["supersedesResultFileSha256"] == original["result"]["fileSha256"], "Stale reconsideration binding")
        updated = payload["assessment"]
        validate_result(updated, tickets)
        first.require(updated["ticketId"] == tid and updated["reviewer"] == original["assessment"]["reviewer"]
                      and updated["ticketFileSha256"] == original["assessment"]["ticketFileSha256"], "Reconsideration author/input mismatch")
        first.require(original["assessment"]["status"] == "error" and updated["status"] == "uncertain"
                      and first._text(payload["reason"]), "Only conservative withdrawal of own error is supported")
        value = {"record": first.file_ref(path), "payload": payload}
        marker = folder / "validated-reconsiderations" / path.name
        first.require(not marker.exists() or first.read(marker) == value, "Validated reconsideration changed")
        values[tid] = value
    return values


def assemble(run):
    run, snapshot, tickets = current_tickets(run)
    folder = run / "focus-review"
    decisions = {}
    for path in sorted((folder / "results").glob("*.json")):
        payload = first.read(path)
        ticket = validate_result(payload, tickets)
        ticket_path = folder / "tickets" / (ticket["ticketId"] + ".json")
        first.require(path.name == ticket["ticketId"] + ".json", "Focus result filename mismatch")
        first.require(first.read(ticket_path) == ticket and first.sha(ticket_path.read_bytes()) == payload["ticketFileSha256"],
                      "Focus result input changed")
        validated = {"ticketId": ticket["ticketId"], "ticket": first.file_ref(ticket_path),
                     "result": first.file_ref(path), "assessment": payload}
        marker = folder / "validated" / path.name
        if marker.exists():
            first.require(first.read(marker) == validated, "Previously validated second decision changed")
        decisions[ticket["ticketId"]] = (marker, validated)
    withdrawn = reconsiderations(run, tickets, {tid: value for tid, (_, value) in decisions.items()})
    # Validate every result and the source bindings before persisting any new acceptance.
    first.preflight(run)
    for marker, validated in decisions.values():
        if not marker.exists():
            first.exclusive_json(marker, validated)
    for tid, value in withdrawn.items():
        marker = folder / "validated-reconsiderations" / (tid + ".json")
        if not marker.exists():
            first.exclusive_json(marker, value)
    supplements = []
    for ticket in tickets.values():
        record = ticket["firstReview"]
        if record["provenance"]["kind"] != "supplementary-source-finding":
            continue
        sealed = {"finding": record["provenance"]["rawFinding"], "sourceReview": record}
        marker = folder / "validated-source-findings" / Path(sealed["finding"]["path"]).name
        if not marker.exists():
            first.exclusive_json(marker, sealed)
        supplements.append(sealed["finding"])
    rows, unresolved, counts = [], [], Counter({"pass": 0, "error": 0, "uncertain": 0, "awaiting_second_review": 0})
    for ticket_id, ticket in tickets.items():
        second = decisions.get(ticket_id)
        assessment = second[1]["assessment"] if second else None
        withdrawal = withdrawn.get(ticket_id)
        if withdrawal:
            assessment = withdrawal["payload"]["assessment"]
        effective = assessment["status"] if assessment else ticket["firstReview"]["status"]
        counts[assessment["status"] if assessment else "awaiting_second_review"] += 1
        row = {**ticket, "secondReview": second[1] if second else None, "effectiveStatus": effective,
               "productionApplied": False, "originalDecisionPreserved": True}
        if withdrawal:
            row["reconsideration"] = withdrawal
        rows.append(row)
        if effective != "pass":
            unresolved.append(row)
    status = {"schemaVersion": 1, "asOf": datetime.now(timezone.utc).isoformat(), "tickets": len(tickets),
              "counts": dict(counts), "unresolved": len(unresolved), "unreviewedCorpusFieldsIncluded": False,
              "conservativeWithdrawals": len(withdrawn),
              "supplementarySourceFindings": len(supplements),
              "productionModified": False, "professionalHumanCertification": False,
              "note": "A focused second pass of flagged fields; not a full-corpus completion or human certification."}
    first.atomic_json(folder / "status.json", status)
    first.atomic_json(folder / "ledger.json", rows)
    (folder / "unresolved.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in unresolved))
    lines = ["# 日译语义复审：重点问题", "", "保留初审与二审原记录；建议尚未写入生产词库。", ""]
    for row in unresolved:
        assessment = row["reconsideration"]["payload"]["assessment"] if row.get("reconsideration") else (
            row["secondReview"]["assessment"] if row["secondReview"] else row["firstReview"])
        lines += ["## " + row["entryId"] + " / " + row["path"], "", "状态：" + row["effectiveStatus"]
                  + ("（等待二审）" if not row["secondReview"] else "（已二审）"), "",
                  "源文：" + row["field"]["sourceText"], "", "日译：" + row["field"]["currentJapanese"], "",
                  "说明：" + assessment["explanation"], ""]
        if row.get("reconsideration"):
            lines += ["补充：同二审者基于新证据撤回确认错误，原二审记录保留。", ""]
        if assessment.get("suggestion"):
            lines += ["候选修改：" + assessment["suggestion"], ""]
    (folder / "unresolved.md").write_text("\n".join(lines))
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "assemble"])
    parser.add_argument("--run", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps((prepare if args.command == "prepare" else assemble)(args.run), ensure_ascii=False))
        return 0
    except (first.ReviewError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "refused", "reason": str(error) if isinstance(error, first.ReviewError)
                          else "Malformed source/focus artifact; no new acceptance"}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
