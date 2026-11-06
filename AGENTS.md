# Working rules for this project

Read PROJECT_STATUS.md before planning changes. Consult docs/HANDOFF.md for historical details and the latest update if they differ. Review relevant source code and saved experiment artifacts before implementing; do not recreate completed features.

Follow the supplied proposal and user decisions. LeafLens is reference only. Work in this project directory. Keep real model outputs, dataset reference labels and illustrative explanations distinct. Do not fake successful classifications or hide known model failures. Do not enable management guidance without evaluated policy and curated sources.

After each meaningful milestone, update PROJECT_STATUS.md with what changed, what was actually run/tested, measured results, known limitations and the next tasks. Append a concise checkpoint to docs/HANDOFF.md when needed for the scheduled continuation. Existing test/field results are exposed research benchmarks, not new blind evaluation cohorts.

Use `.venv/bin/python -m unittest discover -s tests -v` for project tests. Document skipped tests or unexecuted training. Run actual inference checks for model/preprocessing changes. Latest user instruction: manage usage limits alongside the ten-day deadline. Work in focused batches, avoid redundant reads/tests and unnecessary expensive experiments, and save status after meaningful milestones. Report remaining allowance only from an actual available usage reading; never infer it from token counts or promise a warning before an unseen limit. Do not create reset automations without a confirmed schedule.
