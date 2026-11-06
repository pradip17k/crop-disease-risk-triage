# End-of-day summary — 5 November 2026 (Nepal)

Work stopped at the user's request. Resume only when asked. No new continuation is scheduled; the earlier one-time automation was deleted after completion. Usage tracking remains suspended.

## Project and purpose

College mini project: crop disease screening and risk-triage based on the supplied proposal. Main implementation lives in `main project`; LeafLens is reference only. Restrained interface, real photo inference, confidence calibration, conformal prediction sets, unfamiliar-input research, and guidance/recapture/expert triage. Tomato is the only trained crop; paddy and corn are future work.

## What works

- Local app with photo upload, three real sample photos, project flow and research/evidence pages.
- Active source-v2 MobileNetV3-Small ONNX model; original v1 preserved in models/archive/pilot-v1.
- Four tomato classes: healthy, early blight, late blight, Septoria.
- Source-fitted temperature scaling and LAC sets; APS evaluated separately.
- Quality heuristics, recapture and expert-review recommendations. Guidance disabled.
- Reproducible evaluation, error review, deferral ablations and data-review tools.
- Latest full Python suite:37 tests passed. Latest frontend change passed JavaScript syntax check.

## Actual evidence and limitations

| Measurement | Result |
|---|---|
| Controlled test accuracy |45/49 =91.8% |
| Historical field accuracy |19/38 =50.0% |
| Healthy field recall |0/8 |
| Controlled LAC coverage |47/49 =95.9% |
| Historical field LAC coverage |21/38 =55.3% |
| Controlled singleton accuracy |40/42 =95.2% |
| Historical field singleton accuracy |15/26 =57.7% |
| Historical unknown energy AUROC |0.5956;19 unknown versus38 known |

The field benchmark has already been inspected and is not an untouched final test. Only one healthy image was in source-v2 conformal calibration. No validated live unknown cutoff. All known cases are deferred by the current policy; zero accepted errors comes with zero accepted coverage and does not establish useful selective prediction.

User's latest concern is usefulness: expert verification currently substitutes for dependable automatic screening too often. It is a recommendation only, with no expert connection, submission or review service. It does not prove the system detected its own mistake. Practical usefulness remains limited; prioritize classifier reliability over more presentation features.

## Scanner percentage issue

The server status and a real POST request were verified working. Scores had been hidden in collapsed details. Added visible model percentage, expanded class scores and a30-second analysis timeout. Browser reload needed for new frontend. Percentage is the model score, not percent diseased or verified correctness. The healthy reference still predicts Septoria at85.7%, with expert recommendation: the UI fix did not fix classification. Do not hardcode this sample to appear correct.

## Field-data work completed

Primary licences verified as CC BY4.0: PlantDoc pinned training folders; Mendeley jttrv2w27r v2; CCMT bwh3zbpkpv v1 raw healthy/Septoria folders. Ambiguous CCMT leaf blight and augmented folders excluded.

- Inventory:4604 candidate files, including905 labelled healthy; these are not independent leaf counts.
- First batch:834 downloaded/audited, including255 labelled healthy.
- Re-download recovered one SHA mismatch. One publisher file remains truncated.
- Reviewed38 perceptual candidate pairs;21 same-scene/derivative links.
- Screened against934 earlier source/field/reference/user files;3 earlier-field matches visually confirmed.
- Staged review:805 pending capture/background review,21 duplicate copies,4 conflicting-label images,3 prior-scene overlaps,1 bad file.
- All roles remain unassigned; physical capture groups unresolved. Data is not training-ready.
- Several farm-collected images are detached leaves on plain backgrounds. Record collection origin separately from actual scene domain; do not claim these all establish natural-field performance.

Artifacts: data/field-development/{inventory.json,download-audit.json,recheck.json,duplicate-review.json,visual-pair-review.json,prior-overlap.json,prior-visual-review.json,staged-review.csv,staged-summary.json,review-sheets/}. Review decisions are tied to input hashes. Protocol: docs/FIELD_DATA_PROTOCOL.md; targets: configs/field-data.json.

## Next session — priority order

1. Read PROJECT_STATUS.md and this summary. Review remaining805 candidates for background type and capture/leaf sequences; use conservative grouping and record uncertainty. Perceptual screening misses some crops/rotations, so do not equate no match with independence.
2. Expand truly natural-background data, especially healthy leaves, if the audited pool cannot support the quotas. Keep all derivatives and capture sequences in one role.
3. Freeze separate train, validation, temperature, conformal, policy and final-test groups. Targets:100+ field images each in conformal/policy/final test with25+ healthy each and all four classes represented. These targets have not been achieved as assigned independent splits.
4. Retrain with field data and stronger augmentation; compare a frozen DINOv2 baseline on the same development protocol. DINOv2 superiority is an unverified hypothesis. Test background removal rather than assuming it helps.
5. Recalibrate on mixed domains, report per-domain/source coverage, and evaluate domain routing, confidence versus set-size triage and unknown rejection. Select choices only on development data; final test stays sealed until frozen.
6. Keep guidance disabled until evaluated reliability and a curated guidance policy justify it. Retain50% field accuracy and healthy0/8 as current limitations until genuine new evaluation exists.

## Resume commands and repository status

Use project `.venv/bin/python` (system Python lacks ML dependencies). Run `.venv/bin/python -m unittest discover -s tests`. Check port4180 before starting `.venv/bin/python server.py`; local server was reachable at the final scanner check, future availability is not guaranteed. Preview http://127.0.0.1:4180/#scanner. No main-project GitHub repository/push is recorded; do not edit or push LeafLens.
