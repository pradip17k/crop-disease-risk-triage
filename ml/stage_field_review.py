"""Apply reviewed duplicate links conservatively; never allocate experiment roles."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from ml.inventory_field import BASE


def stage(rows, links, prior_ids):
    lookup={r['id']:r for r in rows}
    if len(lookup)!=len(rows): raise ValueError('Repeated IDs')
    parent={key:key for key in lookup}
    def root(key):
        while parent[key]!=key:
            parent[key]=parent[parent[key]]; key=parent[key]
        return key
    for a,b in links:
        if a not in parent or b not in parent: raise ValueError('Unknown review ID')
        parent[root(a)]=root(b)
    if not set(prior_ids)<=set(lookup): raise ValueError('Unknown prior ID')
    components=defaultdict(list)
    for key in lookup: components[root(key)].append(key)
    result=[]
    for members in components.values():
        members.sort(); group='scene:'+hashlib.sha256('|'.join(members).encode()).hexdigest()[:20]
        labels={lookup[key]['label'] for key in members}
        prior=any(key in prior_ids or lookup[key]['status']=='excluded_prior_image' for key in members)
        valid=[key for key in members if lookup[key]['status']!='download_or_decode_failure']
        keep=min(valid) if valid else None
        for key in members:
            row=lookup[key]
            state='excluded_prior_scene' if prior else 'excluded_label_conflict' if len(labels)>1 else 'excluded_bad_file' if key not in valid else 'duplicate_copy' if key!=keep else 'pending_capture_and_background_review'
            result.append(dict(id=key,path=row.get('path',''),label=row['label'],source=row['source'],
                source_url=row['source_url'],license=row['license'],sha256=row.get('sha256',''),
                scene_group=group,physical_capture_group='unresolved',domain='review_required',
                role='unassigned',review_status=state))
    return sorted(result,key=lambda r:r['id'])


def reviewed(name, original):
    review=json.loads((BASE/name).read_text())
    if review['input_sha256']!=hashlib.sha256((BASE/original).read_bytes()).hexdigest():
        raise ValueError('Review input changed; repeat review')
    return review


def main():
    rows=json.loads((BASE/'download-audit.json').read_text())
    duplicates=json.loads((BASE/'duplicate-review.json').read_text())
    visual=reviewed('visual-pair-review.json','duplicate-review.json')
    prior=reviewed('prior-visual-review.json','prior-overlap.json')
    links=[]
    for group in duplicates['exact_pixel_duplicate_groups']:
        links.extend((group['ids'][0],key) for key in group['ids'][1:])
    for pair in visual['pairs']:
        if pair['decision'] not in {'same_scene_or_derivative','same_scene_conflicting_labels','different_photographs'}:
            raise ValueError('Unreviewed pair')
        if pair['decision']!='different_photographs': links.append((pair['first'],pair['second']))
    if any(m['decision']!='same_scene_or_derivative' for m in prior['matches']): raise ValueError('Unreviewed prior match')
    staged=stage(rows,links,{m['candidate_id'] for m in prior['matches']})
    with (BASE/'staged-review.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(staged[0]));writer.writeheader();writer.writerows(staged)
    summary=dict(rows=len(staged),counts=dict(Counter(r['review_status'] for r in staged)),
                 physical_grouping_complete=False,training_ready=False,
                 note='Scene links reflect reviewed duplicates only; singleton scene IDs do not establish independent leaves. Background/label/capture review still required.')
    (BASE/'staged-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))


if __name__=='__main__': main()
