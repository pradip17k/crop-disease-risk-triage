"""Assign pre-labelled original images to reproducible group-disjoint roles.
Inventory uses audit_manifest.REQUIRED columns except role; supply real capture groups.
No guessed leaf IDs, image augmentation or downloads are performed here.
"""
import argparse,csv,hashlib,json
from pathlib import Path
from ml.audit_manifest import REQUIRED,audit
ROLES=[('train',.55),('validation',.10),('temperature',.10),('conformal',.10),('policy',.05),('test',.10)]

def assign(rows,seed='crop-triage-v1'):
    assigned={}; output=[]
    for row in rows:
        if not row.get('group'):raise ValueError('A physical capture group is required')
        group=row['group']
        # One global assignment per group, even across domains/classes.
        value=int(hashlib.sha256((seed+':'+group).encode()).hexdigest()[:12],16)/16**12
        cumulative=0
        for role,fraction in ROLES:
            cumulative+=fraction
            if value<cumulative:break
        assigned[group]=role
        output.append(dict(row,role=role))
    return output
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('inventory');p.add_argument('--root',required=True);p.add_argument('--output',required=True);p.add_argument('--seed',default='crop-triage-v1');a=p.parse_args()
    out=Path(a.output)
    if out.exists():raise SystemExit('Output exists. Preserve the frozen manifest.')
    with open(a.inventory,newline='') as f:
        reader=csv.DictReader(f)
        if not (REQUIRED-{'role'})<=set(reader.fieldnames or []):raise SystemExit('Inventory missing provenance/group columns')
        rows=assign(list(reader),a.seed)
    report=audit(rows,Path(a.root))
    if not report['passes']:raise SystemExit(json.dumps(report['errors'],indent=2))
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=sorted(REQUIRED),extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    out.with_suffix('.audit.json').write_text(json.dumps(report,indent=2))
    print('Frozen manifest saved. Review class/domain/role counts before training; small classes can have empty roles.')
