#!/usr/bin/env python3
"""Validate blinded, source-grounded field annotations before unmasking labels."""
from pathlib import Path
from collections import Counter
import argparse
import json

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / '.local/ja-quant-benchmark/evaluation'
CATEGORIES = {'wrong_meaning', 'omission', 'addition_or_fabrication', 'negation_or_modality',
              'quantity_time_or_entity', 'grammar_or_terminology', 'untranslated'}

def raw_strings(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for item in value for text in raw_strings(item)]
    if isinstance(value, dict):
        return [text for item in value.values() for text in raw_strings(item)]
    return []

parser = argparse.ArgumentParser()
parser.add_argument('--unblind', action='store_true')
parser.add_argument('--artifacts', type=Path, default=BASE.parent)
args = parser.parse_args()
BASE = args.artifacts / 'evaluation'
packets = {}
for path in sorted((BASE / 'packets').glob('*.json')):
    for case in json.loads(path.read_text())['cases']:
        assert case['case'] not in packets
        packets[case['case']] = case
scores = {}
problems = []
for path in sorted((BASE / 'scores').glob('*.json')):
    for score in json.loads(path.read_text())['cases']:
        cid = score['case']
        if cid in scores:
            problems.append(f'Duplicate score: {cid}')
            continue
        scores[cid] = score
        if cid not in packets:
            problems.append(f'Unknown case: {cid}')
            continue
        case = packets[cid]
        source = {row['path']: row['text'] for row in case['sourceFields']}
        evaluated = score['evaluatedFields']
        unavailable = score['unavailableFields']
        if len(evaluated) != len(set(evaluated)) or len(unavailable) != len(set(unavailable)):
            problems.append(f'Duplicate field coverage: {cid}')
        if set(evaluated) & set(unavailable) or set(evaluated) | set(unavailable) != set(source):
            problems.append(f'Incomplete or overlapping coverage: {cid}')
        error_paths = []
        for error in score['errors']:
            field = error['path']
            error_paths.append(field)
            if field not in evaluated:
                problems.append(f'Error on unevaluated field: {cid}/{field}')
            if error['category'] not in CATEGORIES:
                problems.append(f'Invalid category: {cid}/{field}')
            evidence = error.get('sourceEvidence', '')
            if not evidence or evidence not in source.get(field, ''):
                problems.append(f'Source evidence is not a literal source excerpt: {cid}/{field}')
            if not error.get('reason', '').strip():
                problems.append(f'Missing reasoning: {cid}/{field}')
        if len(error_paths) != len(set(error_paths)):
            problems.append(f'More than one counted error per field: {cid}')
        borderline_paths = []
        for item in score.get('borderline', []):
            field = item['path']
            borderline_paths.append(field)
            if field not in evaluated or not item.get('reason', '').strip():
                problems.append(f'Invalid borderline annotation: {cid}/{field}')
            if not item.get('sourceEvidence') or item['sourceEvidence'] not in source.get(field, ''):
                problems.append(f'Borderline evidence is not a literal source excerpt: {cid}/{field}')
        if len(borderline_paths) != len(set(borderline_paths)):
            problems.append(f'Duplicate borderline field: {cid}')
        # Unavailable fields may be aligned from untouched raw drafts only if recorded.
        newly_available = set(evaluated) & set(case['unavailableFields'])
        if newly_available:
            alignments = score.get('rawAlignment', {})
            if not newly_available.issubset(alignments):
                problems.append(f'Unrecorded raw draft alignment: {cid}')
            for field in newly_available:
                value = alignments.get(field, '')
                if not value or not any(value in text for text in raw_strings(case.get('rawDraftFallback'))):
                    problems.append(f'Raw alignment text absent from fallback: {cid}/{field}')

report = {'expectedCases': 400, 'exportedCases': len(packets), 'scoredCases': len(scores),
          'missingCases': sorted(set(packets) - set(scores)), 'problems': problems,
          'unmasked': False}
if args.unblind:
    assert not problems and len(packets) == 400 and set(scores) == set(packets), report
    # Secondary checks must be finished while labels are still hidden.
    for prefix in ['D', 'R']:
        for number in range(1, 11):
            name = f'{prefix}-{number:02}'
            path = BASE / 'adjudications' / f'{name}.json'
            assert path.exists(), f'Missing blinded adjudication: {name}'
            audit = json.loads(path.read_text())
            assert audit.get('status') == 'complete' and audit.get('labelsRevealed') is False, name
            score_path = BASE / 'scores' / f'{name}.json'
            batch = json.loads(score_path.read_text())['cases']
            for key, count_key, actual in [
                ('confirmedErrorFields', 'confirmedErrorFieldCount', sum(len(c['errors']) for c in batch)),
                ('confirmedBorderlineFields', 'confirmedBorderlineFieldCount', sum(len(c.get('borderline', [])) for c in batch))]:
                expected = audit.get(count_key, audit.get(key))
                if isinstance(expected, list):
                    expected = len(expected)
                assert expected == actual, f'Stale adjudication count: {name}/{key}'
            if audit.get('scoreSha256After'):
                import hashlib
                assert audit['scoreSha256After'] == hashlib.sha256(score_path.read_bytes()).hexdigest(), name
    # No quantization mapping is read until complete source-grounded coverage passes.
    key = json.loads((BASE / 'private-key.json').read_text())['cases']
    groups = {}
    for stage in ['draft', 'reviewed']:
        for variant in ['q4', 'q8']:
            cases = [(cid, score) for cid, score in scores.items()
                     if key[cid]['stage'] == stage and key[cid]['variant'] == variant]
            evaluated = sum(len(s['evaluatedFields']) for _, s in cases)
            unavailable = sum(len(s['unavailableFields']) for _, s in cases)
            errors = sum(len(s['errors']) for _, s in cases)
            categories = Counter(e['category'] for _, s in cases for e in s['errors'])
            groups[f'{stage}/{variant}'] = {
                'entries': len(cases), 'evaluatedFields': evaluated,
                'unavailableFields': unavailable, 'substantiveErrorFields': errors,
                'errorRateAmongEvaluatedFields': round(errors / max(evaluated, 1), 6),
                'entriesWithSubstantiveError': sum(bool(s['errors']) for _, s in cases),
                'entriesWithUnavailableField': sum(bool(s['unavailableFields']) for _, s in cases),
                'borderlineFields': sum(len({b['path'] for b in s.get('borderline', [])}) for _, s in cases),
                'errorCategories': dict(categories),
                'annotations': [{'case': cid, 'id': key[cid]['id'], 'errors': s['errors'],
                                 'unavailableFields': s['unavailableFields'],
                                 'borderline': s.get('borderline', []),
                                 'formatNotes': s.get('formatNotes', [])}
                                for cid, s in cases if s['errors'] or s['unavailableFields']
                                or s.get('borderline') or s.get('formatNotes')]}
            if stage == 'reviewed':
                eligible = []
                for cid, score in cases:
                    record_path = BASE.parent / variant / 'reviews' / f"{key[cid]['id']}.json"
                    record = json.loads(record_path.read_text())
                    usable = record.get('status') == 'complete' and record.get('approval') is True and not record.get('errors')
                    if usable:
                        eligible.append(score)
                groups[f'{stage}/{variant}']['automaticallyEligibleEntries'] = len(eligible)
                groups[f'{stage}/{variant}']['eligibleEntriesWithSubstantiveError'] = sum(bool(s['errors']) for s in eligible)
                groups[f'{stage}/{variant}']['eligibleEntriesWithUnavailableField'] = sum(bool(s['unavailableFields']) for s in eligible)
    paired = {}
    for stage in ['draft', 'reviewed']:
        by_entry = {}
        for cid, score in scores.items():
            info = key[cid]
            if info['stage'] == stage:
                by_entry.setdefault(info['id'], {})[info['variant']] = score
        shared_total = q4_shared_errors = q8_shared_errors = 0
        differences = Counter()
        for entry, variants in by_entry.items():
            a, b = variants['q4'], variants['q8']
            shared = set(a['evaluatedFields']) & set(b['evaluatedFields'])
            ae = {e['path'] for e in a['errors']}
            be = {e['path'] for e in b['errors']}
            shared_total += len(shared)
            q4_shared_errors += len(ae & shared)
            q8_shared_errors += len(be & shared)
            for field in shared:
                differences[f'q4_{"error" if field in ae else "clear"}/q8_{"error" if field in be else "clear"}'] += 1
        paired[stage] = {'commonEvaluableFields': shared_total,
                         'q4ErrorFieldsInCommonSet': q4_shared_errors,
                         'q8ErrorFieldsInCommonSet': q8_shared_errors,
                         'pairedFieldOutcomes': dict(differences)}
    report.update({'unmasked': True, 'groups': groups, 'paired': paired})
    (BASE / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
summary = {k: v for k, v in report.items() if k not in ['groups', 'missingCases']}
summary['missingCaseCount'] = len(report['missingCases'])
print(json.dumps(summary, ensure_ascii=False, indent=2))
if problems:
    raise SystemExit(1)
