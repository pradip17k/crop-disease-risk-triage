# Background screening checkpoint — 6 November 2026

All 805 pending candidates were visually screened across nine numbered contact sheets. These are broad thumbnail observations, not expert disease labels or proof of independent captures. Input and image hashes bind the decisions to the reviewed data.

| Visible scene domain | Candidate images |
|---|---:|
| natural_background | 237 |
| staged_plain | 520 |
| ambiguous | 35 |
| composite_or_illustration | 13 |

Only **44 publisher-labelled healthy images** were screened as natural-background candidates. The three evaluation-role targets alone need 75 healthy images, before reserving training, validation and temperature fitting. Current data cannot meet those targets even if every candidate survives grouping and label review. Plain-background farm photographs remain potentially useful training data, but cannot be counted as natural-background field evidence.

## Integrity and remaining review

- 13 composites/illustrations quarantined in screened-review.csv.
- One additional same-scene pair with early-blight versus Septoria labels confirmed in the enlarged cross-label sheet; both images quarantined. No diagnosis chosen.
- 53 possible capture/derivative pairs recorded; 3 enlarged pairs examined: 1 conflict confirmed, 2 different photographs (physical identity still unresolved). 50 pairs await enlarged review.
- 35 ambiguous backgrounds require larger inspection; 10 healthy-labelled PlantDoc photographs flagged for priority species/label review.
- Every physical capture group remains unresolved and every role remains unassigned. Original staging is preserved; screened-review.csv contains the new quarantine decisions and must be used alongside it.
- Model predictions were not used to curate this pool. The active model has not been retrained.

## Resume

1. Review the 50 queued capture pairs and 35 ambiguous backgrounds; propagate confirmed links and conflicts through full existing scene components.
2. Review priority healthy labels against publisher/source evidence. Do not relabel based on filename or thumbnail appearance alone.
3. Expand the natural-background healthy pool, audit it against every old cohort and preserve grouping limits.
4. Amend feasible split targets before fitting if independent data cannot support the original quotas. Only then freeze roles and train.

Commands: `.venv/bin/python -m ml.review_field_backgrounds --report` validates saved hashes and regenerates screening outputs. `.venv/bin/python -m ml.review_field_backgrounds` regenerates the contact sheets/index and can invalidate previous decisions if the input changes.

Validation: 40 tests passed, including actual ONNX inference and new rejection checks for incomplete, duplicated or stale review records.

## Enlarged review and consolidation update

All53 capture candidates have now been reviewed:32 same-leaf/scene,9 conservative keep-together,1 cross-label same-scene conflict,11 different photographs without proof of physical independence. Of35 previously ambiguous backgrounds,26 received a broad category and9 remain uncertain. Source/species/label concerns are quarantined without assigning new diagnoses.

The consolidated834-row manifest has726 candidate representatives:504 plain/staged and222 natural-background (31 healthy,59 early blight,64 late blight,68 Septoria). It preserves prior exclusions and propagates conflicts/label concerns through existing and newly linked components. All roles remain unassigned and physical independence unresolved.

A separately predeclared40-image CCMT healthy expansion downloaded successfully (publisher hashes and decode verified):39 quarantined candidates,1 exact overlap with the old batch. Preliminary thumbnail domains are20 natural,3 plain and17 ambiguous; repeated views remain and no independent additions are claimed.

44 tests pass. Rebuild consolidated metadata using `.venv/bin/python -m ml.consolidate_field_review` after restoring the local source photos and review sheets. See PROJECT_STATUS.md for the current entry point.
