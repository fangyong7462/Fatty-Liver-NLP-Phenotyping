# Rule description

This package exposes the fixed five-category report-derived rule set used for primary phenotyping. The classifier accepts one free-text string and returns exactly one of Normal, Trend, Mild, Moderate, or Severe. It does not diagnose MASLD, does not provide an Unclassified/abstention output, and does not use patient-level data.

Text cleaning removes ASCII spaces, selected Chinese/ASCII punctuation, tabs, and carriage returns. The pattern priority is documented in rules/rule_priority.md and is copied from the frozen source. The package deliberately preserves source behavior, including cases in which a Chinese negative phrase is captured by the Mild/generic pattern before the later negation pattern. This is a known source-rule limitation, not a new public-release bug; the exposure audit found zero such constructions in the analyzed and validation corpora. Future deployment should use negation-first logic and an Unclassified/abstention route.
