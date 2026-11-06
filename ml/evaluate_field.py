"""Frozen pilot evaluation on original PlantDoc test images; no fitting on this set."""
import argparse,csv,hashlib,json,math,subprocess
from pathlib import Path
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image,ImageOps
import onnxruntime as ort
from ml.reliability import metrics,probabilities,prediction_set
REV='5467f6012d78d1c446145d5f582da6096f852ae8'
MAPPING={'Tomato Early blight leaf':'early_blight','Tomato Septoria leaf spot':'septoria','Tomato leaf late blight':'late_blight','Tomato leaf':'healthy','Tomato leaf bacterial spot':'unknown','Tomato leaf mosaic virus':'unknown'}
def fetch(url,path):
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True);subprocess.run(['curl','-fsSL','--retry','2','--max-time','60',url,'-o',str(path)],check=True)
    return path.read_bytes()
def run(model_path='experiments/pilot-v1/classifier.onnx',profile_path='experiments/pilot-v1-lac/profile.json',output_path='experiments/pilot-field-v1',historical=False):
    output=Path(output_path);output.mkdir(exist_ok=True)
    if (output/'evaluation.json').exists():raise SystemExit('Preserve completed field evaluation; do not retune on this cohort')
    model=Path(model_path);profile=json.loads(Path(profile_path).read_text());classes=profile['classes']
    if hashlib.sha256(model.read_bytes()).hexdigest()!=profile['model_sha256']:raise ValueError('Model mismatch')
    exclude={r['sha256'] for r in csv.DictReader(open('data/manifest.csv',newline=''))};exclude|={hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('web/samples').glob('*.jpg')}
    planned=[]
    for name,label in MAPPING.items():
        listing=json.loads(fetch(f'https://api.github.com/repos/pratikkayal/PlantDoc-Dataset/contents/test/{quote(name)}?ref={REV}',Path('data/source/field-'+name+'.json')))
        for entry in sorted(listing,key=lambda r:r['name']):
            if entry['type']=='file' and Path(entry['name']).suffix.lower() in ['.jpg','.jpeg','.png']:
                planned.append((name,label,entry))
    def download(item):
        name,label,e=item;url=f'https://raw.githubusercontent.com/pratikkayal/PlantDoc-Dataset/{REV}/test/{quote(name)}/{quote(e["name"])}'
        path=Path('data/field')/e['sha'];raw=fetch(url,path)
        return dict(id=e['sha'],label=label,source_class=name,path=str(path),sha256=hashlib.sha256(raw).hexdigest(),source_url=url)
    with ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(download,planned))
    rows=[r for r in rows if r['sha256'] not in exclude];unique={r['sha256']:r for r in rows};rows=list(unique.values())
    session=ort.InferenceSession(str(model),providers=['CPUExecutionProvider']);records=[];unknown=[];rejected=[]
    for r in rows:
        try:
            with Image.open(r['path']) as im:
                im=ImageOps.exif_transpose(im).convert('RGB').resize((224,224),Image.Resampling.BILINEAR)
                x=np.array(im,dtype=np.float32)/255
            x=((x-[.485,.456,.406])/[.229,.224,.225]).transpose(2,0,1)[None].astype(np.float32)
            logits=session.run(None,{'images':x})[0][0].tolist();p=probabilities(logits,profile['temperature']);pred=classes[p.index(max(p))]
            energy=-max(logits)-math.log(sum(math.exp(v-max(logits)) for v in logits))
            row=dict(r,logits=logits,predicted=pred,confidence=max(p),energy=energy,candidates=prediction_set(p,classes,profile))
            (unknown if r['label']=='unknown' else records).append(row)
        except Exception as e:rejected.append(dict(id=r['id'],reason=str(e)))
    known_energy=[r['energy'] for r in records];unknown_energy=[r['energy'] for r in unknown]
    auroc=sum(u>k or .5*(u==k) for u in unknown_energy for k in known_energy)/(len(known_energy)*len(unknown_energy)) if known_energy and unknown_energy else None
    result=dict(historical_benchmark_reused=historical,cohort='Original PlantDoc publisher test split, selected tomato classes',revision=REV,model_sha256=profile['model_sha256'],known=metrics(records,classes,profile['temperature']),unknown_count=len(unknown),unknown_energy_auroc=auroc,
        set_coverage=sum(r['label'] in r['candidates'] for r in records)/len(records) if records else None,
        average_set_size=sum(len(r['candidates']) for r in records)/len(records) if records else None,
        source_counts={name:sum(r['source_class']==name for r in records+unknown) for name in MAPPING},decode_failures=rejected,
        limits=['Small web-sourced field-style benchmark, not a prospective farm trial.','No model/calibration/policy fitting on these images. Do not tune the frozen pilot against these results.','Exact source byte overlap excluded; related leaves, near duplicates and label noise remain possible.','Unknown classes are same-crop bacterial spot/mosaic; no non-leaf detection evidence.','No quality gate; these are model-only measurements. Guidance remains disabled.'])
    if historical:result['limits'].insert(0,'Previously inspected historical benchmark reused for comparison; not a new blind field test. No model fitting or candidate selection on these scores.')
    (output/'predictions.json').write_text(json.dumps(records+unknown,indent=2));(output/'evaluation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model',default='experiments/pilot-v1/classifier.onnx');p.add_argument('--profile',default='experiments/pilot-v1-lac/profile.json');p.add_argument('--output',default='experiments/pilot-field-v1');p.add_argument('--historical',action='store_true');a=p.parse_args();run(a.model,a.profile,a.output,a.historical)
