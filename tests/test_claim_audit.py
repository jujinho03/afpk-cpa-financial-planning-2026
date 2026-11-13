"""Reject stale review sources and cross-model input contamination."""
import csv
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('claim_audit', REPO / 'scripts/audit_ai_claims.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class ClaimAuditTests(unittest.TestCase):
    def test_committed_audit_is_reproducible_and_never_grants_human_approval(self):
        result = audit.build_audit()
        self.assertEqual(audit.serialized(result), (REPO / audit.OUTPUT).read_text(encoding='utf-8'))
        raw = json.loads((REPO / audit.SOURCE).read_text(encoding='utf-8'))
        expected_ids = {f'{r["id"]}/{c["id"]}' for r in raw['runs'] for c in r['claims']}
        self.assertEqual({r['id'] for r in result['results']}, expected_ids)
        self.assertTrue(all(r['human_approval'] == 'NOT_RECORDED' for r in result['results']))
        self.assertEqual(result['source_provenance_status'], 'IMPORTED_UNREVIEWED')
        self.assertEqual(result['csv_comparison_ends'], '2027-09')

    def test_changed_source_is_rejected_instead_of_inheriting_old_review(self):
        with tempfile.TemporaryDirectory(dir=REPO, prefix='.test-reproduce-') as directory:
            root = Path(directory)
            source = root / audit.SOURCE
            source.parent.mkdir(parents=True)
            source.write_bytes((REPO / audit.SOURCE).read_bytes() + b'\n')
            with self.assertRaisesRegex(audit.AuditError, 'Imported source changed'):
                audit.build_audit(root)

    def test_same_input_csv_disagreement_is_not_silently_accepted(self):
        with tempfile.TemporaryDirectory(dir=REPO, prefix='.test-reproduce-') as directory:
            root = Path(directory)
            for name in [audit.SOURCE, audit.NOTES, Path('outputs/tables/monthly_cashflows.csv')]:
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(REPO / name, root / name)
            csv_path = root / 'outputs/tables/monthly_cashflows.csv'
            with csv_path.open(encoding='utf-8-sig', newline='') as stream:
                reader = csv.DictReader(stream)
                fields = reader.fieldnames
                rows = list(reader)
            row = next(r for r in rows if r['plan'] == 'A' and r['outcome'] == 'U' and r['ym'] == '2027-09')
            row['raw_cash'] = '406'
            with csv_path.open('w', encoding='utf-8', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(audit.AuditError, 'Same-input CSV'):
                audit.build_audit(root)


if __name__ == '__main__':
    unittest.main()
