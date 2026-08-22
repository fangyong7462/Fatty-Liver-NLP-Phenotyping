#!/usr/bin/env python3
import csv
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from aggregate_analysis import aggregate_outputs, build_primary_cohort


class SyntheticAggregateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.input_path = ROOT / 'examples' / 'synthetic_analytic_input.csv'
        cls.primary = build_primary_cohort(pd.read_csv(cls.input_path))

    def test_cohort_construction_and_first_exam(self):
        self.assertEqual(len(self.primary), 5)
        self.assertEqual(set(self.primary['ID'].astype(str)), {'1001', '1002', '1003', '1004', '1008'})
        row = self.primary.loc[self.primary['ID'].astype(str).eq('1001')].iloc[0]
        self.assertEqual(str(row['exam_date'])[:10], '2024-10-05')
        self.assertEqual(row['SeverityStage'], 'Mild')

    def test_stage_assignment_and_distribution(self):
        expected = {'Normal': 1, 'Trend': 1, 'Mild': 1, 'Moderate': 1, 'Severe': 1}
        self.assertEqual(self.primary['SeverityStage'].value_counts().to_dict(), expected)

    def test_aggregate_outputs_against_expected(self):
        dist, effects = aggregate_outputs(self.primary, seed=20250421, repetitions=2000)
        with (ROOT / 'examples' / 'synthetic_expected_stage_distribution.csv').open(encoding='utf-8-sig', newline='') as f:
            expected_dist = pd.DataFrame(list(csv.DictReader(f)))
        self.assertEqual(dist['Stage'].tolist(), expected_dist['Stage'].tolist())
        np.testing.assert_array_equal(dist['N'].to_numpy(), expected_dist['N'].astype(int).to_numpy())
        expected_effects = pd.read_csv(ROOT / 'examples' / 'synthetic_expected_adjacent_effects.csv')
        keys = ['Earlier_stage', 'Later_stage', 'Metric']
        self.assertEqual(effects[keys].astype(str).values.tolist(), expected_effects[keys].astype(str).values.tolist())
        numeric = ['Earlier_available_N', 'Later_available_N', 'Median_difference', 'CI_low_95', 'CI_high_95', 'Bootstrap_repetitions', 'Seed']
        for col in numeric:
            np.testing.assert_allclose(effects[col].to_numpy(), expected_effects[col].to_numpy(), rtol=0, atol=1e-12)


if __name__ == '__main__':
    unittest.main(verbosity=2)
