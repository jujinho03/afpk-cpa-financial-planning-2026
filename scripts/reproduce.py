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
    return summary


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
    print("Exported 12 scenarios / 720 monthly rows to", args.output_dir)


if __name__ == "__main__":
    main()
