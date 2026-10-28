#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import argparse, json, hashlib, datetime

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description='Audit frozen prompts, generation parameters and recorded timings without inference.')
parser.add_argument('--artifacts', type=Path, default=root / '.local/ja-quant-benchmark')
base = parser.parse_args().artifacts
protocol = json.loads((base / 'protocol.json').read_text())
digest = lambda b: hashlib.sha256(b).hexdigest()
canonical = lambda obj: json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
issues = []
assert digest((base / 'worker-v4.py').read_bytes()) == protocol['workerSha256']
assert digest((base / 'harness-frozen.py').read_bytes()) == protocol['harnessSha256']
assert digest((root / 'scripts/atlas/ja-benchmark-100.json').read_bytes()) == protocol['sampleFileSha256']
groups = {}
calls_by = {}
for variant in ['q4', 'q8']:
    for phase in ['draft', 'review']:
        files = sorted((base / variant / 'calls' / phase).glob('*/attempt-*/*.json'))
        calls = [json.loads(path.read_text()) for path in files]
        for path, call in zip(files, calls):
            req = call['request']
            if req['options'] != protocol['options']:
                issues.append(f'Changed options: {path.relative_to(base)}')
            if phase == 'review' and req.get('think') is not False:
                issues.append(f'Thinking condition changed: {path.relative_to(base)}')
            if call.get('thinkingChars', 0):
                issues.append(f'Thinking emitted: {path.relative_to(base)}')
            calls_by[(variant, phase, path.parent.parent.name, path.name)] = call
        metrics = [c.get('metrics', {}) for c in calls]
        folder = 'drafts' if phase == 'draft' else 'reviews'
        entries = [json.loads(path.read_text()) for path in (base / variant / folder).glob('*.json')]
        terminal = [r for r in entries if r['status'] in ['complete', 'error', 'skipped']]
        start = min((r['startedAt'] for r in entries), default=None)
        finish = max((r['finishedAt'] for r in terminal), default=None)
        elapsed = (datetime.datetime.fromisoformat(finish) - datetime.datetime.fromisoformat(start)).total_seconds() if start and finish else None
        groups[f'{variant}/{phase}'] = {
            'calls': len(calls), 'entryRecords': len(entries),
            'statuses': dict(Counter(r['status'] for r in entries)),
            'terminalPhase': len(terminal) == 100,
            'recordSpanSeconds': elapsed,
            'loadSeconds': sum(m.get('load_duration', 0) for m in metrics) / 1e9,
            'prefillSeconds': sum(m.get('prompt_eval_duration', 0) for m in metrics) / 1e9,
            'generationSeconds': sum(m.get('eval_duration', 0) for m in metrics) / 1e9,
            'generatedTokens': sum(m.get('eval_count', 0) for m in metrics),
            'modelApproved': sum(r.get('approval') is True for r in entries),
            'modelRejected': sum(r.get('approval') is False for r in entries),
            'structuralBlocked': sum(bool(r.get('structuralErrors') or r.get('errors')) for r in entries),
            'pipelineUsable': sum(r.get('status') == 'complete' and r.get('approval') is True and not r.get('errors') for r in entries) if phase == 'review' else None}
draft_pairs = review_pairs = 0
for (variant, phase, entry, callnum), a in calls_by.items():
    if variant != 'q4':
        continue
    b = calls_by.get(('q8', phase, entry, callnum))
    if not b:
        continue
    ar, br = a['request'], b['request']
    if phase == 'draft':
        draft_pairs += 1
        if ar['messages'] != br['messages']:
            issues.append(f'Draft source prompt mismatch: {entry}/{callnum}')
    else:
        review_pairs += 1
        if ar['messages'][0] != br['messages'][0] or ar.get('format') != br.get('format'):
            issues.append(f'Review system/schema mismatch: {entry}/{callnum}')
report = {'sampleSha256': protocol['sampleFileSha256'], 'draftPairedPromptsChecked': draft_pairs,
          'reviewSystemAndSchemaPairsChecked': review_pairs,
          'note': 'Review user prompts necessarily contain each variant own draft; this is an end-to-end pipeline comparison, not an isolated review-model crossover.',
          'issues': issues, 'groups': groups}
(base / 'request-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
if issues:
    raise SystemExit(1)
