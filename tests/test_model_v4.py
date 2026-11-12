"""Financial regression checks for supplied assumptions, not reality validation."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from afpk_cpa.financial import model_v4 as model


class BaselineFinancialModelTests(unittest.TestCase):
    def test_period_and_cash_accounting(self):
        self.assertEqual(model.MONTHS[0], (2026, 12))
        self.assertEqual(model.MONTHS[-1], (2031, 11))
        for plan in "ABCD":
            for state in "PUF":
                previous = 1400
                rows = model.simulate(plan, state)
                self.assertEqual(len(rows), 60)
                for row in rows:
                    self.assertAlmostEqual(
                        row["raw_cash"] - previous,
                        row["income"] + row["family"] - row["living"]
                        - row["exam"] - row["debt_cash"], places=8,
                    )
                    self.assertEqual(row["cash_floor"], max(0, row["raw_cash"]))
                    self.assertEqual(row["unfunded"], max(0, -row["raw_cash"]))
                    previous = row["raw_cash"]

    def test_18_month_outcome_regressions(self):
        expected = {
            "A": {"P": 895.0, "U": -555.0, "F": 365.0},
            "B": {"P": 1775.0, "U": 1025.0, "F": 1325.0},
            "C": {"P": 2833.8, "U": 2833.8, "F": 2833.8},
            "D": {"P": 1295.0, "U": 845.0, "F": 845.0},
        }
        for plan, outcomes in expected.items():
            for state, value in outcomes.items():
                with self.subTest(plan=plan, state=state):
                    self.assertEqual(model.metrics(plan, state)["c18"], value)

    def test_weighted_60_month_values(self):
        for plan, value in {"A": 5259.216, "B": 6062.21, "C": 6716.7, "D": 5853.492}.items():
            with self.subTest(plan=plan):
                self.assertAlmostEqual(model.expected_pv(plan), value, places=6)

    def test_discounted_total_is_not_final_cash(self):
        rows = model.simulate("C", "F")
        self.assertAlmostEqual(model.pv(rows, r=0), rows[-1]["raw_cash"], places=8)
        self.assertNotAlmostEqual(model.pv(rows), rows[-1]["raw_cash"], places=2)

    def test_safety_breach_does_not_mean_negative_cash(self):
        result = model.metrics("A", "U")
        rows = result["rows"]
        self.assertEqual(result["first_violation"], (2027, 10))
        breach = next(row for row in rows if row["ym"] == (2027, 10))
        self.assertEqual(breach["raw_cash"], 285)
        self.assertEqual(breach["unfunded"], 0)
        self.assertEqual(next(row["ym"] for row in rows if row["unfunded"] > 0), (2028, 1))
        self.assertTrue(all(row["unfunded"] == 0 for row in model.simulate("A", "P")[:18]))

    def test_d_one_month_delay_has_only_five_units_reserve_margin(self):
        result = model.metrics("D", "U", job_delay=1)
        self.assertIsNone(result["first_violation"])
        self.assertEqual(result["min18"], 5)
        self.assertEqual(result["c18"], 695)

    def test_d_two_month_delay_breaches_before_recovery(self):
        result = model.metrics("D", "U", job_delay=2)
        self.assertEqual(result["first_violation"], (2028, 3))
        self.assertEqual(result["min18"], -35)
        self.assertEqual(result["c18"], 545)

    def test_c_three_month_delay_can_reverse_b_c_ranking(self):
        delayed = model.expected_pv("C", job_delay=3)
        self.assertEqual(delayed, 5968.6)
        self.assertLess(delayed, model.expected_pv("B"))

    def test_icl_outflows_remain_voluntary_assumption(self):
        rows = model.simulate("C", "F")
        self.assertTrue(all(row["debt_cash"] == 0 for row in rows if row["ym"] < (2029, 1)))
        self.assertEqual(sum(row["debt_cash"] for row in rows), 700)


class KnownUnchangedLimitations(unittest.TestCase):
    """Explicit characterization; these passing tests do not fix or endorse defects."""

    def test_long_delay_calendar_bug_is_reproduced(self):
        # Intended 2027-04 + 10 months = 2028-02. Supplied v4 pays in January.
        first = next(row for row in model.simulate("C", "F", job_delay=10) if row["income"] > 0)
        self.assertEqual(first["ym"], (2028, 1))
        self.assertEqual(first["income"], 223.300971)

    def test_job_delay_does_not_move_parttime_start(self):
        for plan, start in [("B", (2027, 2)), ("D", (2027, 8))]:
            first = next(row for row in model.simulate(plan, "U", job_delay=2) if row["income"] > 0)
            self.assertEqual(first["ym"], start)
            self.assertEqual(first["income"], 80)

    def test_out_of_range_weights_are_currently_accepted(self):
        self.assertAlmostEqual(model.expected_pv("B", p=1.2, q=1.5, delta=-.2), 11657.06)


if __name__ == "__main__":
    unittest.main()
