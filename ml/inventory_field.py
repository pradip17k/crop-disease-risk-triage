"""Inventory original licensed field candidates; no fitting or final-test access.

Run with --download-per-class 100 for a bounded provenance/decode audit.
Candidates stay quarantined until label, background and capture-group review.
"""
import argparse
import csv
import hashlib
import json
import subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT/'data/field-development'
REV = '5467f6012d78d1c446145d5f582da6096f852ae8'


def fetch(url, path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix+'.partial')
        subprocess.run(['curl', '-fsSL', '--retry', '2', '--max-time', '60', url, '-o', str(tmp)], check=True)
        tmp.replace(path)
    return path.read_bytes()


def metadata(url, name):
    data = json.loads(fetch(url, BASE/'metadata'/name))
    if isinstance(data, dict) and 'error' in data:
        raise ValueError(f'Metadata error: {url}')
    return data


def mendeley(dataset, version, paths):
    api = f'https://data.mendeley.com/public-api/datasets/{dataset}'
    snapshot = metadata(f'{api}/snapshot/{version}', f'{dataset}-snapshot.json')
    if snapshot['licence']['short_name'] != 'CC BY 4.0':
        raise ValueError('Review changed dataset licence before use')
    folders = metadata(f'{api}/folders/{version}', f'{dataset}-folders.json')
    lookup = {f['id']: f for f in folders}
    def full_path(f):
        return full_path(lookup[f['parent_id']])+'/'+f['name'] if f.get('parent_id') in lookup else f['name']
    rows = []
    for f in folders:
        name = full_path(f)
        if name not in paths: continue
        start = 0
        while True:
            files = metadata(f'{api}/files?folder_id={f["id"]}&version={version}&$start={start}&$limit=1000',
                             f'{dataset}-{f["id"]}-{start}.json')
            for item in files:
                detail = item['content_details']
                if not detail['content_type'].startswith('image/'): continue
                rows.append(dict(id=f'{dataset}:{item["id"]}', source=dataset, version=str(version),
                    source_class=name, label=paths[name], source_url=detail['download_url'],
                    license='CC BY 4.0', expected_sha256=detail['sha256_hash'], bytes=detail['size'],
                    filename=item['filename'], publisher_split='unsplit'))
            if len(files) < 1000: break
            start += 1000
    return rows


def plantdoc():
    url = f'https://raw.githubusercontent.com/pratikkayal/PlantDoc-Dataset/{REV}'
    licence = fetch(url+'/LICENSE.txt', BASE/'metadata/plantdoc-LICENSE.txt').decode()
    if not licence.startswith('Attribution 4.0 International'): raise ValueError('Review PlantDoc licence')
    rows = []
    mapping = {'Tomato Early blight leaf':'early_blight', 'Tomato leaf late blight':'late_blight',
               'Tomato Septoria leaf spot':'septoria', 'Tomato leaf':'healthy'}
    for name, label in mapping.items():
        items = metadata(f'https://api.github.com/repos/pratikkayal/PlantDoc-Dataset/contents/train/{quote(name)}?ref={REV}',
                         f'plantdoc-train-{label}.json')
        for item in items:
            if item['type'] != 'file' or Path(item['name']).suffix.lower() not in {'.jpg','.jpeg','.png'}: continue
            rows.append(dict(id='plantdoc:'+item['sha'], source='plantdoc', version=REV, source_class=name,
                label=label, source_url=url+'/train/'+quote(name)+'/'+quote(item['name']), license='CC BY 4.0',
                expected_sha256='', bytes=item['size'], filename=item['name'], publisher_split='train'))
    return rows


def fingerprint(path):
    with Image.open(path) as im:
        rgb = ImageOps.exif_transpose(im).convert('RGB'); rgb.load()
        width, height = rgb.size
        pixel_hash = hashlib.sha256(str(rgb.size).encode()+rgb.tobytes()).hexdigest()
        gray = list(rgb.convert('L').resize((9, 8)).tobytes())
        bits = ''.join('1' if gray[y*9+x] > gray[y*9+x+1] else '0' for y in range(8) for x in range(8))
    return dict(pixel_sha256=pixel_hash, dhash=f'{int(bits,2):016x}', width=width, height=height)


def inspect_image(row, excluded):
    result = dict(row, status='quarantine', role='unassigned', grouping='unresolved')
    path = BASE/'images'/hashlib.sha256(row['id'].encode()).hexdigest()
    try:
        raw = fetch(row['source_url'], path)
        sha = hashlib.sha256(raw).hexdigest()
        if row['expected_sha256'] and row['expected_sha256'] != sha: raise ValueError('Publisher checksum mismatch')
        result.update(path=str(path.relative_to(ROOT/'data')), sha256=sha,
                      **fingerprint(path))
        if sha in excluded: result['status'] = 'excluded_prior_image'
    except Exception as e:
        result.update(status='download_or_decode_failure', error=str(e))
    return result


def main():
    p = argparse.ArgumentParser(); p.add_argument('--download-per-class', type=int, default=0); args = p.parse_args()
    rows = mendeley('jttrv2w27r', 2, {'Tomato Dataset/Healthy':'healthy', 'Tomato Dataset/Early Blight':'early_blight',
        'Tomato Dataset/Late Blight':'late_blight'})
    rows += mendeley('bwh3zbpkpv', 1, {'Raw Data/CCMT Dataset/Tomato/healthy':'healthy',
        'Raw Data/CCMT Dataset/Tomato/septoria leaf spot':'septoria'})
    rows += plantdoc()
    rows.sort(key=lambda r: (r['source'], r['label'], hashlib.sha256(r['id'].encode()).hexdigest()))
    (BASE/'inventory.json').write_text(json.dumps(rows, indent=2))
    excluded = set()
    for name in ['data/manifest.csv','data/source-v2-training.csv']:
        with (ROOT/name).open() as f: excluded.update(r['sha256'] for r in csv.DictReader(f))
    for name in ['experiments/pilot-field-v1/predictions.json','experiments/source-v2-historical-field/predictions.json']:
        excluded.update(r['sha256'] for r in json.loads((ROOT/name).read_text()))
    for folder in ['web/samples','outputs']:
        for file in (ROOT/folder).glob('*'):
            if file.suffix.lower() in {'.jpg','.jpeg','.png'}: excluded.add(hashlib.sha256(file.read_bytes()).hexdigest())
    counts = Counter(); selected = []
    for row in rows:
        key = (row['source'], row['label'])
        if counts[key] < args.download_per_class: selected.append(row); counts[key] += 1
    with ThreadPoolExecutor(max_workers=6) as pool:
        audited = list(pool.map(lambda r: inspect_image(r, excluded), selected))
    (BASE/'download-audit.json').write_text(json.dumps(audited, indent=2))
    summary = dict(listed=len(rows), listed_bytes=sum(r['bytes'] for r in rows),
        counts=dict(Counter(r['source']+':'+r['label'] for r in rows)),
        downloaded_audited=len(audited), status_counts=dict(Counter(r['status'] for r in audited)),
        distinct_decoded_pixels=len({r['pixel_sha256'] for r in audited if 'pixel_sha256' in r}),
        final_test_assigned=0, ready_for_training=False,
        limits=['Inventory counts are not independent leaf counts.', 'All downloads quarantined pending background/label/capture-group review.',
                'Exact historical overlap excluded; near-duplicate audit still required.',
                'CCMT ambiguous leaf blight and augmented folders excluded. No disease inference executed.'])
    (BASE/'summary.json').write_text(json.dumps(summary, indent=2)); print(json.dumps(summary, indent=2))


if __name__ == '__main__': main()
