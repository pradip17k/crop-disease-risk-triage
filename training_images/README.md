# Training images — active source-v2 model

475 original PlantVillage tomato photographs actually used in the active model training split, grouped by class. Validation, calibration, policy and test photographs are excluded. New field-development candidates have not been used to train this model and are not included here.

## Attribution and licence

Source: PlantVillage dataset, Mohanty, Hughes and Salathé. Publisher-declared [Creative Commons Attribution-ShareAlike 3.0](https://creativecommons.org/licenses/by-sa/3.0/). Original pinned source: https://github.com/spMohanty/PlantVillage-Dataset/tree/7f7ecc7e1eaca78107e3affe7cb5abd9427e139a/raw/color

Images are unmodified byte-for-byte copies; filenames and folder organization were changed for this package. Each original URL, label, capture group and SHA-256 is recorded in manifest.csv, along with its packaged_path. Retain this attribution and applicable licence when sharing. Labels are dataset reference labels, not new expert verification.

## Class counts

- early_blight: 145
- healthy: 76
- late_blight: 127
- septoria: 127

The training pipeline still uses data/source-v2-training.csv and its original paths. This folder is a convenient review copy; it does not replace the complete six-role dataset needed for reproducing calibration and evaluation.
