# Related research and projects: decisions adopted

Reviewed 5 November 2026. This is a targeted reference review, not an exhaustive novelty or performance assessment. No external repository's model weights, reported scores or source code were imported in this update. Our supplied proposal remains the scope.

| Primary source inspected | Useful lesson | Project decision |
|---|---|---|
| Jenpoer/plant-disease-detection README: https://github.com/Jenpoer/plant-disease-detection | Related project already combines source-to-field benchmarking, candidate disease lists and confidence-based retake prompts. Its README also compares many strategies using target-test performance; we must avoid treating repeated target-test comparisons as an untouched final model-selection protocol. Reported numbers were not independently reproduced. | Do not claim generic triage or a top-three shortlist is new. Keep separate policy development and final evaluation. Our conformal sets must depend on calibrated thresholds, not a fixed top-k. |
| Original PlantDoc repository: https://github.com/pratikkayal/PlantDoc-Dataset | Classification dataset version and crop/disease label mapping need explicit identification. | Audit declared labels and image provenance before promising a class intersection. |
| PlantWild author project page: https://tqwei05.github.io/PlantWild/ | Offers an in-the-wild dataset and expert-refined v2; the page declares CC BY-NC-ND 4.0. | Candidate extra field benchmark, not downloaded or adopted automatically. Check actual matching classes, sample counts and permitted handling first. |
| TorchCP authors' repository: https://github.com/ml-stat-Sustech/TorchCP | Provides established conformal scoring/prediction implementations. | Reference implementation for future numerical cross-checks. Not installed; no claim of library parity yet. Keep lightweight pure-Python core for now and state exact APS convention. |
| OpenOOD authors' repository: https://github.com/Jingkang50/OpenOOD | Dedicated benchmark infrastructure for unknown-input detection. | Evaluate unknown-input rejection separately from classification and calibration. No benchmark numbers transferred to our task. |
| Dong et al., 2025: https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2025.1623907/full | Plant-disease anomaly detection has direct prior work; motivates explicit known/unknown evaluation. | Retain separate same-crop unseen diseases, other crops and non-leaf evaluation groups. A knowledge-ensemble extension is optional, not required for the mini project. |
| Xie et al., 2026 MRC-Net, previously verified: https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2026.1895287/full | Conformal prediction in plant-disease classification already exists. | Novelty remains a measured, reproducible three-action integration under shift, subject to further prior-art review. |

## Implemented improvements from this review

1. **Pre-training manifest audit** (`ml/audit_manifest.py`): requires source, license, role, domain, class, capture group, ID and exact checksum; rejects declared group/image overlap between roles, conflicting image labels, changed checksums, missing files and paths outside the dataset root. Produces per-domain/role/class counts and shared-label lists. It cannot prove group annotations are truthful or detect all near duplicates.
2. **Stricter calibration partitions** (`ml/calibrate.py`): rejects reused record IDs even if capture groups have been relabelled; previous capture-group overlap checks remain.
3. **More informative evaluation**: calibration reports now include per-disease set coverage and counts, separate per-domain metrics, empty-set count, singleton rate, macro-F1 and confusion matrices. Macro-F1 includes the full class vocabulary with undefined divisions set to zero; inspect class support before comparing domains.
4. **Numerical input validation**: LAC/APS scores reject malformed probability vectors.

## Kept out of scope

No large ensemble, segmentation pipeline, multimodal model, camera integration or paid service was added. These would add implementation/evaluation burden before our baseline is trained. A clean working mini project with defensible evidence takes priority over architectural complexity.

## Status

Eleven automated tests pass. No dataset audit on actual training data has yet been completed because a project training manifest has not been created. Tests use temporary synthetic files only. No improved prediction accuracy or field reliability is established by these engineering changes.
