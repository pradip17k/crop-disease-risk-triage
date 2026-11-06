"""Download a small pinned original PlantVillage cohort with recorded leaf groups.
This development pilot is not an independent field-validation dataset.
"""
import argparse,csv,hashlib,json,subprocess
from pathlib import Path
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
from ml.prepare_manifest import assign
from ml.audit_manifest import audit,REQUIRED
REV='7f7ecc7e1eaca78107e3affe7cb5abd9427e139a'
CLASSES={'Tomato___healthy':'healthy','Tomato___Early_blight':'early_blight','Tomato___Late_blight':'late_blight','Tomato___Septoria_leaf_spot':'septoria'}
ROOT=Path('data');SOURCE=ROOT/'source';SOURCE.mkdir(parents=True,exist_ok=True)
def fetch(url,path):
    if not path.exists():
        subprocess.run(['curl','-fsSL','--retry','2','--max-time','60',url,'-o',str(path)],check=True)
    return path.read_bytes()
def run(groups_per_class=120,exclude_manifest=None):
    if (ROOT/'manifest.csv').exists():raise SystemExit('Manifest already frozen')
    mapping=json.loads(fetch(f'https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/{REV}/leaf_grouping/leaf-map.json',SOURCE/'leaf-map.json'))
    omitted_groups=set()
    if exclude_manifest:
        with open(exclude_manifest,newline='') as f:omitted_groups={r['group'] for r in csv.DictReader(f)}
    provenance=json.loads(Path('web/samples/credits.json').read_text())
    from urllib.parse import unquote,urlparse
    for entry in provenance:
        key=Path(unquote(urlparse(entry['download']).path)).stem.split('___')[-1].lower().strip()
        omitted_groups.update(mapping.get(key,[]))
    for p in Path('outputs').glob('*source.json'):
        known=json.loads(p.read_text());group=known.get('recorded_leaf_group')
        if group:omitted_groups.add(group)
    planned=[];excluded={}
    for source_class,label in CLASSES.items():
        raw=fetch(f'https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color/{quote(source_class)}?ref={REV}',SOURCE/(label+'-listing.json'))
        listing=json.loads(raw)
        candidates=[]
        for entry in listing:
            if entry['type']!='file':continue
            name=entry['name'];key=Path(name).stem.split('___')[-1].lower().strip()
            groups=mapping.get(key,[])
            if len(groups)!=1 or not groups[0].startswith(source_class+':::'):continue
            group=groups[0]
            if group in omitted_groups:continue
            if group.endswith(':::') or group.endswith(':::nan'):continue
            candidates.append(dict(entry=entry,label=label,group=group))
        # Hash order is fixed before any prediction is observed. Include a small cohort.
        candidates.sort(key=lambda r:hashlib.sha256(r['group'].encode()).hexdigest())
        selected_groups=[]
        for r in candidates:
            if r['group'] not in selected_groups:selected_groups.append(r['group'])
        selected_groups=set(selected_groups[:groups_per_class])
        candidates=[r for r in candidates if r['group'] in selected_groups]
        # One image per recorded leaf makes the first CPU pilot small and explicit.
        seen=set();chosen=[]
        for r in sorted(candidates,key=lambda r:r['entry']['name']):
            if r['group'] in seen:continue
            seen.add(r['group']);chosen.append(r)
        planned.extend(chosen);excluded[label]=dict(listed=len(listing),mapped=len(candidates),chosen=len(chosen),grouping='publisher recorded leaf ID; one photograph per group')
    def download(item):
        e=item['entry'];dest=ROOT/'images'/item['label']/e['name'];dest.parent.mkdir(parents=True,exist_ok=True)
        url=f'https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/{REV}/raw/color/{quote(CLASSES_REVERSE[item["label"]])}/{quote(e["name"])}'
        data=fetch(url,dest)
        return dict(id=e['sha'],path=str(dest.relative_to(ROOT)),label=item['label'],domain='controlled',group=item['group'],sha256=hashlib.sha256(data).hexdigest(),source_url=url,license='CC BY-SA 3.0 (publisher dataset declaration)')
    with ThreadPoolExecutor(max_workers=8) as pool:
        rows=[]
        for i,row in enumerate(pool.map(download,planned),1):
            rows.append(row)
            if i%40==0:print(f'Downloaded {i}/{len(planned)}',flush=True)
    rows=assign(rows)
    # Demo photographs must not contribute to an independent test.
    demo_hashes={hashlib.sha256(p.read_bytes()).hexdigest() for p in list(Path('web/samples').glob('*.jpg'))+list(Path('outputs').glob('*.jpg'))}
    rows=[r for r in rows if r['sha256'] not in demo_hashes]
    report=audit(rows,ROOT)
    if not report['passes']:raise ValueError(report['errors'])
    with (ROOT/'manifest.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=sorted(REQUIRED));w.writeheader();w.writerows(rows)
    (ROOT/'source-summary.json').write_text(json.dumps(dict(revision=REV,selection=excluded,limits='Small controlled-image pilot; API directory listings may be capped at 1000 entries. Does not represent all source images. No field-image validation.',audit=report),indent=2))
    print(json.dumps(report['counts'],indent=2),flush=True)
CLASSES_REVERSE={v:k for k,v in CLASSES.items()}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='data');parser.add_argument('--groups-per-class',type=int,default=120);parser.add_argument('--exclude-manifest');args=parser.parse_args()
    if args.groups_per_class<1:raise SystemExit('Group count must be positive')
    ROOT=Path(args.root);ROOT.mkdir(parents=True,exist_ok=True)
    run(args.groups_per_class,args.exclude_manifest)
