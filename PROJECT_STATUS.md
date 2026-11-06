# Project status — read this first

Last updated: 6 November 2026, Nepal time.

This is the current project reference. Update it after each meaningful implementation, experiment or user decision. Historical details live in docs/HANDOFF.md; actual metrics come from saved experiment files, not recollection.

## Fixed user requirements

- College mini project built around the supplied proposal: crop leaf classification + calibrated confidence + conformal prediction + unknown-input checking + three-action triage (guidance / recapture-monitor / expert).
- Good working demonstration, clear presentation, restrained attractive appearance. No flashy or misleading interface.
- `main project` is the actual project. Sibling LeafLens and external GitHub projects are references only. Do not edit, merge or push to LeafLens.
- Show at least three clickable real reference photographs. Preset results must not masquerade as photo inference; scanner demo buttons have been removed.
- Investigate paddy as second crop; corn is fallback. Neither has a trained model yet. Tomato-only was an initial engineering choice, not the final scope promised by the proposal.
- Latest user steering: prioritize licensed field data, field-inclusive retraining with a frozen DINOv2 comparison, mixed-domain calibration, domain routing and triage ablations. Keep guidance disabled; paddy/corn are future work. Usage tracking remains suspended. Completed one-time continuation was removed on 5 November.

## Built and verified

| Component | Current state |
|---|---|
| Scanner / sample selection / local upload | Working |
| Project flow / measured evidence page | Working |
| Local server | `.venv/bin/python server.py`, http://127.0.0.1:4180 |
| Actual inference | source-v2 MobileNetV3-Small tomato research pilot; original v1 archived; cached ONNX/profile integrity checks |
| Dataset preparation | Original PlantVillage photo download, declared leaf grouping, deterministic split manifest and checksum/leakage audit |
| Training | CPU frozen-feature baseline executed; validation macro-F1 selection; ONNX parity verified |
| Calibration/conformal | Separate probability/conformal splits; LAC live, APS comparison; nominal90% coverage under assumptions |
| Unknown-input scoring | Energy score implemented; measured ranking poor; no validated live cutoff |
| Quality checks | Exposure/detail plus alpha/checkerboard-cutout heuristics; not a learned leaf detector |
| Guidance | Disabled: no validated policy or complete curated management KB |
| Tests | 44 passing in `.venv`, including actual ONNX inference |

## Actual pilot-v1 evidence — do not overwrite

480 original source photos, one per publisher-recorded leaf; four tomato classes. Split counts:250 train /39 validation /47 temperature /62 conformal /27 policy /55 test.

- Controlled test:90.9% accuracy, macro-F1 .906, LAC coverage89.1%.
- Field-style test:42.1% accuracy on38 known images, macro-F1 .352, LAC coverage42.1%.
- Unknown energy AUROC .512 on19 same-crop unfamiliar disease images: no reliable rejection evidence.
- Full traces: data/manifest.csv; data/source-summary.json; experiments/pilot-v1*; models/evaluation.json; docs/PILOT_RESULTS.md.
- Test/field cohorts have now been inspected. They cannot be reused as blind final tests after tuning.

## Known pilot-v1 failures — do not hide or hardcode away

1. Healthy reference photograph predicted Septoria with high confidence.
2. User-reported healthy watermarked multi-leaf photograph (`images.jpeg`) predicted early blight .9758; healthy status is user-reported, not independently verified.
3. Different original PlantVillage early-blight check predicted late blight .8916, even though recorded leaf group was absent from pilot.
4. Checkerboard stock cutout predicted Septoria .7385. A generic input guard now requests recapture without inference. This fixes the input-type handling, not classifier accuracy.

Local error records: data/error-analysis/. Never train on these and then call the same examples independent tests. No image-specific label override, no confidence thresholds fitted on final tests, no diagnosis guarantee from singleton sets. Model UI leads with triage action and marks the candidate unverified; scores remain inspectable.

## Latest improvement: per-class error review

`ml/report_errors.py` now generates `models/error-review.json` from frozen saved logits, without retraining or threshold fitting. It includes per-class recalls/confusions, descriptive score>=0.8 errors and Wilson 95% intervals (independence assumption explicitly stated).

Measured field failures: healthy0/8 correct, late blight4/10, Septoria3/11, early blight9/9. Overall22/38 field errors, including17 errors with model score>=0.8. This is a systematic field-generalization problem, not just a confusing UI. Controlled test has5/55 errors, none with score>=0.8. These are small cohorts; do not treat class performance as a precise population estimate.

23 tests pass. No model weights, calibration thresholds or claimed accuracy changed in this milestone.

## Immediate priorities

1. Review source-v2 per-class errors and predeclare the next experiment before fitting it.
2. Prioritize audited, field-representative training and development data, especially healthy leaves; preserve both completed pilots and keep user check photographs out of training/calibration.
3. Build independent field-development/calibration data and separate unseen-disease/non-leaf groups; do not silently treat previously inspected field tests as new development evidence.
4. Measure accepted error at useful coverage, per-class/domain calibration and set coverage with uncertainty estimates.
5. Continue actual paddy file/label/license/group audit; do not add a decorative crop option that uses the tomato model.
6. Curate guidance and evaluate policy before enabling automatic management advice.
7. Re-run tests, verify app behavior and update this file plus HANDOFF after every milestone.

## Next-session entry point

Usage tracking is suspended at the user’s request; do not query or report it unless asked again. Current preview process last started as session8444. Inspect port before launching another server. Environment:project `.venv` Python3.12; locked versions in ml/environment-lock.txt. System Python3.14 lacks ML dependencies. curl uses working system TLS; do not disable certificate verification.

No main-project GitHub repository has been created. Earlier LeafLens draft PR#1 is unrelated to this main implementation and must remain untouched.

## Activity log

- 5 Nov 2026: Created this canonical status record and project AGENTS.md instructions for persistent reference/update discipline. Added a reproducible per-class failure review and two tests. Preserved original model and all known failures.

## Executed source-v2 and refreshed flow

User asks to ignore usage tracking for now; no limit checks/reports. Updated app flow with eight labelled stages, actual readiness, two active triage outcomes and crop roadmap; browser checked.

Predeclared source-v2 experiment tests stronger augmentation and final-three-feature-block fine-tuning after3 classifier-only warmup epochs. Dataset audit yielded391 additional valid groups, not the requested880; protocol amended before fitting to reuse original250 TRAIN-ONLY groups, giving641 images and475 training examples. All original non-training groups and the public check-photo group remain excluded; two tests verify these boundaries. Training completed in experiments/source-v2; ONNX parity and25 tests passed. source-v2 is now the active research pilot after explicit disclosure; original files archived under models/archive/pilot-v1. Guidance remains disabled.

## Source-v2 measured checkpoint

- Matched development validation38 images: original pilot macro-F1 .9544; selected source-v2 macro-F1 1.0. Selection score is not independent test evidence.
- Fresh grouped controlled test49 images:91.8% accuracy, macro-F1 .912; LAC coverage95.9%, mean set size1.143. APS coverage93.9%, mean size1.796. Different controlled test cohort from pilot-v1, so do not directly rank the two controlled accuracies.
- Same previously inspected38-image field benchmark:50.0% accuracy, macro-F1 .432, LAC coverage55.3%. Healthy field recall still0/8; no reliable field diagnosis. This is a historical comparison, not a new blind result.
- Only one healthy conformal-calibration image. Per-class calibration evidence is inadequate; do not enable guidance.
- Original training groups reused only in training; every original non-training group and public-check group excluded. New untouched source roles are separate.
- Runtime and API both verified as source-v2; source-v1 archive preserved. Error-review generation now verifies profile/logit model hashes to prevent reporting old logits under the new temperature.
-25 tests pass, including experiment-boundary checks. UI flow shows eight stages with actual statuses, active recapture/expert paths, disabled guidance and paddy/corn roadmap.

## Deferral analysis checkpoint — 5 November

Reviewed the user-supplied `deferral_analysis (1).py`. Adapted its useful reporting into `ml/deferral_analysis.py`, reusing probabilities, conformal inversion, actual decision policy and Wilson intervals. Corrected invented monitor actions, empty-set priority and confidence tie-breaking masquerading as pure set size. Existing confidence metrics remain available; new analysis adds raw-softmax/calibrated-confidence/pure-set-size ablation with whole tied-score blocks and explicitly defined step AURC.

Executed on saved source-v2 predictions only; outputs in `experiments/source-v2-deferral/` (report.md, report.json, predictions.csv, risk_coverage.csv). Replayed actions assume capture quality passes and unfamiliar=False; these are not logged end-to-end app outcomes. Controlled singleton accuracy40/42 (95.2%); historical field15/26 (57.7%). All87 known predictions deferred, so accepted coverage0 and accepted accuracy undefined. Historical unknown energy AUROC0.5956 on19 unknown versus38 known, copied from matching prior evaluation. No new fitting or independent test claim. 30 tests pass. No plotting dependency installed; curve coordinates exported as CSV.

Next data work must reserve additional training/validation and temperature-fitting groups alongside the requested conformal calibration, threshold-tuning and sealed final test sets. Already inspected PlantDoc images cannot become an untouched final test. Aim for100+ images in each requested field evaluation role with healthy leaves represented, subject to actual licensed independent groups; targets are not achieved counts. DINOv2 superiority remains an unverified hypothesis. Background removal and domain routing require development ablations; neither is implemented. Current field accuracy50%, healthy0/8 remain report limitations. Guidance remains disabled; paddy/corn future work only.

## Field-data acquisition and audit — 5 November

Verified primary publisher licences (CC BY4.0) and pinned versions: PlantDoc training partition at5467f6012d78d1c446145d5f582da6096f852ae8; Mendeley jttrv2w27r v2; CCMT bwh3zbpkpv v1 raw healthy/Septoria only. References and full pre-fitting protocol: docs/FIELD_DATA_PROTOCOL.md; targets configs/field-data.json. Ambiguous CCMT leaf blight and augmented images excluded.

Executed ml/inventory_field.py --download-per-class100. Inventory4604 files (~406MB), including905 labelled healthy. Downloaded/audited834 deterministic candidates (255 labelled healthy);830 quarantine rows,2 exact overlaps with earlier images excluded,1 truncated image and1 publisher-checksum mismatch. Quarantine is not training-ready. File counts are not independent leaf counts. Metadata and download provenance retained in data/field-development/. No inference run on these images.

Executed ml/review_field_duplicates.py:2 exact pixel-duplicate groups (no conflicting labels),38 perceptual candidate pairs pending review. dHash<=4 is only a screening heuristic; rotated/cropped duplicates and physical leaf/capture identity remain unresolved. Existing historical/source exact-byte overlap checked; perceptual comparison against all prior cohorts remains unfinished. No final-test roles assigned. No model retraining or new accuracy result.

Flow page updated with data-audit progress and paddy/corn future-work wording.33 tests pass; JS syntax check passed. Next: resolve checksum anomaly, review duplicate/background/label/capture groups (including old-cohort perceptual overlap), expand healthy/source-balanced downloads as needed, then freeze six role partitions. Targets100+ field images each in conformal/policy/final test with25+ healthy per role remain targets, not achieved splits. Never manufacture independence or treat the38 historical field images as unseen final evidence.

## Reviewed field duplicates and prior overlaps — 5 November

Re-downloaded both flagged files. Bangladesh Healthy_62.jpg now matches the publisher SHA and decodes; preserved initial mismatched payload under rechecks/. CCMT healthy443_.jpg still matches publisher SHA but is truncated; exclude it. Rebuilt cached download audit:831 quarantine,2 initial exact prior overlaps,1 bad file.

Visually reviewed38 near-pair candidates in5 contact sheets.21 pairs show the same scene/derivatives (including a cross-label scene);17 show different photographs but do not establish independent leaves. Review decisions with input hashes saved to visual-pair-review.json. Several inspected Bangladesh/CCMT images are detached leaves on plain backgrounds; field collection origin must not be equated with natural field-scene domain. No diagnosis labels validated from visual inspection.

ml/field_prior_overlap.py screened834 candidates against934 unique earlier source/field/reference/user image paths, no decode failures.3 candidate pairs matched prior field images; all3 visually confirmed. Includes1 additional recompressed/resized scene beyond2 earlier byte overlaps. Saved prior-overlap.json and prior-visual-review.json. Whole-image dHash can miss crops/rotations; no claim of complete independence.

ml/stage_field_review.py propagates prior exclusion and label conflicts through reviewed duplicate components; picks one deterministic representative per otherwise eligible scene. staged-review.csv has805 pending capture/background review,21 duplicate copies,4 conflicting-label images,3 prior-scene overlaps,1 bad file. All roles unassigned; physical capture groups unresolved; training_ready=false.37 tests pass including propagation, deterministic representative, conflict and unknown-ID checks. Next: background annotation and capture-sequence review of805 remaining candidates, augment download pool if natural-field quotas fail, freeze independent split roles only after readiness checks. Current model/accuracy unchanged.

## Scanner score visibility fix

User reported Analyze showing no percentage. Live status and POST /api/analyze verified working. UI previously hid headline score for unvalidated model and collapsed score details. Added visible labelled model score and expanded class-score details; retained expert/recapture lead and diagnostic caveat. Added30-second request timeout. JS syntax passed. Actual healthy reference test returned Septoria .857154 with expert referral: known classification failure remains, no accuracy fix claimed. Reload browser for frontend changes.

## End of day — 5 November 2026

User requested a saved summary and stopping for the day. Comprehensive resume checkpoint: docs/DAY_SUMMARY_2026-11-05.md. Main priority is actual field/healthy classification reliability; expert verification is only a recommendation, not an expert service or proof of error detection. Current model remains unchanged. Resume only when asked.

## Deadline steering

User reports10 days left and explicitly asks to focus on the project, considering presentation later. No deck created. See docs/TEN_DAY_PLAN.md for bounded tomato-only work, data/training/evaluation milestones and stabilization buffer. Immediate next task remains scene-domain/capture review of805 candidates, followed by independent splits and field-inclusive training. No new crop scope or UI decoration. This is a plan, not a scheduled automation or promise of accuracy.

## Latest usage preference — supersedes suspension

User again requests managing usage limits. Use focused milestone batches, cached data, targeted tests and bounded experiments. Prioritize data review and one field-inclusive model before optional comparisons. Save restart instructions and completed/pending work after meaningful milestones. Remaining allowance requires an actual reading; no fabricated percentage, assumed reset time or guarantee of a pre-limit warning. No reset automation created.

## Background screening — 6 November 2026

Visually screened all805 remaining candidates using nine hashed contact sheets. Preliminary domains:237 natural-background,520 staged/plain,35 ambiguous,13 composite/illustration. Only44 healthy-labelled natural-background candidates; insufficient for75 healthy across conformal/policy/test alone. These counts are not independent validated leaves.

Saved decisions, screened-review.csv, summary,53 possible capture links and10 priority healthy-label checks under data/field-development/background-review/. Enlarged review of3 cross-label candidates confirmed1 same-scene label conflict (2 quarantined images);2 are different photographs with identity unresolved.50 candidate pairs remain pending.13 composites quarantined. Original staged-review.csv preserved; use screened-review.csv for new exclusions. Physical groups remain unresolved, roles unassigned, training_ready=false.

Added reproducible sheet/report tool with identity/hash validation and3 tests; full suite40 passed including actual ONNX inference. No retraining or new accuracy result. Next: enlarged pair/ambiguous-domain and label review, propagate groups/exclusions, expand natural-background healthy data before independent role freeze. Details: docs/BACKGROUND_REVIEW_2026-11-06.md.

## Capture consolidation and healthy expansion — 6 November 2026

Reviewed all53 capture candidates:32 same-leaf/scene links,9 precautionary keep-together links,1 confirmed cross-label scene,11 different photographs with physical identity unresolved. Enlarged all35 ambiguous thumbnails:26 assigned broad background categories,9 remain uncertain. Flagged17 screened images for source/species/label review; no automatic relabelling.

Consolidated all834 original downloads with original duplicate groups and propagated exclusions.726 candidate representatives remain (504 staged/plain,222 natural-background); natural-background labels:31 healthy,59 early blight,64 late blight,68 Septoria. Exclusions/statuses:58 duplicate/related captures,6 label-conflict images,18 source-label concerns,13 composites,3 prior overlaps,1 bad file,9 background-provenance cases. Reviewed component IDs do not establish independent plants; physical groups unresolved, roles unassigned, training_ready=false.

Downloaded40 additional CCMT healthy candidates (~2MB), preserving the original batch and predeclaring filename-neighborhood convenience sampling. All decode and match publisher checksums;1 exact match with the original batch,39 quarantined. Thumbnail screen:20 natural-background candidates,3 plain,17 ambiguous closeups. Full old-cohort overlap and capture/label review pending; not added to the726 count.

Added ml/consolidate_field_review.py with transitive prior/conflict propagation, precautionary grouping and hash checks.44 tests pass including actual ONNX inference. No model retraining or accuracy change. Current resume artifacts: data/field-development/background-review/consolidated-review.csv, consolidated-summary.json, capture-review.json and healthy-expansion/. Next: complete expansion overlap/group audit and source-label provenance; resolve realistic data/split scope before fitting.

GitHub: user explicitly requests a new PUBLIC pradip17k/crop-disease-risk-triage repository and terminal-based creation/push. Preparation in progress; LeafLens remains untouched.

## GitHub publication — 6 November 2026

Created public repository https://github.com/pradip17k/crop-disease-risk-triage using GitHub CLI at the user’s request. Initial project commit6534883 pushed to main; origin configured and tracking origin/main. Code, models/checkpoints, experiment results, manifests and review metadata included. Downloaded datasets, local user-check images, contact sheets, environment and caches excluded by .gitignore.44 tests passed before publication. LeafLens untouched.

## Shareable training-image folder — 6 November 2026

Added training_images/ with475 original active source-v2 train-role photographs grouped by class, manifest with source URLs/groups/hashes, and PlantVillage CC BY-SA3.0 attribution. All475 copies verified against saved SHA-256 values; evaluation/calibration roles and untrained field candidates excluded. Original data paths and model unchanged.
