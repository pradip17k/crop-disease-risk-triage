# Ten-day project plan

User reports10 days remaining on5 November2026. Day numbers are relative planning slots; exact submission date/time is unconfirmed. Latest instruction: focus on the project, defer presentation work. No deck created. This plan does not schedule autonomous work.

## Scope

Tomato screening and risk-triage, four existing classes. Prioritize actual healthy/field performance and a reproducible working demo. Paddy/corn remain future work. No new UI features unless they fix a usability failure. Guidance stays disabled until justified by independent policy evaluation. Existing50% historical field accuracy and0/8 healthy recall remain current facts.

## Sequence and decision points

| Days | Work | Completion evidence |
|---|---|---|
|1–2|Review805 staged candidates for scene/background and capture grouping; expand natural-background healthy data only where needed.|Documented group manifest, exclusions and actual domain/class counts. Plain-background farm photos do not count as natural-field evidence.|
|3–4|Freeze role partitions and train one field-inclusive MobileNet candidate; select on validation only.|Recorded recipe, saved weights, validation comparison and inference/export parity.|
|5|Run a frozen DINOv2 feature baseline if data, weights and compute are ready.|Same development protocol comparison; otherwise explicitly defer it rather than delay the main experiment.|
|6|Fit temperature and conformal calibration on separate mixed-domain groups. Evaluate domain routing only if development support is sufficient.|Domain/source coverage, set size, calibration and policy-development metrics.|
|7|Freeze model and policy, then run the untouched final test once.|Accuracy, healthy recall, uncertainty intervals, risk/coverage and unknown AUROC with actual sample counts.|
|8|Integrate the selected version and fix scanner/server failures.|Reproducible local startup, upload errors/loading/results checked, full test suite.|
|9–10|Stabilization and submission buffer. User will decide presentation work later.|Versioned project bundle, dependencies, experiment records and known limitations.|

## Cutoffs

- If data review cannot establish enough independent natural-field groups by Day2, document the shortfall and narrow the experimental claim. Never fill quotas with duplicate/augmented copies or invent physical-leaf independence.
- No background-removal system, extra crop model or elaborate domain detector unless it can be evaluated without jeopardizing the primary experiment.
- Model comparison uses validation only. Do not tune against the exposed38-image field benchmark or the final test.
- If a new candidate does not improve appropriate development metrics, preserve the stronger verified version and report the failed experiment. No accuracy guarantee or hardcoded demo success.
- Final test remains sealed until the pipeline freezes. Final-test findings go in the report even when disappointing.
- Target100+ field images per conformal/policy/test role and25+ healthy each remains a design goal, subject to actual independent data. Also reserve separate training, validation and temperature groups.

## Immediate next task

Annotate actual scene domain and investigate capture sequences for the805 pending candidates. Produce counts by source/class/background and record grouping limitations before allocating train/calibration/test roles. Use staged-review.csv and preserve reviewed duplicate exclusions. Do not spend the next session on slide design or additional interface decoration.

## Latest usage preference — supersedes suspension

User again requests managing usage limits. Use focused milestone batches, cached data, targeted tests and bounded experiments. Prioritize data review and one field-inclusive model before optional comparisons. Save restart instructions and completed/pending work after meaningful milestones. Remaining allowance requires an actual reading; no fabricated percentage, assumed reset time or guarantee of a pre-limit warning. No reset automation created.
