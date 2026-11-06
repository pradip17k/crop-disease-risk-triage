# Resume here: Crop Disease Risk Triage

Updated 5 November 2026. This file is a factual handoff, not evidence of training completion.

## User decisions

- Main project directory: `/Users/pradiphapa/Documents/Crop Disease Risk Triage/main project`.
- The supplied proposal PDF is the fixed theme: lightweight crop disease classifier, calibrated confidence, conformal sets, unfamiliar-input checking, three-action triage and controlled-to-field evaluation. College mini project; polished, restrained, understandable presentation.
- Sibling `leaflens` is reference ONLY. Earlier work created draft PR https://github.com/pradip17k/leaflens/pull/1 before the user clarified this; do not continue or merge it. No new main-project GitHub repository exists yet. Do not push this project to LeafLens.
- Initial crop candidate tomato with healthy/early blight/late blight/Septoria, subject to actual dataset compatibility and counts.
- User asks usage checks at milestones, a summary before limits run out, and a continuation when the limit resets. No guarantee of last-second notification. At the latest check 57% five-hour / 93% weekly remained; five-hour reset 5 Nov 2026 19:07:33 Nepal. One-time heartbeat `continue-crop-disease-mini-project` scheduled 19:10 Nepal. Check usage and current schedule before expensive work; avoid duplicate automations.

## Completed

- Clean frontend: scanner, project flow, research/evidence status. Local preview `python3 server.py`, URL http://127.0.0.1:4180. Previous running session 88399 may still own that port: check before launching another server.
- Three clickable PlantVillage sample photos with attribution and reference labels. Sample photos were reused as attributed public dataset assets from the reference checkout after direct download hit Python certificate validation failure. No LeafLens weights or metrics copied. Demo scenarios are explicitly preset, unrelated to uploads; do not call them predictions.
- `server.py`: optional ONNX adapter, model/profile hash check, capture heuristics, normalized 224px RGB, probabilities, conformal sets, energy-cutoff hook and triage. Actual inference remains disabled: models/ is empty. Backend model path has NOT been end-to-end tested.
- `ml/reliability.py`: pure Python probabilities, LAC/APS, finite sample quantile, calibration/classification/risk metrics and triage.
- `ml/calibrate.py`: distinct temperature/conformal/test roles with group and ID overlap rejection; class/domain metrics and conformal coverage. Guidance always disabled in generated profile.
- `ml/audit_manifest.py`: required provenance/capture groups; checksum, path, class and cross-role overlap checks. Does not detect every near duplicate or prove group identities.
- `ml/prepare_manifest.py`: deterministic global group assignment to train/validation/temperature/conformal/policy/test. Does not invent group IDs. Small class/role counts may be zero; inspect before training.
- `ml/train_baseline.py`: CPU MobileNetV3-Small frozen-feature classifier training, validation macro-F1 selection, ONNX export/parity and saved calibration logits. Syntax checked ONLY, not run. Optional training requirements provided; dependency versions still need a tested environment.
- Twelve automated tests pass with `python3 -m unittest discover -s tests -v`. UI sample selection/ambiguous demo previously checked in browser. No new dataset audit or model-training result yet.
- Sources and prior-art decisions: docs/RELATED_WORK.md; methodology docs/PROJECT_FLOW.md.

## Next tasks in order

1. Inspect actual current files and usage. Do not recreate completed components.
2. Prepare isolated ML environment and record tested versions. System Python 3.14 arm64 has none of torch/torchvision/numpy/Pillow/onnxruntime; bundled runtime has some imaging libs but not assumed to have torch. Network requests may need scoped permission. Do not disable TLS verification to work around certificate errors.
3. Obtain public original data with attribution/licensing and trustworthy source IDs. Explicitly map crop/disease names. Build inventory.csv with real capture group IDs and class/domain counts, dedup exact/near duplicates; document unresolved leaf grouping. Keep public demo samples out of final independent tests.
4. Freeze viable split manifest. Existing prep uses ~55/10/10/10/5/10 percent group hashing. For source-only vs target-supervised experiments adapt explicit role allocation before training; do not silently mix target training data into a source-only claim.
5. Run tiny end-to-end smoke training/ONNX validation before a real baseline. Align server resize/normalization with the chosen recipe. Compare current square-resize recipe with weight-default crop preprocessing only as a declared experiment, not a silent change. Pin the verified environment.
6. Run real baseline, calibration, source/field evaluation, held-out unseen-condition tests, policy-development threshold selection. Main script currently excludes unseen labels from training/calibration input; build separate OOD evaluation. Energy uses raw logits T=1; fitted cutoff must use the same definition.
7. Add curated attributable guidance and a strict inference gate: no disease-specific guidance unless policy/unknown handling and knowledge entry are all evaluated. The core can return a guidance action for an enabled profile but the real frontend does not yet provide a complete curated guidance block. Do not enable flags as a substitute for evidence.
8. Surface genuine evaluation results in UI, produce presentation/report and demo. Preserve no-data status until measurements exist.

## Known gaps to inspect

- `bundle_status()` checks files exist, not full dependency/profile readiness. Improve status before real model deployment.
- ONNX session/model are loaded per request. Cache safely after actual bundle integration.
- Inference preprocessing and quality thresholds are heuristic; not a learned leaf detector.
- Robustness under distribution shift, accepted risk and management action validity remain unproven.
- No formal library cross-check for custom APS yet; convention is deterministic inclusive-prefix score inversion, tied probability block scores, empty sets allowed. Do not describe it as nonempty randomized APS.
- Date-based scheduled continuation is an attempt; cannot bypass account limits or guarantee device/app availability. Update this handoff after work and give the user a short truthful summary.

## Latest executed milestone (supersedes earlier no-model status)

- Python3.12 project `.venv` created; training/inference dependencies installed, `pip check` passed, versions frozen in `ml/environment-lock.txt`.
- `ml/fetch_pilot.py` downloaded 480 original grouped PlantVillage tomato photos; data/manifest.csv and data/source-summary.json contain provenance and audited splits. Original metadata revision pinned. curl was used with normal TLS verification because system Python's trust store did not validate HTTPS.
- Trained `experiments/pilot-v1` for 10 epochs; best validation macro-F1 selected; exported ONNX with parity verification. Baseline weights/profile deployed to models/. Real inference tested via Python, HTTP API and browser sample selection.
- Actual controlled test: 90.9% accuracy / 55 images; macro-F1 .906. LAC coverage .891. APS comparison also saved.
- `ml/evaluate_field.py` evaluated 38 known PlantDoc test photos (accuracy .421, macro-F1 .352) and 19 same-crop unknowns (energy AUROC .512). These cohorts are now inspected: do not tune on them then describe them as blind.
- Actual unknown check is NOT reliable. No fitted rejection cutoff; guidance still disabled. Healthy reference photo is confidently misclassified as Septoria; UI exposes disagreement rather than faking success.
- Server now uses cached ONNX runtime and profile checks, with /api/evaluation. Research & evidence page displays measured pilot charts/tables. Browser verified early-blight actual 97.0% probability and expert action; evidence page verified counts/scores.
- Running preview session now **8986**, using `.venv/bin/python server.py`, port4180. Older session88399 stopped.
- 17 tests passed, including 5 actual inference integration tests; final small test resource-handle correction applied. Run in .venv to include ML integration tests.
- See docs/PILOT_RESULTS.md for precise limitations and reproduction details.
- Next: design a larger source/field development protocol before more model experiments; add representative unknown development data, useful operating-point comparisons and fresh final evaluation. Add knowledge-base gating before ever enabling guidance. No further edits to LeafLens.

## Crop-expansion steering

The user asked about corn and paddy and agreed to investigate paddy first. Metadata review completed in docs/CROP_EXPANSION.md; configs/crop-scope.json distinguishes actual tomato pilot from untrained candidates. Prioritize paddy feasibility (Paddy Doctor exact RGB release + RiceyLeafDisease originals), with corn fallback. Four paddy candidate classes: healthy, bacterial leaf blight, brown spot, leaf blast; mapping/counts/licence of exact releases and physical-leaf grouping remain unverified. Ricey v1 explicitly contains originals and augmented images; do not randomly split them. Dhan-Shomadhan has field/white backgrounds but lacks healthy in the source description and may contain paired same-leaf views. Paddy Doctor is already field-collected: cross-source paddy evaluation must not be mislabelled controlled-to-field. No rice/corn model or UI support added yet.

## User-reported stock image failure

User supplied `/Users/pradiphapa/Downloads/pngtree-green-tomato-leaves-psd-png-png-image_4609568.png`. Original pilot returned Septoria probability .7385 although no disease diagnosis is established for the stock image. It is an opaque palette PNG with a baked checkerboard (not alpha transparency). Added generic capture guard `ml/image_quality.py` for regular neutral checkerboard borders and substantial alpha; no filename-specific override or fake healthy label. Exact image now returns quality/recapture with no disease confidence. Added synthetic checkerboard/plain/alpha tests; all 21 tests pass, existing real sample inference still passes. These are heuristics, not a general learned unknown-input detector or an accuracy improvement. Live server restarted after change; verify current port4180 session before launching another. Pilot test metrics remain the original model-only values, not a re-evaluation of the added capture gate.

## User-reported healthy photo and demo confusion

User supplied images.jpeg and a screenshot of preset Early blight 91% demo. Reproduced real inference separately: early_blight .975783 on the watermarked multi-leaf stock photo, whose healthy label is user-reported, not expert-confirmed. No filename or image-hash-specific output override; no training/calibration performed on this example. Failure metadata recorded locally in data/error-analysis; photo not copied into repository. Removed preset demo buttons and hardcoded example objects from scanner entirely; Project flow still explains outcomes and three real sample photos remain. Unvalidated real results now lead with triage action rather than a disease name/large confidence percentage; candidate labelled unverified and class scores under details. This corrects misleading presentation, NOT underlying classification accuracy. Need broader independently partitioned field training/validation and fresh evaluation. Existing 21 tests pass. Server remains session8444; frontend reload picks up changes.

## Additional confirmed classification failure / usage milestone

The distinct PlantVillage early-blight photograph provided for checking (outputs/tomato-leaf-check.jpg, recorded leaf group absent from pilot) was classified as late_blight at .8915677, confirmed directly against the saved model. Failure record is data/error-analysis/unseen-early-blight-v1.json. Expert verification was correctly requested, but classification quality remains inadequate. Do not claim this is solved by UI wording or a singleton conformal set. Prioritize a larger audited training cohort, a declared fine-tuning experiment and separate development error analysis before claiming readiness; do not optimize against the exposed check images or now-inspected final benchmarks. User screenshot shows the older large-score layout; a full reload is needed for current presentation. Latest usage 22% five-hour remaining / 88% weekly; reset remains19:07 Nepal and scheduled continuation19:10. Preserve a summary before expensive new work.

## Canonical running reference

User explicitly requested a file continuously recording completed work and further progress. PROJECT_STATUS.md at project root is now the concise current-state reference; AGENTS.md instructs future work to read/update it. HANDOFF remains historical supporting detail. Keep both consistent, with actual model metrics sourced from saved experiments.

## Latest error-review milestone

`ml/report_errors.py` creates models/error-review.json using existing frozen logits; no fitting. Shows source versus field class recalls and score>=.8 error counts plus Wilson intervals with assumptions. Field healthy0/8, late4/10, Septoria3/11, early9/9;17/22 field errors have score>=.8. Controlled5/55 errors, none>=.8. These findings substantiate the user's observed healthy-leaf failures. Future training needs actual domain-diverse data and a fixed development protocol, not another arbitrary threshold or image-specific rule. All23 tests pass. PROJECT_STATUS.md updated; use it as the first reference.

## Latest source-v2 training and flow checkpoint

User explicitly suspended usage tracking for now: AGENTS and PROJECT_STATUS updated; do not check/report limits unless asked again.

Completed a new predeclared source-v2 experiment (configs/source-v2.json; docs/SOURCE_V2_PROTOCOL.md). Cached capped listings provided391 additional valid leaf groups, not880 requested. Before fitting, protocol amended to combine these with original250 TRAIN-only images:641 total,475train/38val/32temperature/25conformal/22policy/49test. All original non-training groups and public-check group excluded, verified by2 new tests. Fine-tuned final3 MobileNetV3 blocks after3 warmup epochs, stronger crop/color augmentation, frozen feature BN stats,12epochs CPU. Selected source validation macro-F1=1.0; original v1=.9544 on same38 development images. Not independent selection evidence.

Executed ONNX parity and separate LAC/APS calibration. New controlled test49:accuracy .9184,macro-F1 .9121,LAC coverage .9592,APS .9388. Historical PlantDoc38 known/19unknown check repeated with explicit historical flag:accuracy .5,macro-F1 .4319,LAC coverage .5526; healthy still0/8. Do not tune on these now-exposed results. Healthy conformal partition only1 image; no per-class reliability claim.

Active bundle changed to source-v2 after explicit user-facing disclosure; original weights/profile/evaluation/error review archived in models/archive/pilot-v1. Guidance disabled, no validated live unknown cutoff. Server current session8444 auto-loads new model via file timestamp cache; HTTP /api/status and /api/evaluation verified source-v2.25 tests pass. test_inference now accepts either expert or recapture for unvalidated actual predictions; never guidance. report_errors.py updated to require matching model/logit hashes and accepts explicit run/profile/field paths.

App flow expanded to8 actual-state stages plus three-outcome status and crop roadmap; browser checked before activation, current experiment text now states source-v2 connected. Next major work remains truly field-representative development/training and separate final data, with sufficient healthy examples and per-class calibration. Paddy original-data audit remains planned, not model support.

## Supplied deferral script review and execution

Integrated corrected analysis as ml/deferral_analysis.py; source unchanged in Downloads. See PROJECT_STATUS latest checkpoint and experiments/source-v2-deferral/report.md. Existing reliability/decision functions reused. No invented monitor action; empty sets ranked last; score ties accepted as entire blocks; raw versus calibrated confidence versus pure set size exported. Replayed actions explicitly assume quality passes and no unfamiliar rejection. All known images deferred (zero accepted coverage); singleton accuracy40/42 controlled versus15/26 historical field. 30 tests pass. No training/threshold/model/UI changes this milestone. Field-data/licence audit, frozen DINOv2 comparison, mixed-domain recalibration and domain detector remain outstanding. Additional train/validation/temperature roles are necessary beyond the user's three field evaluation splits; never reuse historical test as blind final. Completed one-time continuation automation removed; usage tracking remains suspended.

## Field acquisition checkpoint

See PROJECT_STATUS field-data checkpoint and docs/FIELD_DATA_PROTOCOL.md. ml/inventory_field.py inventories4604 licensed candidates; first834 downloaded/audited,255 labelled healthy.830 quarantined,2 prior-image overlaps,1 truncated CCMT healthy and1 publisher SHA mismatch (jttrv2w27r Healthy_62.jpg). ml/review_field_duplicates.py emits2 exact groups and38 near-pair review candidates. No final splits, training or new results yet. Metadata files, inventory, download-audit, summary and duplicate-review under data/field-development. Quarantine roles stay unassigned; do not feed them to trainer.33 tests and JS syntax passed. Flow text updated. Next resolve image issues and duplicate/capture/background review before partitioning; expand downloads as needed to meet per-role targets. All primary licence/version/source links in protocol.

## Field review applied

See PROJECT_STATUS latest checkpoint. Checksum retry recovered Healthy_62.jpg; CCMT healthy443_.jpg remains publisher-level truncation. Reviewed38 near pairs,21 same-scene links. Screened934 prior paths and visually confirmed3 prior-scene matches. Applied exclusions via ml/stage_field_review.py:805 candidates pending capture/background review,21 duplicates,4 label-conflict images,3 prior-scene overlaps,1 bad file. data/field-development/staged-review.csv is NOT a training manifest: roles unassigned and physical groups unresolved. Decisions bound to input hashes.37 tests pass; no training/calibration changes. Several reviewed field-collected images have plain staged backgrounds: annotate actual scene domain rather than blindly calling all field.

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
