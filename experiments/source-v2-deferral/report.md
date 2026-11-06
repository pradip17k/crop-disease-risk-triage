# Retrospective deferral analysis

- Retrospective exposed benchmarks; no threshold fitting or new independent evaluation.
- Actions replay the current decision function on saved logits, assuming quality passes and unfamiliar=False. These are not logged end-to-end app actions.
- Guidance is disabled: deferring all errors at zero accepted coverage does not demonstrate useful selective prediction.
- Curves are hypothetical acceptance rankings, not enabled guidance policies. Pure set size uses whole tie blocks, with empty sets last.
- AURC uses a right-endpoint step area; coarse set-size ties limit direct ranking comparisons. No significance claim.
- Wilson intervals assume independent Bernoulli trials; small samples, unresolved dependence and label noise limit interpretation.
- Unknown images are excluded from known-class accuracy/coverage; energy AUROC is copied from the matching historical evaluation.

## controlled (n=49)

Accuracy: 91.8%; conformal coverage: 95.9%.
Actions: {'expert': 42, 'recapture': 7}. Accepted coverage: 0.0%.
Singleton top-1 accuracy: {'numerator': 40, 'denominator': 42, 'value': 0.9523809523809523, 'interval_95': [0.8421014760304114, 0.9868424750910944]}.
Healthy accuracy: {'numerator': 8, 'denominator': 8, 'value': 1.0, 'interval_95': [0.6755924351161198, 1]}.
- raw_softmax: step AURC 0.0177
- calibrated_confidence: step AURC 0.0177
- set_size_empty_last: step AURC 0.0525

## historical_field (n=38)

Accuracy: 50.0%; conformal coverage: 55.3%.
Actions: {'expert': 26, 'recapture': 12}. Accepted coverage: 0.0%.
Singleton top-1 accuracy: {'numerator': 15, 'denominator': 26, 'value': 0.5769230769230769, 'interval_95': [0.3894861374659171, 0.7445555668634343]}.
Healthy accuracy: {'numerator': 0, 'denominator': 8, 'value': 0.0, 'interval_95': [0, 0.32440756488388023]}.
- raw_softmax: step AURC 0.3532
- calibrated_confidence: step AURC 0.3522
- set_size_empty_last: step AURC 0.4474
