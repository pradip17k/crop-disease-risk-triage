"""Validate a prepared CSV manifest before training; does not download/change data.
Required columns: id,path,label,domain,role,group,sha256,source_url,license.
Usage: python3 -m ml.audit_manifest data/manifest.csv --output experiments/audit.json
"""
import argparse,csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
ROLES={'train','validation','temperature','conformal','policy','test'}
REQUIRED={'id','path','label','domain','role','group','sha256','source_url','license'}

def audit(rows,root):
    errors=[];warnings=[];ids=set();identity={};counts=Counter();classes=defaultdict(set)
    for index,r in enumerate(rows,2):
        missing=[k for k in REQUIRED if not str(r.get(k,'')).strip()]
        if missing:errors.append(f'Row {index}: missing {", ".join(sorted(missing))}');continue
        if r['id'] in ids:errors.append(f'Row {index}: repeated ID {r["id"]}')
        ids.add(r['id'])
        if r['role'] not in ROLES:errors.append(f'Row {index}: invalid role')
        path=(root/r['path']).resolve()
        if not path.is_relative_to(root.resolve()):errors.append(f'Row {index}: image outside dataset root');continue
        if not path.is_file():errors.append(f'Row {index}: image missing');continue
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=r['sha256']:errors.append(f'Row {index}: checksum mismatch')
        # Group IDs are globally unique physical capture identities, not per-split IDs.
        for kind,key in [('group',r['group']),('sha256',actual),('path',str(path))]:
            previous=identity.get((kind,key))
            if previous and previous[0]!=r['role']:errors.append(f'Row {index}: {kind} overlaps {previous[0]} and {r["role"]}')
            if previous and previous[1]!=r['label'] and kind!='group':errors.append(f'Row {index}: same image has conflicting labels')
            identity[(kind,key)]=(r['role'],r['label'])
        counts[(r['domain'],r['role'],r['label'])]+=1
        classes[r['domain']].add(r['label'])
        if r.get('grouping')=='image_only':warnings.append('Some groups are image-only; physical leaf independence remains unresolved.')
    domains=sorted(classes)
    shared=sorted(set.intersection(*(classes[d] for d in domains))) if domains else []
    for domain in domains:
        for role in ROLES:
            if not any(k[0]==domain and k[1]==role for k in counts):warnings.append(f'{domain}: no {role} examples; declare source-only/target-supervised protocol explicitly.')
    return dict(passes=not errors,rows=len(rows),errors=errors,warnings=sorted(set(warnings)),shared_labels=shared,
        counts=[dict(domain=d,role=r,label=c,count=n) for (d,r,c),n in sorted(counts.items())],
        limits='Checks exact bytes and declared capture groups. Cannot detect every near duplicate, incorrect label, or invented group identity.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--root',default='.');p.add_argument('--output',required=True);a=p.parse_args()
    with open(a.manifest,newline='') as f:
        reader=csv.DictReader(f)
        if not REQUIRED<=set(reader.fieldnames or []):raise SystemExit('Manifest missing required columns')
        rows=list(reader)
    report=audit(rows,Path(a.root));out=Path(a.output)
    if out.exists():raise SystemExit('Output already exists; preserve audit history')
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2));print(json.dumps(dict(passes=report['passes'],rows=report['rows'],errors=report['errors']),indent=2))
    raise SystemExit(0 if report['passes'] else 1)
