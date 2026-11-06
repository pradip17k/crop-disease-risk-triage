# Field data preparation — protocol before fitting

Recorded 5 November 2026. This is the next data experiment, not a new model result.

## Sources and licence audit

- **PlantDoc**, pinned revision `5467f6012d78d1c446145d5f582da6096f852ae8`: [publisher licence](https://github.com/pratikkayal/PlantDoc-Dataset/blob/5467f6012d78d1c446145d5f582da6096f852ae8/LICENSE.txt) is CC BY 4.0. Inventory only the publisher's training folders for the four mapped tomato classes. Previously evaluated test images stay historical. Web collection provenance and capture identity remain limitations.
- **Rachin and Likhon, Tomato Leaf Disease Classification Dataset**, [Mendeley version 2](https://data.mendeley.com/datasets/jttrv2w27r/2), DOI `10.17632/jttrv2w27r.2`, CC BY 4.0. The publisher reports Bangladesh collection and 380 healthy, 524 early-blight and 112 late-blight images. Verify actual files, label quality and whether capture sequences share leaves before allocating roles.
- **Mensah and collaborators, Dataset for Crop Pest and Disease Detection**, [Mendeley version 1](https://data.mendeley.com/datasets/bwh3zbpkpv/1), DOI `10.17632/bwh3zbpkpv.1`, CC BY 4.0. Use only the raw tomato healthy and Septoria folders. Exclude augmented folders and ambiguous “leaf blight”; its label cannot establish early versus late blight. The publisher describes mixed backgrounds, so farm origin does not mean every image is a natural-background field photograph.

Metadata snapshots retain publisher attribution/licence information. Any later distributed subset must include attribution, licence links and a record of selection or preprocessing changes. Downloaded images remain local research data.

## Roles and leakage boundaries

The requested three evaluation roles need additional training roles:

1. Train: field plus eligible controlled training groups; augmentation only here.
2. Validation: checkpoint/model/background-removal selection.
3. Temperature: probability calibration after selecting a frozen model.
4. Conformal: mixed-domain conformal calibration, separate from temperature fitting.
5. Policy: threshold/domain-detector tuning, separate from calibration.
6. Final test: sealed until the complete model, calibration and policy are frozen.

Target at least100 field images each for conformal, policy and final test, with at least25 healthy images per role and representation of all four known classes. These are minimum design targets, not current counts or statistical power guarantees. Record physical capture groups and per-source/class counts; never fill a quota using augmented copies. Reserve unknown disease/non-leaf development and final cohorts separately.

Group before splitting: exact bytes → decoded-pixel identity → candidate perceptual duplicates → reviewed capture/leaf sequences. Quarantine conflicting labels, drawings/composites, ambiguous species and unresolved derivative copies. Compare against all earlier source/field cohorts, user check photos and UI samples. All views or derivatives of a leaf remain in one role. Perceptual similarity alone does not establish physical-leaf independence.

No automatic final-test allocation while grouping is unresolved. A download inventory is deliberately not accepted by the training manifest auditor: its roles are unassigned and groups unresolved. No model predictions are run on candidate final images during data curation. Independent label/data-quality review may precede sealing; model-informed cherry-picking may not.

## Analysis plan

Compare field-inclusive MobileNetV3 against a frozen DINOv2 feature baseline using the same training/validation protocol; the claim that DINOv2 transfers better remains a hypothesis. Evaluate background augmentation/removal on validation only. A domain detector is an auxiliary routing signal, not proof of disease uncertainty or unknown detection. Evaluate its errors and coverage before live routing.

Report accuracy, healthy recall, conformal coverage and set size separately by domain and source. Report raw-confidence versus calibrated-confidence versus pure-set-size risk/coverage, singleton accuracy and unknown AUROC. A pooled conformal guarantee does not imply per-domain coverage under arbitrary shift. Preserve the exposed38-image field benchmark as historical. Current accuracy50% and healthy0/8 remain the stated limitations until a separately documented new evaluation exists.

Guidance remains disabled. Paddy and corn remain future work.

## Background audit clarification

The first visual duplicate review shows that farm-collected candidates include detached leaves photographed against plain backgrounds. Record collection origin separately from visible scene domain: natural background, staged/plain background, or ambiguous/composite. Do not count every candidate from these sources toward natural-field evaluation targets.805 candidates survive the first exclusions but still await this annotation and physical-capture grouping.
