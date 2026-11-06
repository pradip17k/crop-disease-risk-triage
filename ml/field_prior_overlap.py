"""Compare quarantined candidates to earlier images without model inference."""
import csv
import json
from pathlib import Path
from ml.inventory_field import BASE, ROOT, fingerprint


def main():
    paths = set()
    for name in ['manifest.csv', 'source-v2-training.csv']:
        with (ROOT/'data'/name).open() as f:
            paths.update(ROOT/'data'/r['path'] for r in csv.DictReader(f))
    for name in ['pilot-field-v1', 'source-v2-historical-field']:
        paths.update(ROOT/r['path'] for r in json.loads((ROOT/'experiments'/name/'predictions.json').read_text()))
    for folder in ['web/samples','outputs']:
        paths.update(p for p in (ROOT/folder).glob('*') if p.suffix.lower() in {'.jpg','.jpeg','.png'})
    paths.update(Path(p) for p in ['/Users/pradiphapa/Downloads/images.jpeg',
        '/Users/pradiphapa/Downloads/pngtree-green-tomato-leaves-psd-png-png-image_4609568.png'])
    previous=[]; failures=[]
    for path in sorted(paths):
        try: previous.append(dict(path=str(path), **fingerprint(path)))
        except Exception as e: failures.append(dict(path=str(path), error=str(e)))
    rows=json.loads((BASE/'download-audit.json').read_text()); matches=[]
    for r in rows:
        if 'pixel_sha256' not in r: continue
        for old in previous:
            exact=r['pixel_sha256']==old['pixel_sha256']
            distance=(int(r['dhash'],16)^int(old['dhash'],16)).bit_count()
            if exact or distance<=4:
                matches.append(dict(candidate_id=r['id'], prior_path=old['path'],
                    exact_pixels=exact, distance=distance, decision='pending_visual_review'))
    report=dict(prior_files=len(previous), failures=failures, matches=matches,
        limitation='Whole-image dHash screening can miss crop/rotation duplicates and capture sequences. Similarity is not a label or independent-group verdict.')
    (BASE/'prior-overlap.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(prior_files=len(previous), failures=len(failures), pairs=len(matches),
                         candidates=len({r['candidate_id'] for r in matches}))))


if __name__=='__main__':main()
