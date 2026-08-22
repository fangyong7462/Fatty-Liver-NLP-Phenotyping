#!/usr/bin/env python3
"""Aggregate analysis from an authorized CSV input; no data are bundled."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from phenotype_classifier import classify_stage

STAGES = ["Normal", "Trend", "Mild", "Moderate", "Severe"]
METRICS = ["BMI", "ALT", "FBG", "TG", "UA", "SBP"]
ADJACENT = [("Normal", "Trend"), ("Trend", "Mild"), ("Mild", "Moderate"), ("Moderate", "Severe")]


def build_primary_cohort(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    required = {"ID", "exam_date", "age", "Summary_Conclusion", *METRICS}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    df["_source_row_index"] = np.arange(len(df))
    df["_exam_dt"] = pd.to_datetime(df["exam_date"], errors="coerce")
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    for c in METRICS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    eligible = df[
        (df["_exam_dt"] >= "2024-10-01")
        & (df["_exam_dt"] < "2025-11-01")
        & (df["age"] >= 18)
        & df["Summary_Conclusion"].fillna("").astype(str).str.strip().ne("")
    ].copy()
    eligible = eligible.sort_values(["ID", "_exam_dt", "_source_row_index"])
    primary = eligible.drop_duplicates("ID", keep="first").copy()
    primary.loc[primary["BMI"] <= 0, "BMI"] = np.nan
    primary["SeverityStage"] = primary["Summary_Conclusion"].map(classify_stage)
    return primary


def bootstrap_median(values, rng, repetitions=2000, chunk=32):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    out = np.empty(repetitions)
    for start in range(0, repetitions, chunk):
        k = min(chunk, repetitions - start)
        idx = rng.integers(0, len(values), size=(k, len(values)))
        out[start : start + k] = np.median(values[idx], axis=1)
    return out


def aggregate_outputs(primary, seed=20250421, repetitions=2000):
    dist = (
        primary["SeverityStage"].value_counts()
        .reindex(STAGES, fill_value=0)
        .rename_axis("Stage")
        .reset_index(name="N")
    )
    dist["Proportion"] = dist["N"] / len(primary)
    rng = np.random.default_rng(seed)
    med = {
        (stage, metric): bootstrap_median(
            primary.loc[primary.SeverityStage.eq(stage), metric].dropna().to_numpy(),
            rng,
            repetitions,
        )
        for stage in STAGES
        for metric in METRICS
    }
    rows = []
    for earlier, later in ADJACENT:
        for metric in METRICS:
            early_values = primary.loc[primary.SeverityStage.eq(earlier), metric].dropna()
            late_values = primary.loc[primary.SeverityStage.eq(later), metric].dropna()
            boot = med[(later, metric)] - med[(earlier, metric)]
            rows.append(
                {
                    "Earlier_stage": earlier,
                    "Later_stage": later,
                    "Metric": metric,
                    "Earlier_available_N": len(early_values),
                    "Later_available_N": len(late_values),
                    "Median_difference": float(late_values.median() - early_values.median()),
                    "CI_low_95": float(np.percentile(boot, 2.5)),
                    "CI_high_95": float(np.percentile(boot, 97.5)),
                    "Bootstrap_repetitions": repetitions,
                    "Seed": seed,
                }
            )
    return dist, pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seed", type=int, default=20250421)
    parser.add_argument("--repetitions", type=int, default=2000)
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    primary = build_primary_cohort(pd.read_csv(args.input, low_memory=False))
    dist, effects = aggregate_outputs(primary, args.seed, args.repetitions)
    dist.to_csv(output_dir / "stage_distribution.csv", index=False)
    effects.to_csv(output_dir / "adjacent_stage_median_effects.csv", index=False)
    print(f"primary_N={len(primary)}")


if __name__ == "__main__":
    main()

