"""Render deterministic judge-facing SVGs from committed model exports.

No financial calculation or model assumption is changed here. All plotted
values are read from model_summary.json and monthly_cashflows.csv. Run after
scripts/reproduce.py. The standard library is sufficient.

Visual style: black-and-white minimalist financial report (white page, black
type, thin rules, generous margins) with a single restrained accent reserved
for the conditionally recommended strategy B. Titles state the finding
(action titles); every figure carries unit, period and source lines.
"""
from __future__ import annotations

import argparse
import csv
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INK = "#111111"      # titles, key lines
TEXT = "#2B2B2B"     # body text
MUTED = "#6E6E6E"    # secondary text
RULE = "#D6D6D6"     # grid and hairlines
LIGHT = "#F3F3F3"    # tracks, negative zone
GRAY = "#8A8A8A"     # non-highlighted series
ACCENT = "#1F4E79"   # single point colour: strategy B only
COLORS = {"A": INK, "B": ACCENT, "C": GRAY, "D": GRAY}
DASHES = {"A": None, "B": None, "C": None, "D": "10 6"}
LABELS = {"A": "A · 전업 수험", "B": "B · 근로 병행", "C": "C · 취업 전환", "D": "D · 조건부 전환"}
SOURCE = "자료: 저자 계산(참조 모형 Python v4, 가상 가정)"


def n(value: float) -> str:
    """Compact stable geometry formatting."""
    return f"{value:.2f}".rstrip("0").rstrip(".")


def ym(value: str) -> str:
    return value.replace("-", ".")


class Figure:
    def __init__(self, height: int, title: str, description: str):
        self.height = height
        self.parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 {height}" '
            f'width="1280" height="{height}" role="img" aria-labelledby="title desc" '
            'style="max-width:100%;height:auto">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="desc">{escape(description)}</desc>',
            '<style>text{font-family:"Noto Sans KR","Malgun Gothic","Apple SD Gothic Neo",Arial,sans-serif}'
            '.number{font-family:Arial,"Malgun Gothic",sans-serif;font-variant-numeric:tabular-nums}'
            '</style>',
        ]
        self.rect(0, 0, 1280, height, "#FFFFFF")

    def rect(self, x, y, width, height, fill, radius=0, stroke=None):
        border = f' stroke="{stroke}"' if stroke else ""
        self.parts.append(f'<rect x="{n(x)}" y="{n(y)}" width="{n(width)}" height="{n(height)}" '
                          f'rx="{radius}" fill="{fill}"{border}/>')

    def text(self, x, y, value, size=18, color=TEXT, weight=400, anchor="start", number=False):
        css = ' class="number"' if number else ""
        self.parts.append(f'<text x="{n(x)}" y="{n(y)}" font-size="{size}" fill="{color}" '
                          f'font-weight="{weight}" text-anchor="{anchor}"{css}>{escape(str(value))}</text>')

    def line(self, x1, y1, x2, y2, color=RULE, width=1, dash=None):
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

    def header(self, kicker, title, subtitle):
        """Kicker label, action title and unit/period subtitle above a heavy rule."""
        self.text(56, 52, kicker, 14, MUTED, 700)
        self.text(56, 98, title, 30, INK, 700)
        self.text(56, 134, subtitle, 17, MUTED)
        self.line(56, 158, 1224, 158, INK, 2)

    def footer(self, y, notes):
        self.line(56, y, 1224, y, RULE)
        for i, note in enumerate(notes):
            self.text(56, y + 30 + i * 28, note, 15, MUTED)

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


def pv1(summary):
    """60-month indicators rounded to one decimal, as reported in the text."""
    return {p: round(v + 1e-9, 1) for p, v in summary["weighted_discounted_cashflow_60"].items()}


def overview(summary, rows):
    au = next(x for x in summary["scenarios"] if x["plan"] == "A" and x["outcome"] == "U")
    pv = pv1(summary)
    b_margin = min(x["minimum_safety_margin_18"] for x in summary["scenarios"] if x["plan"] == "B")
    d_margin = min(x["minimum_safety_margin_18"] for x in summary["scenarios"] if x["plan"] == "D")
    f = Figure(560, "합격해도 끝나지 않는다 — 핵심 결과 요약",
               "가상 고객의 18개월 유동성 검사, 60개월 조건부 장기 지표, 재현 근거를 한 장에 요약한다. "
               f"A/U는 {ym(au['first_safety_violation_18'])}에 안전자금 하한을 밑돌고 {ym(au['first_unfunded_month_18'])}에 미충당이 생긴다. "
               f"60개월 지표는 C {pv['C']:,.1f}만 원, B {pv['B']:,.1f}만 원이다.")
    f.text(56, 52, "AFPK YOUNG PLANNER CHALLENGE 2026  ·  B안 가상 고객 사례", 14, MUTED, 700)
    f.text(56, 112, "합격해도 끝나지 않는다", 44, INK, 700)
    f.text(56, 152, "CPA 2차 유예생의 합격·수습·첫 급여 사이, 소득 공백을 견디는 재무설계", 20, TEXT)
    f.line(56, 182, 1224, 182, INK, 3)
    f.text(56, 222, "결론", 15, MUTED, 700)
    f.text(108, 222, "안전자금을 지키는 대안 중, 응시기회 보존을 원하는 고객에게는 B(근로 병행)를 조건부로 우선 검토한다.", 19, INK, 700)
    tiles = [
        ("단기 유동성 · 18개월", "A 전업 수험", ym(au["first_safety_violation_18"]),
         "안전자금 하한 최초 위반", f"미충당 발생 {ym(au['first_unfunded_month_18'])} · 두 사건은 다름", INK),
        ("하한 여유 · 18개월", "B 근로 병행", f"{b_margin:,.0f}만 원",
         "모든 결과 경로의 최소 여유", f"D는 {d_margin:,.0f}만 원으로 얇음", ACCENT),
        ("장기 지표 · 60개월", "C 취업 전환 vs B", f"{pv['C'] - pv['B']:,.1f}만 원",
         f"C {pv['C']:,.1f} − B {pv['B']:,.1f}", "첫 급여 일정에 의존하는 차이", INK),
        ("재현 근거", "참조 모형 v4", f"{len(summary['scenarios'])}경로 · {len(rows):,}행",
         "월별 계산 결과", "가정 원장 → 코드 → 표 → 테스트", INK),
    ]
    for i, (kicker, subject, value, label, sub, color) in enumerate(tiles):
        x = 56 + i * 296
        f.line(x, 262, x + 272, 262, color, 3)
        f.text(x, 292, kicker, 14, MUTED, 700)
        f.text(x, 320, subject, 17, TEXT, 700)
        f.text(x, 374, value, 34, color, 700, number=True)
        f.text(x, 408, label, 15, TEXT)
        f.text(x, 434, sub, 14, MUTED)
    f.footer(476, ["가상 고객·가정값 기반 계산입니다. 개인 합격확률 예측이나 확정 수익이 아닙니다.", SOURCE])
    return f.finish()


def financial_value(summary):
    pv = pv1(summary)
    gap = pv["C"] - pv["B"]
    f = Figure(610, f"C의 장기 지표가 가장 높지만 B와의 차이는 {gap:,.1f}만 원이며 첫 급여 일정에 의존한다",
               "초기 가용현금을 포함한 60개월 가중 할인 순현금흐름. "
               + ", ".join(f"{p} {pv[p]:,.1f}만원" for p in "CBDA")
               + ". A는 단기 안전자금 제약을 위반한다.")
    f.header("장기 조건부 지표 · 60개월",
             f"C의 장기 지표가 가장 높지만, B와의 차이는 {gap:,.1f}만 원이다",
             "가중 할인 순현금흐름(초기 현금 포함) · 2026.12~2031.11 · 단위: 만원")
    left, width, top, gap_y = 250, 640, 196, 70
    maximum = 7500
    for tick in (0, 2500, 5000, 7500):
        x = left + width * tick / maximum
        f.line(x, top - 8, x, top + 4 * gap_y - 20, RULE, 1)
        f.text(x, top + 4 * gap_y + 4, f"{tick:,}", 14, MUTED, anchor="middle", number=True)
    statuses = {"C": "첫 급여 3개월 지연 시 B 아래", "B": "응시기회 유지 · 조건부 우선",
                "D": "급여 시점에 취약", "A": "안전자금 하한 위반 · 제외"}
    for i, plan in enumerate("CBDA"):
        y = top + i * gap_y
        color = ACCENT if plan == "B" else (INK if plan == "C" else GRAY)
        f.text(56, y + 27, LABELS[plan], 19, INK if plan in "BC" else TEXT, 700)
        f.rect(left, y, width, 38, LIGHT)
        f.rect(left, y, width * pv[plan] / maximum, 38, color)
        f.text(left + width * pv[plan] / maximum + 12, y + 27, f"{pv[plan]:,.1f}", 20, color, 700, number=True)
        f.text(1000, y + 26, statuses[plan], 15, ACCENT if plan == "B" else MUTED, 700 if plan == "B" else 400)
    weights = summary["weights"]
    f.footer(506, [
        f'가정: p={weights["p"]:.2f}, q={weights["q"]:.2f}, B의 Δp={weights["delta_B"]*100:.0f}%p, 연 할인율 {summary["annual_discount_rate"]*100:.0f}% (예시 가중치, 개인 확률 아님)',
        "순자산·확정 수익이 아니며, 응시기회의 비금전적 가치는 포함하지 않습니다. " + SOURCE,
    ])
    return f.finish()


def liquidity(paths, summary):
    breach = next((i for i, r in enumerate(paths["A"]) if r["raw_cash"] < r["cmin"]), None)
    unfunded = next((i for i, r in enumerate(paths["A"]) if r["raw_cash"] < 0), None)
    breach_month = "없음" if breach is None else ym(paths["A"][breach]["ym"])
    unfunded_month = "없음" if unfunded is None else ym(paths["A"][unfunded]["ym"])
    f = Figure(720, f"A는 {breach_month}에 안전자금 하한을 밑돌고 {unfunded_month}부터 미충당이 생긴다",
               "2026년12월부터 2028년5월까지 A/U B/U C/U D/U의 월말 원시 잔액과 안전자금 하한. 음수는 미충당액으로 표시하며 0에서 자르지 않는다. U는 합격 후 수습 미확보 상태이고 대체 취업 시점은 전략마다 다르다.")
    f.header("단기 유동성 · 18개월",
             f"A는 {breach_month}에 안전자금 하한을 밑돌고, {unfunded_month}부터 미충당이 생긴다",
             "월말 잔액 · U: 합격 후 수습 미확보 + 전략별 대체 취업 경로 · 2026.12~2028.05 · 단위: 만원")
    for i, plan in enumerate("ABCD"):
        x = 56 + i * 220
        f.line(x, 192, x + 30, 192, COLORS[plan], 3.5 if plan in "AB" else 2.5, DASHES[plan])
        f.text(x + 42, 198, LABELS[plan], 16, TEXT, 700 if plan == "B" else 400)
    f.line(946, 192, 976, 192, INK, 1.5, "2 5")
    f.text(988, 198, "안전자금 하한", 16, TEXT)
    x0, x1, y0, y1 = 100, 1112, 228, 532
    vmin, vmax = -700, 3100
    xp = lambda i: x0 + i / 17 * (x1 - x0)
    yp = lambda value: y1 - (value - vmin) / (vmax - vmin) * (y1 - y0)
    f.rect(x0, yp(0), x1 - x0, y1 - yp(0), LIGHT)
    for value in [-500, 0, 500, 1000, 2000, 3000]:
        y = yp(value)
        f.line(x0, y, x1, y, INK if value == 0 else RULE, 1.2 if value == 0 else 1)
        f.text(x0 - 14, y + 5, f"{value:,}", 14, MUTED, anchor="end", number=True)
    f.text(x0 + 10, yp(0) + 24, "0 미만 = 미충당액", 14, TEXT, 700)
    for i in [0, 3, 6, 9, 12, 15, 17]:
        f.line(xp(i), y1, xp(i), y1 + 6, MUTED, 1)
        f.text(xp(i), y1 + 26, ym(paths["A"][i]["ym"][2:]), 14, MUTED, anchor="middle", number=True)
    floor_points = [(xp(0), yp(paths["A"][0]["cmin"]))]
    for i in range(1, 18):
        if paths["A"][i]["cmin"] != paths["A"][i-1]["cmin"]:
            floor_points.append((xp(i), yp(paths["A"][i-1]["cmin"])))
        floor_points.append((xp(i), yp(paths["A"][i]["cmin"])))
    f.path(floor_points, INK, 1.5, "2 5")
    for plan in "DCAB":  # highlighted series drawn last
        points = [(xp(i), yp(row["raw_cash"])) for i, row in enumerate(paths[plan])]
        f.path(points, COLORS[plan], 3.5 if plan in "AB" else 2.5, DASHES[plan])
        f.dot(xp(17), yp(paths[plan][-1]["raw_cash"]), COLORS[plan])
    # End labels, nudged apart vertically so close values stay legible.
    ends = sorted(((yp(paths[p][-1]["raw_cash"]), p) for p in "ABCD"))
    placed = []
    for y, plan in ends:
        y = max(y, placed[-1] + 24) if placed else y
        placed.append(y)
        last = paths[plan][-1]["raw_cash"]
        f.text(x1 + 16, y + 6, f"{plan} {last:,.0f}", 17, COLORS[plan], 700, number=True)
    # Distinguish the policy reserve breach from the later payment shortfall.
    for i, label, x, y in [(breach, "안전자금 이탈", 560, 262), (unfunded, "미충당액 발생", 760, 318)]:
        if i is not None:
            label = ym(paths["A"][i]["ym"][2:]) + " " + label
            px, py = xp(i), yp(paths["A"][i]["raw_cash"])
            f.line(px, py - 8, x + 80, y + 10, INK, 1)
            f.dot(px, py, INK, 5)
            f.rect(x, y - 17, 176, 32, "#FFFFFF", stroke=INK)
            f.text(x + 12, y + 5, label, 15, INK, 700)
    floors = []
    for row in paths["A"]:
        if not floors or floors[-1] != row["cmin"]:
            floors.append(row["cmin"])
    f.footer(590, [
        f"A/U 안전자금 하한 위반 {breach_month} · 미충당액 발생 {unfunded_month}. 두 사건은 서로 다릅니다. "
        f"하한 {' → '.join(f'{v:,.0f}' for v in floors)}(만원).",
        "가상 고객·고정 소득경로의 월말 계산입니다. 실제 채용·급여를 보장하지 않으며 월중 지급일까지 검증한 결과는 아닙니다.",
        SOURCE,
    ])
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
