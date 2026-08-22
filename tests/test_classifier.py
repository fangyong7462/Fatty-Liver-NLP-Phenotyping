#!/usr/bin/env python3
import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from phenotype_classifier import classify_stage


class FrozenRuleUnitTests(unittest.TestCase):
    def test_expected_outputs_from_frozen_source(self):
        with (ROOT / "examples" / "expected_outputs.csv").open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertGreaterEqual(len(rows), 12)
        for row in rows:
            with self.subTest(test_id=row["test_id"]):
                self.assertEqual(classify_stage(row["synthetic_text"]), row["expected_stage"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

