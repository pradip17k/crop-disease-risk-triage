"""Pure-Python reliability and triage; no training dependencies required."""
import math

def probabilities(logits, temperature=1.0):
    if not logits or not math.isfinite(temperature) or temperature <= 0 or not all(math.isfinite(x) for x in logits):
        raise ValueError('Invalid model logits or temperature')
    z = [x / temperature for x in logits]
    peak = max(z)
    values = [math.exp(x - peak) for x in z]
    return [x / sum(values) for x in values]

def quantile(scores, alpha):
    if not scores or not 0 < alpha < 1 or not all(math.isfinite(x) for x in scores):
        raise ValueError('Invalid conformal calibration')
    rank = math.ceil((len(scores) + 1) * (1 - alpha))
    return sorted(scores)[rank - 1] if rank <= len(scores) else None

def scores(p, method):
    if not p or not all(math.isfinite(x) and 0 <= x <= 1 for x in p) or abs(sum(p)-1)>1e-6:
        raise ValueError('Invalid probability vector')
    if method == 'LAC':
        return [1-x for x in p]
    if method == 'APS':
        # Deterministic inclusive-prefix inversion; ties share the block score.
        return [min(1, sum(v for v in p if v >= x)) for x in p]
    raise ValueError('Unknown conformal method')

def prediction_set(p, classes, profile):
    q = profile['qhat']
    if len(p) != len(classes) or q is not None and (not math.isfinite(q) or not 0 <= q <= 1):
        raise ValueError('Invalid conformal profile')
    return [label for label, score in zip(classes, scores(p, profile['method'])) if q is None or score <= q]

def metrics(records, classes, temperature=1):
    if not records:
        return dict(count=0, accuracy=None, nll=None, brier=None, ece=None, risk_coverage=[])
    matrix = [[0]*len(classes) for _ in classes]
    bins = [[] for _ in range(15)]
    nll = brier = hits = 0
    ranked = []
    for row in records:
        p = probabilities(row['logits'], temperature)
        target = classes.index(row['label'])
        hit = p.index(max(p)) == target
        if len(p)!=len(classes): raise ValueError('Class order mismatch')
        matrix[target][p.index(max(p))] += 1
        hits += hit
        z = [x/temperature for x in row['logits']]
        nll += max(z) + math.log(sum(math.exp(x-max(z)) for x in z)) - z[target]
        brier += sum((v-int(i == target))**2 for i,v in enumerate(p))
        bins[min(14,int(max(p)*15))].append((max(p),hit))
        ranked.append((max(p), not hit))
    ece = sum(abs(sum(c for c,h in b)-sum(h for c,h in b)) for b in bins)/len(records)
    ranked.sort(reverse=True)
    curve = []; errors = 0; i = 0; area = 0; previous = 0
    while i < len(ranked):
        j = i
        while j < len(ranked) and ranked[j][0] == ranked[i][0]:
            errors += ranked[j][1]; j += 1
        coverage = j/len(ranked); risk = errors/j
        area += (coverage-previous)*risk; previous = coverage
        curve.append(dict(coverage=coverage,risk=risk)); i = j
    f1=[]
    for i in range(len(classes)):
        denominator=sum(matrix[i])+sum(row[i] for row in matrix)
        f1.append(2*matrix[i][i]/denominator if denominator else 0)
    return dict(macro_f1=sum(f1)/len(classes),confusion_matrix=matrix,class_order=classes,count=len(records), accuracy=hits/len(records), nll=nll/len(records), brier=brier/len(records), ece=ece, aurc=area, risk_coverage=curve)

def decide(label, confidence, candidates, profile, quality_ok=True, unfamiliar=False):
    if not quality_ok:
        return dict(action='recapture', reason='Retake one leaf in even light, keeping the camera steady and the leaf in focus.')
    if unfamiliar or label == 'unknown' or not candidates:
        return dict(action='expert', reason='The image does not support a reliable known condition. Ask an agricultural specialist to verify it.')
    if len(candidates) > 1:
        return dict(action='recapture', reason='More than one condition remains plausible. Add a clearer photo of another affected leaf; seek expert review if uncertainty persists.')
    if not profile.get('independently_evaluated') or not profile.get('guidance_enabled'):
        return dict(action='expert', reason='This prediction has no independently evaluated guidance policy. Expert verification is recommended.')
    threshold = profile.get('min_confidence')
    if threshold is None or not math.isfinite(threshold) or not 0 <= threshold <= 1 or not math.isfinite(confidence) or not 0 <= confidence <= 1 or confidence < threshold or candidates != [label]:
        return dict(action='expert', reason='The prediction does not meet the evaluated guidance policy.')
    return dict(action='guidance', reason='This known-condition prediction meets the evaluated screening policy. Read the basic guidance and monitor changes.')
