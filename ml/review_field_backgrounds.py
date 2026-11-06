"""Build reproducible contact sheets for manual scene-domain review (no inference)."""
import csv
import hashlib
import json
import re
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
BASE = Path(__file__).resolve().parents[1] / 'data/field-development'

def build():
    inventory = {r['id']: r for r in json.loads((BASE/'inventory.json').read_text())}
    rows = [r for r in csv.DictReader((BASE/'staged-review.csv').open()) if r['review_status']=='pending_capture_and_background_review']
    def key(r):
        name=inventory[r['id']]['filename']
        return r['source'],r['label'],re.sub(r'\d+',lambda m:m[0].zfill(8),name)
    rows.sort(key=key)
    out=BASE/'background-review';out.mkdir(exist_ok=True)
    index=[]
    for source,label in sorted({(r['source'],r['label']) for r in rows}):
        group=[r for r in rows if (r['source'],r['label'])==(source,label)]
        height=max(220,((len(group)+9)//10)*220)
        sheet=Image.new('RGB',(2000,height),'#dddddd');draw=ImageDraw.Draw(sheet)
        for n,row in enumerate(group):
            data=(BASE.parent/row['path']).read_bytes()
            if hashlib.sha256(data).hexdigest()!=row['sha256']: raise ValueError('Image changed')
            x,y=(n%10)*200,(n//10)*220
            with Image.open(BASE.parent/row['path']) as im:
                thumb=ImageOps.contain(ImageOps.exif_transpose(im).convert('RGB'),(196,192))
                sheet.paste(thumb,(x,y))
            draw.text((x+2,y+194),f'{n+1}: {inventory[row["id"]]["filename"][:28]}',fill='black')
            index.append(dict(row,filename=inventory[row['id']]['filename'],sheet=f'{source}-{label}.jpg',tile=n+1))
        sheet.save(out/f'{source}-{label}.jpg',quality=90)
    (out/'index.json').write_text(json.dumps(dict(staged_sha256=hashlib.sha256((BASE/'staged-review.csv').read_bytes()).hexdigest(),rows=index),indent=2))
    print(f'Created contact sheets for {len(index)} candidates')




def apply_review(index, decisions):
    """Attach screening observations, retaining unresolved grouping and roles."""
    from collections import Counter
    indexed={r['id']:r for r in index['rows']}
    observed={r['id']:r for r in decisions['rows']}
    if len(indexed)!=len(index['rows']) or len(observed)!=len(decisions['rows']):
        raise ValueError('Duplicate review IDs')
    if set(indexed)!=set(observed): raise ValueError('Review does not cover exact candidate set')
    result=[]
    allowed={'natural_background','staged_plain','ambiguous','composite_or_illustration'}
    for key,row in indexed.items():
        review=observed[key]
        if any(review[k]!=row[k] for k in ('sha256','sheet','tile')): raise ValueError('Stale review identity')
        if review['domain'] not in allowed: raise ValueError('Invalid domain')
        state='quarantine_composite' if review['domain']=='composite_or_illustration' else 'pending_full_size_background_review' if review['domain']=='ambiguous' else 'pending_capture_and_label_review'
        if review.get('label_status')=='requires_source_label_review': state='quarantine_source_label_review'
        if review.get('label_status')=='conflicting_scene_labels': state='quarantine_label_conflict'
        result.append(dict(row,domain=review['domain'],review_status=state,physical_capture_group='unresolved',role='unassigned',label_status=review['label_status'],review_level=review['review_level']))
    counts=Counter((r['source'],r['label'],r['domain']) for r in result)
    summary=dict(rows=len(result),domain_counts=dict(Counter(r['domain'] for r in result)),status_counts=dict(Counter(r['review_status'] for r in result)),
        by_source_class_domain=[dict(source=s,label=l,domain=d,count=n) for (s,l,d),n in sorted(counts.items())],
        physical_grouping_complete=False,training_ready=False,
        note='Contact-sheet screening only. Natural-background counts are candidates, not independent or validated examples. All roles unassigned.')
    return result,summary


def report():
    b=BASE/'background-review'
    index=json.loads((b/'index.json').read_text()); decisions=json.loads((b/'decisions.json').read_text())
    if decisions['index_sha256']!=hashlib.sha256((b/'index.json').read_bytes()).hexdigest(): raise ValueError('Index changed')
    if index['staged_sha256']!=hashlib.sha256((BASE/'staged-review.csv').read_bytes()).hexdigest(): raise ValueError('Staging changed')
    for r in index['rows']:
        if hashlib.sha256((BASE.parent/r['path']).read_bytes()).hexdigest()!=r['sha256']: raise ValueError('Image changed')
    rows,summary=apply_review(index,decisions)
    with (b/'screened-review.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (b/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps({k:v for k,v in summary.items() if k!='by_source_class_domain'},indent=2))


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',action='store_true',help='Validate and export saved visual decisions')
    args=parser.parse_args()
    report() if args.report else build()
