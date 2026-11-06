# Crop Disease Risk Triage

A new college mini project built around the supplied proposal. LeafLens remains reference material in a separate sibling folder; no LeafLens weights or results have been copied into this project.

## Run locally

The verified ML runtime is Python 3.12 in the project virtual environment. Start the working pilot with:

```sh
.venv/bin/python server.py
```

Open http://127.0.0.1:4180. The scanner, project-flow page, evidence page and image preview are available. A small MobileNetV3-Small pilot is now connected for real predictions; it is not a reliable farm diagnostic. The three reference photographs run through actual inference.

## Actual inference

Install optional dependencies in an isolated environment with `python3 -m venv .venv` and `.venv/bin/python -m pip install -r ml/requirements.txt`. Place a trained 224×224 ImageNet-normalized ONNX classifier at `models/classifier.onnx` (input name `images`, output logits), and a matching `models/profile.json` produced by calibration. Model SHA-256 and class order must match. Restart the server. Images are sent only to the local Python process and are not written to disk. No external prediction API is used.

## What works now

- Responsive scanner, project-flow explanation and honest research-status page.
- Image validation/preview, three real reference photographs and downloadable JSON observation reports.
- Local inference adapter with model/profile integrity checking, capture heuristics, calibrated probabilities, conformal sets, energy-cutoff support and three-action triage.
- Pure-Python LAC/APS, temperature fitting from saved logits, ECE/NLL/Brier, prediction-set coverage and risk–coverage metrics.
- Tests for numeric calculations, triage and cross-partition group leakage.

## What is still pending

Broader field-representative data, representative negative data, fitting a useful unknown-input cutoff, stronger independent field evaluation, guidance curation and enabling a validated policy. The first pilot has actual measured results below; it does not establish reliable guidance.

Run checks with `.venv/bin/python -m unittest discover -s tests -v`. Calibrate saved logits with `python3 -m ml.calibrate input.json --output experiments/run-name --method LAC`. See its input contract in `ml/calibrate.py`; no example scores are experimental evidence. Outputs never enable guidance automatically.

The first scope candidate is tomato healthy/early blight/late blight/Septoria, subject to actual source/field label compatibility and sample counts. See `docs/PROJECT_FLOW.md` for the research protocol.

## Dataset audit and related-work decisions

Before training, prepare a CSV with `id,path,label,domain,role,group,sha256,source_url,license` and run:

```sh
python3 -m ml.audit_manifest data/manifest.csv --root data --output experiments/dataset-audit.json
```

Image paths are relative to `--root`. Roles are `train`, `validation`, `temperature`, `conformal`, `policy`, `test`. Capture group IDs must have consistent meaning across datasets and roles. Audit checks exact duplicates and declared groups; it cannot guarantee physical leaf independence or detect every near duplicate.

Calibration reports include macro-F1/confusion matrices, per-domain measurements and per-class conformal coverage. See `docs/RELATED_WORK.md` for the related repositories/papers reviewed, the changes adopted, and limitations. These changes improve evaluation readiness; they are not new model-performance results.

## Reproducible baseline pipeline

`ml/prepare_manifest.py` freezes deterministic capture-group splits from a labelled, provenance-bearing inventory. `ml/train_baseline.py` implements a CPU MobileNetV3-Small frozen-feature classifier baseline, selects by validation macro-F1, verifies ONNX tensor parity and exports saved logits for calibration. The baseline training script has been executed successfully for pilot-v1, including ONNX parity checks. The tested dependency versions are in ml/environment-lock.txt.

```sh
python3 -m ml.prepare_manifest data/inventory.csv --root data --output data/manifest.csv
python3 -m ml.train_baseline --manifest data/manifest.csv --root data --output experiments/baseline-v1
python3 -m ml.calibrate experiments/baseline-v1/calibration-input.json --output experiments/baseline-v1-lac
```

Install `ml/training-requirements.txt` in an isolated environment first. Freeze tested dependency versions once the environment is verified. All six roles must cover the chosen classes before training. No accuracy claim follows from code existing.

## First real pilot (5 November 2026)

480 pinned original PlantVillage tomato photos, one per publisher-recorded leaf: 250 train, 39 validation, 47 temperature, 62 conformal, 27 reserved policy and 55 test. The demo image exact byte hashes were excluded. Source selection is a small hash-selected cohort, not the full dataset.

- Controlled test: 90.9% accuracy; macro-F1 0.906; LAC coverage 89.1%.
- PlantDoc field-style check: 42.1% accuracy on 38 known images; macro-F1 0.352; LAC coverage 42.1%.
- Unknown energy ranking: AUROC 0.512 on 19 same-crop unfamiliar disease images. This does not support reliable unknown detection.
- Guidance remains disabled. Live predictions request expert verification or recapture; high confidence is not enough.

The healthy reference photo is currently misclassified with high confidence. The UI explicitly displays model disagreement with a known reference label. Do not replace this result with a preset success.

Seventeen tests pass in the virtual environment, including real inference, quality gating and model/profile integrity. See docs/PILOT_RESULTS.md and the Research & evidence page.

## Active research pilot: source-v2

The active local bundle is now source-v2; the original pilot is preserved in models/archive/pilot-v1. Source-v2 uses475 training images, stronger training-only augmentation and partial feature fine-tuning after3 warmup epochs. Exact protocol and pre-training dataset amendment: docs/SOURCE_V2_PROTOCOL.md.

New controlled test:91.8% accuracy on49 images. On the reused38-image historical field benchmark:50.0% accuracy, but healthy recall remains0/8. This is not independent proof of improvement or farm reliability. Healthy conformal calibration has only1 image. Automatic guidance remains disabled.25 tests pass. The Project flow page distinguishes actual active components from unvalidated/pending work.

## Latest checkpoint — 6 November 2026

44 tests pass locally, including real ONNX inference. Data review has produced726 candidate representatives from834 original downloaded candidates, including222 natural-background candidates and only31 healthy-labelled natural-background candidates. Physical capture independence and source labels still need review; no new splits or retraining have been run. A separate40-image healthy expansion remains quarantined. See PROJECT_STATUS.md for the latest resume point and docs/HANDOFF.md for history.

## Repository contents

Code, tests, active/archived model bundles, saved training checkpoints, calibration/evaluation records, dataset manifests and review metadata are versioned. The active model’s475 training photographs are included in training_images/ with attribution and a manifest. Other downloaded dataset photographs, user check images, generated contact sheets, runtime caches and the Python environment remain local. The three attributed UI sample photos are included; see web/samples/credits.json. Download provenance and licences are recorded in manifests and docs/FIELD_DATA_PROTOCOL.md. Re-running photo audits requires restoring the referenced source images; a Git checkout alone is not the full training dataset.

For a fresh checkout, use Python3.12: `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install -r ml/requirements.txt`. The included active model enables local inference. Training requires the additional ml/training-requirements.txt dependencies and restored datasets. Version details from the tested environment are in ml/environment-lock.txt.

## Browse the training photographs

Open [training_images/](training_images/README.md) for the475 photographs actually used to train source-v2, organized into healthy, early_blight, late_blight and septoria folders. These download with a normal clone.
