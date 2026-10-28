from pathlib import Path
import argparse,json,hashlib,secrets,importlib.util
root=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description='Export immutable label-masked translation pairs from frozen model artifacts.')
parser.add_argument('--artifacts',type=Path,default=root/'.local/ja-quant-benchmark')
base=parser.parse_args().artifacts; out=base/'evaluation'; out.mkdir(parents=True,exist_ok=True)
load=lambda p:json.loads(p.read_text())
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
source=load(base/'source-snapshot.json'); protocol=load(base/'protocol.json')
spec=importlib.util.spec_from_file_location('frozen_worker',base/'worker-v4.py');worker=importlib.util.module_from_spec(spec);spec.loader.exec_module(worker)
key_path=out/'private-key.json'
if key_path.exists():key=load(key_path)
else:key={'sampleSha256':protocol['sampleFileSha256'],'secret':secrets.token_hex(32),'cases':{}}
assert key['sampleSha256']==protocol['sampleFileSha256']
rubric={'sampleSha256':protocol['sampleFileSha256'],'expectedEntries':100,'expectedFieldsPerVariant':829,
 'reviewer':'Independent Codex source-grounded review; quantization labels hidden; not professional human certification',
 'rules':['English sourceFields are authoritative for bilingual text; Chinese sourceFields apply only to Chinese-only text.',
 'Evaluate meaning, complete clauses, negation, modality, quantities, times, entities and grammar/terminology that affects meaning.',
 'Count at most one substantive error per field. Explain each flag using exact source evidence and the target problem.',
 'Do not penalize an acceptable synonym, style/register preference alone, ordinary Japanese pronoun omission or implicit number.',
 'Do not treat model approval or rejection as correctness; those values are hidden from these packets.',
 'Ambiguous or reasonable alternative interpretations must be marked borderline, not confidently counted wrong.',
 'A missing/unusable generated field is unavailable; report it separately, never count it as a correct translation.',
 'If raw draft numbering failed but text can unambiguously align, evaluate the unchanged text and record the alignment/format issue.',
 'No manual repair of model texts before scoring. Suggested corrections belong only in the review annotations.'],
 'categories':['wrong_meaning','omission','addition_or_fabrication','negation_or_modality','quantity_time_or_entity','grammar_or_terminology','untranslated'],
 'responseShape':{'cases':[{'case':'D-001-A','evaluatedFields':['senses.0'],'unavailableFields':[],
 'errors':[{'path':'senses.0','category':'wrong_meaning','reason':'explain in Chinese or English','sourceEvidence':'exact short source text','suggestedCorrection':'optional'}],
 'borderline':[{'path':'senses.0','reason':'explain uncertainty without counting it as error','sourceEvidence':'exact short source text'}],'formatNotes':[]}]} }
save(out/'rubric.json',rubric)
packets=out/'packets';packets.mkdir(exist_ok=True)
created=[]
for stage,folder,prefix in [('draft','drafts','D'),('reviewed','reviews','R')]:
 for start in range(0,100,10):
  batch=source[start:start+10]; cases=[]; complete=True
  for offset,e in enumerate(batch,start+1):
   records={}
   for variant in ['q4','q8']:
    p=base/variant/folder/f"{e['id']}.json"
    if not p.exists():complete=False;break
    r=load(p)
    if r.get('status') not in ['complete','error','skipped']:complete=False;break
    records[variant]=r
   if not complete:break
   flip=hashlib.sha256((key['secret']+stage+e['id']).encode()).digest()[0]%2
   variants=['q4','q8'] if flip==0 else ['q8','q4']
   for letter,variant in zip(['A','B'],variants):
    r=records[variant];case=f'{prefix}-{offset:03}-{letter}'
    if stage=='draft':
     targets=r.get('fields');raw=r.get('raw') if targets is None else None
    else:
     targets=r.get('candidateFields');raw=None
    if targets is None:targets={}
    expected=[x['path'] for x in worker.translation_rows(e)]
    cases.append({'case':case,'stage':stage,'entryId':e['id'],'word':e['w'],
      'sourceFields':worker.translation_rows(e),'targetFields':targets,
      'unavailableFields':[p for p in expected if not isinstance(targets.get(p),str) or not targets[p].strip()],
      'rawDraftFallback':raw})
    key['cases'][case]={'id':e['id'],'stage':stage,'variant':variant}
  if not complete:continue
  p=packets/f'{prefix}-{start//10+1:02}.json'
  packet={'sampleSha256':protocol['sampleFileSha256'],'rubric':'../rubric.json','cases':cases}
  if p.exists():assert load(p)==packet,'Frozen blind packet changed'
  else:save(p,packet);created.append(p.name)
save(key_path,key)
print(json.dumps({'newPackets':created,'totalPackets':len(list(packets.glob('*.json'))),'blindCases':len(key['cases'])}))
