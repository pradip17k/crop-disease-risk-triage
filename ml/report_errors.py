"""Describe frozen pilot failures; never fits a model or threshold."""
import argparse,json,math
from pathlib import Path
from ml.reliability import probabilities

def wilson(correct,total):
    if not total:return None
    z=1.959963984540054;p=correct/total;den=1+z*z/total
    center=(p+z*z/(2*total))/den
    spread=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/den
    return [max(0,center-spread),min(1,center+spread)]

def describe(rows,classes,temperature):
    details=[]
    for row in rows:
        p=probabilities(row['logits'],temperature);guess=classes[p.index(max(p))]
        details.append(dict(actual=row['label'],predicted=guess,score=max(p),correct=row['label']==guess))
    per_class=[]
    for label in classes:
        actual=[r for r in details if r['actual']==label];correct=sum(r['correct'] for r in actual)
        errors=[r for r in actual if not r['correct']]
        confusion={c:sum(r['predicted']==c for r in errors) for c in classes if c!=label}
        per_class.append(dict(label=label,count=len(actual),correct=correct,recall=correct/len(actual) if actual else None,
            recall_interval_95=wilson(correct,len(actual)),confusions=confusion,
            wrong_with_score_at_least_08=sum(r['score']>=.8 for r in errors)))
    correct=sum(r['correct'] for r in details)
    return dict(count=len(details),accuracy=correct/len(details) if details else None,accuracy_interval_95=wilson(correct,len(details)),
        total_errors=len(details)-correct,wrong_with_score_at_least_08=sum(not r['correct'] and r['score']>=.8 for r in details),per_class=per_class)

def main():
    root=Path(__file__).resolve().parent.parent
    p=argparse.ArgumentParser();p.add_argument('--run',default='experiments/source-v2');p.add_argument('--profile',default='models/profile.json');p.add_argument('--field',default='experiments/source-v2-historical-field');p.add_argument('--output',default='models/error-review.json');a=p.parse_args()
    profile=json.loads((root/a.profile).read_text())
    source=json.loads((root/a.run/'calibration-input.json').read_text())
    field_report=json.loads((root/a.field/'evaluation.json').read_text())
    if source['model_sha256']!=profile['model_sha256'] or field_report['model_sha256']!=profile['model_sha256']:raise ValueError('Error-review model and logits do not match')
    field=json.loads((root/a.field/'predictions.json').read_text())
    report=dict(model_sha256=profile['model_sha256'],score_band=.8,
        note='0.8 is a descriptive score band, not a validated guidance threshold. Wilson intervals assume independent Bernoulli trials; unresolved image dependence/label noise limits their interpretation.',
        controlled=describe(source['test_rows'],profile['classes'],profile['temperature']),
        field=describe([r for r in field if r['label']!='unknown'],profile['classes'],profile['temperature']))
    output=root/a.output;output.write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
