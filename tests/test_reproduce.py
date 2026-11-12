"""Validate the exported evidence files and deterministic output contract."""
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("reproduce", REPO / "scripts" / "reproduce.py")
reproduce = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reproduce)


class ReproductionExportTests(unittest.TestCase):
    def test_exports_are_deterministic_and_keep_all_cashflow_rows(self):
        # Keep scratch artifacts within the workspace on restricted Windows hosts.
        with tempfile.TemporaryDirectory(dir=REPO, prefix=".test-reproduce-") as directory:
            output = Path(directory)
            reproduce.export(output)
            first = {p.name: p.read_bytes() for p in output.iterdir()}
            reproduce.export(output)
            self.assertEqual(first, {p.name: p.read_bytes() for p in output.iterdir()})
            summary = json.loads((output / "model_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["amount_unit"], "10,000 KRW")
            self.assertEqual(len(summary["scenarios"]), 12)
            with (output / "monthly_cashflows.csv").open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 720)
            self.assertEqual(rows[0]["ym"], "2026-12")
            self.assertEqual(rows[-1]["ym"], "2031-11")
            scenario = next(x for x in summary["scenarios"] if x["plan"] == "A" and x["outcome"] == "U")
            self.assertEqual(scenario["first_safety_violation_18"], "2027-10")
            self.assertEqual(scenario["first_unfunded_month_18"], "2028-01")


    def test_sensitivity_export_matches_documented_cases(self):
        with tempfile.TemporaryDirectory(dir=REPO, prefix=".test-reproduce-") as directory:
            output = Path(directory)
            reproduce.export(output)
            data = json.loads((output / "sensitivity.json").read_text(encoding="utf-8"))
            c = {row["job_delay_months"]: row for row in data["c_first_salary_delay"]}
            self.assertEqual(c[0]["weighted_discounted_cashflow_60_C"], 6716.7)
            self.assertEqual(c[3]["weighted_discounted_cashflow_60_C"], 5968.6)
            self.assertLess(c[3]["weighted_discounted_cashflow_60_C"], c[3]["base_weighted_discounted_cashflow_60_B"])
            d = {row["job_delay_months"]: row for row in data["d_regular_salary_delay_unassigned"]}
            self.assertEqual((d[0]["cash_18"], d[0]["minimum_safety_margin_18"]), (845.0, 45.0))
            self.assertEqual((d[1]["minimum_safety_margin_18"], d[1]["cash_18"]), (5, 695))
            self.assertIsNone(d[1]["first_safety_violation_18"])
            self.assertEqual(d[2]["first_safety_violation_18"], "2028-03")
            self.assertEqual((d[2]["minimum_safety_margin_18"], d[2]["cash_18"]), (-35, 545))
            b = [round(row["weighted_discounted_cashflow_60_B"]) for row in data["b_pass_condition_drop"]]
            self.assertEqual(b, [6266, 6164, 6062, 5960])

if __name__ == "__main__":
    unittest.main()
