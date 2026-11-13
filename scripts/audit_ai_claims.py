"""Reproduce an independent audit of imported claims, without AI/model calls.

Amounts are in 10,000 KRW. Source-review notes are authored annotations;
running this script does not re-fetch legislation or approve a financial plan.
"""
import argparse
from collections import Counter
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('apps/demo/ai/evaluations/cpa_experiment_runs.json')
NOTES = Path('ai_evidence/claim_review_notes.json')
OUTPUT = Path('ai_evidence/claim_audit.json')
SOURCE_SHA256 = 'cfae9faa0c1db35da6c482f38346e4438129089986944b09729141c5a5f682a3'


class AuditError(ValueError):
    """Evidence no longer meets the pinned review contract."""


def require(condition, message):
    if not condition:
        raise AuditError(message)


def simulate_original(wage_from=None, grants=False):
    """Original prompt expenses continue after September, unlike v4 A/U."""
    cash = Decimal(1400)
    rows = []
    for index in range(18):
        year, month = divmod(2026 * 12 + 11 + index, 12)
        ym = f'{year:04}-{month + 1:02}'
        family = Decimal(60 if ym <= '2027-02' else 30 if ym <= '2027-08' else 0)
        exam = Decimal(20 if ym <= '2027-06' else 5)
        wage = Decimal(80 if wage_from and ym >= wage_from else 0)
        grant = Decimal(
            (50 if grants and '2027-03' <= ym <= '2027-08' else 0)
            + (20 if grants and '2027-01' <= ym <= '2027-12' else 0)
        )
        cash += family + wage + grant - 120 - exam
        rows.append({
            'ym': ym, 'family': str(family), 'exam': str(exam),
            'wage': str(wage), 'grant': str(grant), 'cash': str(cash),
        })
    return rows


def build_audit(root=ROOT):
    source_bytes = (root / SOURCE).read_bytes()
    digest = hashlib.sha256(source_bytes).hexdigest()
    require(digest == SOURCE_SHA256, 'Imported source changed; review it before updating the pin.')
    runs = json.loads(source_bytes)['runs']
    notes_bytes = (root / NOTES).read_bytes()
    review = json.loads(notes_bytes)
    notes = review['claims']
    require(review['source_sha256'] == digest, 'Review notes refer to another source.')
    require(len(runs) == 8 and sum(len(r['claims']) for r in runs) == 23,
            'Expected eight original outputs and 23 selected claims.')
    base = simulate_original()
    cash = {r['ym']: Decimal(r['cash']) for r in base}
    require([cash[m] for m in ['2027-06', '2027-08', '2027-09']] == [720, 530, 405],
            'Original prompt checkpoints differ.')
    with (root / 'outputs/tables/monthly_cashflows.csv').open(
            encoding='utf-8-sig', newline='') as stream:
        comparable = [r for r in csv.DictReader(stream)
                      if r['plan'] == 'A' and r['outcome'] == 'U' and r['ym'] <= '2027-09']
    require(len(comparable) == 10 and len({r['ym'] for r in comparable}) == 10,
            'Expected ten distinct same-input CSV months.')
    require(all(Decimal(r['raw_cash']) == cash[r['ym']] for r in comparable),
            'Same-input CSV and independent calculation differ.')

    e4 = simulate_original(wage_from='2027-09')
    e5 = simulate_original(wage_from='2027-10', grants=True)
    arithmetic = {
        'E4/c4_end_cash': e4[-1]['cash'],
        'E5/c1_minimum_cash_with_unverified_grants': str(min(Decimal(r['cash']) for r in e5)),
        'E5/c1_total_unverified_grants': str(sum(Decimal(r['grant']) for r in e5)),
        'E6/c1_own_expression': str(80 * 2 + 110 * 6 + 140),
        'E7/c2_december_cash_if_monthly_wage_is_80': next(r['cash'] for r in e4 if r['ym'] == '2027-12'),
        'E8/c1_expenses': str(420 + 560 + 375),
        'E8/c1_september_cash': str(1400 + 360 - (420 + 560 + 375)),
        'E8/c2_own_item_sum': str(1000 + 465 + 13320 - 1600 + 1540),
        'E8/c2_inclusive_months': (2031 - 2026) * 12 + (12 - 12) + 1,
        'E3_unselected_prose_subtotal': str(140 * 7),
    }
    require(arithmetic == review['expected_arithmetic'], 'Authored notes and executed arithmetic differ.')
    results = []
    used_notes = set()
    for ri, run in enumerate(runs):
        for ci, claim in enumerate(run['claims']):
            key = f'{run["experimentId"]}/{claim["id"]}'
            if key in notes:
                used_notes.add(key)
                note = notes[key]
            else:
                require(claim['kind'] == 'cash' and claim.get('strategy') == 'A',
                        'Claim needs an explicit review note: ' + key)
                calculated = cash[claim['month']]
                require(calculated == Decimal(str(claim['aiValue'])) / 10000,
                        'Imported cash claim differs: ' + key)
                note = {
                    'category': 'CALCULATION_MATCH',
                    'evidence': f'{claim["month"]}: {calculated}만원. 같은 입력의 월별 재계산 및 CSV와 일치.',
                    'method': 'EXECUTED_DECIMAL_AND_CSV', 'sources': [],
                }
            results.append({
                'id': f'{run["id"]}/{claim["id"]}',
                'source_pointer': f'/runs/{ri}/claims/{ci}',
                **note,
                'review_author': 'Codex LLM',
                'human_approval': 'NOT_RECORDED',
            })
    require(used_notes == set(notes), 'Review contains unbound claim IDs.')
    require(len({r['id'] for r in results}) == 23, 'Duplicate or missing claim IDs.')
    return {
        'schema_version': 1,
        'source_path': SOURCE.as_posix(), 'source_sha256': digest,
        'review_notes_sha256': hashlib.sha256(notes_bytes).hexdigest(),
        'source_provenance_status': 'IMPORTED_UNREVIEWED',
        'audit_status': 'CODE_RECALCULATED_WITH_AUTHORED_SOURCE_NOTES',
        'provider_invocation': 'NOT_INDEPENDENTLY_VERIFIED',
        'human_approval': 'NOT_RECORDED', 'financial_judgments_written': False,
        'new_api_calls': 0, 'unit': '10,000 KRW',
        'original_output_count': 8, 'selected_claim_count': 23,
        'same_input_csv_rows_compared': 10,
        'csv_comparison_ends': '2027-09',
        'original_prompt_exam_expenses_continue_after_september': True,
        'original_no_income_first_fixed_360_breach': next(r['ym'] for r in base if Decimal(r['cash']) < 360),
        'original_no_income_first_negative_cash': next(r['ym'] for r in base if Decimal(r['cash']) < 0),
        'original_no_income_end_cash': base[-1]['cash'],
        'category_counts': dict(sorted(Counter(r['category'] for r in results).items())),
        'arithmetic': arithmetic, 'results': results,
        'supplementary_findings': review['supplementary_findings'],
        'monthly_original_inputs': base,
        'E5_rows_with_unverified_added_assumptions': e5,
    }


def serialized(audit):
    return json.dumps(audit, ensure_ascii=False, indent=2) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write', action='store_true', help='Regenerate the public code-audit JSON.')
    mode.add_argument('--check', action='store_true', help='Check committed output (the default).')
    args = parser.parse_args()
    try:
        audit = build_audit()
        expected = serialized(audit)
        if args.write:
            (ROOT / OUTPUT).write_text(expected, encoding='utf-8', newline='\n')
        else:
            require((ROOT / OUTPUT).read_text(encoding='utf-8') == expected,
                    'Audit artifact differs. Review inputs, then run --write.')
    except (AuditError, OSError, KeyError, ValueError) as error:
        parser.exit(1, f'Audit failed: {error}\n')
    print('PASS: 8 outputs, 23 selected claims, 10 same-input CSV rows; no API calls or human approval.')


if __name__ == '__main__':
    main()
