"""CPU-capable MobileNetV3-Small transfer baseline. No final-test-based selection.
Run from project root: python -m ml.train_baseline --manifest data/manifest.csv --root data --output experiments/baseline-v1
"""
import argparse,csv,hashlib,json,random,time
from pathlib import Path
from ml.audit_manifest import audit

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--root',required=True);p.add_argument('--output',required=True);p.add_argument('--epochs',type=int,default=10);p.add_argument('--seed',type=int,default=42);p.add_argument('--fine-tune-last',type=int,default=0);p.add_argument('--warmup-epochs',type=int,default=3);p.add_argument('--strong-augmentation',action='store_true');a=p.parse_args()
    if a.fine_tune_last<0 or a.fine_tune_last>12 or a.warmup_epochs<0:raise SystemExit('Invalid fine-tuning configuration')
    if a.epochs<1:raise SystemExit('Epochs must be positive')
    out=Path(a.output)
    if out.exists():raise SystemExit('Run already exists; choose a new output')
    root=Path(a.root)
    with open(a.manifest,newline='') as f:rows=list(csv.DictReader(f))
    report=audit(rows,root)
    if not report['passes']:raise SystemExit(json.dumps(report['errors']))
    import numpy as np
    import torch
    from torch import nn
    from torch.utils.data import Dataset,DataLoader
    from torchvision.models import mobilenet_v3_small,MobileNet_V3_Small_Weights
    from torchvision import transforms
    from PIL import Image,ImageOps
    from ml.reliability import metrics
    torch.hub.set_dir(str(Path('data/torch-cache')))
    random.seed(a.seed);np.random.seed(a.seed);torch.manual_seed(a.seed);torch.set_num_threads(4)
    classes=sorted({r['label'] for r in rows if r['role']=='train'})
    if len(classes)<2:raise SystemExit('At least two training classes are required')
    if any(r['label'] not in classes for r in rows):raise SystemExit('An evaluation label is absent from training; handle unknown classes in a separate OOD evaluation.')
    for role in ['train','validation','temperature','conformal','policy','test']:
        if {r['label'] for r in rows if r['role']==role}!=set(classes):raise SystemExit(f'{role} does not cover every class. Revisit the dataset scope before training.')
    # Fixed training recipe: ImageNet RGB normalization. Only train is augmented.
    normalize=transforms.Normalize([.485,.456,.406],[.229,.224,.225])
    base=[transforms.Resize((224,224),interpolation=transforms.InterpolationMode.BILINEAR)]
    augment=[transforms.RandomResizedCrop(224,scale=(.7,1),ratio=(.85,1.15)),transforms.RandomHorizontalFlip(),transforms.RandomRotation(10),transforms.ColorJitter(.25,.25,.15,.03)] if a.strong_augmentation else base+[transforms.RandomHorizontalFlip(),transforms.RandomRotation(10)]
    train_transform=transforms.Compose(augment+[transforms.ToTensor(),normalize])
    eval_transform=transforms.Compose(base+[transforms.ToTensor(),normalize])
    class Photos(Dataset):
        def __init__(self,role):self.rows=[r for r in rows if r['role']==role];self.transform=train_transform if role=='train' else eval_transform
        def __len__(self):return len(self.rows)
        def __getitem__(self,i):
            r=self.rows[i];path=root/r['path']
            if hashlib.sha256(path.read_bytes()).hexdigest()!=r['sha256']:raise ValueError('Image changed after audit')
            with Image.open(path) as image:x=self.transform(ImageOps.exif_transpose(image).convert('RGB'))
            return x,classes.index(r['label'])
    train=Photos('train');validation=Photos('validation')
    train_loader=DataLoader(train,batch_size=32,shuffle=True,num_workers=0)
    val_loader=DataLoader(validation,batch_size=32,num_workers=0)
    model=mobilenet_v3_small(weights=MobileNet_V3_Small_Weights.DEFAULT)
    for parameter in model.features.parameters():parameter.requires_grad=False
    model.classifier[-1]=nn.Linear(model.classifier[-1].in_features,len(classes))
    groups=[dict(params=list(model.classifier.parameters()),lr=.001)]
    fine_blocks=list(model.features)[-a.fine_tune_last:] if a.fine_tune_last else []
    if fine_blocks:groups.append(dict(params=[p for b in fine_blocks for p in b.parameters()],lr=.0001))
    optimizer=torch.optim.AdamW(groups,weight_decay=.001)
    counts=[sum(r['label']==c for r in train.rows) for c in classes]
    loss_fn=nn.CrossEntropyLoss(weight=torch.tensor([len(train)/(len(classes)*n) for n in counts]))
    out.mkdir(parents=True)
    config=dict(model='MobileNetV3-Small',classes=classes,seed=a.seed,epochs=a.epochs,input_size=224,
        manifest_sha256=hashlib.sha256(Path(a.manifest).read_bytes()).hexdigest(),selection='validation macro-F1 only',
        device='cpu',trainable=f'classifier + last {a.fine_tune_last} feature blocks after {a.warmup_epochs} warmup epochs; feature batch norms fixed',strong_augmentation=a.strong_augmentation,field_validated=False)
    (out/'config.json').write_text(json.dumps(config,indent=2));best=-1;history=[]
    for epoch in range(a.epochs):
        started=time.time();model.train();model.features.eval()
        if epoch>=a.warmup_epochs:
            for block in fine_blocks:
                block.train()
                for parameter in block.parameters():parameter.requires_grad=True
            for module in model.features.modules():
                if isinstance(module,nn.BatchNorm2d):module.eval()
        for x,y in train_loader:
            optimizer.zero_grad();loss=loss_fn(model(x),y);loss.backward();optimizer.step()
        model.eval();records=[]
        with torch.inference_mode():
            for x,y in val_loader:
                for logits,target in zip(model(x).tolist(),y.tolist()):records.append(dict(logits=logits,label=classes[target]))
        score=metrics(records,classes);history.append(dict(epoch=epoch+1,validation_macro_f1=score['macro_f1'],seconds=time.time()-started))
        if score['macro_f1']>best:
            best=score['macro_f1'];torch.save(model.state_dict(),out/'best.pt')
        (out/'history.json').write_text(json.dumps(history,indent=2));print(history[-1],flush=True)
    model.load_state_dict(torch.load(out/'best.pt',weights_only=True));model.eval()
    # Export outputs with logits; probability calibration is a separate stage.
    torch.onnx.export(model,torch.zeros(1,3,224,224),str(out/'classifier.onnx'),input_names=['images'],output_names=['logits'],dynamic_axes={'images':{0:'batch'},'logits':{0:'batch'}},opset_version=17,dynamo=False)
    import onnxruntime as ort
    session=ort.InferenceSession(str(out/'classifier.onnx'),providers=['CPUExecutionProvider'])
    x,_=next(iter(val_loader)); parity_count=len(x)
    with torch.inference_mode():expected=model(x).numpy()
    observed=session.run(None,{'images':x.numpy()})[0];np.testing.assert_allclose(expected,observed,atol=1e-4,rtol=1e-4)
    output=dict(classes=classes,model_sha256=hashlib.sha256((out/'classifier.onnx').read_bytes()).hexdigest())
    for role in ['temperature','conformal','test']:
        dataset=Photos(role);records=[];index=0
        with torch.inference_mode():
            for x,y in DataLoader(dataset,batch_size=32,num_workers=0):
                for logits,target in zip(model(x).tolist(),y.tolist()):
                    r=dataset.rows[index];records.append(dict(id=r['id'],group=r['group'],label=classes[target],domain=r['domain'],logits=logits));index+=1
        output[role+'_rows']=records
    (out/'calibration-input.json').write_text(json.dumps(output,indent=2));(out/'status.json').write_text(json.dumps(dict(status='complete',onnx_parity_samples=parity_count,guidance_enabled=False)))
    print('Baseline exported. Run ml.calibrate next. No test scores were used to select the checkpoint.')
if __name__=='__main__':main()
