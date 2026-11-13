"""Export the unchanged v4 synthetic-case calculations, without external services.

Run from any working directory: python /path/to/repo/scripts/reproduce.py
Amounts are in 10,000 KRW. No output is a verified salary or personal prediction.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from afpk_cpa.financial import model_v4 as model  # noqa: E402


def iso_month(ym):
    return None if ym is None else f"{ym[0]:04d}-{ym[1]:02d}"


def export(output_dir: Path) -> dict:
    """Write deterministic UTF-8 JSON and CSV; no live data or AI calls."""
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries = []
    monthly = []
    for plan in "ABCD":
        for outcome in "PUF":
            result = model.metrics(plan, outcome)
            rows = result["rows"]
            first_negative = next(
                (row["ym"] for row in rows[:18] if row["raw_cash"] < 0), None
            )
            summaries.append({
                "plan": plan,
                "outcome": outcome,
                "cash_18": result["c18"],
                "minimum_safety_margin_18": result["min18"],
                "first_safety_violation_18": iso_month(result["first_violation"]),
                "first_unfunded_month_18": iso_month(first_negative),
                "discounted_cashflow_60": result["pv60"],
                "cash_60": result["c60"],
            })
            for row in rows:
                monthly.append({
                    "plan": plan,
                    "outcome": outcome,
                    **{k: (iso_month(v) if k == "ym" else v) for k, v in row.items()},
                })
    summary = {
        "model": "supplied v4; formulas and assumptions unchanged",
        "status": "synthetic assumptions; not a personal outcome prediction",
        "amount_unit": "10,000 KRW",
        "period_start": iso_month(model.MONTHS[0]),
        "period_end": iso_month(model.MONTHS[-1]),
        "short_horizon_months": 18,
        "long_horizon_months": 60,
        "initial_cash": model.INITIAL_CASH,
        "weights": {"p": model.P_BASE, "q": model.Q_BASE, "delta_B": model.DELTA_BASE},
        "annual_discount_rate": model.DISCOUNT,
        "weighted_discounted_cashflow_60": {
            plan: model.expected_pv(plan) for plan in "ABCD"
        },
        "scenarios": summaries,
        "limitations": [
            "Weights and salaries are hypothetical, not estimated personal probabilities or verified income.",
            "Safety-reserve breach differs from an unfunded payment; monthly rows do not verify within-month timing.",
            "ICL cash outflow is a fixed voluntary assumption, not a statutory repayment calculation.",
            "Calendar rollover for long job_delay inputs is a known unchanged defect.",
            "job_delay does not delay the fixed part-time income start.",
            "No live demo or AI experiment is executed by this script.",
        ],
    }
    (output_dir / "model_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    with (output_dir / "monthly_cashflows.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=list(monthly[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(monthly)
    (output_dir / "sensitivity.json").write_text(
        json.dumps(sensitivity(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )
    return summary


def _short_horizon(plan: str, outcome: str, job_delay: int) -> dict:
    result = model.metrics(plan, outcome, job_delay=job_delay)
    return {
        "plan": plan,
        "outcome": outcome,
        "job_delay_months": job_delay,
        "cash_18": result["c18"],
        "minimum_safety_margin_18": result["min18"],
        "first_safety_violation_18": iso_month(result["first_violation"]),
    }


def _parttime_pay_delay(plan: str, outcome: str, unpaid_months: int) -> dict:
    """Short-horizon stress on top of unchanged v4 rows.

    The first `unpaid_months` part-time paychecks (rows whose v4 income equals
    PARTTIME) are treated as never received; nothing else in the row changes.
    This is a conservative overlay (lost, not deferred pay); the v4 job_delay
    input does not move part-time income, so v4 itself is not modified.
    """
    rows = model.simulate(plan, outcome)[:18]
    cash, skipped = model.INITIAL_CASH, 0
    margins, first_violation, first_unfunded = [], None, None
    for row in rows:
        lost = 0.0
        if skipped < unpaid_months and row["income"] == model.PARTTIME:
            lost, skipped = row["income"], skipped + 1
        cash += row["net"] - lost
        margins.append(cash - row["cmin"])
        if first_violation is None and cash < row["cmin"]:
            first_violation = row["ym"]
        if first_unfunded is None and cash < 0:
            first_unfunded = row["ym"]
    return {
        "plan": plan,
        "outcome": outcome,
        "parttime_unpaid_months": unpaid_months,
        "cash_18": round(cash, 1),
        "minimum_safety_margin_18": round(min(margins), 1),
        "first_safety_violation_18": iso_month(first_violation),
        "first_unfunded_month_18": iso_month(first_unfunded),
    }


def sensitivity() -> dict:
    """Export the documented sensitivity cases by calling unchanged v4 functions.

    No new formula: values are what tests/README already cite, so documents can
    cite one generated file instead of test code. Delay grids stay short because
    long job_delay inputs hit the known calendar-rollover defect.
    """
    base_b = round(model.expected_pv("B"), 3)
    return {
        "model": "supplied v4; formulas and assumptions unchanged",
        "status": "synthetic assumptions; not a personal outcome prediction",
        "amount_unit": "10,000 KRW",
        "base_weights": {"p": model.P_BASE, "q": model.Q_BASE, "delta_B": model.DELTA_BASE},
        "c_first_salary_delay": [
            {
                "job_delay_months": d,
                "weighted_discounted_cashflow_60_C": round(model.expected_pv("C", job_delay=d), 3),
                "base_weighted_discounted_cashflow_60_B": base_b,
                **{k: v for k, v in _short_horizon("C", "F", d).items()
                   if k in ("cash_18", "minimum_safety_margin_18", "first_safety_violation_18")},
            }
            for d in (0, 3, 6)
        ],
        "d_regular_salary_delay_unassigned": [_short_horizon("D", "U", d) for d in (0, 1, 2)],
        "b_pass_condition_drop": [
            {"delta_B": delta, "weighted_discounted_cashflow_60_B": round(model.expected_pv("B", delta=delta), 3)}
            for delta in (0.0, 0.05, 0.10, 0.15)
        ],
        "parttime_first_pay_delay": [
            _parttime_pay_delay(plan, outcome, k)
            for plan in ("B", "D")
            for outcome in ("P", "U", "F")
            for k in range(7)
        ],
        "notes": [
            "parttime_first_pay_delay: first k part-time paychecks (80/month) treated as lost, not deferred; "
            "overlay on unchanged v4 rows, short horizon only. A scenario stress, not a hiring forecast.",
            "job_delay shifts the first regular/CPA salary month only; part-time start is unchanged (known limitation).",
            "Delays are scenario inputs, not forecasts of hiring or salary timing.",
            "delta_B is an assumed drop in the pass-condition weight for part-time study, not measured data.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path, default=REPOSITORY_ROOT / "outputs" / "tables"
    )
    args = parser.parse_args()
    summary = export(args.output_dir)
    print("Synthetic v4 results; amount unit: 10,000 KRW")
    for plan, value in summary["weighted_discounted_cashflow_60"].items():
        print(f"{plan}: {value:.3f}")
    print("Exported 12 scenarios / 720 monthly rows / sensitivity cases to", args.output_dir)


if __name__ == "__main__":
    main()
