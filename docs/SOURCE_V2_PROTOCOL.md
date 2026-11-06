# Source-v2: a separate candidate experiment

This experiment follows repeated confident healthy/blight failures in the source-only pilot. It tests a larger training partition and limited pretrained-feature fine-tuning. It does not claim to solve field shift.

The recipe was written in configs/source-v2.json before fitting. The source-file audit provided391 eligible new leaf groups from the pinned/capped listing instead of880 requested. Before training, the protocol was amended to retain only the original250 training groups. Total641 images:475 train /38 validation /32 temperature /25 conformal /22 policy /49 test. Every original non-training group and public-check group is excluded. Original pilot artifacts remain immutable. Original grouping and exact hash audits do not guarantee all near duplicates or incorrect source labels are absent.

Maximum12 CPU epochs; classifier-only warmup3 epochs; then final3 feature blocks train at1e-4 while the head uses1e-3. Feature BatchNorm statistics remain fixed. Training augmentation adds random resized crops and moderate color jitter to flips/rotation; deterministic evaluation/server preprocessing remains square224px bilinear resize and ImageNet normalization. Seed42.

Checkpoint selection uses only candidate validation macro-F1. A first checkpoint wins ties. Original pilot macro-F1 on these same38 development images is0.9544; the new candidate's selected validation score is not independent evidence because it guided checkpoint selection. The49 new test images are separate recorded groups, but a small controlled test still cannot establish field reliability.

LAC/APS calibration must use the separate role partitions. Healthy conformal support is only1 image, so class-specific reliability cannot be estimated credibly. Guidance must remain disabled even if overall source accuracy is high. No unknown-disease threshold can be asserted from this source-only experiment.

Any check on the previously inspected38-known/19-unknown PlantDoc cohort must be labelled historical comparison, not a fresh blind field test. Do not select thresholds or retrain after looking at that result and claim the same cohort is independent. Do not tune against the user's individual photographs or the demonstration examples.

Do not silently replace the live pilot. Record completed candidate checks, measured limits and the active model version separately. A broader target-development and fresh independent evaluation protocol is still needed before reliable farm screening or automatic management guidance.
