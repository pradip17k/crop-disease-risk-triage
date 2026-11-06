"""Fit reliability parameters on explicit, disjoint saved-logit partitions.
Input JSON: classes, model_sha256, temperature_rows, conformal_rows, test_rows.
Every row requires id, group, label, logits; all groups must be disjoint across roles.
"""
import argparse,json,math
from pathlib import Path
from ml.reliability import probabilities,quantile,scores,metrics

def run(data,method='LAC',alpha=.1):
    classes=data['classes']; seen=set(); all_ids=set()
    if len(set(classes))!=len(classes) or not classes: raise ValueError('Invalid class order')
    for role in ['temperature_rows','conformal_rows','test_rows']:
        rows=data[role]
        if not rows: raise ValueError('Every partition must be nonempty')
        groups=set(); ids=set()
        for row in rows:
            if not row.get('group') or not row.get('id') or row['id'] in ids: raise ValueError('Missing group/ID or repeated ID')
            ids.add(row['id']);groups.add(row['group'])
            if row['label'] not in classes or len(row['logits'])!=len(classes): raise ValueError('Class mismatch')
            probabilities(row['logits'])
        if ids & all_ids: raise ValueError('ID leakage across partitions')
        all_ids |= ids
        if groups & seen: raise ValueError('Group leakage across partitions')
        seen |= groups
    grid=[1]+[math.exp(math.log(.1)+i*math.log(100)/80) for i in range(81)]
    t=min(grid,key=lambda t:metrics(data['temperature_rows'],classes,t)['nll'])
    values=[scores(probabilities(r['logits'],t),method)[classes.index(r['label'])] for r in data['conformal_rows']]
    profile=dict(model_name='Tomato research classifier',model_sha256=data['model_sha256'],classes=classes,temperature=t,
        method=method,alpha=alpha,qhat=quantile(values,alpha),independently_evaluated=False,guidance_enabled=False,energy_cutoff=None)
    report=dict(before=metrics(data['test_rows'],classes),after=metrics(data['test_rows'],classes,t),
        caveat='Independence from training/model selection must be established by the dataset manifest; group checks alone do not establish it.')
    from ml.reliability import prediction_set
    sets=[prediction_set(probabilities(r['logits'],t),classes,profile) for r in data['test_rows']]
    report.update(set_coverage=sum(r['label'] in s for r,s in zip(data['test_rows'],sets))/len(sets),average_set_size=sum(map(len,sets))/len(sets))
    report['by_class']={label:dict(count=len(subset),coverage=sum(label in prediction_set(probabilities(r['logits'],t),classes,profile) for r in subset)/len(subset)) for label in classes if (subset:=[r for r in data['test_rows'] if r['label']==label])}
    report['by_domain']={domain:metrics([r for r in data['test_rows'] if r.get('domain','unspecified')==domain],classes,t) for domain in sorted({r.get('domain','unspecified') for r in data['test_rows']})}
    report['empty_sets']=sum(not s for s in sets)
    report['singleton_rate']=sum(len(s)==1 for s in sets)/len(sets)
    report['class_order']=classes
    return profile,report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--output',required=True);p.add_argument('--method',choices=['LAC','APS'],default='LAC');args=p.parse_args()
    out=Path(args.output)
    if out.exists():raise SystemExit('Output exists: preserve previous experiments.')
    profile,report=run(json.loads(Path(args.input).read_text()),args.method)
    out.mkdir(parents=True);(out/'profile.json').write_text(json.dumps(profile,indent=2));(out/'evaluation.json').write_text(json.dumps(report,indent=2))
