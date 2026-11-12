"""Render deterministic judge-facing SVGs from committed model exports.

No financial calculation or model assumption is changed here. All plotted
values are read from model_summary.json and monthly_cashflows.csv. Run after
scripts/reproduce.py. The standard library is sufficient.
"""
from __future__ import annotations

import argparse
import csv
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAVY = "#142638"
INK = "#22384B"
MUTED = "#637487"
TEAL = "#007F7A"
BLUE = "#3268AB"
AMBER = "#B47A20"
RED = "#B45250"
GRID = "#DFE7ED"
BACKGROUND = "#F5F8FA"
COLORS = {"A": RED, "B": BLUE, "C": TEAL, "D": AMBER}
LABELS = {"A": "A · 전업 수험", "B": "B · 근로 병행", "C": "C · 취업 전환", "D": "D · 조건부 전환"}


def n(value: float) -> str:
    """Compact stable geometry formatting."""
    return f"{value:.2f}".rstrip("0").rstrip(".")


class Figure:
    def __init__(self, height: int, title: str, description: str, dark: bool = False):
        self.height = height
        self.parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 {height}" '
            f'width="1280" height="{height}" role="img" aria-labelledby="title desc" '
            'style="max-width:100%;height:auto">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="desc">{escape(description)}</desc>',
            '<style>text{font-family:"Noto Sans KR","Malgun Gothic",Arial,sans-serif}'
            '.number{font-family:Arial,"Malgun Gothic",sans-serif;font-variant-numeric:tabular-nums}'
            '</style>',
        ]
        self.rect(0, 0, 1280, height, NAVY if dark else "#FFFFFF", radius=20)

    def rect(self, x, y, width, height, fill, radius=0, stroke=None):
        border = f' stroke="{stroke}"' if stroke else ""
        self.parts.append(f'<rect x="{n(x)}" y="{n(y)}" width="{n(width)}" height="{n(height)}" '
                          f'rx="{radius}" fill="{fill}"{border}/>')

    def text(self, x, y, value, size=18, color=INK, weight=400, anchor="start", number=False):
        css = ' class="number"' if number else ""
        self.parts.append(f'<text x="{n(x)}" y="{n(y)}" font-size="{size}" fill="{color}" '
                          f'font-weight="{weight}" text-anchor="{anchor}"{css}>{escape(str(value))}</text>')

    def line(self, x1, y1, x2, y2, color=GRID, width=1, dash=None):
        dashed = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" '
                          f'stroke="{color}" stroke-width="{width}"{dashed}/>')

    def path(self, points, color, width=3, dash=None):
        d = " ".join(("M" if i == 0 else "L") + f"{n(x)},{n(y)}" for i, (x, y) in enumerate(points))
        dashed = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
                          f'stroke-linecap="round" stroke-linejoin="round"{dashed}/>')

    def dot(self, x, y, color, radius=4):
        self.parts.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{radius}" fill="{color}"/>')

    def finish(self):
        return "\n".join(self.parts + ["</svg>"]) + "\n"


def load_exports(input_dir: Path):
    summary = json.loads((input_dir / "model_summary.json").read_text(encoding="utf-8"))
    with (input_dir / "monthly_cashflows.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if summary["amount_unit"] != "10,000 KRW":
        raise ValueError("Expected 10,000 KRW units")
    horizon = summary["short_horizon_months"]
    paths = {}
    for plan in "ABCD":
        selected = [r for r in rows if r["plan"] == plan and r["outcome"] == "U" and int(r["month_index"]) <= horizon]
        if len(selected) != horizon:
            raise ValueError(f"Incomplete short horizon for {plan}/U")
        paths[plan] = [{**r, "raw_cash": float(r["raw_cash"]), "cmin": float(r["cmin"])} for r in selected]
    return summary, rows, paths


def overview(summary, rows):
    au = next(x for x in summary["scenarios"] if x["plan"] == "A" and x["outcome"] == "U")
    pv = summary["weighted_discounted_cashflow_60"]
    f = Figure(514, "합격해도 끝나지 않는다 — 분석의 세 단계",
               "가상 고객의 18개월 유동성, 60개월 조건부 현금흐름, 재현 가능한 근거를 연결한 프로젝트 개요.", dark=True)
    f.text(48, 48, "AFPK YOUNG PLANNER CHALLENGE 2026", 15, "#9BC6CF", 700)
    f.text(48, 112, "합격해도 끝나지 않는다", 43, "#FFFFFF", 700)
    f.text(48, 154, "CPA 2차 유예생의 합격·수습·첫 급여 사이, 소득 공백을 견디는 재무설계", 22, "#D5E2EC")
    f.rect(48, 183, 1184, 1, "#355064")
    cards = [
        ("01", f'{summary["short_horizon_months"]}개월 지급능력', "현금이 버티는가?",
         f'A/U 안전자금 이탈 {au["first_safety_violation_18"].replace("-", ".")}',
         f'미충당액 발생 {au["first_unfunded_month_18"].replace("-", ".")}', "#74CBC3"),
        ("02", f'{summary["long_horizon_months"]}개월 조건부 비교', "어떤 경로가 유리한가?",
         f'C {pv["C"]:,.0f}만 원 · B {pv["B"]:,.0f}만 원',
         "같은 기간·할인율의 현금흐름 현가", "#9FBDE4"),
        ("03", "재현 가능한 근거", "결과를 다시 확인할 수 있는가?",
         f'{len(summary["scenarios"])}개 경로 · {len(rows):,}개 월별 행',
         "가정 원장 → 코드 → 표 → 회귀검증", "#E2BD7E"),
    ]
    for i, (idx, title, question, detail, sub, accent) in enumerate(cards):
        x = 48 + i * 404
        f.rect(x, 212, 376, 218, "#20394D", radius=12)
        f.text(x + 22, 247, idx, 16, accent, 700, number=True)
        f.text(x + 22, 283, title, 25, "#FFFFFF", 700)
        f.text(x + 22, 319, question, 17, "#C4D5E2")
        f.text(x + 22, 365, detail, 19, accent, 700)
        f.text(x + 22, 399, sub, 16, "#C4D5E2")
    f.text(48, 474, "가상 고객·가정값 기반 계산  |  개인 합격확률 예측이나 확정 수익이 아닙니다.", 17, "#B5C7D7")
    return f.finish()


def financial_value(summary):
    pv = summary["weighted_discounted_cashflow_60"]
    f = Figure(574, "60개월 조건부 재무가치 — 기본 가정에서는 C가 우세",
               "초기 가용현금을 포함한 60개월 가중 할인 순현금흐름. "
               + ", ".join(f"{p} {pv[p]:,.3f}만원" for p in "CBDA")
               + ". A는 단기 안전자금 제약을 위반한다.")
    f.text(48, 44, "02 / CONDITIONAL FINANCIAL VALUE", 14, MUTED, 700)
    f.text(48, 90, "기본 가정에서는 C, 선택권 보존 대안은 B", 31, NAVY, 700)
    f.text(48, 125, "초기 현금을 포함한 60개월 가중 할인 순현금흐름 · 단위: 만원", 18, MUTED)
    left, width, top, gap = 236, 690, 168, 73
    maximum = 7500
    statuses = {"C": "재무지표 1위", "B": "응시 기회 유지", "D": "급여 시점에 취약", "A": "안전자금 하한 위반"}
    for i, plan in enumerate("CBDA"):
        y = top + i * gap
        f.text(48, y + 29, LABELS[plan], 20, INK, 700)
        f.rect(left, y, width, 42, BACKGROUND, radius=6)
        f.rect(left, y, width * pv[plan] / maximum, 42, COLORS[plan], radius=6)
        f.text(left + width * pv[plan] / maximum + 13, y + 29, f"{pv[plan]:,.0f}", 22, COLORS[plan], 700, number=True)
        f.text(1006, y + 28, statuses[plan], 17, COLORS[plan], 700)
    f.line(48, 473, 1232, 473)
    weights = summary["weights"]
    f.text(48, 505, f'가정: p={weights["p"]:.2f}, q={weights["q"]:.2f}, B의 Δp={weights["delta_B"]*100:.0f}%p · 연 할인율 {summary["annual_discount_rate"]*100:.0f}%', 17, MUTED)
    f.text(48, 538, "예시 가중치와 가상 임금의 비교입니다. 순자산·확정 수익이 아니며, 응시 기회의 비금전적 가치는 포함하지 않습니다.", 16, MUTED)
    return f.finish()


def liquidity(paths, summary):
    f = Figure(680, "18개월 유동성 — A는 안전자금 이탈 이후 미충당액이 발생",
               "2026년12월부터 2028년5월까지 A/U B/U C/U D/U의 월말 원시 잔액과 안전자금 하한. 음수는 미충당액으로 표시하며 0에서 자르지 않는다. U는 합격 후 수습 미확보 상태이고 대체 취업 시점은 전략마다 다르다.")
    f.text(48, 44, "01 / LIQUIDITY BEFORE VALUE", 14, MUTED, 700)
    f.text(48, 90, "장기 가치보다 먼저, 생활을 유지할 수 있는가", 31, NAVY, 700)
    f.text(48, 125, "18개월 월말 잔액 · U: 합격 후 수습 미확보 + 전략별 대체 취업 경로 · 단위: 만원", 18, MUTED)
    for i, plan in enumerate("ABCD"):
        x = 48 + i * 230
        f.line(x, 160, x + 26, 160, COLORS[plan], 4)
        f.text(x + 38, 166, LABELS[plan], 17, INK, 700)
    f.line(1010, 160, 1036, 160, MUTED, 2, "6 5")
    f.text(1048, 166, "안전자금 하한", 17, MUTED)
    x0, x1, y0, y1 = 92, 1112, 204, 496
    vmin, vmax = -700, 3100
    xp = lambda i: x0 + i / 17 * (x1 - x0)
    yp = lambda value: y1 - (value - vmin) / (vmax - vmin) * (y1 - y0)
    f.rect(x0, yp(0), x1 - x0, y1 - yp(0), "#FFF3F1")
    for value in [-500, 0, 500, 1000, 2000, 3000]:
        y = yp(value)
        f.line(x0, y, x1, y, "#AEBCCA" if value == 0 else GRID, 1.5 if value == 0 else 1)
        f.text(x0 - 17, y + 6, f"{value:,}", 15, MUTED, anchor="end", number=True)
    f.text(x0 + 10, yp(0) + 26, "0 미만 = 미충당액", 14, RED)
    for i in [0, 3, 6, 9, 12, 15, 17]:
        month = paths["A"][i]["ym"]
        f.line(xp(i), y0, xp(i), y1, GRID, 1)
        f.text(xp(i), 526, month[2:].replace("-", "."), 15, MUTED, anchor="middle", number=True)
    floor_points = [(xp(0), yp(paths["A"][0]["cmin"]))]
    for i in range(1, 18):
        if paths["A"][i]["cmin"] != paths["A"][i-1]["cmin"]:
            floor_points.append((xp(i), yp(paths["A"][i-1]["cmin"])))
        floor_points.append((xp(i), yp(paths["A"][i]["cmin"])))
    f.path(floor_points, MUTED, 2, "6 5")
    for plan in "ABCD":
        points = [(xp(i), yp(row["raw_cash"])) for i, row in enumerate(paths[plan])]
        f.path(points, COLORS[plan], 3.5)
        last = paths[plan][-1]["raw_cash"]
        f.dot(xp(17), yp(last), COLORS[plan])
        f.text(x1 + 18, yp(last) + 6, f"{plan} {last:,.0f}", 18, COLORS[plan], 700, number=True)
    # Distinguish the policy reserve breach from the later payment shortfall.
    breach = next((i for i, r in enumerate(paths["A"]) if r["raw_cash"] < r["cmin"]), None)
    unfunded = next((i for i, r in enumerate(paths["A"]) if r["raw_cash"] < 0), None)
    for i, label, x, y in [(breach, "안전자금 이탈", 564, 248), (unfunded, "미충당액 발생", 760, 300)]:
        if i is not None:
            label = paths["A"][i]["ym"][2:].replace("-", ".") + " " + label
            px, py = xp(i), yp(paths["A"][i]["raw_cash"])
            f.line(px, py - 8, x + 78, y + 10, RED, 1.2)
            f.dot(px, py, RED, 5)
            f.rect(x, y - 17, 188, 34, "#FFF3F1", radius=6)
            f.text(x + 12, y + 6, label, 15, RED, 700)
    f.line(48, 557, 1232, 557)
    breach_month = "없음" if breach is None else paths["A"][breach]["ym"].replace("-", ".")
    unfunded_month = "없음" if unfunded is None else paths["A"][unfunded]["ym"].replace("-", ".")
    f.text(48, 591, f"A/U 안전자금 하한 위반: {breach_month} · 미충당액 발생: {unfunded_month}. 두 사건은 서로 다릅니다.", 17, INK, 700)
    f.text(48, 623, "가상 고객·고정 소득경로의 월말 계산입니다. 실제 채용·급여를 보장하지 않으며 월중 지급일까지 검증한 결과는 아닙니다.", 16, MUTED)
    f.text(48, 653, "출처: outputs/tables/monthly_cashflows.csv · 기본 가정: docs/assumptions/BASELINE.md", 14, MUTED)
    return f.finish()


def render(input_dir: Path, output_dir: Path):
    summary, rows, paths = load_exports(input_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    figures = {
        "decision-overview.svg": overview(summary, rows),
        "financial-value.svg": financial_value(summary),
        "liquidity-paths.svg": liquidity(paths, summary),
    }
    for filename, value in figures.items():
        (output_dir / filename).write_text(value, encoding="utf-8", newline="\n")
    return figures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT / "outputs" / "tables")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs" / "figures")
    args = parser.parse_args()
    figures = render(args.input_dir, args.output_dir)
    print(f"Rendered {len(figures)} deterministic SVG figures from model exports; model unchanged.")


if __name__ == "__main__":
    main()
