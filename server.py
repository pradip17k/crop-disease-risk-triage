"""Local-only app server. Optional trained ONNX bundle enables actual inference."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import base64, hashlib, io, json, math, mimetypes
from functools import lru_cache
from urllib.parse import unquote, urlsplit
from ml.reliability import probabilities, prediction_set, decide
from ml.image_quality import check_cutout
ROOT = Path(__file__).resolve().parent
WEB = ROOT/'web'
BUNDLE = ROOT/'models'
MAX_BYTES = 7 * 1024 * 1024

@lru_cache(maxsize=1)
def load_runtime(model_stamp,profile_stamp):
    import onnxruntime as ort
    import numpy
    from PIL import Image
    profile=json.loads((BUNDLE/'profile.json').read_text())
    raw=(BUNDLE/'classifier.onnx').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=profile['model_sha256']:
        raise ValueError('Model and reliability profile do not match.')
    classes=profile['classes']
    if not classes or len(classes)!=len(set(classes)) or not set(classes)<={'healthy','early_blight','late_blight','septoria'}:
        raise ValueError('Invalid tomato class mapping')
    prediction_set(probabilities([0]*len(classes),profile['temperature']),classes,profile)
    options=ort.SessionOptions();options.intra_op_num_threads=2
    session=ort.InferenceSession(raw,sess_options=options,providers=['CPUExecutionProvider'])
    if session.get_inputs()[0].name!='images' or session.get_outputs()[0].shape[-1]!=len(classes):
        raise ValueError('Model tensor contract does not match class profile')
    return profile,session

def runtime():
    return load_runtime((BUNDLE/'classifier.onnx').stat().st_mtime_ns,(BUNDLE/'profile.json').stat().st_mtime_ns)

def bundle_status():
    try:
        profile,_=runtime()
        return dict(model_connected=True,model=profile['model_name'],version=profile.get('version','pilot-v1'),crop='Tomato',stage='pilot',field_validated=False)
    except (OSError,ValueError,KeyError,ImportError) as error:
        return dict(model_connected=False,crop='Tomato',stage='implementation',field_validated=False,reason='Trained bundle/dependencies unavailable or incompatible')

def infer(data):
    if not bundle_status()['model_connected']:
        raise ValueError('No trained model is connected. Use Workflow demo or complete the training protocol.')
    try:
        import numpy as np
        import onnxruntime as ort
        from PIL import Image, ImageOps
    except ImportError as e:
        raise ValueError('Install ml/requirements.txt to enable model inference.') from e
    raw = base64.b64decode(data['image'], validate=True)
    if len(raw) > 5*1024*1024:
        raise ValueError('Use an image below 5 MB.')
    profile,session=runtime()
    with Image.open(io.BytesIO(raw)) as im:
        if im.width * im.height > 20_000_000 or min(im.size) < 128:
            raise ValueError('Use an image at least 128 pixels per side and below 20 megapixels.')
        im = ImageOps.exif_transpose(im)
        cutout_issue=check_cutout(im)
        if cutout_issue:
            return dict(mode='quality',model=profile['model_name'],quality_ok=False,decision=dict(action='recapture',reason=cutout_issue))
        im=im.convert('RGB')
        gray = np.array(im.resize((128,128)).convert('L'),dtype=float)
        detail = float((np.abs(np.diff(gray,axis=0)).mean()+np.abs(np.diff(gray,axis=1)).mean())/2)
        quality_ok = 35 <= gray.mean() <= 225 and detail >= 2
        if not quality_ok:
            return dict(mode='quality',model=profile['model_name'],quality_ok=False,decision=decide('',0,[],{},False))
        pixels = np.array(im.resize((224,224),Image.Resampling.BILINEAR),dtype=np.float32)/255
    x = ((pixels - [.485,.456,.406])/[.229,.224,.225]).transpose(2,0,1)[None].astype(np.float32)
    logits = session.run(None,{'images':x})[0][0].tolist()
    if len(logits) != len(profile['classes']):
        raise ValueError('Model output does not match class order.')
    p = probabilities(logits,profile['temperature'])
    labels = profile['classes']; label = labels[p.index(max(p))]
    candidates = prediction_set(p,labels,profile)
    energy = -math.log(sum(math.exp(v-max(logits)) for v in logits))-max(logits)
    # OOD cutoff must come from policy-development data, never an arbitrary constant.
    cutoff = profile.get('energy_cutoff')
    unfamiliar = cutoff is not None and energy > cutoff
    decision = decide(label,max(p),candidates,profile,unfamiliar=unfamiliar)
    return dict(mode='model',model=profile['model_name'],quality_ok=True,label=label,confidence=max(p),candidates=candidates,
                probabilities=dict(zip(labels,p)),energy=energy,unknown_check_available=cutoff is not None,
                alpha=profile['alpha'],decision=decision,independently_evaluated=profile.get('independently_evaluated',False))

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, code=200):
        raw=json.dumps(data,allow_nan=False).encode();self.send_response(code)
        self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        route=urlsplit(self.path).path
        if route == '/api/status':
            self.send_json(bundle_status());return
        if route == '/api/evaluation':
            report=BUNDLE/'evaluation.json'
            self.send_json(json.loads(report.read_text()) if report.exists() else dict(available=False));return
        file=(WEB/unquote(route).lstrip('/')).resolve() if route != '/' else WEB/'index.html'
        if not file.is_relative_to(WEB) or not file.is_file():
            self.send_error(404);return
        self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(file)[0] or 'application/octet-stream');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(file.read_bytes())
    def do_POST(self):
        if self.path != '/api/analyze': self.send_error(404);return
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0 < size <= MAX_BYTES: raise ValueError('Invalid upload size')
            data=json.loads(self.rfile.read(size)); self.send_json(infer(data))
        except (ValueError,KeyError,TypeError) as e:self.send_json(dict(error=str(e)),400)
        except Exception:self.send_json(dict(error='Inference failed. Check image format and model configuration.'),422)
if __name__ == '__main__':
    print('Crop Disease Risk Triage: http://127.0.0.1:4180',flush=True)
    ThreadingHTTPServer(('127.0.0.1',4180),Handler).serve_forever()
