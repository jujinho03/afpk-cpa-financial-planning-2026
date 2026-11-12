"""Imported demo assets must survive .gitignore and be loadable without AI keys."""
import json
from pathlib import Path
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
AI=ROOT/'apps/demo/ai'


class DemoResourceTests(unittest.TestCase):
    def test_registered_prompts_and_schemas_exist(self):
        agents=json.loads((AI/'config/agents.json').read_text(encoding='utf-8'))
        referenced={'prompts/analysis/copilot.md'}
        for agent in agents:
            referenced.update(agent[k] for k in ['systemPrompt','taskPrompt','inputSchema','outputSchema'])
        for relative in referenced:
            with self.subTest(path=relative):
                path=(AI/relative).resolve()
                self.assertTrue(path.is_relative_to(AI.resolve()))
                self.assertTrue(path.is_file(),relative)
        for relative in ['prompts/analysis/copilot.md','prompts/analysis/financial_analyst.md','prompts/analysis/risk_detector.md']:
            status=subprocess.run(['git','check-ignore','--no-index','--quiet',str(AI/relative)],cwd=ROOT).returncode
            self.assertEqual(status,1,'Required runtime prompt must not be ignored')

    def test_imported_evidence_retains_required_raw_fields(self):
        records=json.loads((AI/'evaluations/cpa_experiment_runs.json').read_text(encoding='utf-8'))['runs']
        self.assertEqual(len(records),8)
        self.assertEqual({r['experimentId'] for r in records},{f'E{i}' for i in range(1,9)})
        for record in records:
            self.assertTrue(all(record.get(k) for k in ['model','ranAt','systemPrompt','prompt','output']))


if __name__=='__main__':unittest.main()
