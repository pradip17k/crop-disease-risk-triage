# First executed pilot: v1

The goal of this run was an actual, traceable end-to-end classifier and reliability pipeline. It is not the final college-project model and it has not established autonomous management reliability.

## Frozen data and model

Original PlantVillage revision `7f7ecc7e1eaca78107e3affe7cb5abd9427e139a`. Four tomato classes: early blight, healthy, late blight and Septoria. 120 publisher-recorded leaf groups per class, one image per group; 480 images total. A small hash-ordered source cohort was chosen before observing predictions. GitHub directory listings can be capped at 1,000 entries; this is not a full-dataset sample. Original source URLs and checksums are recorded in data/manifest.csv; code in ml/fetch_pilot.py.

Role counts: 250 train, 39 validation, 47 temperature, 62 conformal, 27 policy, 55 test. No declared group or exact byte overlap across roles. Near duplicates, incorrect leaf metadata and source labels remain possible. Exact demo photo hashes are excluded.

MobileNetV3-Small ImageNet pretrained features frozen, classifier trained 10 epochs on CPU; class-weighted cross entropy, training-only flip/rotation augmentation. Validation macro-F1 selects the checkpoint; test results do not. Model SHA-256 `432913b461e4f4de5afa91a274c8101fbe71ff8482bd4808f71221b4d45bdca3`. ONNX tensor parity passed on a validation batch, with tolerance 1e-4 absolute/relative. Training and server use EXIF-oriented RGB, square bilinear resize to 224×224 and ImageNet normalization. This is an explicit fine-tuning recipe, not the pretrained weights' default resize/crop geometry.

## Measured results

| Metric | Controlled test | Field-style check |
|---|---:|---:|
| Known images | 55 | 38 |
| Accuracy | 90.9% | 42.1% |
| Macro-F1 | 0.906 | 0.352 |
| ECE, 15 bins | 0.068 | 0.470 |
| NLL | 0.180 | 3.412 |
| Brier | 0.109 | 0.977 |
| LAC label coverage | 89.1% | 42.1% |
| LAC average set size | 0.964 | 0.947 |
| AURC | 0.008 | 0.634 |

Nominal conformal target is 90%; finite-test observed coverage varies, and exchangeability with source calibration is not established for field-shifted images. A small mean set size can coexist with wrong predictions or empty sets. APS was also evaluated on the same controlled cohort: coverage 83.6%, mean set size 1.455. No accepted-subset risk guarantee is inferred.

Field-style images come from original PlantDoc revision `5467f6012d78d1c446145d5f582da6096f852ae8`, publisher test directories: 9 early blight, 11 Septoria, 10 late blight and 8 tomato leaf/healthy. There are 19 unfamiliar same-crop examples (9 bacterial spot, 10 mosaic). Energy AUROC is 0.512, with higher energy pointing toward unknown. No classifier, probability calibration, conformal quantile or rejection threshold was fitted on this cohort. These are web-sourced cropped images with unresolved label noise/related-leaf independence; not an expert-confirmed farm trial.

## Working application and safeguards

Actual ONNX inference is connected. Samples are input photos, not preset predictions. Model profile and weights are hash checked; output/class contract checked; ONNX session cached; malformed uploads fail; low-quality images request recapture. Model predictions remain research estimates. Management guidance is disabled; no live unknown-input cutoff is fitted. The healthy demo reference currently receives a confidently incorrect Septoria prediction, which the UI exposes as disagreement.

## What follows

Do not retune pilot-v1 against its now-inspected test or field results. Define a next protocol before fitting: larger source cohort, separate field training/validation/calibration if used, and fresh independent final evaluation or clearly disclose benchmark reuse. Gather same-crop unseen disease and non-leaf negatives separately. Select policy thresholds only on development data; report useful guidance coverage and accepted errors with uncertainty intervals. Curate guidance before enabling it. A better interface is complete enough to demonstrate the flow; better field reliability remains the main research problem.

Executed dependencies are recorded in ml/environment-lock.txt. Saved run configs, logits, source manifest and reports are under data/ and experiments/; deployed summary under models/evaluation.json. These directories include public research data and are intentionally excluded from Git where appropriate.
