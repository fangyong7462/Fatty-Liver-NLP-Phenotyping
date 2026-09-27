# Fatty-Liver-NLP-Phenotyping

This research-use implementation reproduces the exact fixed five-category rule used in the study. It contains no patient-level data, identifiers, health-examination values, or real patient narratives. The executable entry point is `frozen_rule_as_used`, which preserves the exact research implementation.

## Run one report

    python src/phenotype_classifier.py --text "中度脂肪肝"

## Run unit tests

    python -m unittest discover -s tests -v

The released implementation was tested with Python 3.12.13, NumPy 2.3.5, and pandas 2.2.3. Install the verified dependencies with:

    python -m pip install -r requirements.txt

The classifier test covers the synthetic rule-output examples. The end-to-end synthetic aggregate test covers date-window eligibility, age and text eligibility, first-examination selection, stage assignment, stage counts, and adjacent-stage aggregate outputs:

    python -m unittest discover -s tests -v

The synthetic input is `examples/synthetic_analytic_input.csv`; expected aggregate outputs are stored in the same `examples` directory.

## Aggregate analysis

The repository is public. It provides the released phenotyping implementation and code supporting selected reported aggregate analyses. src/aggregate_analysis.py accepts an authorized CSV and writes aggregate category distributions and adjacent-category median effects. It does not contain the institution's data. The public package is not a substitute for institutional data-access approval.

For an authorized dataset with the required columns, run:

    python src/aggregate_analysis.py --input /path/to/authorized_input.csv --output-dir /path/to/output --seed 20250421 --repetitions 2000

The command writes `stage_distribution.csv` and `adjacent_stage_median_effects.csv`. The seed and repetition count should be recorded with any reproduction.

## Known Source-Rule Limitation

The source implementation places the Mild/generic branch before the later negation branch. A narrow class of synthetic Chinese negative constructions containing the generic fatty-liver substring can therefore be forced into Mild. This is inherited source behavior, not a new public-release bug. The exposure audit found zero affected constructions in the analytic and validation corpora. The public package reproduces the exact research implementation and does not silently change the reported labels.

For future deployment, use negation-first handling, an Unclassified/abstention route, and local challenge-set validation. This research code is not a clinical diagnostic system. Patient data are not distributed. The public repository is https://github.com/fangyong7462/Fatty-Liver-NLP-Phenotyping; version 1.0.0 is archived at https://doi.org/10.5281/zenodo.22057927. Some reported analyses require additional, nonreleased local scripts.
