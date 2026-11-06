"""Retrospective deferral ablation, adapted from the user's supplied script.

Run: .venv/bin/python -m ml.deferral_analysis
Uses saved source-v2 logits; never fits thresholds or changes the live policy.
"""
import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path

from ml.reliability import probabilities, prediction_set, decide
from ml.report_errors import wilson


def proportion(k, n):
    return dict(numerator=k, denominator=n, value=k/n if n else None,
                interval_95=wilson(k, n))


def risk_coverage(correct, scores):
    """Threshold-achievable points, accepting entire tied-score blocks.

    AURC is the right-endpoint step area; ties never depend on row order.
    No artificial zero-risk point is assigned to zero accepted images.
    """
    if len(correct) != len(scores) or not all(math.isfinite(s) for s in scores):
        raise ValueError('Invalid scores')
    if not scores:
        return dict(points=[], aurc=None)
    blocks = {}
    for hit, score in zip(correct, scores):
        blocks.setdefault(score, []).append(bool(hit))
    points = []; errors = accepted = 0; area = 0
    for score in sorted(blocks, reverse=True):
        block = blocks[score]
        accepted += len(block); errors += len(block)-sum(block)
        risk = errors/accepted
        area += len(block)/len(scores)*risk
        points.append(dict(threshold=score, accepted=accepted,
                           coverage=accepted/len(scores), risk=risk))
    return dict(points=points, aurc=area)


def export_rows(records, domain, profile):
    rows = []
    for r in records:
        if r['label'] not in profile['classes']:
            continue  # Unknown-detection evaluation stays separate from known-class coverage.
        if len(r['logits']) != len(profile['classes']):
            raise ValueError('Class/logit mismatch')
        p = probabilities(r['logits'], profile['temperature'])
        raw = probabilities(r['logits'])
        label = profile['classes'][p.index(max(p))]
        candidates = prediction_set(p, profile['classes'], profile)
        action = decide(label, max(p), candidates, profile)['action']
        rows.append(dict(image_id=r['id'], domain=domain, true_label=r['label'],
                         pred_label=label, confidence=max(p), raw_confidence=max(raw),
                         conformal_set='|'.join(candidates), triage_action=action))
    return rows


def analyze(rows, class_count):
    if not rows:
        raise ValueError('No known-class rows')
    ids = [r['image_id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate image IDs')
    if any(r['triage_action'] not in {'expert', 'recapture', 'guidance'} for r in rows):
        raise ValueError('Unknown action; do not silently count it as accepted')
    sets = [r['conformal_set'].split('|') if r['conformal_set'] else [] for r in rows]
    correct = [r['true_label'] == r['pred_label'] for r in rows]
    deferred = [r['triage_action'] in {'expert', 'recapture'} for r in rows]
    singleton = [i for i, s in enumerate(sets) if len(s) == 1]
    healthy = [i for i, r in enumerate(rows) if r['true_label'] == 'healthy']
    n = len(rows); kept = n-sum(deferred); errors = n-sum(correct)
    signals = {
        'raw_softmax': [r['raw_confidence'] for r in rows],
        'calibrated_confidence': [r['confidence'] for r in rows],
        # Empty sets indicate rejection; place them AFTER every nonempty set.
        'set_size_empty_last': [-len(s) if s else -(class_count+1) for s in sets],
    }
    return dict(count=n, accuracy=proportion(sum(correct), n),
        conformal_coverage=proportion(sum(r['true_label'] in s for r, s in zip(rows, sets)), n),
        mean_set_size=sum(map(len, sets))/n, empty_sets=sum(not s for s in sets),
        actions=dict(Counter(r['triage_action'] for r in rows)),
        deferred=proportion(sum(deferred), n), accepted_coverage=kept/n,
        accepted_accuracy=proportion(sum(c and not d for c, d in zip(correct, deferred)), kept),
        errors_deferred=proportion(sum(not c and d for c, d in zip(correct, deferred)), errors),
        wrong_not_deferred=sum(not c and not d for c, d in zip(correct, deferred)),
        singleton_top1_accuracy=proportion(sum(correct[i] for i in singleton), len(singleton)),
        singleton_label_accuracy=proportion(sum(rows[i]['true_label'] == sets[i][0] for i in singleton), len(singleton)),
        healthy_accuracy=proportion(sum(correct[i] for i in healthy), len(healthy)),
        curves={name: risk_coverage(correct, score) for name, score in signals.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', default='experiments/source-v2-deferral')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    read = lambda name: json.loads((root/name).read_text())
    profile = read('models/profile.json')
    source = read('experiments/source-v2/calibration-input.json')
    field = read('experiments/source-v2-historical-field/evaluation.json')
    predictions = read('experiments/source-v2-historical-field/predictions.json')
    if source['model_sha256'] != profile['model_sha256'] or field['model_sha256'] != profile['model_sha256']:
        raise ValueError('Profile and saved prediction model hashes must match')
    if source['classes'] != profile['classes'] or field['known']['class_order'] != profile['classes']:
        raise ValueError('Class order mismatch')
    rows = export_rows(source['test_rows'], 'controlled', profile)
    rows += export_rows(predictions, 'historical_field', profile)
    reports = {d: analyze([r for r in rows if r['domain'] == d], len(profile['classes']))
               for d in sorted({r['domain'] for r in rows})}
    notes = [
        'Retrospective exposed benchmarks; no threshold fitting or new independent evaluation.',
        'Actions replay the current decision function on saved logits, assuming quality passes and unfamiliar=False. These are not logged end-to-end app actions.',
        'Guidance is disabled: deferring all errors at zero accepted coverage does not demonstrate useful selective prediction.',
        'Curves are hypothetical acceptance rankings, not enabled guidance policies. Pure set size uses whole tie blocks, with empty sets last.',
        'AURC uses a right-endpoint step area; coarse set-size ties limit direct ranking comparisons. No significance claim.',
        'Wilson intervals assume independent Bernoulli trials; small samples, unresolved dependence and label noise limit interpretation.',
        'Unknown images are excluded from known-class accuracy/coverage; energy AUROC is copied from the matching historical evaluation.',
    ]
    report = dict(model_sha256=profile['model_sha256'], notes=notes, domains=reports,
                  historical_unknown_energy_auroc=field['unknown_energy_auroc'],
                  historical_unknown_count=field['unknown_count'])
    out = root/args.outdir; out.mkdir(parents=True, exist_ok=True)
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    with (out/'predictions.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    curve_rows = [dict(domain=d, signal=s, **p) for d, v in reports.items()
                  for s, curve in v['curves'].items() for p in curve['points']]
    with (out/'risk_coverage.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(curve_rows[0])); writer.writeheader(); writer.writerows(curve_rows)
    text = ['# Retrospective deferral analysis', '', *['- '+note for note in notes], '']
    for domain, r in reports.items():
        text += [f'## {domain} (n={r["count"]})', '',
                 f'Accuracy: {r["accuracy"]["value"]:.1%}; conformal coverage: {r["conformal_coverage"]["value"]:.1%}.',
                 f'Actions: {r["actions"]}. Accepted coverage: {r["accepted_coverage"]:.1%}.',
                 f'Singleton top-1 accuracy: {r["singleton_top1_accuracy"]}.',
                 f'Healthy accuracy: {r["healthy_accuracy"]}.',
                 *[f'- {name}: step AURC {curve["aurc"]:.4f}' for name, curve in r['curves'].items()], '']
    (out/'report.md').write_text('\n'.join(text))
    print(json.dumps({d: {k:v for k,v in r.items() if k != 'curves'} for d,r in reports.items()}, indent=2))


if __name__ == '__main__':
    main()
