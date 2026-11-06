# Second-crop feasibility: paddy versus corn

Reviewed 5 November 2026. This is a metadata-level feasibility review, not a completed image-level audit. Tomato remains the only trained crop. Paddy and corn have not been added to inference.

## Paddy: viable and worth pursuing

### Paddy Doctor (primary authors)

Paper: https://arxiv.org/abs/2205.11108
Author dataset description: https://github.com/paddydoc/paddy-doctor-dataset/blob/main/dataset.md

The original authors describe 16,225 annotated images across 13 categories, collected in real paddy fields near Tirunelveli, Tamil Nadu, using a CAT S62 Pro. Labels include bacterial leaf blight, blast, brown spot and normal. Do not confuse this release with the widely mirrored 10-category Kaggle competition subset. The original author page also mixes disease and pest terminology and mentions visual/infrared imagery. Before download, resolve the exact release, RGB-only selection, image licence and leaf/capture grouping. Age/variety metadata is useful but does not automatically identify a physical leaf or independent capture session.

### RiceyLeafDisease (original depositor)

https://data.mendeley.com/datasets/t46kkgh2yw/1

Version 1 reports 1,701 originals plus 5,188 augmented images, with healthy rice, bacterial leaf blight, brown spot, leaf blast and four other conditions. It covers Sirajganj/Pabna, Bangladesh, collected July–October 2023 with mixed indoor/outdoor lighting. Declared licence CC BY 4.0. A possible independently sourced evaluation cohort after image-level provenance/overlap checks. Use originals, not a random split of an already augmented collection. Keep every derivative with its original. Disease semantics still need checking; generic blast must not silently be equated with every anatomical blast subtype.

### Dhan-Shomadhan (original depositor)

https://data.mendeley.com/datasets/znsxdctwtt/1

Version 1 reports 1,106 images across five disease conditions, with field-background and white-background variants. Declared licence CC BY 4.0. Useful candidate for a background-shift experiment; it does not provide a healthy class in its description or bacterial leaf blight. Check whether the two background variants show the same physical leaves. Never put paired leaf photographs on opposite sides of an independent split.

## Provisional paddy scope

Candidate labels: healthy, bacterial leaf blight, brown spot and leaf blast. Paddy Doctor plus RiceyLeafDisease appears plausible for shared-label cross-source testing, but no exact intersection, per-class usable original counts or group IDs are yet verified. Dhan-Shomadhan is a possible smaller blast/brown-spot experiment rather than a complete four-class replacement.

Because Paddy Doctor itself is field-collected, a Paddy Doctor→Ricey comparison is **cross-source/region shift**, not automatically controlled-to-field shift. Preserve the proposal's controlled-to-field tomato experiment and describe the paddy extension accurately.

## Corn comparison

Corn fits the already researched PlantVillage/PlantDoc direction (common rust, gray leaf spot, northern leaf blight candidate labels). However, valid corn leaf/capture grouping and exact target class counts have not been audited in main project. It is a technically simpler candidate extension but is not a completed or guaranteed dataset option.

## Decision

Prioritize **paddy as the second-crop investigation**, while retaining corn as a fallback. This is a data-readiness decision, not a new trained-model claim. Keep two trained crops as the initial college mini-project goal; do not add a third merely for display.

Next gates: exact release/licence → RGB/original-image file inventory → disease-name mapping → class counts → duplicate/physical-leaf grouping → fixed source/target split protocol → independent paddy model and reliability profile. Do not route rice photos through the tomato model or make the interface imply paddy is supported before those gates pass.
