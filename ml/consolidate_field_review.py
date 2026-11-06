"""Combine reviewed scene links without claiming physical independence or assigning roles."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from ml.review_field_backgrounds import BASE, report

LINKED = {'same_leaf_or_scene','possible_shared_capture_keep_together','confirmed_same_scene_conflicting_labels'}
ALLOWED = LINKED | {'different_photographs_identity_unresolved'}

def consolidate(staged, screened, pairs):
    lookup={r['id']:dict(r) for r in staged}
    if len(lookup)!=len(staged): raise ValueError('Duplicate staged ID')
    observed={r['id']:r for r in screened}
    if len(observed)!=len(screened) or not set(observed)<=set(lookup): raise ValueError('Invalid screening IDs')
    expected={r['id'] for r in staged if r['review_status']=='pending_capture_and_background_review'}
    if set(observed)!=expected: raise ValueError('Incomplete screening')
    parent={key:key for key in lookup}
    def root(key):
        while parent[key]!=key:
            parent[key]=parent[parent[key]];key=parent[key]
        return key
    def link(a,b): parent[root(a)]=root(b)
    scenes=defaultdict(list)
    for r in staged: scenes[r['scene_group']].append(r['id'])
    for members in scenes.values():
        for key in members[1:]:link(members[0],key)
    for p in pairs:
        if p['status'] not in ALLOWED: raise ValueError('Unreviewed pair')
        for side in ('first','second'):
            if p[side] not in lookup: raise ValueError('Unknown pair ID')
            if p[f'{side}_sha256']!=lookup[p[side]]['sha256']: raise ValueError('Stale pair hash')
        if p['status'] in LINKED:link(p['first'],p['second'])
    for key,r in observed.items():
        if r['sha256']!=lookup[key]['sha256']: raise ValueError('Stale screening hash')
        lookup[key].update(r)
    components=defaultdict(list)
    for key in lookup:components[root(key)].append(key)
    result=[]
    for members in components.values():
        members.sort(); rows=[lookup[k] for k in members]
        group='review:'+hashlib.sha256('|'.join(members).encode()).hexdigest()[:20]
        prior=any(r['review_status']=='excluded_prior_scene' for r in rows)
        conflict=len({r['label'] for r in rows})>1 or any(r['review_status'] in {'excluded_label_conflict','quarantine_label_conflict'} for r in rows)
        concern=any(r.get('label_status')=='requires_source_label_review' for r in rows)
        eligible=[r['id'] for r in rows if r['id'] in observed and r['domain'] not in {'ambiguous','composite_or_illustration'} and r['review_status']!='excluded_bad_file']
        representative=min(eligible) if eligible else None
        for r in rows:
            state='excluded_prior_scene' if prior else 'quarantine_label_conflict' if conflict else 'quarantine_source_label_review' if concern else 'excluded_bad_file' if r['review_status']=='excluded_bad_file' else 'quarantine_composite' if r.get('domain')=='composite_or_illustration' else 'pending_background_provenance' if r.get('domain')=='ambiguous' else 'pending_capture_provenance' if r['id']==representative else 'duplicate_or_related_capture'
            result.append(dict(id=r['id'],path=r['path'],label=r['label'],source=r['source'],sha256=r['sha256'],source_url=r['source_url'],license=r['license'],original_scene_group=r['scene_group'],review_capture_group=group,physical_capture_group='unresolved',domain=r.get('domain','review_required'),role='unassigned',review_status=state))
    return sorted(result,key=lambda r:r['id'])

def main():
    report()  # validates index/staging/image hashes before use
    b=BASE/'background-review'
    review=json.loads((b/'capture-review.json').read_text())
    if review['input_sha256']!=hashlib.sha256((b/'capture-candidates.json').read_bytes()).hexdigest():raise ValueError('Capture queue changed')
    index_hash=hashlib.sha256((b/'index.json').read_bytes()).hexdigest()
    if review['index_sha256']!=index_hash:raise ValueError('Capture index changed')
    for p in review['pairs']:
        if 'review_sheet' in p and hashlib.sha256((b/p['review_sheet']).read_bytes()).hexdigest()!=p['review_sheet_sha256']:raise ValueError('Review sheet changed')
    staged=list(csv.DictReader((BASE/'staged-review.csv').open()))
    screened=list(csv.DictReader((b/'screened-review.csv').open()))
    rows=consolidate(staged,screened,review['pairs'])
    with (b/'consolidated-review.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    candidates=[r for r in rows if r['review_status']=='pending_capture_provenance']
    summary=dict(rows=len(rows),status_counts=dict(Counter(r['review_status'] for r in rows)),
        candidate_representatives=len(candidates),candidate_domains=dict(Counter(r['domain'] for r in candidates)),
        natural_background_by_label=dict(Counter(r['label'] for r in candidates if r['domain']=='natural_background')),
        physical_grouping_complete=False,training_ready=False,
        note='Conservative reviewed components, not independently verified plants/captures. Labels retained from publisher; all roles unassigned.')
    (b/'consolidated-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
